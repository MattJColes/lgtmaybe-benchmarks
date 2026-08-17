"""Git case construction and lgtmaybe subprocess execution."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from lgtmaybe_bench.scoring import Finding, parse_findings

TRUNCATION_MARKERS = ("truncat", "output_limit", "length", "max_tokens")
RAW_IN_PROGRESS = "in_progress"
RAW_COMPLETE = "complete"
RAW_INELIGIBLE = "ineligible"
CANONICAL_PROFILE_ID = "canonical-breadth"
LONG_HORIZON_PROFILE_ID = "canonical-long-horizon"
CANONICAL_MAX_TOKENS = 16_384

# A full-corpus run under either of these profiles publishes a result only when every
# observation is failure-free, so it has nothing left to earn after its first failure.
FAIL_FAST_PROFILE_IDS = frozenset({CANONICAL_PROFILE_ID, LONG_HORIZON_PROFILE_ID})


@dataclass(frozen=True, slots=True)
class ResolvedProfile:
    id: str
    base_profile_id: str
    schema_version: int
    canonical: bool
    repeats: int
    preset: str
    reasoning_effort: str | None
    max_tokens: int | None
    max_input_tokens: int
    reflect: bool
    recursive: bool
    spec_review: bool
    static_analysis: bool
    mid_review_retrieval: bool
    diagnostic_overrides: tuple[str, ...] = ()


def _profile(
    profile_id: str,
    *,
    canonical: bool = False,
    repeats: int = 1,
    preset: str = "fast",
    max_tokens: int | None = None,
    max_input_tokens: int = 100_000,
) -> ResolvedProfile:
    return ResolvedProfile(
        id=profile_id,
        base_profile_id=profile_id,
        schema_version=1,
        canonical=canonical,
        repeats=repeats,
        preset=preset,
        reasoning_effort=None,
        max_tokens=max_tokens,
        max_input_tokens=max_input_tokens,
        reflect=True,
        recursive=True,
        spec_review=True,
        static_analysis=False,
        mid_review_retrieval=False,
    )


PROFILES = {
    CANONICAL_PROFILE_ID: _profile(
        CANONICAL_PROFILE_ID, canonical=True, repeats=3, max_tokens=CANONICAL_MAX_TOKENS
    ),
    LONG_HORIZON_PROFILE_ID: _profile(LONG_HORIZON_PROFILE_ID, repeats=1, preset="full"),
    "diagnostic-full-v1": _profile("diagnostic-full-v1", preset="full"),
    "diagnostic-4k-v1": _profile("diagnostic-4k-v1", max_tokens=4096),
    "diagnostic-large-diff-v1": _profile("diagnostic-large-diff-v1", max_input_tokens=20_000),
}


def get_profile(profile_id: str) -> ResolvedProfile:
    try:
        return PROFILES[profile_id]
    except KeyError as exc:
        raise ValueError(f"unknown profile: {profile_id}") from exc


def resolve_profile(profile_id: str, overrides: dict[str, Any]) -> ResolvedProfile:
    base = get_profile(profile_id)
    allowed = {
        "repeats",
        "preset",
        "reasoning_effort",
        "max_tokens",
        "max_input_tokens",
        "reflect",
        "recursive",
        "spec_review",
        "static_analysis",
        "mid_review_retrieval",
    }
    unknown = sorted(overrides.keys() - allowed)
    if unknown:
        raise ValueError(f"unknown profile override(s): {', '.join(unknown)}")
    changed = tuple(sorted(key for key, value in overrides.items() if getattr(base, key) != value))
    if not changed:
        return base
    values = {key: overrides[key] for key in changed}
    return replace(
        base,
        **values,
        id="diagnostic-custom-v1",
        canonical=False,
        diagnostic_overrides=changed,
    )


def resolve_profile_args(args: Any) -> ResolvedProfile:
    override_names = (
        "repeats",
        "preset",
        "reasoning_effort",
        "max_tokens",
        "max_input_tokens",
    )
    overrides = {
        name: value for name in override_names if (value := getattr(args, name, None)) is not None
    }
    return resolve_profile(getattr(args, "profile", CANONICAL_PROFILE_ID), overrides)


@dataclass(frozen=True, slots=True)
class RunConfig:
    provider: str
    model: str
    reasoning_effort: str | None
    max_tokens: int | None
    max_input_tokens: int | None
    preset: str
    api_base: str | None
    concurrency: int
    timeout: int
    reflect: bool = True
    recursive: bool = True
    spec_review: bool = True
    static_analysis: bool = False
    mid_review_retrieval: bool = False


@dataclass(frozen=True, slots=True)
class ProfileCall:
    label: str
    batch: int
    attempts: int
    elapsed_seconds: float
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    findings: int | None
    error: str | None
    truncated: bool


@dataclass(frozen=True, slots=True)
class AuditCapture:
    state: str
    jsonl: str | None
    schema_versions: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class Observation:
    findings: tuple[Finding, ...]
    stdout: str
    stderr: str
    profile: str
    calls: tuple[ProfileCall, ...]
    wall_seconds: float
    wall_excluding_truncation_seconds: float
    exit_code: int
    timed_out: bool
    failures: int
    failure_class: str | None
    truncation_lenses: tuple[str, ...]
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    audit: AuditCapture


def read_audit_trace(target: Path | None) -> AuditCapture:
    if target is None:
        return AuditCapture("unsupported", None)
    partial = target.with_name(f"{target.name}.partial")
    source = target if target.is_file() else partial if partial.is_file() else None
    if source is None:
        return AuditCapture("unavailable", None)
    serialized = source.read_text(encoding="utf-8")
    try:
        events = [json.loads(line) for line in serialized.splitlines()]
    except json.JSONDecodeError:
        return AuditCapture("malformed", serialized)
    if not events or not all(isinstance(event, dict) for event in events):
        return AuditCapture("malformed", serialized)
    versions = tuple(
        sorted(
            {
                version
                for event in events
                if isinstance((version := event.get("schema_version")), int)
            }
        )
    )
    terminal = events[-1]
    state = (
        str(terminal.get("status"))
        if terminal.get("event") == "run_finished" and terminal.get("status")
        else "partial"
    )
    return AuditCapture(state, serialized, versions)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


def build_case_repo(case_dir: Path, destination: Path) -> Path:
    """Build a two-commit repository and tag its clean base."""
    if destination.exists():
        raise ValueError(f"temporary repository already exists: {destination}")
    shutil.copytree(case_dir / "base", destination)
    _git(destination, "init", "-q")
    _git(destination, "config", "user.name", "lgtmaybe-bench")
    _git(destination, "config", "user.email", "bench@example.invalid")
    _git(destination, "add", ".")
    _git(destination, "commit", "-qm", "clean base")
    _git(destination, "tag", "bench-base")
    shutil.copytree(case_dir / "changed", destination, dirs_exist_ok=True)
    _git(destination, "add", "-A")
    _git(destination, "add", "--renormalize", ".")
    metadata = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    message = metadata.get("commit_message", f"plant {case_dir.name}")
    if not isinstance(message, str) or not message.strip():
        raise ValueError(f"{case_dir.name}: commit_message must be a non-empty string")
    _git(destination, "commit", "-qm", message)
    return destination


def _reported(value: str) -> str:
    """lgtmaybe renders `-` for a count it never received; that call still happened."""
    return "0" if value == "-" else value


def parse_review_output(stdout: str) -> tuple[tuple[Finding, ...], str, tuple[ProfileCall, ...]]:
    decoder = json.JSONDecoder()
    try:
        raw_findings, end = decoder.raw_decode(stdout.lstrip())
    except json.JSONDecodeError as exc:
        raise ValueError("lgtmaybe stdout did not start with valid JSON") from exc
    profile = stdout.lstrip()[end:].strip()
    calls: list[ProfileCall] = []
    columns: list[str] | None = None
    for line in profile.splitlines():
        stripped = line.strip()
        if stripped.startswith("call "):
            columns = stripped.split()
            continue
        if columns is None:
            continue
        fields = stripped.split(maxsplit=len(columns) - 1)
        if len(fields) != len(columns):
            continue
        values = dict(zip(columns, fields, strict=True))
        try:
            raw_error = values["error"]
            error = None if raw_error == "-" else raw_error
            raw_finding_count = values.get("findings")
            calls.append(
                ProfileCall(
                    label=values["call"],
                    batch=int(_reported(values["batch"])),
                    attempts=int(_reported(values["tries"])),
                    elapsed_seconds=float(_reported(values["elapsed"].removesuffix("s"))),
                    input_tokens=int(_reported(values["in_tok"])),
                    output_tokens=int(_reported(values["out_tok"])),
                    reasoning_tokens=int(_reported(values["think_tok"])),
                    cache_read_tokens=int(_reported(values["cache_rd"])),
                    cache_creation_tokens=int(_reported(values["cache_wr"])),
                    findings=(None if raw_finding_count in (None, "-") else int(raw_finding_count)),
                    error=error,
                    truncated=bool(
                        error and any(marker in error.casefold() for marker in TRUNCATION_MARKERS)
                    ),
                )
            )
        except (KeyError, ValueError):
            continue
    return parse_findings(raw_findings), profile, tuple(calls)


def _command(config: RunConfig, executable: list[str], audit_path: Path | None = None) -> list[str]:
    command = [
        *executable,
        "review",
        "--provider",
        config.provider,
        "--model",
        config.model,
        "--base",
        "bench-base",
        "--format",
        "json",
        "--profile",
        "--preset",
        config.preset,
        "--max-concurrency",
        str(config.concurrency),
        "--reflect" if config.reflect else "--no-reflect",
        "--recursive" if config.recursive else "--no-recursive",
        "--spec" if config.spec_review else "--no-spec",
        "--static-analysis" if config.static_analysis else "--no-static-analysis",
        ("--mid-review-retrieval" if config.mid_review_retrieval else "--no-mid-review-retrieval"),
    ]
    options = (
        ("--reasoning-effort", config.reasoning_effort),
        ("--max-tokens", config.max_tokens),
        ("--max-input-tokens", config.max_input_tokens),
        ("--api-base", config.api_base),
    )
    for flag, value in options:
        if value is not None:
            command.extend((flag, str(value)))
    if audit_path is not None:
        command.extend(("--audit-jsonl", str(audit_path)))
    return command


def _failure_class(
    timed_out: bool,
    exit_code: int,
    truncated_calls: tuple[ProfileCall, ...],
    unparseable: bool,
) -> str | None:
    """Name why an observation failed; a truncated call that still exits zero has not."""
    if not (timed_out or exit_code != 0):
        return None
    if timed_out:
        return "timeout"
    if truncated_calls:
        return "truncated_output"
    return "unparseable_output" if unparseable else "nonzero_exit"


def run_review(
    repo: Path,
    config: RunConfig,
    executable: list[str],
    audit_path: Path | None = None,
) -> Observation:
    started = time.perf_counter()
    timed_out = False
    try:
        completed = subprocess.run(
            _command(config, executable, audit_path),
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=config.timeout,
            check=False,
        )
        stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        exit_code = 124
    wall = time.perf_counter() - started
    unparseable = False
    try:
        findings, profile, calls = parse_review_output(stdout) if stdout.strip() else ((), "", ())
    except ValueError:
        if exit_code == 0 and not timed_out:
            raise
        unparseable = True
        findings, profile, calls = (), "", ()
    calls = tuple(
        replace(call, truncated=True)
        if config.max_tokens is not None and call.output_tokens >= config.max_tokens
        else call
        for call in calls
    )
    truncated_calls = tuple(call for call in calls if call.truncated)
    truncated_seconds = sum(call.elapsed_seconds for call in truncated_calls)
    return Observation(
        findings=findings,
        stdout=stdout,
        stderr=stderr,
        profile=profile,
        calls=calls,
        wall_seconds=wall,
        wall_excluding_truncation_seconds=max(0.0, wall - truncated_seconds),
        exit_code=exit_code,
        timed_out=timed_out,
        failures=int(exit_code != 0 or timed_out),
        failure_class=_failure_class(timed_out, exit_code, truncated_calls, unparseable),
        truncation_lenses=tuple(call.label for call in truncated_calls),
        input_tokens=sum(call.input_tokens for call in calls),
        output_tokens=sum(call.output_tokens for call in calls),
        reasoning_tokens=sum(call.reasoning_tokens for call in calls),
        audit=read_audit_trace(audit_path),
    )


def reserve_raw_result_path(directory: Path, timestamp: str, slug: str) -> Path:
    """Claim the single unused path a configuration run writes to for its whole life."""
    directory.mkdir(parents=True, exist_ok=True)
    stamp = timestamp.replace(":", "").replace("-", "").replace("T", "-").replace("Z", "")
    path = directory / f"{stamp}-{slug}.json"
    suffix = 2
    while path.exists():
        path = directory / f"{stamp}-{slug}-{suffix}.json"
        suffix += 1
    return path


def write_raw_result(path: Path, data: dict[str, Any]) -> Path:
    """Replace a raw result atomically so an interrupted write cannot truncate evidence."""
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    temporary.replace(path)
    return path


def save_raw_result(directory: Path, timestamp: str, slug: str, data: dict[str, Any]) -> Path:
    return write_raw_result(reserve_raw_result_path(directory, timestamp, slug), data)


def _jsonable_observation(
    observation: Observation, observation_id: str, audit: dict[str, Any]
) -> dict[str, Any]:
    data = asdict(observation)
    data.pop("audit")
    data["observation_id"] = observation_id
    data["findings"] = [
        {**finding.raw, "finding_id": f"{observation_id}:finding:{index}"}
        for index, finding in enumerate(observation.findings, start=1)
    ]
    data["calls"] = [asdict(call) for call in observation.calls]
    data["audit"] = audit
    return data


def _audit_supported(executable: list[str]) -> bool:
    try:
        help_result = subprocess.run(
            [*executable, "review", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return help_result.returncode == 0 and "--audit-jsonl" in help_result.stdout


def _store_audit(root: Path, observation_id: str, capture: AuditCapture) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "state": capture.state,
        "schema_versions": list(capture.schema_versions),
        "path": None,
        "sha256": None,
    }
    if capture.jsonl is None:
        return metadata
    directory = root / "results" / "audit"
    directory.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", observation_id).strip("-")
    artifact = directory / f"{name}.jsonl.gz"
    compressed = gzip.compress(capture.jsonl.encode(), mtime=0)
    with artifact.open("xb") as stream:
        stream.write(compressed)
    metadata["path"] = artifact.relative_to(root).as_posix()
    metadata["sha256"] = hashlib.sha256(compressed).hexdigest()
    return metadata


def _redact_api_base(value: str | None) -> str | None:
    if value is None:
        return None
    parts = urlsplit(value)
    host = parts.netloc.rsplit("@", 1)[-1]
    return urlunsplit((parts.scheme, host, parts.path, "<redacted>" if parts.query else "", ""))


def _parse_uv_tool_version(output: str) -> str | None:
    match = re.search(r"^lgtmaybe\s+v?([^\s,]+)", output, flags=re.MULTILINE)
    return f"lgtmaybe {match.group(1)}" if match else None


def _lgtmaybe_version(executable: list[str]) -> str:
    direct = subprocess.run(
        [*executable, "--version"], capture_output=True, text=True, timeout=30, check=False
    )
    if direct.returncode == 0 and direct.stdout.strip():
        return direct.stdout.strip()
    uv = shutil.which("uv")
    if uv:
        tools = subprocess.run(
            [uv, "tool", "list"], capture_output=True, text=True, timeout=30, check=False
        )
        parsed = _parse_uv_tool_version(tools.stdout)
        if parsed:
            return parsed
    return "unknown"


def execute_benchmark(root: Path, args: Any, executable: str | list[str]) -> Path:
    """Execute a full configuration run, persist it, and regenerate reports."""
    from lgtmaybe_bench.cli import resolved_concurrency
    from lgtmaybe_bench.corpus import load_suite, select_cases, validate_breadth_matrix
    from lgtmaybe_bench.reporting import regenerate_reports

    suite = load_suite(root / "corpus", getattr(args, "suite", "legacy-v1"))
    if suite.id == "breadth":
        validate_breadth_matrix(suite)
    cases = select_cases(list(suite.cases), args.case)
    profile = resolve_profile_args(args)
    config = RunConfig(
        provider=args.provider,
        model=args.model,
        reasoning_effort=profile.reasoning_effort,
        max_tokens=profile.max_tokens,
        max_input_tokens=profile.max_input_tokens,
        preset=profile.preset,
        api_base=args.api_base,
        concurrency=resolved_concurrency(args.provider, args.concurrency),
        timeout=args.timeout,
        reflect=profile.reflect,
        recursive=profile.recursive,
        spec_review=profile.spec_review,
        static_analysis=profile.static_analysis,
        mid_review_retrieval=profile.mid_review_retrieval,
    )
    executable_parts = [executable] if isinstance(executable, str) else executable
    version = _lgtmaybe_version(executable_parts)
    audit_supported = _audit_supported(executable_parts)
    timestamp = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    observations: list[dict[str, Any]] = []
    full_corpus = args.case is None and len(cases) == len(suite.cases)
    fail_fast = profile.id in FAIL_FAST_PROFILE_IDS and full_corpus

    def record(status: str, termination: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "run_id": run_id,
            "status": status,
            "termination": termination,
            "timestamp": timestamp,
            "lgtmaybe_version": version,
            "configuration": {
                **asdict(config),
                "api_base": _redact_api_base(config.api_base),
                "suite": suite.id,
                "profile": profile.id,
                "base_profile": profile.base_profile_id,
                "profile_schema_version": profile.schema_version,
                "profile_canonical": profile.canonical,
                "diagnostic_overrides": list(profile.diagnostic_overrides),
                "resolved_profile": asdict(profile),
                "audit_available": audit_supported,
                "repeats": profile.repeats,
                "cases": [c.truth.name for c in cases],
                "full_corpus": full_corpus,
            },
            "observations": observations,
        }

    slug = re.sub(r"[^a-z0-9]+", "-", f"{args.provider}-{args.model}".casefold()).strip("-")
    path = reserve_raw_result_path(root / "results" / "raw", timestamp, slug)
    run_id = path.stem
    for repeat in range(1, profile.repeats + 1):
        for case in cases:
            observed_version = _lgtmaybe_version(executable_parts)
            if observed_version != version:
                raise ValueError(
                    "lgtmaybe version changed during run: "
                    f"expected {version}, got {observed_version}"
                )
            with tempfile.TemporaryDirectory(prefix="lgtmaybe-bench-") as temporary:
                temporary_path = Path(temporary)
                repo = build_case_repo(case.path, temporary_path / "repo")
                audit_path = temporary_path / "audit.jsonl" if audit_supported else None
                observation = run_review(repo, config, executable_parts, audit_path)
            observation_id = f"{run_id}:repeat:{repeat}:case:{case.truth.name}"
            observations.append(
                {
                    "repeat": repeat,
                    "case": case.truth.name,
                    "ground_truth": case.raw,
                    **_jsonable_observation(
                        observation,
                        observation_id,
                        _store_audit(root, observation_id, observation.audit),
                    ),
                }
            )
            if fail_fast and observation.failures:
                termination = {
                    "case": case.truth.name,
                    "classification": observation.failure_class,
                    "exit_code": observation.exit_code,
                    "observation_id": observation_id,
                    "repeat": repeat,
                    "timed_out": observation.timed_out,
                }
                write_raw_result(path, record(RAW_INELIGIBLE, termination))
                raise ValueError(
                    "canonical run stopped: "
                    f"{observation.failure_class} in repeat {repeat} case {case.truth.name} "
                    f"(exit {observation.exit_code}); recorded {RAW_INELIGIBLE} in {path.name}"
                )
            write_raw_result(path, record(RAW_IN_PROGRESS))
    write_raw_result(path, record(RAW_COMPLETE))
    regenerate_reports(root)
    return path
