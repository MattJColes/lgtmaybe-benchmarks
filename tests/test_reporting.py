from __future__ import annotations

import json
from pathlib import Path

from lgtmaybe_bench.reporting import (
    build_dashboard_data,
    regenerate_reports,
    render_dashboard,
    render_detailed_results,
    render_results,
)


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


def v2_raw(
    timestamp: str,
    model: str,
    *,
    version: str = "lgtmaybe 2.0",
    profile: str = "canonical-v1",
    full_corpus: bool = True,
) -> dict[str, object]:
    result = raw(timestamp, model, True)
    result["schema_version"] = 2
    result["run_id"] = f"run-{model}"
    result["status"] = "complete"
    result["lgtmaybe_version"] = version
    config = result["configuration"]
    assert isinstance(config, dict)
    config.update(
        {
            "suite": "v2",
            "profile": profile,
            "profile_canonical": profile in {"canonical-v1", "canonical-v2"},
            "full_corpus": full_corpus,
        }
    )
    observations = result["observations"]
    assert isinstance(observations, list)
    observation = observations[0]
    assert isinstance(observation, dict)
    observation["observation_id"] = f"obs-{model}"
    ground_truth = observation["ground_truth"]
    assert isinstance(ground_truth, dict)
    ground_truth["language"] = "python"
    ground_truth["clean"] = False
    findings = observation["findings"]
    assert isinstance(findings, list)
    findings[0]["finding_id"] = f"finding-{model}"
    observation["audit"] = {"state": "completed", "path": f"results/audit/{model}.jsonl.gz"}
    return result


def test_render_contains_one_per_lens_table() -> None:
    rendered = render_results([raw("2026-01-01T00:00:00Z", "model", True)])

    header = next(line for line in rendered.splitlines() if line.startswith("| date"))
    assert header == (
        "| date | lgtmaybe version | provider | model | score | false positives | security | "
        "correctness | performance | complexity | tests | documentation | deprecation | intent | "
        "ponytail | spec | settings |"
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


def test_render_counts_every_unmatched_finding_as_a_false_positive() -> None:
    run = raw("2026-01-01T00:00:00Z", "noisy", True)
    observations = run["observations"]
    assert isinstance(observations, list)
    observation = observations[0]
    assert isinstance(observation, dict)
    findings = observation["findings"]
    assert isinstance(findings, list)
    findings.append(
        {
            "file": "other.py",
            "line": 99,
            "severity": "high",
            "title": "Plausible uncatalogued issue",
            "body": "Still a benchmark false positive",
        }
    )

    rendered = render_results([run])
    row = next(line for line in rendered.splitlines() if "noisy" in line)

    assert row.split(" | ")[5] == "1"


def test_render_orders_highest_score_first() -> None:
    rendered = render_results(
        [raw("2026-02-01T00:00:00Z", "low", False), raw("2026-01-01T00:00:00Z", "high", True)]
    )

    assert rendered.index("high") < rendered.index("low")


def test_render_orders_score_ties_newest_first() -> None:
    rendered = render_results(
        [raw("2026-01-01T00:00:00Z", "old", True), raw("2026-02-01T00:00:00Z", "new", True)]
    )

    assert rendered.index("new") < rendered.index("old")


def test_readme_partition_uses_only_newest_complete_canonical_comparison_key() -> None:
    older_key = v2_raw("2026-01-01T00:00:00Z", "old-version", version="lgtmaybe 1.9")
    newest_a = v2_raw("2026-02-02T00:00:00Z", "new-a")
    newest_b = v2_raw("2026-02-01T00:00:00Z", "new-b")
    diagnostic = v2_raw("2026-03-01T00:00:00Z", "diagnostic", profile="diagnostic-full-v1")
    focused = v2_raw("2026-03-02T00:00:00Z", "focused", full_corpus=False)
    incomplete = v2_raw("2026-03-03T00:00:00Z", "incomplete")
    incomplete["status"] = "in_progress"

    rendered = render_results([older_key, newest_a, newest_b, diagnostic, focused, incomplete])

    assert "Comparison key: `v2 / canonical-v1 / lgtmaybe 2.0`" in rendered
    assert "new-a" in rendered
    assert "new-b" in rendered
    assert "old-version" not in rendered
    assert "diagnostic" not in rendered
    assert "focused" not in rendered
    assert "incomplete" not in rendered.split("## Incomplete runs")[0]


def test_v2_leaderboard_exposes_balanced_quality_false_positives_and_audit() -> None:
    run = v2_raw("2026-02-02T00:00:00Z", "model")

    rendered = render_results([run])

    header = next(line for line in rendered.splitlines() if line.startswith("| date"))
    assert header == (
        "| date | provider | model | balanced F1 | balanced recall | precision | "
        "false positives | clean pass | adjudication | audit | settings |"
    )
    row = next(line for line in rendered.splitlines() if line.startswith("| 2026-"))
    assert "100.0%" in row
    assert "| 0 |" in row
    assert "| yes |" in row


def test_canonical_generations_never_mix_and_the_newest_generation_wins() -> None:
    v1_run = v2_raw("2026-03-01T00:00:00Z", "v1-model", profile="canonical-v1")
    v2_old = v2_raw("2026-03-15T00:00:00Z", "v2-old", profile="canonical-v2")
    v2_new = v2_raw("2026-04-01T00:00:00Z", "v2-new", profile="canonical-v2")

    rendered = render_results([v1_run, v2_old, v2_new])

    assert "Comparison key: `v2 / canonical-v2 / lgtmaybe 2.0`" in rendered
    assert "v2-old" in rendered
    assert "v2-new" in rendered
    assert "v1-model" not in rendered


def test_canonical_v1_generation_keeps_ranking_until_v2_runs_exist() -> None:
    v1_run = v2_raw("2026-03-01T00:00:00Z", "v1-model", profile="canonical-v1")

    rendered = render_results([v1_run])

    assert "Comparison key: `v2 / canonical-v1 / lgtmaybe 2.0`" in rendered
    assert "v1-model" in rendered


def test_dashboard_marks_both_canonical_generations() -> None:
    v1_run = v2_raw("2026-03-01T00:00:00Z", "v1-model", profile="canonical-v1")
    v2_run = v2_raw("2026-04-01T00:00:00Z", "v2-model", profile="canonical-v2")

    data = build_dashboard_data([v1_run, v2_run])

    by_model = {run["model"]: run for run in data["runs"]}
    assert by_model["v1-model"]["canonical"] is True
    assert by_model["v2-model"]["canonical"] is True


def test_dashboard_data_is_deterministic_and_keeps_every_run_class() -> None:
    legacy = raw("2026-01-01T00:00:00Z", "legacy", True)
    canonical = v2_raw("2026-02-01T00:00:00Z", "canonical")
    diagnostic = v2_raw("2026-02-02T00:00:00Z", "diagnostic", profile="diagnostic-full-v1")
    focused = v2_raw("2026-02-03T00:00:00Z", "focused", full_corpus=False)
    incomplete = v2_raw("2026-02-04T00:00:00Z", "incomplete")
    incomplete["status"] = "in_progress"
    runs = [legacy, canonical, diagnostic, focused, incomplete]

    first = build_dashboard_data(runs)
    second = build_dashboard_data(list(reversed(runs)))

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    by_model = {run["model"]: run for run in first["runs"]}
    assert set(by_model) == {"legacy", "canonical", "diagnostic", "focused", "incomplete"}
    assert by_model["legacy"]["suite"] == "legacy-v1"
    assert by_model["canonical"]["canonical"] is True
    assert by_model["diagnostic"]["profile"] == "diagnostic-full-v1"
    assert by_model["focused"]["focused"] is True
    assert by_model["incomplete"]["status"] == "in_progress"
    assert by_model["canonical"]["metrics"]["balanced_f1"] == 1.0


def test_dashboard_is_labelled_keyboard_sortable_and_has_a_no_script_fallback() -> None:
    html = render_dashboard({"schema_version": 1, "runs": []})

    for control in (
        "search",
        "suite",
        "profile",
        "version",
        "provider",
        "language",
        "lens",
        "audit",
    ):
        assert f'id="{control}"' in html
    assert html.count('<option value="">') == 7
    assert '<button type="button" data-sort="balanced_f1" data-type="number">' in html
    assert "localeCompare(String(right), undefined, {numeric: true})" in html
    assert 'aria-sort="none"' in html
    assert "setAttribute('aria-sort'" in html
    assert "<noscript><p>JavaScript is disabled." in html
    assert '<a href="../RESULTS.md">RESULTS.md</a>' in html


def test_render_complete_row_uses_iso_date() -> None:
    rendered = render_results([raw("2026-08-14T01:44:23Z", "model", True)])

    assert "| 2026-08-14 |" in rendered
    assert "2026-08-14T01:44:23Z" not in rendered


def test_render_omits_incomplete_run() -> None:
    partial = raw("2026-08-14T01:44:23Z", "interrupted", True)
    partial["status"] = "in_progress"

    rendered = render_results([partial])

    assert rendered == "No benchmark runs recorded.\n"


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


def test_render_excludes_complete_runs_with_failures() -> None:
    failed = raw("2026-02-01T00:00:00Z", "failed-model", False)
    observations = failed["observations"]
    assert isinstance(observations, list)
    observation = observations[0]
    assert isinstance(observation, dict)
    observation["failures"] = 1

    rendered = render_results([raw("2026-01-01T00:00:00Z", "valid-model", True), failed])

    assert "valid-model" in rendered
    assert "failed-model" not in rendered


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


def test_custom_profile_reports_overrides_from_its_named_base() -> None:
    run = v2_raw(
        "2026-01-01T00:00:00Z",
        "custom-profile",
        profile="diagnostic-custom-v1",
    )
    config = run["configuration"]
    assert isinstance(config, dict)
    config.update(
        {
            "base_profile": "canonical-v1",
            "max_tokens": 4096,
            "max_input_tokens": 100_000,
            "preset": "fast",
            "repeats": 1,
            "resolved_profile": {
                "max_tokens": 4096,
                "repeats": 1,
                "preset": "fast",
                "max_input_tokens": 100_000,
                "reasoning_effort": None,
            },
        }
    )

    dashboard = build_dashboard_data([run])

    assert dashboard["runs"][0]["settings"] == "max tokens 4096; repeats 1"


def test_in_progress_run_is_omitted() -> None:
    complete = raw("2026-01-01T00:00:00Z", "finished", True)
    partial = raw("2026-02-01T00:00:00Z", "interrupted", True)
    partial["status"] = "in_progress"

    rendered = render_results([complete, partial])

    assert "finished" in rendered
    assert "interrupted" not in rendered
    assert "Incomplete runs" not in rendered


def test_only_in_progress_runs_render_empty_state() -> None:
    partial = raw("2026-02-01T00:00:00Z", "interrupted", True)
    partial["status"] = "in_progress"

    rendered = render_results([partial])

    assert rendered == "No benchmark runs recorded.\n"


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
    incomplete = raw("2026-01-02T00:00:00Z", "partial", True)
    incomplete["status"] = "in_progress"
    (raw_dir / "partial.json").write_text(json.dumps(incomplete))
    readme = (
        "# Intro\n\nKeep me.\n\n<!-- BENCH_RESULTS_START -->\n"
        "old\n<!-- BENCH_RESULTS_END -->\n\nTail.\n"
    )
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")

    regenerate_reports(tmp_path)
    first_results = (tmp_path / "RESULTS.md").read_bytes()
    first_readme = (tmp_path / "README.md").read_bytes()
    first_dashboard_data = (tmp_path / "dashboard" / "data.json").read_bytes()
    first_dashboard = (tmp_path / "dashboard" / "index.html").read_bytes()
    regenerate_reports(tmp_path)

    assert (tmp_path / "RESULTS.md").read_bytes() == first_results
    assert (tmp_path / "README.md").read_bytes() == first_readme
    assert (tmp_path / "dashboard" / "data.json").read_bytes() == first_dashboard_data
    assert (tmp_path / "dashboard" / "index.html").read_bytes() == first_dashboard
    assert json.loads(first_dashboard_data)["schema_version"] == 1
    assert b"partial" not in first_results
    assert b"partial" in first_dashboard_data
    assert b'id="results-table"' in first_dashboard
    assert b"Keep me." in first_readme
    assert b"Tail." in first_readme


def context_raw(
    timestamp: str,
    model: str,
    *,
    suite: str = "context-v1",
    profile: str = "context-canonical-v1",
    full_corpus: bool = True,
    status: str = "complete",
) -> dict[str, object]:
    defect_truth = {
        "name": "python-context-small-v1",
        "changed_file": "orders/pipeline.py",
        "language": "python",
        "expected": [
            {
                "label": "sql-injection @ first-file",
                "lens": "security",
                "file": "orders/pipeline.py",
                "line": 12,
                "keywords": ["sql"],
            }
        ],
        "forbidden": [],
    }
    clean_truth = {
        "name": "python-context-clean-large-v1",
        "changed_file": "orders/pipeline.py",
        "language": "python",
        "clean": True,
        "clean_trap": "broad refactor with no behaviour change",
        "expected": [],
        "forbidden": [],
    }
    caught = [
        {
            "file": "orders/pipeline.py",
            "line": 12,
            "severity": "high",
            "title": "SQL injection in query",
            "body": "interpolates customer_id into the sql query",
        }
    ]
    return {
        "schema_version": 2,
        "run_id": f"context-{model}",
        "status": status,
        "timestamp": timestamp,
        "lgtmaybe_version": "lgtmaybe 2.0",
        "configuration": {
            "provider": "openrouter",
            "model": model,
            "reasoning_effort": None,
            "max_tokens": None,
            "max_input_tokens": 100_000,
            "preset": "full",
            "api_base": None,
            "concurrency": 1,
            "timeout": 7200,
            "repeats": 1,
            "cases": ["python-context-small-v1", "python-context-clean-large-v1"],
            "suite": suite,
            "profile": profile,
            "profile_canonical": False,
            "full_corpus": full_corpus,
        },
        "observations": [
            {
                "repeat": 1,
                "case": "python-context-small-v1",
                "ground_truth": defect_truth,
                "findings": caught,
                "wall_seconds": 30.0,
                "wall_excluding_truncation_seconds": 30.0,
                "truncation_lenses": [],
                "input_tokens": 4_000,
                "output_tokens": 900,
                "reasoning_tokens": 0,
                "failures": 0,
            },
            {
                "repeat": 1,
                "case": "python-context-clean-large-v1",
                "ground_truth": clean_truth,
                "findings": [],
                "wall_seconds": 60.0,
                "wall_excluding_truncation_seconds": 60.0,
                "truncation_lenses": [],
                "input_tokens": 50_000,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "failures": 0,
            },
        ],
    }


def test_context_scaling_section_renders_per_case_metrics() -> None:
    rendered = render_results([context_raw("2026-08-14T00:00:00Z", "scaler")])

    assert "## Context scaling" in rendered
    lines = [line for line in rendered.splitlines() if line.startswith("|")]
    assert any(
        "scaler" in line
        and "python-context-small-v1" in line
        and "100.0%" in line
        and "4,000" in line
        for line in lines
    )
    assert any(
        "scaler" in line
        and "python-context-clean-large-v1" in line
        and "—" in line
        and "50,000" in line
        for line in lines
    )


def test_context_scaling_section_renders_model_summary() -> None:
    run = context_raw("2026-08-14T00:00:00Z", "scaler")
    observations = run["observations"]
    assert isinstance(observations, list)
    findings = observations[0]["findings"]
    assert isinstance(findings, list)
    findings.append(
        {
            "file": "orders/pipeline.py",
            "line": 200,
            "severity": "medium",
            "title": "Incorrect extra finding",
            "body": "not a planted issue",
        }
    )

    rendered = render_results([run])

    assert (
        "| date | provider | model | score | recall | precision | true positives | "
        "false positives |" in rendered
    )
    assert "| 2026-08-14 | openrouter | scaler | 98.0% | 100.0% | 50.0% | 1 | 1 |" in rendered


def test_context_dashboard_preserves_finding_totals() -> None:
    run = context_raw("2026-08-14T00:00:00Z", "scaler")
    observations = run["observations"]
    assert isinstance(observations, list)
    findings = observations[0]["findings"]
    assert isinstance(findings, list)
    findings.append(
        {
            "file": "orders/pipeline.py",
            "line": 200,
            "severity": "medium",
            "title": "Incorrect extra finding",
            "body": "not a planted issue",
        }
    )

    metrics = build_dashboard_data([run])["runs"][0]["metrics"]

    assert metrics["true_positives"] == 1.0
    assert metrics["false_positives"] == 1.0


def test_context_detailed_results_preserve_finding_totals() -> None:
    run = context_raw("2026-08-14T00:00:00Z", "scaler")

    rendered = render_detailed_results(build_dashboard_data([run]))

    assert "| precision | true positives | false positives |" in rendered
    assert "| 100.0% | 1.0 | 0.0 |" in rendered


def test_context_scaling_section_rendering_is_deterministic() -> None:
    runs = [
        context_raw("2026-08-14T00:00:00Z", "scaler"),
        context_raw("2026-08-13T00:00:00Z", "other"),
    ]

    assert render_results(runs) == render_results(runs)


def test_context_model_summary_ranks_by_score() -> None:
    higher = context_raw("2026-08-13T00:00:00Z", "higher")
    lower = context_raw("2026-08-14T00:00:00Z", "lower")
    observations = lower["observations"]
    assert isinstance(observations, list)
    observations[0]["findings"] = []

    rendered = render_results([lower, higher])
    summary = rendered.split("### Model summary\n\n", 1)[1].split("\n\n### Case detail", 1)[0]

    assert summary.index("higher") < summary.index("lower")


def test_context_scaling_section_excludes_ineligible_runs() -> None:
    focused = context_raw("2026-08-14T00:00:00Z", "focused", full_corpus=False)
    diagnostic = context_raw("2026-08-14T00:00:00Z", "diag", profile="diagnostic-custom-v1")
    incomplete = context_raw("2026-08-14T00:00:00Z", "partial", status="in_progress")

    for run in (focused, diagnostic, incomplete):
        rendered = render_results([run])
        assert "## Context scaling" not in rendered


def test_context_scaling_section_coexists_with_v2_leaderboard() -> None:
    runs = [v2_raw("2026-08-14T00:00:00Z", "ranked"), context_raw("2026-08-14T01:00:00Z", "scaler")]

    rendered = render_results(runs)

    assert "Comparison key: `v2 / canonical-v1 / lgtmaybe 2.0`" in rendered
    assert "## Context scaling" in rendered
