"""Rescore raw runs and generate deterministic Markdown reports."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Any

from lgtmaybe_bench.cli import resolved_concurrency
from lgtmaybe_bench.runner import RAW_COMPLETE as COMPLETE
from lgtmaybe_bench.runner import get_profile
from lgtmaybe_bench.scoring import (
    AggregateMetrics,
    CaseScore,
    Range,
    RepeatMetrics,
    SuiteAggregateMetrics,
    SuiteObservation,
    SuiteRepeatMetrics,
    aggregate_repeats,
    aggregate_suite_repeats,
    effort_label,
    load_adjudications,
    overall_score,
    parse_case,
    parse_findings,
    score_case,
    score_suite,
)

START = "<!-- BENCH_RESULTS_START -->"
END = "<!-- BENCH_RESULTS_END -->"
README_RESULT_LIMIT = 10
LENSES = (
    "security",
    "correctness",
    "performance",
    "complexity",
    "tests",
    "documentation",
    "deprecation",
    "intent",
    "ponytail",
    "spec",
)


@dataclass(frozen=True, slots=True)
class ScoredRun:
    raw: dict[str, Any]
    repeats: list[RepeatMetrics]
    per_lens: dict[str, Range]
    clean: bool


@dataclass(frozen=True, slots=True)
class ScoredSuiteRun:
    raw: dict[str, Any]
    repeats: list[SuiteRepeatMetrics]
    aggregate: SuiteAggregateMetrics


def _combine(scores: list[CaseScore]) -> CaseScore:
    caught = sum(score.caught for score in scores)
    planted = sum(score.planted for score in scores)
    forbidden = sum(score.forbidden_hits for score in scores)
    unexpected = sum(score.unexpected for score in scores)
    adjudicable = sum(score.adjudicable for score in scores)
    recall = caught / planted
    precision = 1.0 if adjudicable == 0 else caught / adjudicable
    combined = overall_score(recall, forbidden + unexpected)
    lenses = {lens for score in scores for lens in score.per_lens_counts}
    per_lens_counts: dict[str, tuple[int, int]] = {}
    for lens in lenses:
        lens_caught = sum(score.per_lens_counts.get(lens, (0, 0))[0] for score in scores)
        lens_planted = sum(score.per_lens_counts.get(lens, (0, 0))[1] for score in scores)
        per_lens_counts[lens] = (lens_caught, lens_planted)
    per_lens = {
        lens: lens_caught / lens_planted
        for lens, (lens_caught, lens_planted) in per_lens_counts.items()
    }
    return CaseScore(
        caught,
        planted,
        forbidden,
        unexpected,
        adjudicable,
        recall,
        precision,
        combined,
        forbidden == 0,
        per_lens,
        per_lens_counts,
    )


def _score_run(raw: dict[str, Any]) -> ScoredRun:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for observation in raw["observations"]:
        grouped.setdefault(int(observation["repeat"]), []).append(observation)
    repeats: list[RepeatMetrics] = []
    lens_values: dict[str, list[float]] = {}
    clean = True
    max_tokens = raw["configuration"].get("max_tokens")
    for repeat_observations in grouped.values():
        scores = [
            score_case(parse_case(obs["ground_truth"]), parse_findings(obs["findings"]))
            for obs in repeat_observations
        ]
        combined = _combine(scores)
        clean = clean and combined.clean
        for lens, value in combined.per_lens.items():
            lens_values.setdefault(lens, []).append(value)
        truncation_lenses: list[str] = []
        wall_excluding_truncation = 0.0
        for observation in repeat_observations:
            truncated_calls = [
                call
                for call in observation.get("calls", [])
                if call.get("truncated")
                or (max_tokens is not None and int(call.get("output_tokens", 0)) >= int(max_tokens))
            ]
            truncation_lenses.extend(observation["truncation_lenses"])
            truncation_lenses.extend(str(call["label"]) for call in truncated_calls)
            wall_excluding_truncation += (
                max(
                    0.0,
                    float(observation["wall_seconds"])
                    - sum(float(call["elapsed_seconds"]) for call in truncated_calls),
                )
                if truncated_calls
                else float(observation["wall_excluding_truncation_seconds"])
            )
        repeats.append(
            RepeatMetrics(
                combined,
                sum(float(obs["wall_seconds"]) for obs in repeat_observations),
                wall_excluding_truncation,
                tuple(truncation_lenses),
                sum(int(obs["input_tokens"]) for obs in repeat_observations),
                sum(int(obs["output_tokens"]) for obs in repeat_observations),
                sum(int(obs["reasoning_tokens"]) for obs in repeat_observations),
                sum(int(obs["failures"]) for obs in repeat_observations),
            )
        )
    if not repeats:
        raise ValueError("raw run contains no observations")
    return ScoredRun(
        raw,
        repeats,
        {
            lens: Range(float(median(values)), min(values), max(values))
            for lens, values in lens_values.items()
        },
        clean,
    )


def _score_suite_run(
    raw: dict[str, Any], adjudications: dict[str, str] | None = None
) -> ScoredSuiteRun:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for observation in raw["observations"]:
        grouped.setdefault(int(observation["repeat"]), []).append(observation)
    repeats: list[SuiteRepeatMetrics] = []
    max_tokens = raw["configuration"].get("max_tokens")
    for repeat_observations in grouped.values():
        score = score_suite(
            [
                SuiteObservation(
                    parse_case(observation["ground_truth"]),
                    parse_findings(observation["findings"]),
                )
                for observation in repeat_observations
            ],
            adjudications,
        )
        truncation_lenses: list[str] = []
        wall_excluding_truncation = 0.0
        for observation in repeat_observations:
            truncated_calls = [
                call
                for call in observation.get("calls", [])
                if call.get("truncated")
                or (max_tokens is not None and int(call.get("output_tokens", 0)) >= int(max_tokens))
            ]
            truncation_lenses.extend(observation.get("truncation_lenses", []))
            truncation_lenses.extend(str(call["label"]) for call in truncated_calls)
            wall_excluding_truncation += (
                max(
                    0.0,
                    float(observation["wall_seconds"])
                    - sum(float(call["elapsed_seconds"]) for call in truncated_calls),
                )
                if truncated_calls
                else float(observation["wall_excluding_truncation_seconds"])
            )
        repeats.append(
            SuiteRepeatMetrics(
                score,
                sum(float(observation["wall_seconds"]) for observation in repeat_observations),
                wall_excluding_truncation,
                tuple(truncation_lenses),
                sum(int(observation["input_tokens"]) for observation in repeat_observations),
                sum(int(observation["output_tokens"]) for observation in repeat_observations),
                sum(int(observation["reasoning_tokens"]) for observation in repeat_observations),
                sum(int(observation["failures"]) for observation in repeat_observations),
            )
        )
    if not repeats:
        raise ValueError("raw run contains no observations")
    return ScoredSuiteRun(raw, repeats, aggregate_suite_repeats(repeats))


def _range(value: Any, *, percent: bool = False) -> str:
    scale = 100 if percent else 1
    suffix = "%" if percent else ""
    digits = 1 if percent else 2
    med = f"{value.median * scale:.{digits}f}{suffix}"
    if value.minimum == value.maximum:
        return med
    return f"{med} [{value.minimum * scale:.{digits}f}–{value.maximum * scale:.{digits}f}{suffix}]"


def _iso_date(timestamp: str) -> str:
    return timestamp.partition("T")[0]


def _count_range(value: Range) -> str:
    rendered = f"{value.median:g}"
    if value.minimum == value.maximum:
        return rendered
    return f"{rendered} [{value.minimum:g}–{value.maximum:g}]"


def _settings(config: dict[str, Any]) -> str:
    provider = str(config["provider"])
    profile_values: dict[str, Any] | None = None
    resolved = config.get("resolved_profile")
    base_profile = config.get("base_profile")
    overrides = config.get("diagnostic_overrides")
    if (
        config.get("profile") == "diagnostic-custom-v1"
        and isinstance(resolved, dict)
        and isinstance(overrides, list)
    ):
        # Compare against the run's own resolved profile minus what it actually overrode, so a
        # later edit to the base profile cannot rewrite a published run's settings summary.
        overridden = set(overrides)
        profile_values = {key: value for key, value in resolved.items() if key not in overridden}
    elif config.get("profile") == "diagnostic-custom-v1" and isinstance(base_profile, str):
        try:
            profile_values = asdict(get_profile(base_profile))
        except ValueError:
            profile_values = None
    elif isinstance(resolved, dict):
        profile_values = resolved
    elif isinstance(config.get("profile"), str):
        try:
            profile = get_profile(config["profile"])
        except ValueError:
            pass
        else:
            profile_values = {
                "reasoning_effort": profile.reasoning_effort,
                "preset": profile.preset,
                "max_tokens": profile.max_tokens,
                "max_input_tokens": profile.max_input_tokens,
                "repeats": profile.repeats,
            }
    values: list[str] = []
    if (effort := config.get("reasoning_effort")) and (
        profile_values is None or effort != profile_values.get("reasoning_effort")
    ):
        values.append(f"effort {effort_label(provider, effort)}")
    default_preset = profile_values.get("preset") if profile_values is not None else "full"
    if config.get("preset", "full") != default_preset:
        values.append(f"preset {config['preset']}")
    if config.get("max_tokens") is not None and (
        profile_values is None or config.get("max_tokens") != profile_values.get("max_tokens")
    ):
        values.append(f"max tokens {config['max_tokens']}")
    if config.get("max_input_tokens") is not None and (
        profile_values is None
        or config.get("max_input_tokens") != profile_values.get("max_input_tokens")
    ):
        values.append(f"max input tokens {config['max_input_tokens']}")
    if config.get("api_base"):
        values.append(f"api base {config['api_base']}")
    concurrency = int(config.get("concurrency", resolved_concurrency(provider, None)))
    if concurrency != resolved_concurrency(provider, None):
        values.append(f"concurrency {concurrency}")
    repeats = int(config.get("repeats", 3))
    profile_repeats = int(profile_values.get("repeats", 3)) if profile_values else 3
    if repeats != profile_repeats:
        values.append(f"repeats {repeats}")
    timeout = int(config.get("timeout", 7200))
    if timeout != 7200:
        values.append(f"timeout {timeout}s")
    return "; ".join(values) or "—"


LONG_HORIZON_SUITE_ID = "long-horizon"
LONG_HORIZON_PROFILE_ID = "canonical-long-horizon"
BREADTH_SUITE_ID = "breadth"
CANONICAL_PROFILE_IDS = frozenset({"canonical-breadth"})

#: Suite and profile IDs recorded by runs stored before a rename. Published raw results are
#: immutable, so reporting resolves the stored value instead of rewriting it.
SUITE_ALIASES = {"context-v1": LONG_HORIZON_SUITE_ID, "v2": BREADTH_SUITE_ID}
PROFILE_ALIASES = {
    "context-canonical-v1": LONG_HORIZON_PROFILE_ID,
    "canonical-v2": "canonical-breadth",
}


def resolve_suite_id(suite_id: str) -> str:
    """Resolve a stored suite ID to its current name, leaving unknown IDs untouched."""
    return SUITE_ALIASES.get(suite_id, suite_id)


def resolve_profile_id(profile_id: str) -> str:
    """Resolve a stored profile ID to its current name, leaving unknown IDs untouched."""
    return PROFILE_ALIASES.get(profile_id, profile_id)


def _stored_suite(raw: dict[str, Any]) -> str:
    return resolve_suite_id(str(raw.get("configuration", {}).get("suite", "")))


def _stored_profile(raw: dict[str, Any]) -> str:
    return resolve_profile_id(str(raw.get("configuration", {}).get("profile", "")))


def _render_breadth_canonical(
    raw_runs: list[dict[str, Any]],
    adjudications: dict[str, str] | None,
) -> str | None:
    eligible = [
        raw
        for raw in raw_runs
        if raw.get("status", COMPLETE) == COMPLETE
        and _stored_suite(raw) == BREADTH_SUITE_ID
        and _stored_profile(raw) in CANONICAL_PROFILE_IDS
        and raw.get("configuration", {}).get("profile_canonical", True)
        and raw.get("configuration", {}).get("full_corpus", False)
        and not any(observation.get("failures", 0) for observation in raw.get("observations", []))
    ]
    if not eligible:
        return None
    partitions: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for raw in eligible:
        key = (_stored_suite(raw), _stored_profile(raw), raw["lgtmaybe_version"])
        partitions.setdefault(key, []).append(raw)

    blocks: list[str] = []
    for key, partition in sorted(
        partitions.items(),
        key=lambda item: max(str(raw["timestamp"]) for raw in item[1]),
        reverse=True,
    ):
        runs = sorted(
            (_score_suite_run(raw, adjudications) for raw in partition),
            key=lambda run: (
                run.aggregate.balanced_f1.median,
                str(run.raw["timestamp"]),
                str(run.raw.get("run_id", "")),
            ),
            reverse=True,
        )[:README_RESULT_LIMIT]
        rows: list[str] = []
        for run in runs:
            score = _range(run.aggregate.balanced_f1, percent=True)
            if any(repeat.score.provisional for repeat in run.repeats):
                score += " provisional"
            rows.append(
                "| "
                + " | ".join(
                    (
                        _iso_date(run.raw["timestamp"]),
                        run.raw["configuration"]["provider"],
                        run.raw["configuration"]["model"],
                        score,
                        _range(run.aggregate.balanced_recall, percent=True),
                        _range(run.aggregate.precision, percent=True),
                        _count_range(run.aggregate.false_positives),
                        _range(run.aggregate.clean_pass_rate, percent=True),
                        _range(run.aggregate.adjudication_coverage, percent=True),
                        _audit_label(run.raw),
                        _settings(run.raw["configuration"]),
                    )
                )
                + " |"
            )
        blocks.append(
            f"Comparison key: `{key[0]} / {key[1]} / {key[2]}`.\n\n"
            "| date | provider | model | balanced F1 | balanced recall | precision | "
            "false positives | clean pass | adjudication | audit | settings |\n"
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|\n"
            + "\n".join(rows)
        )
    return (
        "## Breadth — top 10\n\n"
        "Complete `breadth` runs with profile `canonical-breadth` only. Cases span seven "
        "programming languages plus GitHub Actions and Terraform, planting one finding per "
        "language and review lens, so the score measures coverage across kinds of issue rather "
        "than diff size. Scored as balanced F1, which is not comparable with the long-horizon "
        "overall score. Rows are ranked highest to lowest by median balanced F1. The first row "
        "is the current leader.\n\n"
        + "\n\n".join(blocks)
        + "\n"
    )


def _audit_label(raw: dict[str, Any]) -> str:
    states = {
        observation.get("audit", {}).get("state", "unsupported")
        for observation in raw.get("observations", [])
    }
    if states and states <= {"completed"}:
        return "yes"
    if states & {"completed", "partial", "interrupted", "failed", "malformed"}:
        return "partial"
    return "no"


def _true_positive_range(repeats: list[RepeatMetrics]) -> Range:
    values = [float(repeat.score.caught) for repeat in repeats]
    return Range(float(median(values)), min(values), max(values))


def _is_long_horizon_canonical(raw: dict[str, Any]) -> bool:
    return (
        raw.get("status", COMPLETE) == COMPLETE
        and _stored_suite(raw) == LONG_HORIZON_SUITE_ID
        and _stored_profile(raw) == LONG_HORIZON_PROFILE_ID
        and raw.get("configuration", {}).get("full_corpus", False)
        and not any(observation.get("failures", 0) for observation in raw.get("observations", []))
    )


def _context_case_metrics(raw: dict[str, Any]) -> list[dict[str, Any]]:
    case_order: list[str] = []
    observations_by_case: dict[str, list[dict[str, Any]]] = {}
    for observation in raw.get("observations", []):
        case = str(observation.get("case", ""))
        if case not in observations_by_case:
            case_order.append(case)
        observations_by_case.setdefault(case, []).append(observation)
    rows: list[dict[str, Any]] = []
    for case in case_order:
        repeats = observations_by_case[case]
        planted = len(parse_case(repeats[0]["ground_truth"]).expected)
        if planted:
            scores = [
                score_case(parse_case(obs["ground_truth"]), parse_findings(obs["findings"]))
                for obs in repeats
            ]
            recall: float | None = median(score.recall for score in scores)
            precision = median(score.precision for score in scores)
        else:
            recall = None
            precision = median(1.0 if not obs["findings"] else 0.0 for obs in repeats)
        rows.append(
            {
                "case": case,
                "recall": recall,
                "precision": precision,
                "findings": median(float(len(obs["findings"])) for obs in repeats),
                "input_tokens": int(median(int(obs["input_tokens"]) for obs in repeats)),
                "output_tokens": int(median(int(obs["output_tokens"]) for obs in repeats)),
                "truncated": bool(
                    any(obs.get("truncation_lenses") for obs in repeats)
                    or any(
                        call.get("truncated") for obs in repeats for call in obs.get("calls", [])
                    )
                ),
                "wall_seconds": median(float(obs["wall_seconds"]) for obs in repeats),
            }
        )
    return rows


def _render_context_scaling(raw_runs: list[dict[str, Any]]) -> str | None:
    """Render model metrics for complete canonical context-scaling runs."""
    eligible = [raw for raw in raw_runs if _is_long_horizon_canonical(raw)]
    if not eligible:
        return None
    ordered = sorted(
        eligible,
        key=lambda item: (
            str(item["configuration"].get("model", "")),
            str(item["timestamp"]),
            str(item.get("run_id", "")),
        ),
    )
    summaries: list[tuple[dict[str, Any], ScoredRun, AggregateMetrics]] = []
    for raw in ordered:
        scored = _score_run(raw)
        metrics = aggregate_repeats(scored.repeats)
        summaries.append((raw, scored, metrics))
    summary_rows: list[str] = []
    for raw, scored, metrics in sorted(
        summaries,
        key=lambda item: (
            item[2].score.median,
            str(item[0]["timestamp"]),
            str(item[0].get("run_id", "")),
        ),
        reverse=True,
    )[:README_RESULT_LIMIT]:
        config = raw["configuration"]
        summary_rows.append(
            "| "
            + " | ".join(
                (
                    _iso_date(str(raw["timestamp"])),
                    str(config.get("provider", "")),
                    str(config.get("model", "")),
                    _range(metrics.score, percent=True),
                    _range(metrics.recall, percent=True),
                    _range(metrics.precision, percent=True),
                    _count_range(_true_positive_range(scored.repeats)),
                    _count_range(metrics.false_positives),
                )
            )
            + " |"
        )
    summary_header = (
        "| date | provider | model | score | recall | precision | true positives | "
        "false positives |\n"
        "|---|---|---|---:|---:|---:|---:|---:|\n"
    )
    return (
        "## Long horizon — top 10\n\n"
        "Complete `long-horizon` runs with profile `canonical-long-horizon` only. "
        "Cases grow from roughly 3% to 90% of the canonical input-token cap, each planting "
        "eight bugs at the same relative positions; the clean case plants none. Model recall "
        "covers the 32 planted findings across the four defect-bearing cases. Scored as the "
        "closed-world overall score, which is not comparable with the breadth balanced F1.\n\n"
        "### Model summary\n\n" + summary_header + "\n".join(summary_rows) + "\n"
    )


def build_dashboard_data(
    raw_runs: list[dict[str, Any]], adjudications: dict[str, str] | None = None
) -> dict[str, Any]:
    """Build one deterministic, lossless-enough exploration model from stored runs."""
    rows: list[dict[str, Any]] = []
    for raw in sorted(
        raw_runs,
        key=lambda item: (
            str(item.get("timestamp", "")),
            str(item.get("run_id", "")),
            str(item.get("configuration", {}).get("model", "")),
        ),
        reverse=True,
    ):
        config = raw.get("configuration", {})
        suite = resolve_suite_id(str(config.get("suite", "legacy-v1")))
        profile = resolve_profile_id(str(config.get("profile", "legacy-v1")))
        status = str(raw.get("status", COMPLETE))
        focused = not bool(config.get("full_corpus", True))
        failed = any(observation.get("failures", 0) for observation in raw.get("observations", []))
        canonical = (
            status == COMPLETE
            and suite == BREADTH_SUITE_ID
            and profile in CANONICAL_PROFILE_IDS
            and bool(config.get("profile_canonical", True))
            and not focused
            and not failed
        )
        metrics: dict[str, Any] | None = None
        if status == COMPLETE and raw.get("observations") and not failed:
            if suite == BREADTH_SUITE_ID:
                scored = _score_suite_run(raw, adjudications)
                aggregate = scored.aggregate
                classes = sorted(
                    {
                        name
                        for repeat in scored.repeats
                        for name in repeat.score.false_positive_classes
                    }
                )
                metrics = {
                    "score_kind": "balanced_f1",
                    "balanced_f1": aggregate.balanced_f1.median,
                    "balanced_recall": aggregate.balanced_recall.median,
                    "precision": aggregate.precision.median,
                    "false_positives": aggregate.false_positives.median,
                    "false_positive_classes": {
                        name: float(
                            median(
                                repeat.score.false_positive_classes.get(name, 0)
                                for repeat in scored.repeats
                            )
                        )
                        for name in classes
                    },
                    "clean_pass_rate": aggregate.clean_pass_rate.median,
                    "adjudication_coverage": aggregate.adjudication_coverage.median,
                    "true_positives": aggregate.true_positives.median,
                    "duplicates": aggregate.duplicates.median,
                    "unadjudicated": aggregate.unadjudicated.median,
                    "provisional": any(repeat.score.provisional for repeat in scored.repeats),
                    "per_language": {
                        name: value.median for name, value in aggregate.per_language.items()
                    },
                    "per_lens": {name: value.median for name, value in aggregate.per_lens.items()},
                    "truncations": aggregate.truncations.median,
                    "truncation_lenses": list(aggregate.truncation_lenses),
                    "failures": aggregate.failures.median,
                    "input_tokens": aggregate.input_tokens.median,
                    "output_tokens": aggregate.output_tokens.median,
                    "reasoning_tokens": aggregate.reasoning_tokens.median,
                    "wall_seconds": aggregate.wall_seconds.median,
                }
            else:
                scored_legacy = _score_run(raw)
                aggregate_legacy = aggregate_repeats(scored_legacy.repeats)
                context_metrics = suite == LONG_HORIZON_SUITE_ID
                metrics = {
                    "score_kind": "legacy_f1",
                    "balanced_f1": aggregate_legacy.score.median,
                    "balanced_recall": aggregate_legacy.recall.median,
                    "precision": aggregate_legacy.precision.median,
                    "false_positives": (
                        aggregate_legacy.false_positives.median if context_metrics else None
                    ),
                    "false_positive_classes": {},
                    "clean_pass_rate": None,
                    "adjudication_coverage": None,
                    "true_positives": (
                        _true_positive_range(scored_legacy.repeats).median
                        if context_metrics
                        else None
                    ),
                    "duplicates": None,
                    "unadjudicated": None,
                    "provisional": False,
                    "per_language": {},
                    "per_lens": {
                        name: value.median for name, value in scored_legacy.per_lens.items()
                    },
                    "truncations": aggregate_legacy.truncations.median,
                    "truncation_lenses": list(aggregate_legacy.truncation_lenses),
                    "failures": aggregate_legacy.failures.median,
                    "input_tokens": aggregate_legacy.input_tokens.median,
                    "output_tokens": aggregate_legacy.output_tokens.median,
                    "reasoning_tokens": aggregate_legacy.reasoning_tokens.median,
                    "wall_seconds": aggregate_legacy.wall_seconds.median,
                }
        run_id = raw.get("run_id") or ":".join(
            (
                "legacy",
                str(raw.get("timestamp", "")),
                str(config.get("provider", "")),
                str(config.get("model", "")),
            )
        )
        rows.append(
            {
                "run_id": run_id,
                "raw_path": raw.get("_source_path"),
                "timestamp": raw.get("timestamp"),
                "date": _iso_date(str(raw.get("timestamp", ""))),
                "suite": suite,
                "profile": profile,
                "lgtmaybe_version": raw.get("lgtmaybe_version", "unknown"),
                "comparison_key": f"{suite} / {profile} / {raw.get('lgtmaybe_version', 'unknown')}",
                "provider": config.get("provider"),
                "model": config.get("model"),
                "status": status,
                "focused": focused,
                "canonical": canonical,
                "audit": _audit_label(raw),
                "audit_paths": sorted(
                    {
                        path
                        for observation in raw.get("observations", [])
                        if isinstance((audit := observation.get("audit")), dict)
                        and isinstance((path := audit.get("path")), str)
                    }
                ),
                "settings": _settings(config),
                "metrics": metrics,
                "context_cases": (
                    _context_case_metrics(raw) if _is_long_horizon_canonical(raw) else []
                ),
            }
        )
    return {"schema_version": 1, "runs": rows}


def render_dashboard(data: dict[str, Any]) -> str:
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    serialized = serialized.replace("</", "<\\/")
    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>lgtmaybe benchmark explorer</title>
  <style>
    :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
    body { margin: 0 auto; max-width: 96rem; padding: 1.5rem; }
    h1 { margin-bottom: .25rem; }
    .filters { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); margin: 1.5rem 0; }
    label { display: grid; gap: .25rem; font-weight: 600; }
    input, select, button { font: inherit; padding: .45rem; }
    .table-wrap { overflow-x: auto; }
    table { border-collapse: collapse; min-width: 80rem; width: 100%; }
    th, td { border-bottom: 1px solid currentColor; padding: .55rem; text-align: left; }
    th button { background: none; border: 0; color: inherit; cursor: pointer; font-weight: 700; padding: 0; }
    td.numeric { text-align: right; }
    .muted { opacity: .75; }
  </style>
</head>
<body>
  <main>
    <h1>lgtmaybe benchmark explorer</h1>
    <p class="muted">Every stored run remains visible. Canonical rankings compare only one suite, profile, and lgtmaybe version.</p>
    <p><a href="../RESULTS.md">Open the complete Markdown results</a></p>
    <section class="filters" aria-label="Result filters">
      <label>Search model or provider<input id="search" type="search"></label>
      <label>Suite<select id="suite"><option value="">All suites</option></select></label>
      <label>Profile<select id="profile"><option value="">All profiles</option></select></label>
      <label>lgtmaybe version<select id="version"><option value="">All versions</option></select></label>
      <label>Provider<select id="provider"><option value="">All providers</option></select></label>
      <label>Language<select id="language"><option value="">All languages</option></select></label>
      <label>Lens<select id="lens"><option value="">All lenses</option></select></label>
      <label>Audit<select id="audit"><option value="">All audit states</option></select></label>
    </section>
    <p id="result-count" aria-live="polite"></p>
    <div class="table-wrap">
      <table id="results-table">
        <thead><tr>
          <th aria-sort="none"><button type="button" data-sort="date" data-type="text">Date</button></th>
          <th aria-sort="none"><button type="button" data-sort="provider" data-type="text">Provider</button></th>
          <th aria-sort="none"><button type="button" data-sort="model" data-type="text">Model</button></th>
          <th aria-sort="none"><button type="button" data-sort="suite" data-type="text">Suite</button></th>
          <th aria-sort="none"><button type="button" data-sort="profile" data-type="text">Profile</button></th>
          <th aria-sort="none"><button type="button" data-sort="lgtmaybe_version" data-type="text">lgtmaybe</button></th>
          <th aria-sort="none"><button type="button" data-sort="balanced_f1" data-type="number">Balanced F1</button></th>
          <th aria-sort="none"><button type="button" data-sort="balanced_recall" data-type="number">Recall</button></th>
          <th aria-sort="none"><button type="button" data-sort="precision" data-type="number">Precision</button></th>
          <th aria-sort="none"><button type="button" data-sort="true_positives" data-type="number">True positives</button></th>
          <th aria-sort="none"><button type="button" data-sort="false_positives" data-type="number">False positives</button></th>
          <th aria-sort="none"><button type="button" data-sort="clean_pass_rate" data-type="number">Clean pass</button></th>
          <th aria-sort="none"><button type="button" data-sort="audit" data-type="text">Audit</button></th>
          <th aria-sort="none"><button type="button" data-sort="status" data-type="text">Status</button></th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <h2>Context case detail</h2>
    <div class="table-wrap">
      <table id="context-case-table">
        <thead><tr>
          <th>Date</th><th>Provider</th><th>Model</th><th>Case</th><th>Recall</th><th>Precision</th><th>Findings</th>
          <th>Input tokens</th><th>Output tokens</th><th>Truncated</th><th>Wall (s)</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <noscript><p>JavaScript is disabled. Use <a href="../RESULTS.md">RESULTS.md</a> for every stored result.</p></noscript>
  </main>
  <script id="benchmark-data" type="application/json">__DATA__</script>
  <script>
    const runs = JSON.parse(document.querySelector('#benchmark-data').textContent).runs;
    const controls = Object.fromEntries(['search','suite','profile','version','provider','language','lens','audit'].map(id => [id, document.getElementById(id)]));
    let sortKey = 'balanced_f1';
    let sortDirection = -1;
    const metric = (run, key) => run.metrics && run.metrics[key] != null ? run.metrics[key] : null;
    const value = (run, key) => key in run ? run[key] : metric(run, key);
    const text = value => value == null ? '—' : String(value);
    const percent = value => value == null ? '—' : `${(value * 100).toFixed(1)}%`;
    const escapeHtml = value => text(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
    function addOptions(control, values) {
      [...new Set(values.filter(Boolean))].sort().forEach(value => control.add(new Option(value, value)));
    }
    addOptions(controls.suite, runs.map(run => run.suite));
    addOptions(controls.profile, runs.map(run => run.profile));
    addOptions(controls.version, runs.map(run => run.lgtmaybe_version));
    addOptions(controls.provider, runs.map(run => run.provider));
    addOptions(controls.audit, runs.map(run => run.audit));
    addOptions(controls.language, runs.flatMap(run => Object.keys(run.metrics?.per_language || {})));
    addOptions(controls.lens, runs.flatMap(run => Object.keys(run.metrics?.per_lens || {})));
    function visible(run) {
      const query = controls.search.value.trim().toLowerCase();
      return (!query || `${run.model} ${run.provider}`.toLowerCase().includes(query))
        && (!controls.suite.value || run.suite === controls.suite.value)
        && (!controls.profile.value || run.profile === controls.profile.value)
        && (!controls.version.value || run.lgtmaybe_version === controls.version.value)
        && (!controls.provider.value || run.provider === controls.provider.value)
        && (!controls.audit.value || run.audit === controls.audit.value)
        && (!controls.language.value || controls.language.value in (run.metrics?.per_language || {}))
        && (!controls.lens.value || controls.lens.value in (run.metrics?.per_lens || {}));
    }
    function compare(a, b) {
      const left = value(a, sortKey);
      const right = value(b, sortKey);
      if (left == null && right == null) return 0;
      if (left == null) return 1;
      if (right == null) return -1;
      if (typeof left === 'number' && typeof right === 'number') return (left - right) * sortDirection;
      return String(left).localeCompare(String(right), undefined, {numeric: true}) * sortDirection;
    }
    function render() {
      const filtered = runs.filter(visible).sort(compare);
      document.querySelector('#result-count').textContent = `${filtered.length} result${filtered.length === 1 ? '' : 's'}`;
      document.querySelector('#results-table tbody').innerHTML = filtered.map(run => `<tr>
        <td>${escapeHtml(run.date)}</td><td>${escapeHtml(run.provider)}</td><td>${escapeHtml(run.model)}</td>
        <td>${escapeHtml(run.suite)}</td><td>${escapeHtml(run.profile)}</td><td>${escapeHtml(run.lgtmaybe_version)}</td>
        <td class="numeric">${percent(metric(run, 'balanced_f1'))}</td><td class="numeric">${percent(metric(run, 'balanced_recall'))}</td>
        <td class="numeric">${percent(metric(run, 'precision'))}</td><td class="numeric">${escapeHtml(metric(run, 'true_positives'))}</td>
        <td class="numeric">${escapeHtml(metric(run, 'false_positives'))}</td>
        <td class="numeric">${percent(metric(run, 'clean_pass_rate'))}</td><td>${escapeHtml(run.audit)}</td><td>${escapeHtml(run.status)}</td>
      </tr>`).join('');
      document.querySelector('#context-case-table tbody').innerHTML = filtered.flatMap(run =>
        (run.context_cases || []).map(caseMetric => `<tr>
          <td>${escapeHtml(run.date)}</td><td>${escapeHtml(run.provider)}</td><td>${escapeHtml(run.model)}</td><td>${escapeHtml(caseMetric.case)}</td>
          <td class="numeric">${percent(caseMetric.recall)}</td><td class="numeric">${percent(caseMetric.precision)}</td>
          <td class="numeric">${escapeHtml(caseMetric.findings)}</td><td class="numeric">${escapeHtml(caseMetric.input_tokens)}</td>
          <td class="numeric">${escapeHtml(caseMetric.output_tokens)}</td><td>${caseMetric.truncated ? 'yes' : 'no'}</td>
          <td class="numeric">${escapeHtml(caseMetric.wall_seconds)}</td>
        </tr>`)
      ).join('');
    }
    Object.values(controls).forEach(control => control.addEventListener('input', render));
    document.querySelectorAll('[data-sort]').forEach(button => button.addEventListener('click', () => {
      const next = button.dataset.sort;
      sortDirection = sortKey === next ? -sortDirection : (button.dataset.type === 'number' ? -1 : 1);
      sortKey = next;
      document.querySelectorAll('th[aria-sort]').forEach(header => header.setAttribute('aria-sort', 'none'));
      button.parentElement.setAttribute('aria-sort', sortDirection === 1 ? 'ascending' : 'descending');
      render();
    }));
    render();
  </script>
</body>
</html>
"""  # noqa: E501 - embedded dependency-free HTML, CSS, and JavaScript
    return template.replace("__DATA__", serialized)


def render_results(
    raw_runs: list[dict[str, Any]], adjudications: dict[str, str] | None = None
) -> str:
    if not raw_runs:
        return "No benchmark runs recorded.\n"
    complete = [raw for raw in raw_runs if raw.get("status", COMPLETE) == COMPLETE]
    context = _render_context_scaling(raw_runs)
    breadth = _render_breadth_canonical(raw_runs, adjudications)
    if breadth is not None:
        return breadth if context is None else breadth + "\n" + context
    if not complete:
        return "No benchmark runs recorded.\n"
    full_runs = [
        raw
        for raw in complete
        if raw.get("configuration", {}).get("full_corpus", True)
        and _stored_suite(raw) != LONG_HORIZON_SUITE_ID
        and not any(observation.get("failures", 0) for observation in raw["observations"])
    ]
    if not full_runs:
        if context is None:
            return "No full benchmark runs recorded.\n"
        return context
    runs = sorted(
        (_score_run(raw) for raw in full_runs),
        key=lambda run: (
            aggregate_repeats(run.repeats).score.median,
            str(run.raw["timestamp"]),
            str(run.raw.get("run_id", "")),
        ),
        reverse=True,
    )[:README_RESULT_LIMIT]
    header = (
        "| date | lgtmaybe version | provider | model | score | false positives | "
        + " | ".join(LENSES)
        + " | settings |\n"
    )
    rule = "|---|---|---|---|---:|---:|" + "---:|" * len(LENSES) + "---|\n"
    rows: list[str] = []
    for run in runs:
        raw, config = run.raw, run.raw["configuration"]
        metrics = aggregate_repeats(run.repeats)
        values: list[object] = [
            _iso_date(raw["timestamp"]),
            raw["lgtmaybe_version"],
            config["provider"],
            config["model"],
            _range(metrics.score, percent=True),
            _count_range(metrics.false_positives),
        ]
        values.extend(
            _range(run.per_lens[lens], percent=True) if lens in run.per_lens else "-"
            for lens in LENSES
        )
        values.append(_settings(config))
        rows.append("| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |")
    return (
        "Full-corpus runs only. Complete configuration and diagnostic evidence remain in "
        "`results/raw/`.\n\n## Per-lens recall\n\n" + header + rule + "\n".join(rows) + "\n"
    ) + ("" if context is None else "\n" + context)


def render_detailed_results(data: dict[str, Any]) -> str:
    runs = [run for run in data["runs"] if run["status"] == COMPLETE]
    if not runs:
        return "No benchmark runs recorded.\n"

    def escaped(value: Any) -> str:
        return str(value).replace("|", "\\|")

    def percentage(value: Any) -> str:
        return "—" if value is None else f"{float(value) * 100:.1f}%"

    rows: list[str] = []
    context_case_rows: list[str] = []
    language_rows: list[str] = []
    lens_rows: list[str] = []
    false_positive_rows: list[str] = []
    for run in runs:
        metrics = run["metrics"] or {}
        raw_link = f"[raw]({run['raw_path']})" if isinstance(run.get("raw_path"), str) else "—"
        audit_links = (
            ", ".join(
                f"[trace {index}]({path})"
                for index, path in enumerate(run.get("audit_paths", []), start=1)
            )
            or "—"
        )
        rows.append(
            "| "
            + " | ".join(
                escaped(value)
                for value in (
                    run["date"],
                    run["provider"],
                    run["model"],
                    run["suite"],
                    run["profile"],
                    run["lgtmaybe_version"],
                    run["status"],
                    percentage(metrics.get("balanced_f1")),
                    percentage(metrics.get("balanced_recall")),
                    percentage(metrics.get("precision")),
                    metrics.get("true_positives", "—"),
                    metrics.get("false_positives", "—"),
                    percentage(metrics.get("clean_pass_rate")),
                    percentage(metrics.get("adjudication_coverage")),
                    run["audit"],
                    raw_link,
                    audit_links,
                    run["settings"],
                )
            )
            + " |"
        )
        for case in run.get("context_cases", []):
            context_case_rows.append(
                "| "
                + " | ".join(
                    (
                        escaped(run["date"]),
                        escaped(run["provider"]),
                        escaped(run["model"]),
                        escaped(case["case"]),
                        percentage(case["recall"]),
                        percentage(case["precision"]),
                        f"{float(case['findings']):g}",
                        f"{int(case['input_tokens']):,}",
                        f"{int(case['output_tokens']):,}",
                        "yes" if case["truncated"] else "no",
                        f"{float(case['wall_seconds']):.1f}",
                    )
                )
                + " |"
            )
        for language, recall in sorted(metrics.get("per_language", {}).items()):
            language_rows.append(
                f"| {escaped(run['model'])} | {escaped(run['comparison_key'])} | "
                f"{escaped(language)} | {percentage(recall)} |"
            )
        for lens, recall in sorted(metrics.get("per_lens", {}).items()):
            lens_rows.append(
                f"| {escaped(run['model'])} | {escaped(run['comparison_key'])} | "
                f"{escaped(lens)} | {percentage(recall)} |"
            )
        for classification, count in sorted(metrics.get("false_positive_classes", {}).items()):
            false_positive_rows.append(
                f"| {escaped(run['model'])} | {escaped(run['comparison_key'])} | "
                f"{escaped(classification)} | {escaped(count)} |"
            )

    sections = [
        "## All stored runs\n\n"
        "Canonical, diagnostic, focused, and legacy completed runs are retained here. "
        "Only identical comparison keys are directly rankable.\n\n"
        "| date | provider | model | suite | profile | lgtmaybe | status | balanced F1 | "
        "balanced recall | precision | true positives | false positives | clean pass | "
        "adjudication | audit | raw | traces | settings |\n"
        "|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|\n"
        + "\n".join(rows)
        + "\n"
    ]
    if context_case_rows:
        sections.append(
            "\n## Context case detail\n\n"
            "| date | provider | model | case | recall | precision | findings | input tokens | "
            "output tokens | truncated | wall (s) |\n"
            "|---|---|---|---|---:|---:|---:|---:|---:|---|---:|\n"
            + "\n".join(context_case_rows)
            + "\n"
        )
    if language_rows:
        sections.append(
            "\n## Per-language recall\n\n"
            "| model | comparison key | language | recall |\n|---|---|---|---:|\n"
            + "\n".join(language_rows)
            + "\n"
        )
    if lens_rows:
        sections.append(
            "\n## Per-lens recall\n\n"
            "| model | comparison key | lens | recall |\n|---|---|---|---:|\n"
            + "\n".join(lens_rows)
            + "\n"
        )
    if false_positive_rows:
        sections.append(
            "\n## False-positive classes\n\n"
            "| model | comparison key | class | median count |\n|---|---|---|---:|\n"
            + "\n".join(false_positive_rows)
            + "\n"
        )
    return "".join(sections)


def _write_atomic(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def regenerate_reports(root: Path) -> None:
    raw_dir = root / "results" / "raw"
    raw_runs: list[dict[str, Any]] = []
    if raw_dir.exists():
        for path in sorted(raw_dir.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            raw["_source_path"] = path.relative_to(root).as_posix()
            raw_runs.append(raw)
    history = load_adjudications(root, raw_runs)
    adjudications = {
        event.evidence_id: event.classification
        for event in history.current.values()
        if event.evidence_kind == "finding"
    }
    rendered = render_results(raw_runs, adjudications)
    dashboard_data = build_dashboard_data(raw_runs, adjudications)
    _write_atomic(
        root / "RESULTS.md",
        "# lgtmaybe benchmark results\n\n"
        "Generated by `bench report` from `results/raw/*.json`. Do not edit by hand.\n\n"
        + render_detailed_results(dashboard_data),
    )
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise ValueError("README.md is missing benchmark result markers")
    before, remainder = readme.split(START, 1)
    _, after = remainder.split(END, 1)
    _write_atomic(readme_path, f"{before}{START}\n{rendered.rstrip()}\n{END}{after}")
    dashboard = root / "dashboard"
    dashboard.mkdir(parents=True, exist_ok=True)
    _write_atomic(
        dashboard / "data.json",
        json.dumps(dashboard_data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )
    _write_atomic(dashboard / "index.html", render_dashboard(dashboard_data))
