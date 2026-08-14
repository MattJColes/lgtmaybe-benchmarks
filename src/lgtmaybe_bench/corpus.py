"""Corpus discovery and validation."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lgtmaybe_bench.scoring import CaseTruth, parse_case

LENSES = {
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
}
LANGUAGES = {
    "python",
    "typescript",
    "javascript",
    "rust",
    "dart",
    "java",
    "go",
    "github-actions",
    "terraform",
}
CORE_LANGUAGES = frozenset({"python", "typescript", "javascript", "rust", "dart", "java", "go"})
CROSS_CUTTING = frozenset({"github-actions", "terraform"})


@dataclass(frozen=True, slots=True)
class CorpusCase:
    path: Path
    truth: CaseTruth
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CorpusSuite:
    id: str
    case_ids: tuple[str, ...]
    cases: tuple[CorpusCase, ...]


@dataclass(frozen=True, slots=True)
class MatrixCoverage:
    language_lens_cells: int
    clean_language_cases: int
    cross_cutting_cases: int
    has_spec_cases: bool
    has_test_cases: bool
    has_single_file: bool
    has_multi_file: bool
    has_large_diff: bool


def discover_cases(root: Path, *, require_coverage: bool = False) -> list[CorpusCase]:
    """Load cases and validate every referenced changed-tree location."""
    if not root.is_dir():
        raise ValueError(f"corpus directory not found: {root}")
    cases: list[CorpusCase] = []
    for metadata in sorted(root.glob("*/case.json")):
        raw = json.loads(metadata.read_text(encoding="utf-8"))
        truth = parse_case(raw)
        if truth.name != metadata.parent.name:
            raise ValueError(
                f"case name {truth.name!r} must match directory {metadata.parent.name!r}"
            )
        for entry in (*truth.expected, *truth.forbidden):
            if entry.lens not in LENSES:
                raise ValueError(f"{truth.name}: invalid lens {entry.lens!r}")
            source = metadata.parent / "changed" / entry.file
            if not source.is_file():
                raise ValueError(f"{truth.name}: missing changed file {entry.file}")
            line_count = len(source.read_text(encoding="utf-8").splitlines())
            if entry.line > line_count:
                raise ValueError(f"{truth.name}: line {entry.line} is outside {entry.file}")
        if not (metadata.parent / "base").is_dir():
            raise ValueError(f"{truth.name}: missing base tree")
        cases.append(CorpusCase(metadata.parent, truth, raw))
    if not cases:
        raise ValueError("corpus contains no cases")
    if require_coverage:
        counts = {lens: 0 for lens in LENSES}
        for case in cases:
            for entry in case.truth.expected:
                counts[entry.lens] += 1
        missing = [lens for lens, count in sorted(counts.items()) if count < 2]
        if missing:
            raise ValueError(
                f"corpus coverage needs two expected findings for: {', '.join(missing)}"
            )
        if not any(len({entry.file for entry in case.truth.expected}) > 1 for case in cases):
            raise ValueError("corpus coverage requires a multi-file case")
    return cases


def select_cases(cases: list[CorpusCase], names: list[str] | None) -> list[CorpusCase]:
    if not names:
        return cases
    by_name = {case.truth.name: case for case in cases}
    unknown = [name for name in names if name not in by_name]
    if unknown:
        raise ValueError(f"unknown case(s): {', '.join(unknown)}")
    return [by_name[name] for name in names]


def load_suite(root: Path, suite_id: str) -> CorpusSuite:
    """Load one immutable ordered suite manifest and its case versions."""
    if suite_id == "legacy-v1":
        legacy_cases = tuple(
            case
            for case in discover_cases(root, require_coverage=True)
            if case.truth.language is None
        )
        return CorpusSuite(
            suite_id,
            tuple(case.truth.name for case in legacy_cases),
            legacy_cases,
        )
    manifest = root / "suites" / f"{suite_id}.json"
    if not manifest.is_file():
        raise ValueError(f"unknown suite: {suite_id}")
    raw = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("id") != suite_id:
        raise ValueError(f"suite manifest id must be {suite_id!r}")
    case_ids = raw.get("cases")
    if (
        not isinstance(case_ids, list)
        or not case_ids
        or not all(isinstance(case_id, str) and case_id for case_id in case_ids)
    ):
        raise ValueError("suite cases must be a non-empty string list")
    if len(set(case_ids)) != len(case_ids):
        raise ValueError(f"suite {suite_id}: duplicate case membership")
    cases = select_cases(discover_cases(root), case_ids)
    for case in cases:
        language = case.truth.language
        if language not in LANGUAGES:
            value = "missing" if language is None else repr(language)
            raise ValueError(f"{case.truth.name}: unknown language {value}")
    return CorpusSuite(suite_id, tuple(case_ids), tuple(cases))


def infer_suite_id(raw_result: dict[str, Any]) -> str:
    """Label pre-suite evidence without rewriting published raw files."""
    configuration = raw_result.get("configuration")
    if not isinstance(configuration, dict):
        return "legacy-v1"
    suite = configuration.get("suite")
    return suite if isinstance(suite, str) and suite else "legacy-v1"


def validate_v2_matrix(suite: CorpusSuite) -> MatrixCoverage:
    """Reject accidental weighting or missing behavior classes in the frozen v2 suite."""
    if suite.id != "v2":
        raise ValueError("v2 matrix validation requires suite 'v2'")
    if len(suite.cases) != 32:
        raise ValueError(f"v2 requires 32 cases, found {len(suite.cases)}")

    cells: Counter[tuple[str, str]] = Counter()
    clean_by_language: Counter[str] = Counter()
    cases_by_language: Counter[str] = Counter()
    cross_clean: Counter[str] = Counter()
    coverage_tags: set[str] = set()
    has_single_file = False
    for case in suite.cases:
        language = case.truth.language
        if language not in LANGUAGES:
            value = "missing" if language is None else repr(language)
            raise ValueError(f"{case.truth.name}: unknown language {value}")
        if case.truth.clean and case.truth.expected:
            raise ValueError(f"{case.truth.name}: clean case has expected findings")
        cases_by_language[language] += 1
        if case.truth.clean:
            clean_by_language[language] += 1
        if language in CORE_LANGUAGES:
            for entry in case.truth.expected:
                cells[(language, entry.lens)] += 1
        else:
            cross_clean[language] += int(case.truth.clean)
        raw_tags = case.raw.get("coverage", [])
        if not isinstance(raw_tags, list) or not all(isinstance(tag, str) for tag in raw_tags):
            raise ValueError(f"{case.truth.name}: coverage must be a string list")
        coverage_tags.update(raw_tags)
        has_single_file |= "multi-file" not in raw_tags

    for language in sorted(CORE_LANGUAGES):
        if cases_by_language[language] != 4:
            raise ValueError(
                f"v2 requires four {language} cases, found {cases_by_language[language]}"
            )
        if clean_by_language[language] != 1:
            raise ValueError(
                f"v2 requires one clean {language} case, found {clean_by_language[language]}"
            )
    for technology in sorted(CROSS_CUTTING):
        if cases_by_language[technology] != 2 or cross_clean[technology] != 1:
            raise ValueError(f"v2 requires one defect and one clean {technology} case")

    for language in sorted(CORE_LANGUAGES):
        for lens in sorted(LENSES):
            count = cells[(language, lens)]
            if count > 1:
                raise ValueError(f"duplicate language/lens cell: {language}/{lens}")
            if count == 0:
                raise ValueError(f"missing language/lens cell: {language}/{lens}")
    if "multi-file" not in coverage_tags:
        raise ValueError("v2 requires multi-file coverage")
    if "large-diff" not in coverage_tags:
        raise ValueError("v2 requires documented large-diff coverage")

    return MatrixCoverage(
        language_lens_cells=sum(cells.values()),
        clean_language_cases=sum(clean_by_language[language] for language in CORE_LANGUAGES),
        cross_cutting_cases=sum(cases_by_language[technology] for technology in CROSS_CUTTING),
        has_spec_cases=all(cells[(language, "spec")] == 1 for language in CORE_LANGUAGES),
        has_test_cases=all(cells[(language, "tests")] == 1 for language in CORE_LANGUAGES),
        has_single_file=has_single_file,
        has_multi_file="multi-file" in coverage_tags,
        has_large_diff="large-diff" in coverage_tags,
    )
