from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from lgtmaybe_bench.cli import build_parser, main, resolved_concurrency
from lgtmaybe_bench.runner import (
    RunConfig,
    _parse_uv_tool_version,
    build_case_repo,
    execute_benchmark,
    parse_review_output,
    run_review,
    save_raw_result,
)
from lgtmaybe_bench.scoring import parse_case

PROFILE = """== lgtmaybe profile ==
total wall time: 9.0s

call             batch tries   elapsed   in_tok  out_tok think_tok cache_rd cache_wr  error
security             1     1     7.50s      100       20         5        0        0  output_limit
correctness          1     1     1.00s      110       10         0        0        0  -

tokens: 240 billable (210 in / 30 out) across 2 calls
"""


def test_cli_defaults_and_repeatable_cases() -> None:
    args = build_parser().parse_args(
        ["run", "--provider", "ollama", "--model", "qwen", "--case", "a", "--case", "b"]
    )

    assert args.repeats == 3
    assert args.timeout == 7200
    assert args.case == ["a", "b"]
    assert resolved_concurrency(args.provider, args.concurrency) == 1
    assert resolved_concurrency("openai-compatible", None) == 1
    assert resolved_concurrency("openai", None) == 6


def test_uv_tool_version_parser() -> None:
    assert _parse_uv_tool_version("lgtmaybe v1.14.1\n- lgtmaybe\n") == "lgtmaybe 1.14.1"
    assert _parse_uv_tool_version("ruff v0.1\n") is None


def test_cli_rejects_missing_lgtmaybe() -> None:
    with pytest.raises(SystemExit) as error:
        main(["run", "--provider", "ollama", "--model", "fake", "--lgtmaybe", "missing-x"])

    assert error.value.code == 2


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
    assert calls[0].truncated is True


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


def test_fake_cli_runs_end_to_end_with_visible_truncation(tmp_path: Path) -> None:
    shutil.copytree("corpus", tmp_path / "corpus")
    (tmp_path / "README.md").write_text(
        "# Bench\n\n<!-- BENCH_RESULTS_START -->\nempty\n<!-- BENCH_RESULTS_END -->\n",
        encoding="utf-8",
    )
    fake = tmp_path / "fake_lgtmaybe.py"
    fake.write_text(
        "import json, sys\n"
        "if '--version' in sys.argv:\n"
        "    print('lgtmaybe fake-1.0')\n"
        "else:\n"
        "    print(json.dumps([{'file':'app.py','line':2,'severity':'high',"
        "'title':'SQL injection','body':'parameterize interpolated SQL'}]))\n"
        f"    print({PROFILE!r})\n",
        encoding="utf-8",
    )
    args = Namespace(
        provider="ollama",
        model="fake",
        reasoning_effort="high",
        max_tokens=1000,
        max_input_tokens=2000,
        preset="full",
        repeats=1,
        case=["sql-injection-basic"],
        api_base="http://user:secret@localhost?key=secret",
        concurrency=1,
        timeout=30,
    )

    raw_path = execute_benchmark(tmp_path, args, [sys.executable, str(fake)])

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert raw["observations"][0]["truncation_lenses"] == ["security"]
    assert "secret" not in raw_path.read_text(encoding="utf-8")
    assert "100.0%" in (tmp_path / "RESULTS.md").read_text(encoding="utf-8")
    assert "security" in (tmp_path / "README.md").read_text(encoding="utf-8")
