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
            "reasoning_effort": "high",
            "max_tokens": 1000,
            "max_input_tokens": 2000,
            "preset": "full",
            "api_base": "http://localhost:11434",
            "concurrency": 1,
            "timeout": 7200,
            "repeats": 1,
            "cases": ["case"],
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


def test_render_is_newest_first_and_contains_full_metrics() -> None:
    rendered = render_results(
        [raw("2026-01-01T00:00:00Z", "old", False), raw("2026-02-01T00:00:00Z", "new", True)]
    )

    assert rendered.index("new") < rendered.index("old")
    assert "score" in rendered
    assert "precision" in rendered
    assert "high (thinking off)" in rendered
    assert "security" in rendered
    assert "local and hosted wall times are not comparable" in rendered.casefold()
    assert "http://localhost:11434" in rendered
    assert "7200" in rendered
    assert "case" in rendered


def test_render_infers_truncation_from_a_call_at_the_configured_ceiling() -> None:
    run = raw("2026-01-01T00:00:00Z", "ceiling", False)
    observations = run["observations"]
    assert isinstance(observations, list)
    observation = observations[0]
    assert isinstance(observation, dict)
    observation["truncation_lenses"] = []
    observation["wall_excluding_truncation_seconds"] = 10.0
    observation["calls"] = [
        {
            "label": "ponytail",
            "elapsed_seconds": 4.0,
            "output_tokens": 1000,
            "truncated": False,
        }
    ]

    rendered = render_results([run])

    row = next(line for line in rendered.splitlines() if "ceiling" in line)
    assert "| 1.00 | 0.00 | 10.00 | 6.00 |" in row


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
