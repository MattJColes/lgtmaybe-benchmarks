from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
from argparse import Namespace
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from lgtmaybe_bench import runner
from lgtmaybe_bench.cli import build_parser, main, resolve_lgtmaybe_command, resolved_concurrency
from lgtmaybe_bench.reporting import regenerate_reports
from lgtmaybe_bench.runner import (
    CANONICAL_PROFILE_ID,
    RunConfig,
    _parse_uv_tool_version,
    build_case_repo,
    execute_benchmark,
    get_profile,
    parse_review_output,
    read_audit_trace,
    resolve_profile,
    resolve_profile_args,
    run_review,
    save_raw_result,
)
from lgtmaybe_bench.scoring import append_adjudication, parse_case

PROFILE = """== lgtmaybe profile ==
total wall time: 9.0s

call             batch tries   elapsed   in_tok  out_tok think_tok cache_rd cache_wr  error
security             1     1     7.50s      100       20         5        0        0  output_limit
correctness          1     1     1.00s      110       10         0        0        0  -

tokens: 240 billable (210 in / 30 out) across 2 calls
"""

CURRENT_PROFILE = (
    "== lgtmaybe profile ==\n"
    "total wall time: 76.83s\n\n"
    "call             batch tries   elapsed   in_tok  out_tok think_tok  think_% "
    "cache_rd cache_wr  error\n"
    "security             1     1    76.83s    63923     8194      2034      25% "
    "       0        0  ProviderTruncated\n"
)

RUNAWAY_PROFILE = (
    "== lgtmaybe profile ==\n"
    "total wall time: 3980.64s\n\n"
    "call             batch tries   elapsed   in_tok  out_tok think_tok  think_% "
    "cache_rd cache_wr findings  error\n"
    "security             1     1   900.00s    63923    16384      2034      25% "
    "       0        0        -  -\n"
    "correctness          1     1   900.00s    63923    16384      2034      25% "
    "       0        0        -  -\n"
    "performance          1     1   900.00s    63923    16384      2034      25% "
    "       0        0        -  -\n"
    "tests                1     1   900.00s    63923    16384      2034      25% "
    "       0        0        -  -\n"
)


def test_canonical_v1_stays_frozen_as_the_provider_resolved_predecessor() -> None:
    profile = get_profile("canonical-v1")

    assert profile.id == "canonical-v1"
    assert profile.schema_version == 1
    assert profile.canonical is True
    assert profile.repeats == 3
    assert profile.preset == "fast"
    assert profile.max_tokens is None
    assert profile.max_input_tokens == 100_000
    assert profile.reasoning_effort is None
    assert profile.reflect is True
    assert profile.recursive is True
    assert profile.spec_review is True
    assert profile.static_analysis is False
    assert profile.mid_review_retrieval is False


def test_canonical_profile_bounds_provider_output_and_keeps_three_repeats() -> None:
    profile = get_profile(CANONICAL_PROFILE_ID)

    assert profile.id == "canonical-v2"
    assert profile.schema_version == 1
    assert profile.canonical is True
    assert profile.repeats == 3
    assert profile.preset == "fast"
    assert profile.max_tokens == 16_384
    assert profile.max_input_tokens == 100_000
    assert profile.reasoning_effort is None
    assert profile.reflect is True
    assert profile.recursive is True
    assert profile.spec_review is True
    assert profile.static_analysis is False
    assert profile.mid_review_retrieval is False


@pytest.mark.parametrize(
    ("profile_id", "field", "value"),
    [
        ("diagnostic-full-v1", "preset", "full"),
        ("diagnostic-4k-v1", "max_tokens", 4096),
        ("diagnostic-large-diff-v1", "max_input_tokens", 20_000),
    ],
)
def test_diagnostic_profiles_have_versioned_noncanonical_overrides(
    profile_id: str, field: str, value: object
) -> None:
    profile = get_profile(profile_id)

    assert profile.schema_version == 1
    assert profile.canonical is False
    assert profile.repeats == 1
    assert getattr(profile, field) == value


def test_override_of_canonical_profile_gets_diagnostic_identity() -> None:
    resolved = resolve_profile("canonical-v1", {"max_tokens": 4096, "repeats": 1})

    assert resolved.id == "diagnostic-custom-v1"
    assert resolved.base_profile_id == "canonical-v1"
    assert resolved.canonical is False
    assert resolved.max_tokens == 4096
    assert resolved.repeats == 1
    assert resolved.diagnostic_overrides == ("max_tokens", "repeats")


def test_override_of_canonical_v2_gets_diagnostic_identity() -> None:
    resolved = resolve_profile("canonical-v2", {"repeats": 1})

    assert resolved.id == "diagnostic-custom-v1"
    assert resolved.base_profile_id == "canonical-v2"
    assert resolved.canonical is False
    assert resolved.max_tokens == 16_384
    assert resolved.repeats == 1
    assert resolved.diagnostic_overrides == ("repeats",)


def test_profiles_do_not_contain_language_specific_settings() -> None:
    for profile_id in (
        "canonical-v1",
        "canonical-v2",
        "diagnostic-full-v1",
        "diagnostic-4k-v1",
        "diagnostic-large-diff-v1",
    ):
        assert "language" not in get_profile(profile_id).__dataclass_fields__


def test_cli_defaults_and_repeatable_cases() -> None:
    args = build_parser().parse_args(
        ["run", "--provider", "ollama", "--model", "qwen", "--case", "a", "--case", "b"]
    )

    assert args.suite == "v2"
    assert args.profile == "canonical-v2"
    assert args.repeats is None
    assert args.preset is None
    assert args.timeout == 7200
    assert args.case == ["a", "b"]
    assert resolved_concurrency(args.provider, args.concurrency) == 1
    assert resolved_concurrency("openai-compatible", None) == 1
    assert resolved_concurrency("openai", None) == 6


def test_cli_accepts_named_suite_profile_and_focused_cases() -> None:
    args = build_parser().parse_args(
        [
            "run",
            "--provider",
            "ollama",
            "--model",
            "qwen",
            "--suite",
            "v2",
            "--profile",
            "diagnostic-full-v1",
            "--case",
            "python-runtime-safety-v1",
        ]
    )

    assert args.suite == "v2"
    assert args.profile == "diagnostic-full-v1"
    assert args.case == ["python-runtime-safety-v1"]
    assert resolve_profile_args(args).id == "diagnostic-full-v1"


def test_cli_override_changes_canonical_profile_to_diagnostic_identity() -> None:
    args = build_parser().parse_args(
        [
            "run",
            "--provider",
            "openai",
            "--model",
            "gpt",
            "--max-tokens",
            "4096",
            "--repeats",
            "1",
        ]
    )

    profile = resolve_profile_args(args)

    assert profile.id == "diagnostic-custom-v1"
    assert profile.canonical is False
    assert profile.diagnostic_overrides == ("max_tokens", "repeats")


def test_cli_budget_equal_to_canonical_v2_keeps_canonical_identity() -> None:
    args = build_parser().parse_args(
        ["run", "--provider", "openai", "--model", "gpt", "--max-tokens", "16384"]
    )

    profile = resolve_profile_args(args)

    assert profile.id == "canonical-v2"
    assert profile.canonical is True
    assert profile.diagnostic_overrides == ()


def test_v2_matrix_validation_runs_before_lgtmaybe(tmp_path: Path) -> None:
    fake = _bench_workspace(tmp_path)
    manifest = tmp_path / "corpus" / "suites" / "v2.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["cases"].pop()
    manifest.write_text(json.dumps(data), encoding="utf-8")
    called = tmp_path / "lgtmaybe-called"
    fake.write_text(
        f"import pathlib\npathlib.Path({str(called)!r}).write_text('called')\nprint('not json')\n",
        encoding="utf-8",
    )
    args = _bench_args(
        suite="v2",
        profile="canonical-v1",
        case=None,
        repeats=None,
        preset=None,
        reasoning_effort=None,
        max_tokens=None,
        max_input_tokens=None,
    )

    with pytest.raises(ValueError, match="v2 requires 32 cases"):
        execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    assert not called.exists()


def test_uv_tool_version_parser() -> None:
    assert _parse_uv_tool_version("lgtmaybe v1.14.1\n- lgtmaybe\n") == "lgtmaybe 1.14.1"
    assert _parse_uv_tool_version("ruff v0.1\n") is None


def test_cli_rejects_missing_lgtmaybe() -> None:
    with pytest.raises(SystemExit) as error:
        main(["run", "--provider", "ollama", "--model", "fake", "--lgtmaybe", "missing-x"])

    assert error.value.code == 2


def test_cli_pins_the_bootstrapped_lgtmaybe_release(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        shutil, "which", lambda command: "C:/tools/uv.exe" if command == "uv" else None
    )
    calls: list[list[str]] = []
    latest_version = "1.15.0"

    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        package = next((part for part in command if part.startswith("lgtmaybe==")), None)
        version = package.removeprefix("lgtmaybe==") if package else latest_version
        return subprocess.CompletedProcess(command, 0, stdout=f"lgtmaybe {version}\n", stderr="")

    monkeypatch.setattr(subprocess, "run", run)

    command = resolve_lgtmaybe_command(None)
    latest_version = "1.16.0"
    resolved = subprocess.run([*command, "--version"], capture_output=True, text=True)

    assert calls == [
        [
            "C:/tools/uv.exe",
            "tool",
            "run",
            "--refresh-package",
            "lgtmaybe",
            "lgtmaybe@latest",
            "--version",
        ],
        [*command, "--version"],
    ]
    assert command == [
        "C:/tools/uv.exe",
        "tool",
        "run",
        "--from",
        "lgtmaybe==1.15.0",
        "lgtmaybe",
    ]
    assert resolved.stdout == "lgtmaybe 1.15.0\n"


def test_cli_fails_when_latest_lgtmaybe_cannot_be_bootstrapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        shutil, "which", lambda command: "C:/tools/uv.exe" if command == "uv" else None
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 1, stdout="", stderr="failed"
        ),
    )

    with pytest.raises(ValueError, match="latest lgtmaybe release"):
        resolve_lgtmaybe_command(None)


def test_parser_separates_json_and_profile() -> None:
    stdout = (
        json.dumps(
            [
                {
                    "file": "app.py",
                    "line": 4,
                    "severity": "high",
                    "title": "SQL injection",
                    "body": "parameterize the query",
                }
            ]
        )
        + "\n"
        + PROFILE
    )

    findings, profile, calls = parse_review_output(stdout)

    assert findings[0].title == "SQL injection"
    assert profile.startswith("== lgtmaybe profile ==")
    assert calls[0].label == "security"
    assert calls[0].elapsed_seconds == 7.5
    assert calls[0].reasoning_tokens == 5
    assert calls[0].findings is None
    assert calls[0].truncated is True


@pytest.mark.parametrize(
    ("header", "row", "expected_findings"),
    [
        (
            "call batch tries elapsed in_tok out_tok think_tok think_% cache_rd cache_wr error",
            "security 1 1 8.50s 5943 88 72 2% 0 4580 -",
            None,
        ),
        (
            "call batch tries elapsed in_tok out_tok think_tok think_% cache_rd cache_wr "
            "findings error",
            "security 1 1 8.50s 5943 88 72 2% 0 4580 0 -",
            0,
        ),
        (
            "call batch tries elapsed in_tok out_tok think_tok think_% cache_rd cache_wr "
            "findings error",
            "reflect 0 1 1.00s 100 15 0 - 0 0 - -",
            None,
        ),
    ],
)
def test_parser_accepts_additive_profile_columns(
    header: str, row: str, expected_findings: int | None
) -> None:
    _, _, calls = parse_review_output(f"[]\n== lgtmaybe profile ==\n{header}\n{row}\n")

    assert len(calls) == 1
    assert calls[0].findings == expected_findings


def test_parser_retains_every_final_finding_field() -> None:
    finding = {
        "path": "app.py",
        "line": 4,
        "side": "RIGHT",
        "severity": "high",
        "title": "Unsafe query",
        "body": "Use a bound value.",
        "failure_scenario": "An attacker changes the query.",
        "suggestion": "Bind the parameter.",
        "category": "security",
        "confidence": 9,
        "broad": False,
        "anchored": True,
        "anchor": "db.execute(query)",
        "future_schema_field": {"kept": True},
    }

    findings, _, _ = parse_review_output(json.dumps([finding]))

    assert findings[0].raw == finding


def test_checkpoint_and_final_raw_keep_stable_evidence_ids_and_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _bench_workspace(tmp_path)
    snapshots: list[dict[str, Any]] = []
    write = runner.write_raw_result

    def capture(path: Path, data: dict[str, Any]) -> Path:
        snapshots.append(deepcopy(data))
        return write(path, data)

    monkeypatch.setattr(runner, "write_raw_result", capture)
    raw_path = execute_benchmark(tmp_path, _bench_args(), [sys.executable, str(fake)])
    final = json.loads(raw_path.read_text(encoding="utf-8"))

    assert final["run_id"] == raw_path.stem
    assert final["configuration"]["resolved_profile"]["base_profile_id"] == "canonical-v1"
    checkpoint_observation = snapshots[0]["observations"][0]
    final_observation = final["observations"][0]
    assert checkpoint_observation["observation_id"] == final_observation["observation_id"]
    assert (
        checkpoint_observation["findings"][0]["finding_id"]
        == final_observation["findings"][0]["finding_id"]
    )


def test_build_case_repo_produces_committed_diff(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    (case_dir / "base").mkdir(parents=True)
    (case_dir / "changed").mkdir()
    (case_dir / "base" / "app.py").write_text("safe = True\n", encoding="utf-8")
    (case_dir / "changed" / "app.py").write_text("safe = False\n", encoding="utf-8")
    (case_dir / "case.json").write_text("{}", encoding="utf-8")

    repo = build_case_repo(case_dir, tmp_path / "repo")

    diff = subprocess.run(
        ["git", "diff", "--unified=0", "bench-base", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "-safe = True" in diff
    assert "+safe = False" in diff


def test_build_case_repo_detects_equal_size_change_with_preserved_timestamp(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "case"
    (case_dir / "base").mkdir(parents=True)
    (case_dir / "changed").mkdir()
    base = case_dir / "base" / "README.md"
    changed = case_dir / "changed" / "README.md"
    base.write_text("timeout=30\n", encoding="utf-8")
    changed.write_text("timeout=10\n", encoding="utf-8")
    timestamp = 1_700_000_000
    os.utime(base, (timestamp, timestamp))
    os.utime(changed, (timestamp, timestamp))
    (case_dir / "case.json").write_text("{}", encoding="utf-8")

    repo = build_case_repo(case_dir, tmp_path / "repo")

    diff = subprocess.run(
        ["git", "diff", "--unified=0", "bench-base", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "-timeout=30" in diff
    assert "+timeout=10" in diff


def test_run_review_retains_failure_and_truncation(tmp_path: Path) -> None:
    executable = tmp_path / "fake-lgtmaybe.py"
    executable.write_text(
        "import sys\n"
        'print(\'[{"file":"app.py","line":4,"severity":"high",\''
        '      \'"title":"SQL injection","body":"parameterize"}]\')\n'
        f"print({PROFILE!r})\n"
        "raise SystemExit(2)\n",
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    config = RunConfig(
        provider="ollama",
        model="fake",
        reasoning_effort=None,
        max_tokens=None,
        max_input_tokens=None,
        preset="full",
        api_base=None,
        concurrency=1,
        timeout=5,
    )

    observation = run_review(repo, config, ["python", str(executable)])

    assert observation.exit_code == 2
    assert observation.failures == 1
    assert observation.truncation_lenses == ("security",)
    assert observation.input_tokens == 210
    assert observation.wall_excluding_truncation_seconds <= observation.wall_seconds
    assert observation.findings[0].title == "SQL injection"


def test_run_review_parses_current_profile_usage_and_truncation(tmp_path: Path) -> None:
    executable = tmp_path / "fake-lgtmaybe.py"
    executable.write_text(f"print('[]')\nprint({CURRENT_PROFILE!r})\n", encoding="utf-8")
    config = RunConfig("openrouter", "fake", None, None, None, "full", None, 1, 5)

    observation = run_review(tmp_path, config, [sys.executable, str(executable)])

    assert observation.input_tokens == 63_923
    assert observation.output_tokens == 8_194
    assert observation.reasoning_tokens == 2_034
    assert observation.truncation_lenses == ("security",)
    assert observation.calls[0].error == "ProviderTruncated"


def test_run_review_marks_a_call_at_the_output_ceiling_as_truncated(tmp_path: Path) -> None:
    executable = tmp_path / "fake-lgtmaybe.py"
    profile = PROFILE.replace("20         5", "512         5").replace("output_limit", "-")
    executable.write_text(f"print('[]')\nprint({profile!r})\n", encoding="utf-8")
    repo = tmp_path / "repo"
    repo.mkdir()
    config = RunConfig("ollama", "fake", None, 512, None, "full", None, 1, 5)

    observation = run_review(repo, config, [sys.executable, str(executable)])

    assert observation.truncation_lenses == ("security",)
    assert observation.calls[0].truncated is True


def test_canonical_v2_bounds_repeated_ceiling_generations(tmp_path: Path) -> None:
    executable = tmp_path / "fake-lgtmaybe.py"
    recorded = tmp_path / "argv.json"
    executable.write_text(
        "import json, pathlib, sys\n"
        f"pathlib.Path({str(recorded)!r}).write_text(json.dumps(sys.argv), encoding='utf-8')\n"
        "print('[]')\n"
        f"print({RUNAWAY_PROFILE!r})\n",
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    profile = get_profile(CANONICAL_PROFILE_ID)
    config = RunConfig(
        provider="openrouter",
        model="fake",
        reasoning_effort=profile.reasoning_effort,
        max_tokens=profile.max_tokens,
        max_input_tokens=profile.max_input_tokens,
        preset=profile.preset,
        api_base=None,
        concurrency=1,
        timeout=30,
    )

    observation = run_review(repo, config, [sys.executable, str(executable)])
    argv = json.loads(recorded.read_text(encoding="utf-8"))

    assert argv[argv.index("--max-tokens") + 1] == "16384"
    assert len(observation.calls) == 4
    assert all(call.output_tokens == 16_384 and call.truncated for call in observation.calls)
    assert observation.truncation_lenses == ("security", "correctness", "performance", "tests")
    assert observation.wall_excluding_truncation_seconds == 0.0
    assert observation.failures == 0
    assert observation.findings == ()


def test_malformed_output_fails_loudly() -> None:
    with pytest.raises(ValueError, match="valid JSON"):
        parse_review_output("not json")


def test_nonzero_command_retains_malformed_stdout(tmp_path: Path) -> None:
    executable = tmp_path / "failure.py"
    executable.write_text("print('provider failed')\nraise SystemExit(2)\n", encoding="utf-8")
    config = RunConfig("ollama", "fake", None, None, None, "full", None, 1, 5)

    observation = run_review(tmp_path, config, ["python", str(executable)])

    assert observation.exit_code == 2
    assert observation.stdout.strip() == "provider failed"
    assert observation.findings == ()


def test_timeout_is_retained_as_failure(tmp_path: Path) -> None:
    executable = tmp_path / "slow.py"
    executable.write_text("import time\ntime.sleep(2)\n", encoding="utf-8")
    config = RunConfig("ollama", "fake", None, None, None, "full", None, 1, 1)

    observation = run_review(tmp_path, config, ["python", str(executable)])

    assert observation.timed_out is True
    assert observation.exit_code == 124
    assert observation.failures == 1


def test_raw_result_is_atomic_and_does_not_add_secrets(tmp_path: Path) -> None:
    data = {"configuration": {"provider": "ollama"}, "observations": []}

    path = save_raw_result(tmp_path, "2026-08-13T00:00:00Z", "ollama-qwen", data)

    assert json.loads(path.read_text(encoding="utf-8")) == data
    assert not list(tmp_path.glob("*.tmp"))
    assert "api_key" not in path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("status", "expected_state"),
    [("completed", "completed"), ("interrupted", "interrupted"), ("failed", "failed")],
)
def test_reads_terminal_audit_trace_states(
    tmp_path: Path, status: str, expected_state: str
) -> None:
    target = tmp_path / "audit.jsonl"
    target.write_text(
        json.dumps({"schema_version": 1, "event": "run_started"})
        + "\n"
        + json.dumps({"schema_version": 1, "event": "run_finished", "status": status})
        + "\n",
        encoding="utf-8",
    )

    capture = read_audit_trace(target)

    assert capture.state == expected_state
    assert capture.jsonl == target.read_text(encoding="utf-8")
    assert capture.schema_versions == (1,)


def test_reads_valid_partial_audit_prefix(tmp_path: Path) -> None:
    target = tmp_path / "audit.jsonl"
    partial = target.with_name(f"{target.name}.partial")
    partial.write_text(
        json.dumps({"schema_version": 1, "event": "call_started"}) + "\n",
        encoding="utf-8",
    )

    capture = read_audit_trace(target)

    assert capture.state == "partial"
    assert capture.jsonl == partial.read_text(encoding="utf-8")


def test_retains_malformed_and_unavailable_audit_outcomes(tmp_path: Path) -> None:
    target = tmp_path / "audit.jsonl"
    target.write_text('{"schema_version":1}\nnot-json\n', encoding="utf-8")

    malformed = read_audit_trace(target)
    target.unlink()
    unavailable = read_audit_trace(target)
    unsupported = read_audit_trace(None)

    assert malformed.state == "malformed"
    assert malformed.jsonl == '{"schema_version":1}\nnot-json\n'
    assert unavailable.state == "unavailable"
    assert unavailable.jsonl is None
    assert unsupported.state == "unsupported"
    assert unsupported.jsonl is None


def test_compatible_cli_writes_one_hashed_gzip_audit_artifact_per_observation(
    tmp_path: Path,
) -> None:
    fake = _bench_workspace(tmp_path)
    fake.write_text(
        "import json, pathlib, sys\n"
        "if '--version' in sys.argv:\n"
        "    print('lgtmaybe fake-2.0')\n"
        "elif '--help' in sys.argv:\n"
        "    print('--audit-jsonl FILE')\n"
        "else:\n"
        "    audit = pathlib.Path(sys.argv[sys.argv.index('--audit-jsonl') + 1])\n"
        "    events = [\n"
        "        {'schema_version': 1, 'event': 'run_started'},\n"
        "        {'schema_version': 1, 'event': 'candidate_parsed', 'candidate_id': 'c1'},\n"
        "        {'schema_version': 1, 'event': 'run_finished', 'status': 'completed'},\n"
        "    ]\n"
        "    audit.write_text(''.join(json.dumps(event) + '\\n' for event in events))\n"
        "    print(json.dumps([{'file':'app.py','line':2,'severity':'high',"
        "'title':'SQL injection','body':'parameterize interpolated SQL'}]))\n"
        f"    print({PROFILE!r})\n",
        encoding="utf-8",
    )

    raw_path = execute_benchmark(tmp_path, _bench_args(), [sys.executable, str(fake)])
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    audit = raw["observations"][0]["audit"]
    artifact = tmp_path / audit["path"]

    assert audit["state"] == "completed"
    assert audit["schema_versions"] == [1]
    assert artifact.suffixes == [".jsonl", ".gz"]
    assert audit["sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert '"event": "candidate_parsed"' in gzip.decompress(artifact.read_bytes()).decode()


def test_case_parser_accepts_multi_file_entry() -> None:
    case = parse_case(
        {
            "name": "multi",
            "changed_file": "app.py",
            "expected": [
                {"label": "bug", "lens": "spec", "file": "spec.md", "line": 1, "keywords": ["bug"]}
            ],
            "forbidden": [],
        }
    )

    assert case.expected[0].file == "spec.md"


def _bench_workspace(tmp_path: Path) -> Path:
    shutil.copytree("corpus", tmp_path / "corpus")
    (tmp_path / "README.md").write_text(
        "# Bench\n\n<!-- BENCH_RESULTS_START -->\nempty\n<!-- BENCH_RESULTS_END -->\n",
        encoding="utf-8",
    )
    fake = tmp_path / "fake_lgtmaybe.py"
    fake.write_text(
        "import json, pathlib, sys\n"
        "if '--version' in sys.argv:\n"
        "    print('lgtmaybe fake-1.0')\n"
        "elif '--help' in sys.argv:\n"
        "    print('--audit-jsonl FILE')\n"
        "else:\n"
        "    page_case = pathlib.Path('page.py').exists()\n"
        "    audit = pathlib.Path(sys.argv[sys.argv.index('--audit-jsonl') + 1])\n"
        "    target = audit.with_name(audit.name + '.partial') if page_case else audit\n"
        "    status = 'interrupted' if page_case else 'completed'\n"
        "    events = [\n"
        "        {'schema_version': 1, 'event': 'run_started'},\n"
        "        {'schema_version': 1, 'event': 'candidate_parsed', 'candidate_id': 'c1'},\n"
        "        {'schema_version': 1, 'event': 'run_finished', 'status': status},\n"
        "    ]\n"
        "    target.write_text(''.join(json.dumps(event) + '\\n' for event in events))\n"
        "    finding = {\n"
        "        'path': 'page.py' if page_case else 'app.py', 'line': 2, 'side': 'RIGHT',\n"
        "        'severity': 'high', 'title': 'Off-by-one' if page_case else 'SQL injection',\n"
        "        'body': 'last item is skipped' if page_case else "
        "'parameterize interpolated SQL',\n"
        "        'failure_scenario': 'A valid item is omitted.' if page_case else "
        "'Input changes the query.',\n"
        "        'suggestion': 'Include the upper bound.' if page_case else "
        "'Bind the parameter.',\n"
        "        'category': 'correctness' if page_case else 'security', 'confidence': 9,\n"
        "        'broad': False, 'anchored': True, 'anchor': 'range' if page_case else 'execute',\n"
        "    }\n"
        "    print(json.dumps([finding]))\n"
        f"    print({PROFILE!r})\n",
        encoding="utf-8",
    )
    return fake


def _bench_args(**overrides: object) -> Namespace:
    defaults: dict[str, object] = {
        "provider": "ollama",
        "model": "fake",
        "reasoning_effort": "high",
        "max_tokens": 1000,
        "max_input_tokens": 2000,
        "preset": "full",
        "repeats": 1,
        "case": ["sql-injection-basic"],
        "api_base": "http://user:secret@localhost?key=secret",
        "concurrency": 1,
        "timeout": 30,
        "suite": "legacy-v1",
        "profile": "canonical-v1",
    }
    return Namespace(**{**defaults, **overrides})


def test_fake_cli_runs_end_to_end_with_visible_truncation(tmp_path: Path) -> None:
    fake = _bench_workspace(tmp_path)

    raw_path = execute_benchmark(tmp_path, _bench_args(), [sys.executable, str(fake)])

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert raw["configuration"]["full_corpus"] is False
    assert raw["configuration"]["cases"] == ["sql-injection-basic"]
    assert raw["observations"][0]["truncation_lenses"] == ["security"]
    assert raw["observations"][0]["audit"]["state"] == "completed"
    assert raw["observations"][0]["findings"][0]["failure_scenario"]
    assert raw["status"] == "complete"
    assert "secret" not in raw_path.read_text(encoding="utf-8")
    detailed_results = (tmp_path / "RESULTS.md").read_text(encoding="utf-8")
    assert "## All stored runs" in detailed_results
    assert "fake" in detailed_results
    assert "No full benchmark runs recorded." in (tmp_path / "README.md").read_text(
        encoding="utf-8"
    )


def test_fake_cli_retains_completed_and_interrupted_audit_artifacts(tmp_path: Path) -> None:
    fake = _bench_workspace(tmp_path)
    args = _bench_args(case=["sql-injection-basic", "off-by-one-page"])

    raw_path = execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert [observation["audit"]["state"] for observation in raw["observations"]] == [
        "completed",
        "interrupted",
    ]
    for observation in raw["observations"]:
        artifact = tmp_path / observation["audit"]["path"]
        assert artifact.is_file()
        assert '"event": "run_finished"' in gzip.decompress(artifact.read_bytes()).decode()


def test_canonical_fake_cli_connects_evidence_scoring_and_reports(tmp_path: Path) -> None:
    fake = _bench_workspace(tmp_path)
    args = _bench_args(
        suite="v2",
        profile="canonical-v1",
        case=None,
        repeats=None,
        preset=None,
        reasoning_effort=None,
        max_tokens=None,
        max_input_tokens=None,
        api_base=None,
        concurrency=None,
        timeout=7200,
    )

    raw_path = execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert raw["configuration"]["profile"] == "canonical-v1"
    assert raw["configuration"]["profile_canonical"] is True
    assert raw["configuration"]["full_corpus"] is True
    assert len(raw["observations"]) == 32 * 3
    observation = raw["observations"][0]
    finding = observation["findings"][0]
    append_adjudication(
        tmp_path / "results" / "adjudications" / "acceptance.jsonl",
        {
            "event_id": "acceptance-adjudication-1",
            "suite": "v2",
            "run_id": raw["run_id"],
            "observation_id": observation["observation_id"],
            "repeat": observation["repeat"],
            "evidence_kind": "finding",
            "evidence_id": finding["finding_id"],
            "classification": "false_positive",
            "reason": "acceptance fixture intentionally emits an unrelated finding",
            "adjudicator": "benchmark-test",
            "timestamp": "2026-08-14T00:00:00Z",
            "supersedes": None,
        },
    )
    regenerate_reports(tmp_path)

    dashboard_data = json.loads((tmp_path / "dashboard" / "data.json").read_text())
    dashboard_run = next(run for run in dashboard_data["runs"] if run["run_id"] == raw["run_id"])
    audit_path = observation["audit"]["path"]
    assert dashboard_run["canonical"] is True
    assert dashboard_run["metrics"]["adjudication_coverage"] > 0
    assert audit_path in dashboard_run["audit_paths"]
    assert raw_path.relative_to(tmp_path).as_posix() in (tmp_path / "RESULTS.md").read_text()
    assert audit_path in (tmp_path / "RESULTS.md").read_text()
    assert "fake" in (tmp_path / "README.md").read_text()
    assert "RESULTS.md" in (tmp_path / "dashboard" / "index.html").read_text()


def test_invalid_v2_matrix_fails_before_invoking_lgtmaybe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _bench_workspace(tmp_path)
    manifest = tmp_path / "corpus" / "suites" / "v2.json"
    suite = json.loads(manifest.read_text(encoding="utf-8"))
    suite["cases"].pop()
    manifest.write_text(json.dumps(suite), encoding="utf-8")
    monkeypatch.setattr(
        runner,
        "_lgtmaybe_version",
        lambda _: pytest.fail("lgtmaybe was invoked before v2 validation"),
    )

    with pytest.raises(ValueError, match="v2 requires 32 cases"):
        execute_benchmark(
            tmp_path,
            _bench_args(suite="v2", case=None),
            [sys.executable, str(fake)],
        )


def test_late_case_failure_retains_completed_observations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _bench_workspace(tmp_path)
    original = runner.build_case_repo
    calls = {"count": 0}

    def failing_build(case_dir: Path, destination: Path) -> Path:
        calls["count"] += 1
        if calls["count"] == 2:
            raise subprocess.CalledProcessError(1, ["git", "commit"])
        return original(case_dir, destination)

    monkeypatch.setattr(runner, "build_case_repo", failing_build)
    args = _bench_args(case=["sql-injection-basic", "off-by-one-page", "deep-nesting"])

    with pytest.raises(subprocess.CalledProcessError):
        execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    raw_files = list((tmp_path / "results" / "raw").glob("*.json"))
    assert len(raw_files) == 1
    raw = json.loads(raw_files[0].read_text(encoding="utf-8"))
    assert raw["status"] == "in_progress"
    assert [observation["case"] for observation in raw["observations"]] == ["sql-injection-basic"]
    assert "secret" not in raw_files[0].read_text(encoding="utf-8")
    assert not list((tmp_path / "results" / "raw").glob("*.tmp"))


def test_late_version_mismatch_retains_completed_observations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _bench_workspace(tmp_path)
    versions = iter(("lgtmaybe fake-1.0", "lgtmaybe fake-1.0", "lgtmaybe fake-2.0"))
    monkeypatch.setattr(runner, "_lgtmaybe_version", lambda _: next(versions))
    args = _bench_args(case=["sql-injection-basic", "off-by-one-page"])

    with pytest.raises(ValueError, match="lgtmaybe version changed during run"):
        execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    raw_files = list((tmp_path / "results" / "raw").glob("*.json"))
    assert len(raw_files) == 1
    raw = json.loads(raw_files[0].read_text(encoding="utf-8"))
    assert raw["lgtmaybe_version"] == "lgtmaybe fake-1.0"
    assert raw["status"] == "in_progress"
    assert [observation["case"] for observation in raw["observations"]] == ["sql-injection-basic"]


def test_checkpoints_reuse_one_reserved_file(tmp_path: Path) -> None:
    fake = _bench_workspace(tmp_path)
    args = _bench_args(case=["sql-injection-basic", "off-by-one-page"], repeats=2)

    raw_path = execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    assert list((tmp_path / "results" / "raw").glob("*.json")) == [raw_path]
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert len(raw["observations"]) == 4
    assert raw["status"] == "complete"


def test_full_fake_cli_run_records_full_corpus_scope(tmp_path: Path) -> None:
    shutil.copytree("corpus", tmp_path / "corpus")
    (tmp_path / "README.md").write_text(
        "# Bench\n\n<!-- BENCH_RESULTS_START -->\nempty\n<!-- BENCH_RESULTS_END -->\n",
        encoding="utf-8",
    )
    fake = tmp_path / "fake_lgtmaybe.py"
    fake.write_text(
        "import sys\n"
        "if '--version' in sys.argv:\n"
        "    print('lgtmaybe fake-1.0')\n"
        "else:\n"
        "    print('[]')\n"
        f"    print({PROFILE!r})\n",
        encoding="utf-8",
    )
    args = Namespace(
        provider="ollama",
        model="fake",
        reasoning_effort=None,
        max_tokens=None,
        max_input_tokens=None,
        preset="full",
        repeats=1,
        case=None,
        api_base=None,
        concurrency=None,
        timeout=7200,
    )

    raw_path = execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert raw["configuration"]["full_corpus"] is True
    assert len(raw["configuration"]["cases"]) == 20
    assert "## Per-lens recall" in (tmp_path / "RESULTS.md").read_text(encoding="utf-8")
