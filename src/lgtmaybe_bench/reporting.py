"""Rescore raw runs and generate deterministic Markdown reports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

from lgtmaybe_bench.cli import resolved_concurrency
from lgtmaybe_bench.runner import RAW_COMPLETE as COMPLETE
from lgtmaybe_bench.scoring import (
    CaseScore,
    Range,
    RepeatMetrics,
    aggregate_repeats,
    effort_label,
    parse_case,
    parse_findings,
    score_case,
)

START = "<!-- BENCH_RESULTS_START -->"
END = "<!-- BENCH_RESULTS_END -->"
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


def _combine(scores: list[CaseScore]) -> CaseScore:
    caught = sum(score.caught for score in scores)
    planted = sum(score.planted for score in scores)
    forbidden = sum(score.forbidden_hits for score in scores)
    unexpected = sum(score.unexpected for score in scores)
    adjudicable = sum(score.adjudicable for score in scores)
    recall = caught / planted
    precision = 1.0 if adjudicable == 0 else 1 - (forbidden + unexpected) / adjudicable
    combined = 0.0 if recall + precision == 0 else 2 * recall * precision / (recall + precision)
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


def _render_incomplete(raw_runs: list[dict[str, Any]]) -> str:
    if not raw_runs:
        return ""
    rows = [
        "| "
        + " | ".join(
            (
                _iso_date(raw["timestamp"]),
                raw["configuration"]["provider"],
                raw["configuration"]["model"],
                str(len(raw["observations"])),
                str(raw["configuration"]["repeats"] * len(raw["configuration"]["cases"])),
            )
        )
        + " |"
        for raw in sorted(raw_runs, key=lambda raw: raw["timestamp"], reverse=True)
    ]
    return (
        "\n## Incomplete runs\n\n"
        "Recorded observations from runs that did not finish. Excluded from every metric above.\n\n"
        "| date | provider | model | observations | expected |\n"
        "|---|---|---|---:|---:|\n" + "\n".join(rows) + "\n"
    )


def _settings(config: dict[str, Any]) -> str:
    provider = str(config["provider"])
    values: list[str] = []
    if effort := config.get("reasoning_effort"):
        values.append(f"effort {effort_label(provider, effort)}")
    if config.get("preset", "full") != "full":
        values.append(f"preset {config['preset']}")
    if config.get("max_tokens") is not None:
        values.append(f"max tokens {config['max_tokens']}")
    if config.get("max_input_tokens") is not None:
        values.append(f"max input tokens {config['max_input_tokens']}")
    if config.get("api_base"):
        values.append(f"api base {config['api_base']}")
    concurrency = int(config.get("concurrency", resolved_concurrency(provider, None)))
    if concurrency != resolved_concurrency(provider, None):
        values.append(f"concurrency {concurrency}")
    repeats = int(config.get("repeats", 3))
    if repeats != 3:
        values.append(f"repeats {repeats}")
    timeout = int(config.get("timeout", 7200))
    if timeout != 7200:
        values.append(f"timeout {timeout}s")
    return "; ".join(values) or "—"


def render_results(raw_runs: list[dict[str, Any]]) -> str:
    if not raw_runs:
        return "No benchmark runs recorded.\n"
    finished = [raw.get("status", COMPLETE) == COMPLETE for raw in raw_runs]
    complete = [raw for raw, done in zip(raw_runs, finished, strict=True) if done]
    incomplete = _render_incomplete(
        [raw for raw, done in zip(raw_runs, finished, strict=True) if not done]
    )
    if not complete:
        return "No benchmark runs recorded.\n" + incomplete
    full_runs = [raw for raw in complete if raw.get("configuration", {}).get("full_corpus", True)]
    if not full_runs:
        return "No full benchmark runs recorded.\n" + incomplete
    runs = sorted(
        (_score_run(raw) for raw in full_runs), key=lambda run: run.raw["timestamp"], reverse=True
    )
    header = (
        "| date | lgtmaybe version | provider | model | score | "
        + " | ".join(LENSES)
        + " | settings |\n"
    )
    rule = "|---|---|---|---|---:|" + "---:|" * len(LENSES) + "---|\n"
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
        ]
        values.extend(
            _range(run.per_lens[lens], percent=True) if lens in run.per_lens else "-"
            for lens in LENSES
        )
        values.append(_settings(config))
        rows.append("| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |")
    return (
        "Full-corpus runs only. Complete configuration and diagnostic evidence remain in "
        "`results/raw/`.\n\n## Per-lens recall\n\n"
        + header
        + rule
        + "\n".join(rows)
        + "\n"
        + incomplete
    )


def _write_atomic(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def regenerate_reports(root: Path) -> None:
    raw_dir = root / "results" / "raw"
    raw_runs = (
        [json.loads(path.read_text(encoding="utf-8")) for path in sorted(raw_dir.glob("*.json"))]
        if raw_dir.exists()
        else []
    )
    rendered = render_results(raw_runs)
    _write_atomic(
        root / "RESULTS.md",
        "# lgtmaybe benchmark results\n\n"
        "Generated by `bench report` from `results/raw/*.json`. Do not edit by hand.\n\n"
        + rendered,
    )
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise ValueError("README.md is missing benchmark result markers")
    before, remainder = readme.split(START, 1)
    _, after = remainder.split(END, 1)
    _write_atomic(readme_path, f"{before}{START}\n{rendered.rstrip()}\n{END}{after}")
