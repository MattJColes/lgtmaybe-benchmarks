"""Ground-truth parsing and deterministic benchmark scoring."""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

LINE_WINDOW = 3
FALSE_POSITIVE_PENALTY = 0.02
SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
ADJUDICATION_CLASSES = frozenset(
    {"true_positive", "false_positive", "duplicate", "invalid_case_evidence", "unadjudicated"}
)
CORE_LANGUAGES = frozenset({"python", "typescript", "javascript", "rust", "dart", "java", "go"})


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    label: str
    lens: str
    file: str
    line: int
    keywords: tuple[str, ...]
    severity_at_least: str | None = None


@dataclass(frozen=True, slots=True)
class CaseTruth:
    name: str
    changed_file: str
    expected: tuple[CatalogEntry, ...]
    forbidden: tuple[CatalogEntry, ...]
    language: str | None = None
    clean: bool = False
    clean_trap: str | None = None


@dataclass(frozen=True, slots=True)
class Finding:
    file: str
    line: int
    severity: str
    title: str
    body: str
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CaseScore:
    caught: int
    planted: int
    forbidden_hits: int
    unexpected: int
    adjudicable: int
    recall: float
    precision: float
    score: float
    clean: bool
    per_lens: dict[str, float]
    per_lens_counts: dict[str, tuple[int, int]]

    @property
    def false_positives(self) -> int:
        return self.forbidden_hits + self.unexpected


@dataclass(frozen=True, slots=True)
class SuiteObservation:
    case: CaseTruth
    findings: tuple[Finding, ...]


@dataclass(frozen=True, slots=True)
class SuiteScore:
    language_lens_cells: int
    caught: int
    planted: int
    balanced_recall: float
    true_positives: int
    false_positives: int
    false_positive_classes: dict[str, int]
    duplicates: int
    unadjudicated: int
    adjudication_coverage: float
    precision: float
    clean_pass_rate: float
    balanced_f1: float
    provisional: bool
    per_language: dict[str, float]
    per_lens: dict[str, float]
    per_cell: dict[str, float]


@dataclass(frozen=True, slots=True)
class RepeatMetrics:
    score: CaseScore
    wall_seconds: float
    wall_excluding_truncation_seconds: float
    truncation_lenses: tuple[str, ...]
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    failures: int


@dataclass(frozen=True, slots=True)
class SuiteRepeatMetrics:
    score: SuiteScore
    wall_seconds: float
    wall_excluding_truncation_seconds: float
    truncation_lenses: tuple[str, ...]
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    failures: int


@dataclass(frozen=True, slots=True)
class Range:
    median: float
    minimum: float
    maximum: float


@dataclass(frozen=True, slots=True)
class AggregateMetrics:
    recall: Range
    precision: Range
    score: Range
    false_positives: Range
    wall_seconds: Range
    wall_excluding_truncation_seconds: Range
    truncations: Range
    input_tokens: Range
    output_tokens: Range
    reasoning_tokens: Range
    failures: Range
    truncation_lenses: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SuiteAggregateMetrics:
    balanced_recall: Range
    precision: Range
    balanced_f1: Range
    clean_pass_rate: Range
    adjudication_coverage: Range
    true_positives: Range
    false_positives: Range
    duplicates: Range
    unadjudicated: Range
    wall_seconds: Range
    wall_excluding_truncation_seconds: Range
    truncations: Range
    input_tokens: Range
    output_tokens: Range
    reasoning_tokens: Range
    failures: Range
    truncation_lenses: tuple[str, ...]
    per_language: dict[str, Range]
    per_lens: dict[str, Range]


@dataclass(frozen=True, slots=True)
class AdjudicationEvent:
    event_id: str
    suite: str
    run_id: str
    observation_id: str
    repeat: int
    evidence_kind: str
    evidence_id: str
    classification: str
    reason: str
    adjudicator: str
    timestamp: str
    supersedes: str | None

    @property
    def identity(self) -> tuple[str, str, str, int, str, str]:
        return (
            self.suite,
            self.run_id,
            self.observation_id,
            self.repeat,
            self.evidence_kind,
            self.evidence_id,
        )


@dataclass(frozen=True, slots=True)
class AdjudicationHistory:
    events: tuple[AdjudicationEvent, ...]
    current: dict[tuple[str, str, str, int, str, str], AdjudicationEvent]


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _parse_adjudication(data: Any) -> AdjudicationEvent:
    if not isinstance(data, dict):
        raise ValueError("adjudication event must be an object")
    repeat = data.get("repeat")
    if not isinstance(repeat, int) or isinstance(repeat, bool) or repeat < 1:
        raise ValueError("adjudication repeat must be a positive integer")
    kind = _string(data.get("evidence_kind"), "evidence_kind")
    if kind not in {"candidate", "finding"}:
        raise ValueError(f"invalid evidence_kind: {kind}")
    classification = _string(data.get("classification"), "classification")
    if classification not in ADJUDICATION_CLASSES:
        raise ValueError(f"invalid adjudication classification: {classification}")
    supersedes = data.get("supersedes")
    if supersedes is not None:
        supersedes = _string(supersedes, "supersedes")
    return AdjudicationEvent(
        event_id=_string(data.get("event_id"), "event_id"),
        suite=_string(data.get("suite"), "suite"),
        run_id=_string(data.get("run_id"), "run_id"),
        observation_id=_string(data.get("observation_id"), "observation_id"),
        repeat=repeat,
        evidence_kind=kind,
        evidence_id=_string(data.get("evidence_id"), "evidence_id"),
        classification=classification,
        reason=_string(data.get("reason"), "reason"),
        adjudicator=_string(data.get("adjudicator"), "adjudicator"),
        timestamp=_string(data.get("timestamp"), "timestamp"),
        supersedes=supersedes,
    )


def append_adjudication(path: Path, event: dict[str, Any]) -> None:
    """Append one validated event without rewriting prior human judgments."""
    _parse_adjudication(event)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush()


def _valid_evidence(
    root: Path, raw_runs: list[dict[str, object]]
) -> set[tuple[str, str, str, int, str, str]]:
    identities: set[tuple[str, str, str, int, str, str]] = set()
    for raw in raw_runs:
        run_id = raw.get("run_id")
        configuration = raw.get("configuration")
        observations = raw.get("observations")
        if not isinstance(run_id, str) or not isinstance(configuration, dict):
            continue
        suite = configuration.get("suite", "legacy-v1")
        if not isinstance(suite, str) or not isinstance(observations, list):
            continue
        for observation in observations:
            if not isinstance(observation, dict):
                continue
            observation_id = observation.get("observation_id")
            repeat = observation.get("repeat")
            if not isinstance(observation_id, str) or not isinstance(repeat, int):
                continue
            for finding in observation.get("findings", []):
                if isinstance(finding, dict) and isinstance(finding.get("finding_id"), str):
                    identities.add(
                        (suite, run_id, observation_id, repeat, "finding", finding["finding_id"])
                    )
            audit = observation.get("audit")
            audit_path = audit.get("path") if isinstance(audit, dict) else None
            if not isinstance(audit_path, str):
                continue
            try:
                with gzip.open(root / audit_path, "rt", encoding="utf-8") as stream:
                    events = [json.loads(line) for line in stream]
            except (OSError, json.JSONDecodeError):
                continue
            for event in events:
                candidate_id = event.get("candidate_id") if isinstance(event, dict) else None
                if isinstance(candidate_id, str):
                    identities.add(
                        (suite, run_id, observation_id, repeat, "candidate", candidate_id)
                    )
    return identities


def load_adjudications(root: Path, raw_runs: list[dict[str, object]]) -> AdjudicationHistory:
    valid_evidence = _valid_evidence(root, raw_runs)
    directory = root / "results" / "adjudications"
    paths = sorted(directory.glob("*.jsonl")) if directory.is_dir() else []
    events: list[AdjudicationEvent] = []
    by_id: dict[str, AdjudicationEvent] = {}
    current: dict[tuple[str, str, str, int, str, str], AdjudicationEvent] = {}
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                event = _parse_adjudication(json.loads(line))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if event.event_id in by_id:
                raise ValueError(f"duplicate adjudication event_id: {event.event_id}")
            if event.identity not in valid_evidence:
                raise ValueError(f"unknown evidence identity: {event.evidence_id}")
            prior = by_id.get(event.supersedes) if event.supersedes else None
            if event.supersedes and prior is None:
                raise ValueError(f"unknown superseded adjudication: {event.supersedes}")
            if prior is not None and prior.identity != event.identity:
                raise ValueError("superseded adjudication has a different evidence identity")
            existing = current.get(event.identity)
            if existing is not None and existing.event_id != event.supersedes:
                raise ValueError(
                    f"adjudication for {event.evidence_id} must supersede current event"
                )
            events.append(event)
            by_id[event.event_id] = event
            current[event.identity] = event
    return AdjudicationHistory(tuple(events), current)


def _entry(data: Any, changed_file: str) -> CatalogEntry:
    if not isinstance(data, dict):
        raise ValueError("catalog entries must be objects")
    keywords = data.get("keywords")
    if (
        not isinstance(keywords, list)
        or not keywords
        or not all(isinstance(k, str) and k for k in keywords)
    ):
        raise ValueError("keywords must be a non-empty string list")
    line = data.get("line")
    if not isinstance(line, int) or isinstance(line, bool) or line < 1:
        raise ValueError("line must be a positive integer")
    severity = data.get("severity_at_least")
    if severity is not None and severity not in SEVERITY_ORDER:
        raise ValueError(f"invalid severity_at_least: {severity}")
    return CatalogEntry(
        label=_string(data.get("label"), "label"),
        lens=_string(data.get("lens"), "lens"),
        file=_string(data.get("file", changed_file), "file"),
        line=line,
        keywords=tuple(keywords),
        severity_at_least=severity,
    )


def parse_case(data: Any) -> CaseTruth:
    """Validate untrusted case metadata into a typed value."""
    if not isinstance(data, dict):
        raise ValueError("case must be an object")
    changed_file = _string(data.get("changed_file"), "changed_file")
    expected = data.get("expected")
    forbidden = data.get("forbidden", [])
    clean = data.get("clean", False)
    if not isinstance(clean, bool):
        raise ValueError("clean must be a boolean")
    if not isinstance(expected, list):
        raise ValueError("expected must be a list")
    if clean and expected:
        raise ValueError("clean case cannot declare expected findings")
    if not clean and not expected:
        raise ValueError("expected must be a non-empty list")
    if not isinstance(forbidden, list):
        raise ValueError("forbidden must be a list")
    language = data.get("language")
    if language is not None:
        language = _string(language, "language")
    clean_trap = data.get("clean_trap")
    if clean or clean_trap is not None:
        clean_trap = _string(clean_trap, "clean_trap")
    return CaseTruth(
        name=_string(data.get("name"), "name"),
        changed_file=changed_file,
        expected=tuple(_entry(item, changed_file) for item in expected),
        forbidden=tuple(_entry(item, changed_file) for item in forbidden),
        language=language,
        clean=clean,
        clean_trap=clean_trap,
    )


def parse_findings(data: Any) -> tuple[Finding, ...]:
    """Validate lgtmaybe's JSON findings array."""
    if not isinstance(data, list):
        raise ValueError("findings must be a JSON array")
    findings: list[Finding] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("finding must be an object")
        line = item.get("line")
        severity = item.get("severity")
        if not isinstance(line, int) or isinstance(line, bool) or line < 1:
            raise ValueError("finding line must be a positive integer")
        if severity not in SEVERITY_ORDER:
            raise ValueError(f"invalid finding severity: {severity}")
        findings.append(
            Finding(
                file=_string(item.get("file", item.get("path")), "finding file"),
                line=line,
                severity=severity,
                title=_string(item.get("title"), "finding title"),
                body=str(item.get("body", item.get("explanation", ""))),
                raw=dict(item),
            )
        )
    return tuple(findings)


def _near(finding: Finding, entry: CatalogEntry) -> bool:
    return (
        finding.file.replace("\\", "/") == entry.file.replace("\\", "/")
        and abs(finding.line - entry.line) <= LINE_WINDOW
    )


def _matches(finding: Finding, entry: CatalogEntry) -> bool:
    text = f"{finding.title}\n{finding.body}".casefold()
    severity_ok = (
        entry.severity_at_least is None
        or SEVERITY_ORDER[finding.severity] >= SEVERITY_ORDER[entry.severity_at_least]
    )
    return (
        _near(finding, entry) and severity_ok and any(k.casefold() in text for k in entry.keywords)
    )


def overall_score(recall: float, false_positives: int) -> float:
    base_score = 2 * recall / (recall + 1)
    return max(0.0, base_score - false_positives * FALSE_POSITIVE_PENALTY)


def score_case(case: CaseTruth, findings: tuple[Finding, ...]) -> CaseScore:
    """Classify each finding once and count each planted bug once."""
    unmatched_expected = set(range(len(case.expected)))
    caught_by_lens: dict[str, int] = {}
    forbidden_hits = unexpected = 0
    adjudicable = len(findings)

    for finding in findings:
        expected_match = next(
            (
                index
                for index in sorted(unmatched_expected)
                if _matches(finding, case.expected[index])
            ),
            None,
        )
        if expected_match is not None:
            entry = case.expected[expected_match]
            unmatched_expected.remove(expected_match)
            caught_by_lens[entry.lens] = caught_by_lens.get(entry.lens, 0) + 1
            continue
        if any(_matches(finding, entry) for entry in case.forbidden):
            forbidden_hits += 1
            continue
        unexpected += 1

    caught = len(case.expected) - len(unmatched_expected)
    planted = len(case.expected)
    recall = caught / planted if planted else 0.0
    false_positives = forbidden_hits + unexpected
    precision = 1.0 if adjudicable == 0 else caught / (caught + false_positives)
    combined = overall_score(recall, false_positives)
    totals: dict[str, int] = {}
    for entry in case.expected:
        totals[entry.lens] = totals.get(entry.lens, 0) + 1
    per_lens = {lens: caught_by_lens.get(lens, 0) / total for lens, total in sorted(totals.items())}
    return CaseScore(
        caught=caught,
        planted=planted,
        forbidden_hits=forbidden_hits,
        unexpected=unexpected,
        adjudicable=adjudicable,
        recall=recall,
        precision=precision,
        score=combined,
        clean=forbidden_hits == 0,
        per_lens=per_lens,
        per_lens_counts={
            lens: (caught_by_lens.get(lens, 0), total) for lens, total in sorted(totals.items())
        },
    )


def score_suite(
    observations: list[SuiteObservation],
    adjudications: dict[str, str] | None = None,
) -> SuiteScore:
    """Score one repeat with balanced core recall and explicit finding classifications."""
    overrides = adjudications or {}
    cell_totals: dict[tuple[str, str], int] = {}
    cell_caught: dict[tuple[str, str], int] = {}
    planted = caught = true_positives = unadjudicated = duplicates = 0
    false_classes = {
        "forbidden": 0,
        "clean_case": 0,
        "unexpected_near": 0,
        "duplicate": 0,
        "adjudicated": 0,
    }
    clean_cases = clean_passes = 0

    for observation in observations:
        case = observation.case
        planted += len(case.expected)
        if case.clean:
            clean_cases += 1
            clean_passes += int(not observation.findings)
        for entry in case.expected:
            if case.language in CORE_LANGUAGES:
                cell = (case.language, entry.lens)
                cell_totals[cell] = cell_totals.get(cell, 0) + 1

        matched_expected: set[int] = set()
        for finding in observation.findings:
            matching_expected = [
                index for index, entry in enumerate(case.expected) if _matches(finding, entry)
            ]
            available_match = next(
                (index for index in matching_expected if index not in matched_expected), None
            )
            if case.clean:
                classification = "clean_case"
            elif available_match is not None:
                classification = "true_positive"
            elif matching_expected:
                classification = "duplicate"
            elif any(_matches(finding, entry) for entry in case.forbidden):
                classification = "forbidden"
            elif any(_near(finding, entry) for entry in (*case.expected, *case.forbidden)):
                classification = "unexpected_near"
            else:
                classification = "unadjudicated"

            finding_id = finding.raw.get("finding_id")
            override = overrides.get(finding_id) if isinstance(finding_id, str) else None
            if override is not None:
                if override not in ADJUDICATION_CLASSES:
                    raise ValueError(f"invalid adjudication classification: {override}")
                classification = {
                    "true_positive": "true_positive",
                    "false_positive": "adjudicated",
                    "duplicate": "duplicate",
                    "invalid_case_evidence": "invalid",
                    "unadjudicated": "unadjudicated",
                }[override]

            if classification == "true_positive":
                true_positives += 1
                if available_match is not None:
                    matched_expected.add(available_match)
                    caught += 1
                    entry = case.expected[available_match]
                    if case.language in CORE_LANGUAGES:
                        cell = (case.language, entry.lens)
                        cell_caught[cell] = cell_caught.get(cell, 0) + 1
            elif classification == "unadjudicated":
                unadjudicated += 1
            elif classification != "invalid":
                false_classes[classification] += 1
                duplicates += int(classification == "duplicate")

    per_cell_values = {
        cell: cell_caught.get(cell, 0) / total for cell, total in sorted(cell_totals.items())
    }
    per_language = {
        language: sum(
            value
            for (cell_language, _), value in per_cell_values.items()
            if cell_language == language
        )
        / sum(1 for cell_language, _ in per_cell_values if cell_language == language)
        for language in sorted({language for language, _ in per_cell_values})
    }
    per_lens = {
        lens: sum(value for (_, cell_lens), value in per_cell_values.items() if cell_lens == lens)
        / sum(1 for _, cell_lens in per_cell_values if cell_lens == lens)
        for lens in sorted({lens for _, lens in per_cell_values})
    }
    balanced_recall = (
        sum(per_cell_values.values()) / len(per_cell_values) if per_cell_values else 1.0
    )
    false_positives = sum(false_classes.values())
    precision_denominator = true_positives + false_positives
    precision = 1.0 if precision_denominator == 0 else true_positives / precision_denominator
    classified = precision_denominator
    coverage_denominator = classified + unadjudicated
    adjudication_coverage = 1.0 if coverage_denominator == 0 else classified / coverage_denominator
    balanced_f1 = (
        0.0
        if balanced_recall + precision == 0
        else 2 * balanced_recall * precision / (balanced_recall + precision)
    )
    return SuiteScore(
        language_lens_cells=len(per_cell_values),
        caught=caught,
        planted=planted,
        balanced_recall=balanced_recall,
        true_positives=true_positives,
        false_positives=false_positives,
        false_positive_classes=false_classes,
        duplicates=duplicates,
        unadjudicated=unadjudicated,
        adjudication_coverage=adjudication_coverage,
        precision=precision,
        clean_pass_rate=1.0 if clean_cases == 0 else clean_passes / clean_cases,
        balanced_f1=balanced_f1,
        provisional=unadjudicated > 0,
        per_language=per_language,
        per_lens=per_lens,
        per_cell={
            f"{language}/{lens}": value for (language, lens), value in per_cell_values.items()
        },
    )


def _range(values: list[int | float]) -> Range:
    return Range(float(median(values)), float(min(values)), float(max(values)))


def aggregate_repeats(repeats: list[RepeatMetrics]) -> AggregateMetrics:
    """Summarise repeated configuration runs without hiding their range."""
    if not repeats:
        raise ValueError("at least one repeat is required")
    return AggregateMetrics(
        recall=_range([repeat.score.recall for repeat in repeats]),
        precision=_range([repeat.score.precision for repeat in repeats]),
        score=_range([repeat.score.score for repeat in repeats]),
        false_positives=_range([repeat.score.false_positives for repeat in repeats]),
        wall_seconds=_range([repeat.wall_seconds for repeat in repeats]),
        wall_excluding_truncation_seconds=_range(
            [repeat.wall_excluding_truncation_seconds for repeat in repeats]
        ),
        truncations=_range([len(repeat.truncation_lenses) for repeat in repeats]),
        input_tokens=_range([repeat.input_tokens for repeat in repeats]),
        output_tokens=_range([repeat.output_tokens for repeat in repeats]),
        reasoning_tokens=_range([repeat.reasoning_tokens for repeat in repeats]),
        failures=_range([repeat.failures for repeat in repeats]),
        truncation_lenses=tuple(sorted({lens for r in repeats for lens in r.truncation_lenses})),
    )


def aggregate_suite_repeats(repeats: list[SuiteRepeatMetrics]) -> SuiteAggregateMetrics:
    if not repeats:
        raise ValueError("at least one repeat is required")
    languages = sorted({language for repeat in repeats for language in repeat.score.per_language})
    lenses = sorted({lens for repeat in repeats for lens in repeat.score.per_lens})
    return SuiteAggregateMetrics(
        balanced_recall=_range([repeat.score.balanced_recall for repeat in repeats]),
        precision=_range([repeat.score.precision for repeat in repeats]),
        balanced_f1=_range([repeat.score.balanced_f1 for repeat in repeats]),
        clean_pass_rate=_range([repeat.score.clean_pass_rate for repeat in repeats]),
        adjudication_coverage=_range([repeat.score.adjudication_coverage for repeat in repeats]),
        true_positives=_range([repeat.score.true_positives for repeat in repeats]),
        false_positives=_range([repeat.score.false_positives for repeat in repeats]),
        duplicates=_range([repeat.score.duplicates for repeat in repeats]),
        unadjudicated=_range([repeat.score.unadjudicated for repeat in repeats]),
        wall_seconds=_range([repeat.wall_seconds for repeat in repeats]),
        wall_excluding_truncation_seconds=_range(
            [repeat.wall_excluding_truncation_seconds for repeat in repeats]
        ),
        truncations=_range([len(repeat.truncation_lenses) for repeat in repeats]),
        input_tokens=_range([repeat.input_tokens for repeat in repeats]),
        output_tokens=_range([repeat.output_tokens for repeat in repeats]),
        reasoning_tokens=_range([repeat.reasoning_tokens for repeat in repeats]),
        failures=_range([repeat.failures for repeat in repeats]),
        truncation_lenses=tuple(
            sorted({lens for repeat in repeats for lens in repeat.truncation_lenses})
        ),
        per_language={
            language: _range(
                [
                    repeat.score.per_language[language]
                    for repeat in repeats
                    if language in repeat.score.per_language
                ]
            )
            for language in languages
        },
        per_lens={
            lens: _range(
                [repeat.score.per_lens[lens] for repeat in repeats if lens in repeat.score.per_lens]
            )
            for lens in lenses
        },
    )


def effort_label(provider: str, effort: str | None) -> str:
    value = effort or "default"
    return f"{value} (thinking off)" if provider == "ollama" else value
