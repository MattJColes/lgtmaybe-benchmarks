from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from lgtmaybe_bench.corpus import (
    LENSES,
    CorpusCase,
    CorpusSuite,
    discover_cases,
    infer_suite_id,
    load_suite,
    select_cases,
    validate_v2_matrix,
)
from lgtmaybe_bench.scoring import CaseTruth, CatalogEntry


def make_case(root: Path, name: str, lens: str, *, file: str = "app.py", line: int = 1) -> None:
    case = root / name
    (case / "base").mkdir(parents=True)
    (case / "changed").mkdir()
    (case / "base" / file).parent.mkdir(parents=True, exist_ok=True)
    (case / "changed" / file).parent.mkdir(parents=True, exist_ok=True)
    (case / "base" / file).write_text("safe\n", encoding="utf-8")
    (case / "changed" / file).write_text("bug\n", encoding="utf-8")
    (case / "case.json").write_text(
        json.dumps(
            {
                "name": name,
                "changed_file": file,
                "expected": [{"label": "bug", "lens": lens, "line": line, "keywords": ["bug"]}],
                "forbidden": [],
            }
        ),
        encoding="utf-8",
    )


def test_discovery_validates_paths_and_lines(tmp_path: Path) -> None:
    make_case(tmp_path, "bad-line", "security", line=2)

    with pytest.raises(ValueError, match="outside"):
        discover_cases(tmp_path)


def test_discovery_rejects_unknown_lens(tmp_path: Path) -> None:
    make_case(tmp_path, "unknown", "style")

    with pytest.raises(ValueError, match="invalid lens"):
        discover_cases(tmp_path)


def test_discovery_rejects_missing_changed_file(tmp_path: Path) -> None:
    make_case(tmp_path, "missing", "security")
    (tmp_path / "missing" / "changed" / "app.py").unlink()

    with pytest.raises(ValueError, match="missing changed file"):
        discover_cases(tmp_path)


def test_discovery_rejects_empty_keywords(tmp_path: Path) -> None:
    make_case(tmp_path, "empty-keywords", "security")
    metadata = tmp_path / "empty-keywords" / "case.json"
    raw = json.loads(metadata.read_text(encoding="utf-8"))
    raw["expected"][0]["keywords"] = []
    metadata.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="keywords"):
        discover_cases(tmp_path)


def test_full_corpus_requires_two_findings_per_lens(tmp_path: Path) -> None:
    make_case(tmp_path, "only-security", "security")

    with pytest.raises(ValueError, match="coverage"):
        discover_cases(tmp_path, require_coverage=True)


def test_case_selection_is_exact(tmp_path: Path) -> None:
    make_case(tmp_path, "one", "security")
    cases = discover_cases(tmp_path)

    assert select_cases(cases, ["one"])[0].truth.name == "one"
    with pytest.raises(ValueError, match="unknown case"):
        select_cases(cases, ["missing"])


def test_named_suite_loads_immutable_membership_in_manifest_order(tmp_path: Path) -> None:
    make_case(tmp_path, "one", "security")
    make_case(tmp_path, "two", "correctness")
    for name in ("one", "two"):
        metadata = tmp_path / name / "case.json"
        raw = json.loads(metadata.read_text(encoding="utf-8"))
        raw["language"] = "python"
        metadata.write_text(json.dumps(raw), encoding="utf-8")
    suites = tmp_path / "suites"
    suites.mkdir()
    (suites / "v2.json").write_text(
        json.dumps({"id": "v2", "cases": ["two", "one"]}),
        encoding="utf-8",
    )

    suite = load_suite(tmp_path, "v2")

    assert suite.id == "v2"
    assert suite.case_ids == ("two", "one")
    assert [case.truth.name for case in suite.cases] == ["two", "one"]
    assert all(case.truth.language == "python" for case in suite.cases)


def test_suite_rejects_duplicate_membership(tmp_path: Path) -> None:
    make_case(tmp_path, "one", "security")
    metadata = tmp_path / "one" / "case.json"
    raw = json.loads(metadata.read_text(encoding="utf-8"))
    raw["language"] = "python"
    metadata.write_text(json.dumps(raw), encoding="utf-8")
    suites = tmp_path / "suites"
    suites.mkdir()
    (suites / "v2.json").write_text(
        json.dumps({"id": "v2", "cases": ["one", "one"]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate case"):
        load_suite(tmp_path, "v2")


def test_clean_case_accepts_empty_truth_and_rejects_contradiction(tmp_path: Path) -> None:
    make_case(tmp_path, "clean", "security")
    metadata = tmp_path / "clean" / "case.json"
    raw = json.loads(metadata.read_text(encoding="utf-8"))
    raw.update(
        language="typescript",
        clean=True,
        clean_trap="The checked helper already enforces the boundary.",
        expected=[],
    )
    metadata.write_text(json.dumps(raw), encoding="utf-8")

    case = discover_cases(tmp_path)[0]

    assert case.truth.clean is True
    assert case.truth.expected == ()
    raw["expected"] = [{"label": "bug", "lens": "security", "line": 1, "keywords": ["bug"]}]
    metadata.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="clean case cannot declare expected"):
        discover_cases(tmp_path)


def test_legacy_raw_without_suite_is_inferred_without_rewrite() -> None:
    raw = {"configuration": {"provider": "ollama", "model": "qwen"}}

    assert infer_suite_id(raw) == "legacy-v1"
    assert "suite" not in raw["configuration"]
    assert infer_suite_id({"configuration": {"suite": "v2"}}) == "v2"


def _matrix_suite() -> CorpusSuite:
    languages = ("python", "typescript", "javascript", "rust", "dart", "java", "go")
    groups = {
        "runtime": ("security", "correctness", "tests", "spec"),
        "efficiency": ("performance", "complexity", "ponytail"),
        "contract": ("documentation", "deprecation", "intent"),
    }
    cases: list[CorpusCase] = []
    for language in languages:
        for group, lenses in groups.items():
            name = f"{language}-{group}-v1"
            expected = tuple(
                CatalogEntry(lens, lens, "app.txt", index, (lens,))
                for index, lens in enumerate(lenses, start=1)
            )
            coverage = []
            if language == "python" and group == "runtime":
                coverage.append("multi-file")
            if language == "python" and group == "efficiency":
                coverage.append("large-diff")
            truth = CaseTruth(name, "app.txt", expected, (), language=language)
            cases.append(CorpusCase(Path(name), truth, {"coverage": coverage}))
        name = f"{language}-clean-v1"
        truth = CaseTruth(
            name,
            "app.txt",
            (),
            (),
            language=language,
            clean=True,
            clean_trap="plausible but safe change",
        )
        cases.append(CorpusCase(Path(name), truth, {"coverage": []}))
    for technology in ("github-actions", "terraform"):
        for clean in (False, True):
            name = f"{technology}-{'clean' if clean else 'defect'}-v1"
            expected = () if clean else (CatalogEntry("bug", "security", "ci.txt", 1, ("bug",)),)
            truth = CaseTruth(
                name,
                "ci.txt",
                expected,
                (),
                language=technology,
                clean=clean,
                clean_trap="plausible but safe config" if clean else None,
            )
            cases.append(CorpusCase(Path(name), truth, {"coverage": []}))
    return CorpusSuite("v2", tuple(case.truth.name for case in cases), tuple(cases))


def test_v2_matrix_has_balanced_cells_clean_cases_and_cross_cutting_coverage() -> None:
    coverage = validate_v2_matrix(_matrix_suite())

    assert coverage.language_lens_cells == 70
    assert coverage.clean_language_cases == 7
    assert coverage.cross_cutting_cases == 4
    assert coverage.has_spec_cases is True
    assert coverage.has_test_cases is True
    assert coverage.has_single_file is True
    assert coverage.has_multi_file is True
    assert coverage.has_large_diff is True


def test_v2_matrix_rejects_duplicate_and_missing_language_lens_cells() -> None:
    suite = _matrix_suite()
    first = suite.cases[0]
    duplicate = replace(
        first,
        truth=replace(first.truth, expected=(*first.truth.expected, first.truth.expected[0])),
    )
    with pytest.raises(ValueError, match="duplicate language/lens cell: python/security"):
        validate_v2_matrix(replace(suite, cases=(duplicate, *suite.cases[1:])))

    missing = replace(first, truth=replace(first.truth, expected=first.truth.expected[1:]))
    with pytest.raises(ValueError, match="missing language/lens cell: python/security"):
        validate_v2_matrix(replace(suite, cases=(missing, *suite.cases[1:])))


def test_v2_matrix_rejects_contradictory_clean_case_and_missing_size_class() -> None:
    suite = _matrix_suite()
    clean_index = next(index for index, case in enumerate(suite.cases) if case.truth.clean)
    clean_case = suite.cases[clean_index]
    contradictory = replace(
        clean_case,
        truth=replace(
            clean_case.truth,
            expected=(CatalogEntry("bug", "security", "x", 1, ("bug",)),),
        ),
    )
    cases = list(suite.cases)
    cases[clean_index] = contradictory
    with pytest.raises(ValueError, match="clean case has expected findings"):
        validate_v2_matrix(replace(suite, cases=tuple(cases)))

    without_large = tuple(
        replace(
            case,
            raw={
                **case.raw,
                "coverage": [tag for tag in case.raw["coverage"] if tag != "large-diff"],
            },
        )
        for case in suite.cases
    )
    with pytest.raises(ValueError, match="large-diff"):
        validate_v2_matrix(replace(suite, cases=without_large))


def test_repository_corpus_has_complete_coverage() -> None:
    cases = discover_cases(Path("corpus"), require_coverage=True)
    lenses = {entry.lens for case in cases for entry in case.truth.expected}

    assert lenses == LENSES
    assert len(cases) >= 20
    assert any(len({entry.file for entry in case.truth.expected}) > 1 for case in cases)
