from __future__ import annotations

import json
from pathlib import Path

from lgtmaybe_bench.reporting import regenerate_reports, render_results


def raw(timestamp: str, model: str, caught: bool) -> dict[str, object]:
    findings = (
        [
            {
                "file": "app.py",
                "line": 1,
                "severity": "high",
                "title": "Bug found",
                "body": "details",
            }
        ]
        if caught
        else []
    )
    return {
        "schema_version": 1,
        "timestamp": timestamp,
        "lgtmaybe_version": "lgtmaybe 1.0",
        "configuration": {
            "provider": "ollama",
            "model": model,
            "reasoning_effort": None,
            "max_tokens": None,
            "max_input_tokens": None,
            "preset": "full",
            "api_base": None,
            "concurrency": 1,
            "timeout": 7200,
            "repeats": 3,
            "cases": ["case"],
            "full_corpus": True,
        },
        "observations": [
            {
                "repeat": 1,
                "case": "case",
                "ground_truth": {
                    "name": "case",
                    "changed_file": "app.py",
                    "expected": [
                        {"label": "bug", "lens": "security", "line": 1, "keywords": ["bug"]}
                    ],
                    "forbidden": [],
                },
                "findings": findings,
                "wall_seconds": 10.0,
                "wall_excluding_truncation_seconds": 2.0,
                "truncation_lenses": ["security"],
                "input_tokens": 100,
                "output_tokens": 20,
                "reasoning_tokens": 5,
                "failures": 0,
            }
        ],
    }


def test_render_is_newest_first_and_contains_one_per_lens_table() -> None:
    rendered = render_results(
        [raw("2026-01-01T00:00:00Z", "old", False), raw("2026-02-01T00:00:00Z", "new", True)]
    )

    assert rendered.index("new") < rendered.index("old")
    header = next(line for line in rendered.splitlines() if line.startswith("| date"))
    assert header == (
        "| date | lgtmaybe version | provider | model | score | security | correctness | "
        "performance | complexity | tests | documentation | deprecation | intent | ponytail | "
        "spec | settings |"
    )
    assert sum(line.startswith("|---") for line in rendered.splitlines()) == 1
    assert "100.0%" in rendered
    for removed in (
        "cases",
        "recall",
        "precision",
        "clean",
        "trunc",
        "failures",
        "wall",
        "in_tok",
        "out_tok",
        "reason_tok",
    ):
        assert removed not in header


def test_render_excludes_focused_runs_and_keeps_legacy_full_runs() -> None:
    legacy = raw("2026-01-01T00:00:00Z", "legacy-model", False)
    config = legacy["configuration"]
    assert isinstance(config, dict)
    del config["full_corpus"]
    focused = raw("2026-02-01T00:00:00Z", "focused-model", True)
    focused_config = focused["configuration"]
    assert isinstance(focused_config, dict)
    focused_config["full_corpus"] = False
    full = raw("2026-03-01T00:00:00Z", "full-model", True)

    rendered = render_results([legacy, focused, full])

    assert "legacy-model" in rendered
    assert "full-model" in rendered
    assert "focused-model" not in rendered


def test_default_settings_render_as_dash() -> None:
    rendered = render_results([raw("2026-01-01T00:00:00Z", "defaults", True)])

    row = next(line for line in rendered.splitlines() if "defaults" in line)
    assert row.endswith("| — |")


def test_non_default_settings_render_in_fixed_order() -> None:
    run = raw("2026-01-01T00:00:00Z", "custom", True)
    config = run["configuration"]
    assert isinstance(config, dict)
    config.update(
        {
            "provider": "openai",
            "reasoning_effort": "high",
            "preset": "fast",
            "max_tokens": 512,
            "max_input_tokens": 2000,
            "api_base": "https://example.test/v1",
            "concurrency": 2,
            "repeats": 1,
            "timeout": 30,
        }
    )

    rendered = render_results([run])

    row = next(line for line in rendered.splitlines() if "custom" in line)
    assert row.endswith(
        "| effort high; preset fast; max tokens 512; max input tokens 2000; "
        "api base https://example.test/v1; concurrency 2; repeats 1; timeout 30s |"
    )


def test_in_progress_run_is_listed_but_never_scored() -> None:
    complete = raw("2026-01-01T00:00:00Z", "finished", True)
    partial = raw("2026-02-01T00:00:00Z", "interrupted", True)
    partial["status"] = "in_progress"

    rendered = render_results([complete, partial])

    leaderboard, incomplete = rendered.split("## Incomplete runs")
    assert "interrupted" not in leaderboard
    assert "finished" in leaderboard
    assert "interrupted" in incomplete
    assert "1" in incomplete


def test_only_in_progress_runs_render_without_a_leaderboard() -> None:
    partial = raw("2026-02-01T00:00:00Z", "interrupted", True)
    partial["status"] = "in_progress"

    rendered = render_results([partial])

    assert "No benchmark runs recorded." in rendered
    assert "interrupted" in rendered.split("## Incomplete runs")[1]


def test_status_free_and_complete_runs_render_identically() -> None:
    without_status = raw("2026-01-01T00:00:00Z", "one", True)
    with_status = raw("2026-01-01T00:00:00Z", "one", True)
    with_status["status"] = "complete"

    assert render_results([with_status]) == render_results([without_status])
    assert "Incomplete runs" not in render_results([without_status])


def test_report_regeneration_is_byte_identical_and_bounded(tmp_path: Path) -> None:
    raw_dir = tmp_path / "results" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "one.json").write_text(json.dumps(raw("2026-01-01T00:00:00Z", "one", True)))
    readme = (
        "# Intro\n\nKeep me.\n\n<!-- BENCH_RESULTS_START -->\n"
        "old\n<!-- BENCH_RESULTS_END -->\n\nTail.\n"
    )
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")

    regenerate_reports(tmp_path)
    first_results = (tmp_path / "RESULTS.md").read_bytes()
    first_readme = (tmp_path / "README.md").read_bytes()
    regenerate_reports(tmp_path)

    assert (tmp_path / "RESULTS.md").read_bytes() == first_results
    assert (tmp_path / "README.md").read_bytes() == first_readme
    assert b"Keep me." in first_readme
    assert b"Tail." in first_readme
