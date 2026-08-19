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
    profile: str = "canonical-v2",
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
            "profile_canonical": profile in {"canonical-v2", "canonical-breadth"},
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


def test_readme_merges_prior_versions_into_one_breadth_table() -> None:
    older_key = v2_raw("2026-01-01T00:00:00Z", "old-version", version="lgtmaybe 1.9")
    newest_a = v2_raw("2026-02-02T00:00:00Z", "new-a")
    newest_b = v2_raw("2026-02-01T00:00:00Z", "new-b")
    diagnostic = v2_raw("2026-03-01T00:00:00Z", "diagnostic", profile="diagnostic-full-v1")
    focused = v2_raw("2026-03-02T00:00:00Z", "focused", full_corpus=False)
    incomplete = v2_raw("2026-03-03T00:00:00Z", "incomplete")
    incomplete["status"] = "in_progress"

    rendered = render_results([older_key, newest_a, newest_b, diagnostic, focused, incomplete])

    assert "Comparison key:" not in rendered
    assert "| new-a | lgtmaybe 2.0 |" in rendered
    assert "| new-b | lgtmaybe 2.0 |" in rendered
    assert "| old-version | lgtmaybe 1.9 |" in rendered
    assert rendered.index("new-a") < rendered.index("old-version")
    assert "diagnostic" not in rendered
    assert "focused" not in rendered
    assert "incomplete" not in rendered.split("## Incomplete runs")[0]


def test_readme_ranks_and_limits_across_versions() -> None:
    older = [
        v2_raw(f"2026-01-{day:02d}T00:00:00Z", f"old-{day}", version="lgtmaybe 1.9")
        for day in range(1, 12)
    ]
    newer = [v2_raw(f"2026-02-{day:02d}T00:00:00Z", f"new-{day}") for day in range(1, 12)]

    rendered = render_results(older + newer)
    rows = [line for line in rendered.splitlines() if line.startswith("| 2026-")]

    assert len(rows) == 10
    assert "| new-1 |" not in rendered
    assert not any("| old-" in row for row in rows)
    assert "new-11" in rendered
    assert rendered.index("new-11") < rendered.index("new-2")


def test_v2_leaderboard_exposes_balanced_quality_false_positives_and_audit() -> None:
    run = v2_raw("2026-02-02T00:00:00Z", "model")

    rendered = render_results([run])

    header = next(line for line in rendered.splitlines() if line.startswith("| date"))
    assert header == (
        "| date | provider | model | lgtmaybe | balanced F0.5 | balanced recall | precision | "
        "false positives | clean pass | adjudication | audit | settings |"
    )
    row = next(line for line in rendered.splitlines() if line.startswith("| 2026-"))
    assert "100.0%" in row
    assert "| 0 |" in row
    assert "| yes |" in row


def test_noncanonical_profiles_never_join_the_canonical_partition() -> None:
    canonical = v2_raw("2026-03-15T00:00:00Z", "ranked")
    diagnostic = v2_raw("2026-04-01T00:00:00Z", "diagnostic", profile="diagnostic-custom-v1")

    rendered = render_results([canonical, diagnostic])

    assert "## Breadth — top 10" in rendered
    assert "ranked" in rendered
    assert "diagnostic" not in rendered


def test_dashboard_marks_superseded_and_current_canonical_profiles() -> None:
    stored = v2_raw("2026-03-01T00:00:00Z", "stored-model", profile="canonical-v2")
    renamed = v2_raw("2026-04-01T00:00:00Z", "renamed-model", profile="canonical-breadth")

    data = build_dashboard_data([stored, renamed])

    by_model = {run["model"]: run for run in data["runs"]}
    assert by_model["stored-model"]["canonical"] is True
    assert by_model["renamed-model"]["canonical"] is True
    assert {run["suite"] for run in data["runs"]} == {"breadth"}
    assert {run["profile"] for run in data["runs"]} == {"canonical-breadth"}


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
            "base_profile": "canonical-breadth",
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


def test_diagnostic_override_survives_a_later_change_to_its_base_profile() -> None:
    run = v2_raw("2026-06-01T00:00:00Z", "diag", profile="diagnostic-custom-v1")
    config = run["configuration"]
    assert isinstance(config, dict)
    config.update(
        {
            "base_profile": "canonical-breadth",
            "diagnostic_overrides": ["reasoning_effort"],
            "reasoning_effort": "low",
            "resolved_profile": {
                "reasoning_effort": "low",
                "preset": "full",
                "max_tokens": None,
                "max_input_tokens": None,
                "repeats": 3,
            },
        }
    )

    settings = build_dashboard_data([run])["runs"][0]["settings"]

    assert settings == "effort low (thinking off)"


def test_ineligible_run_is_retained_but_never_scored_or_ranked() -> None:
    ranked = v2_raw("2026-05-01T00:00:00Z", "ranked")
    abandoned = v2_raw("2026-05-02T00:00:00Z", "abandoned")
    abandoned["status"] = "ineligible"
    abandoned["termination"] = {"case": "case", "classification": "timeout", "repeat": 1}
    runs = [ranked, abandoned]

    rendered = render_results(runs)
    data = build_dashboard_data(runs)
    by_model = {run["model"]: run for run in data["runs"]}

    assert "ranked" in rendered
    assert "abandoned" not in rendered
    assert "abandoned" not in render_detailed_results(data)
    assert by_model["abandoned"]["status"] == "ineligible"
    assert by_model["abandoned"]["canonical"] is False
    assert by_model["abandoned"]["metrics"] is None


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


def test_context_readme_omits_case_detail() -> None:
    rendered = render_results([context_raw("2026-08-14T00:00:00Z", "scaler")])

    assert "## Long horizon" in rendered
    assert "### Model summary" in rendered
    assert "### Case detail" not in rendered
    assert "python-context-small-v1" not in rendered


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
        "| date | provider | model | lgtmaybe | score | recall | precision | true positives | "
        "false positives |" in rendered
    )
    assert (
        "| 2026-08-14 | openrouter | scaler | lgtmaybe 2.0 | 55.6% | 100.0% | 50.0% | 1 | 1 |"
        in rendered
    )


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


def test_detailed_outputs_retain_context_case_metrics() -> None:
    data = build_dashboard_data([context_raw("2026-08-14T00:00:00Z", "scaler")])

    cases = data["runs"][0]["context_cases"]
    assert cases[0] == {
        "case": "python-context-small-v1",
        "recall": 1.0,
        "precision": 1.0,
        "findings": 1.0,
        "input_tokens": 4000,
        "output_tokens": 900,
        "truncated": False,
        "wall_seconds": 30.0,
    }
    markdown = render_detailed_results(data)
    assert "## Context case detail" in markdown
    assert (
        "| 2026-08-14 | openrouter | scaler | python-context-small-v1 | 100.0% | 100.0% | "
        "1 | 4,000 | 900 | no | 30.0 |" in markdown
    )
    html = render_dashboard(data)
    assert 'id="context-case-table"' in html
    assert "run.context_cases" in html
    assert "python-context-small-v1" in html


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


def _assert_top_ten(rendered: str) -> None:
    rows = [line for line in rendered.splitlines() if line.startswith("| 2026-")]

    assert len(rows) == 10
    assert "high-10" in rows[0]
    assert "high-0" not in rendered
    assert not any("| low |" in row for row in rows)


def test_context_readme_ranking_shows_top_ten() -> None:
    runs = [
        context_raw(f"2026-01-{index + 1:02d}T00:00:00Z", f"high-{index}") for index in range(11)
    ]
    low = context_raw("2026-01-12T00:00:00Z", "low")
    observations = low["observations"]
    assert isinstance(observations, list)
    observations[0]["findings"] = []

    _assert_top_ten(render_results([*runs, low]))


def test_v2_readme_ranking_shows_top_ten() -> None:
    runs = [v2_raw(f"2026-01-{index + 1:02d}T00:00:00Z", f"high-{index}") for index in range(11)]
    low = v2_raw("2026-01-12T00:00:00Z", "low")
    observations = low["observations"]
    assert isinstance(observations, list)
    observations[0]["findings"] = []

    _assert_top_ten(render_results([*runs, low]))


def test_legacy_readme_ranking_shows_top_ten() -> None:
    runs = [raw(f"2026-01-{index + 1:02d}T00:00:00Z", f"high-{index}", True) for index in range(11)]
    low = raw("2026-01-12T00:00:00Z", "low", False)

    _assert_top_ten(render_results([*runs, low]))


def test_detailed_outputs_keep_rows_excluded_from_readme() -> None:
    runs = [
        context_raw(f"2026-01-{index + 1:02d}T00:00:00Z", f"high-{index}") for index in range(11)
    ]
    low = context_raw("2026-01-12T00:00:00Z", "low")
    observations = low["observations"]
    assert isinstance(observations, list)
    observations[0]["findings"] = []

    data = build_dashboard_data([*runs, low])

    assert len(data["runs"]) == 12
    assert "low" in render_detailed_results(data)
    html = render_dashboard(data)
    assert "low" in html
    assert 'data-sort="true_positives"' in html
    assert "metric(run, 'true_positives')" in html


def test_context_scaling_section_excludes_ineligible_runs() -> None:
    focused = context_raw("2026-08-14T00:00:00Z", "focused", full_corpus=False)
    diagnostic = context_raw("2026-08-14T00:00:00Z", "diag", profile="diagnostic-custom-v1")
    incomplete = context_raw("2026-08-14T00:00:00Z", "partial", status="in_progress")

    for run in (focused, diagnostic, incomplete):
        rendered = render_results([run])
        assert "## Long horizon" not in rendered
        assert build_dashboard_data([run])["runs"][0]["context_cases"] == []


def test_fable_run_uses_exact_model_identity() -> None:
    root = Path(__file__).parents[1]
    raw_path = root / "results/raw/20260815-060621-openrouter-anthropic-claude-fable-5.json"
    run = json.loads(raw_path.read_text(encoding="utf-8"))
    run["_source_path"] = raw_path.relative_to(root).as_posix()
    expected_model = "anthropic/claude-fable-5"
    expected_run_id = "20260815-060621-openrouter-anthropic-claude-fable-5"

    assert run["configuration"]["model"] == expected_model
    assert run["run_id"] == expected_run_id == raw_path.stem
    assert all(
        observation["observation_id"].startswith(f"{expected_run_id}:")
        for observation in run["observations"]
    )
    assert all(
        finding["finding_id"].startswith(f"{expected_run_id}:")
        for observation in run["observations"]
        for finding in observation["findings"]
    )
    dashboard_run = build_dashboard_data([run])["runs"][0]
    assert dashboard_run["model"] == expected_model
    assert dashboard_run["run_id"] == expected_run_id
    assert dashboard_run["raw_path"] == raw_path.relative_to(root).as_posix()


def test_context_scaling_section_coexists_with_breadth_leaderboard() -> None:
    runs = [v2_raw("2026-08-14T00:00:00Z", "ranked"), context_raw("2026-08-14T01:00:00Z", "scaler")]

    rendered = render_results(runs)

    assert "## Breadth — top 10" in rendered
    assert "## Long horizon" in rendered


def test_superseded_context_identifiers_score_identically() -> None:
    stored = context_raw("2026-08-14T00:00:00Z", "scaler")
    renamed = context_raw(
        "2026-08-14T00:00:00Z",
        "scaler",
        suite="long-horizon",
        profile="canonical-long-horizon",
    )

    assert render_results([stored]) == render_results([renamed])
    assert "scaler" in render_results([stored])


def test_superseded_and_current_identifiers_share_one_displayed_name() -> None:
    data = build_dashboard_data(
        [
            context_raw("2026-08-14T00:00:00Z", "stored"),
            context_raw(
                "2026-08-15T00:00:00Z",
                "renamed",
                suite="long-horizon",
                profile="canonical-long-horizon",
            ),
        ]
    )

    assert {run["suite"] for run in data["runs"]} == {"long-horizon"}
    assert {run["profile"] for run in data["runs"]} == {"canonical-long-horizon"}


def test_superseded_breadth_identifiers_rank_together() -> None:
    rendered = render_results(
        [
            v2_raw("2026-03-01T00:00:00Z", "stored", profile="canonical-v2"),
            v2_raw("2026-03-02T00:00:00Z", "renamed", profile="canonical-breadth"),
        ]
    )

    assert "## Breadth — top 10" in rendered
    assert "stored" in rendered
    assert "renamed" in rendered


def test_unrecognised_identifiers_are_preserved() -> None:
    data = build_dashboard_data(
        [
            context_raw(
                "2026-08-14T00:00:00Z",
                "diagnostic",
                suite="some-future-suite",
                profile="diagnostic-custom-v1",
            )
        ]
    )

    assert data["runs"][0]["suite"] == "some-future-suite"
    assert data["runs"][0]["profile"] == "diagnostic-custom-v1"


def test_breadth_section_is_identified_by_suite() -> None:
    rendered = render_results([v2_raw("2026-08-16T00:00:00Z", "ranked")])

    assert "## Breadth — top 10" in rendered
    assert "`breadth`" in rendered
    assert "`canonical-breadth`" in rendered


def test_breadth_section_explains_ranking_order() -> None:
    rendered = render_results([v2_raw("2026-08-16T00:00:00Z", "ranked")])

    assert (
        "Rows are ranked highest to lowest by median balanced F0.5. "
        "The first row is the current leader."
    ) in rendered


def test_long_horizon_section_is_identified_by_suite() -> None:
    rendered = render_results([context_raw("2026-08-16T00:00:00Z", "scaler")])

    assert "## Long horizon — top 10" in rendered
    assert "## Context scaling" not in rendered


def test_both_sections_disclaim_cross_suite_ranking() -> None:
    rendered = render_results(
        [
            v2_raw("2026-08-16T00:00:00Z", "ranked"),
            context_raw("2026-08-16T01:00:00Z", "scaler"),
        ]
    )

    breadth, long_horizon = rendered.split("## Long horizon", 1)
    assert "not comparable" in breadth
    assert "not comparable" in long_horizon
