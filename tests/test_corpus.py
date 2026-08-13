from __future__ import annotations

import json
from pathlib import Path

import pytest

from lgtmaybe_bench.corpus import LENSES, discover_cases, select_cases


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


def test_repository_corpus_has_complete_coverage() -> None:
    cases = discover_cases(Path("corpus"), require_coverage=True)
    lenses = {entry.lens for case in cases for entry in case.truth.expected}

    assert lenses == LENSES
    assert len(cases) >= 20
    assert any(len({entry.file for entry in case.truth.expected}) > 1 for case in cases)
