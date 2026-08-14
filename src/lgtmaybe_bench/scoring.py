"""Ground-truth parsing and deterministic benchmark scoring."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Any

LINE_WINDOW = 3
SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


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


@dataclass(frozen=True, slots=True)
class Finding:
    file: str
    line: int
    severity: str
    title: str
    body: str


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


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


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
    if not isinstance(expected, list) or not expected:
        raise ValueError("expected must be a non-empty list")
    if not isinstance(forbidden, list):
        raise ValueError("forbidden must be a list")
    return CaseTruth(
        name=_string(data.get("name"), "name"),
        changed_file=changed_file,
        expected=tuple(_entry(item, changed_file) for item in expected),
        forbidden=tuple(_entry(item, changed_file) for item in forbidden),
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
    recall = caught / planted
    false_positives = forbidden_hits + unexpected
    precision = 1.0 if adjudicable == 0 else caught / (caught + false_positives)
    combined = 0.0 if recall + precision == 0 else 2 * recall * precision / (recall + precision)
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


def effort_label(provider: str, effort: str | None) -> str:
    value = effort or "default"
    return f"{value} (thinking off)" if provider == "ollama" else value
