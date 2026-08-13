"""Git case construction and lgtmaybe subprocess execution."""

from __future__ import annotations

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
CALL_PATTERN = re.compile(
    r"^(?P<label>\S+)\s+(?P<batch>\d+)\s+(?P<tries>\d+)\s+"
    r"(?P<elapsed>[\d.]+)s\s+(?P<input>\d+)\s+(?P<output>\d+)\s+"
    r"(?P<reasoning>\d+)\s+(?P<cache_read>\d+)\s+(?P<cache_write>\d+)\s+"
    r"(?P<error>.+)$"
)


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
    error: str | None
    truncated: bool


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
    truncation_lenses: tuple[str, ...]
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int


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


def parse_review_output(stdout: str) -> tuple[tuple[Finding, ...], str, tuple[ProfileCall, ...]]:
    decoder = json.JSONDecoder()
    try:
        raw_findings, end = decoder.raw_decode(stdout.lstrip())
    except json.JSONDecodeError as exc:
        raise ValueError("lgtmaybe stdout did not start with valid JSON") from exc
    profile = stdout.lstrip()[end:].strip()
    calls: list[ProfileCall] = []
    for line in profile.splitlines():
        match = CALL_PATTERN.match(line.strip())
        if not match:
            continue
        values = match.groupdict()
        raw_error = values["error"].strip()
        error = None if raw_error == "-" else raw_error
        calls.append(
            ProfileCall(
                label=values["label"],
                batch=int(values["batch"]),
                attempts=int(values["tries"]),
                elapsed_seconds=float(values["elapsed"]),
                input_tokens=int(values["input"]),
                output_tokens=int(values["output"]),
                reasoning_tokens=int(values["reasoning"]),
                cache_read_tokens=int(values["cache_read"]),
                cache_creation_tokens=int(values["cache_write"]),
                error=error,
                truncated=bool(
                    error and any(marker in error.casefold() for marker in TRUNCATION_MARKERS)
                ),
            )
        )
    return parse_findings(raw_findings), profile, tuple(calls)


def _command(config: RunConfig, executable: list[str]) -> list[str]:
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
    return command


def run_review(repo: Path, config: RunConfig, executable: list[str]) -> Observation:
    started = time.perf_counter()
    timed_out = False
    try:
        completed = subprocess.run(
            _command(config, executable),
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
    try:
        findings, profile, calls = parse_review_output(stdout) if stdout.strip() else ((), "", ())
    except ValueError:
        if exit_code == 0 and not timed_out:
            raise
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
        truncation_lenses=tuple(call.label for call in truncated_calls),
        input_tokens=sum(call.input_tokens for call in calls),
        output_tokens=sum(call.output_tokens for call in calls),
        reasoning_tokens=sum(call.reasoning_tokens for call in calls),
    )


def save_raw_result(directory: Path, timestamp: str, slug: str, data: dict[str, Any]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = timestamp.replace(":", "").replace("-", "").replace("T", "-").replace("Z", "")
    path = directory / f"{stamp}-{slug}.json"
    suffix = 2
    while path.exists():
        path = directory / f"{stamp}-{slug}-{suffix}.json"
        suffix += 1
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    temporary.replace(path)
    return path


def _jsonable_observation(observation: Observation) -> dict[str, Any]:
    data = asdict(observation)
    data["findings"] = [asdict(finding) for finding in observation.findings]
    data["calls"] = [asdict(call) for call in observation.calls]
    return data


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
    from lgtmaybe_bench.corpus import discover_cases, select_cases
    from lgtmaybe_bench.reporting import regenerate_reports

    cases = select_cases(discover_cases(root / "corpus", require_coverage=True), args.case)
    config = RunConfig(
        provider=args.provider,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        max_tokens=args.max_tokens,
        max_input_tokens=args.max_input_tokens,
        preset=args.preset,
        api_base=args.api_base,
        concurrency=resolved_concurrency(args.provider, args.concurrency),
        timeout=args.timeout,
    )
    executable_parts = [executable] if isinstance(executable, str) else executable
    version = _lgtmaybe_version(executable_parts)
    timestamp = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    observations: list[dict[str, Any]] = []
    for repeat in range(1, args.repeats + 1):
        for case in cases:
            with tempfile.TemporaryDirectory(prefix="lgtmaybe-bench-") as temporary:
                repo = build_case_repo(case.path, Path(temporary) / "repo")
                observation = run_review(repo, config, executable_parts)
            observations.append(
                {
                    "repeat": repeat,
                    "case": case.truth.name,
                    "ground_truth": case.raw,
                    **_jsonable_observation(observation),
                }
            )
    data = {
        "schema_version": 1,
        "timestamp": timestamp,
        "lgtmaybe_version": version,
        "configuration": {
            **asdict(config),
            "api_base": _redact_api_base(config.api_base),
            "repeats": args.repeats,
            "cases": [c.truth.name for c in cases],
        },
        "observations": observations,
    }
    slug = re.sub(r"[^a-z0-9]+", "-", f"{args.provider}-{args.model}".casefold()).strip("-")
    path = save_raw_result(root / "results" / "raw", timestamp, slug, data)
    regenerate_reports(root)
    return path
