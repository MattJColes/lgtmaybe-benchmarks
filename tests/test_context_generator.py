from __future__ import annotations

import json
from pathlib import Path

from lgtmaybe_bench.context_generator import (
    BUG_COUNT,
    CASE_NAMES,
    SUITE_ID,
    TARGET_FRACTIONS,
    generate_suite,
)
from lgtmaybe_bench.corpus import discover_cases, load_suite
from lgtmaybe_bench.runner import get_profile
from lgtmaybe_bench.scoring import parse_case


def generate(root: Path) -> Path:
    corpus = root / "corpus"
    generate_suite(corpus)
    return corpus


def changed_python_files(case_dir: Path) -> list[Path]:
    return sorted((case_dir / "changed").rglob("*.py"))


def total_changed_lines(case_dir: Path) -> int:
    return sum(
        len(path.read_text(encoding="utf-8").splitlines())
        for path in changed_python_files(case_dir)
    )


def entry_slot(label: str) -> str:
    return label.rpartition(" @ ")[2]


def test_generation_is_deterministic(tmp_path: Path) -> None:
    first = generate(tmp_path / "a")
    second = generate(tmp_path / "b")

    first_files = sorted(
        path.relative_to(first).as_posix() for path in first.rglob("*") if path.is_file()
    )
    second_files = sorted(
        path.relative_to(second).as_posix() for path in second.rglob("*") if path.is_file()
    )
    assert first_files == second_files
    for relative in first_files:
        assert (first / relative).read_bytes() == (second / relative).read_bytes()


def test_generated_cases_pass_corpus_validation(tmp_path: Path) -> None:
    corpus = generate(tmp_path)

    cases = discover_cases(corpus)
    assert [case.truth.name for case in cases] == sorted(CASE_NAMES)
    for case in cases:
        assert case.truth.language == "python"
        assert "context-scaling" in case.raw["coverage"]
        assert "multi-file" in case.raw["coverage"]

    suite = load_suite(corpus, SUITE_ID)
    assert suite.id == SUITE_ID
    assert [case.truth.name for case in suite.cases] == list(CASE_NAMES)


def test_defect_cases_plant_eight_bugs_and_clean_case_plants_none(tmp_path: Path) -> None:
    corpus = generate(tmp_path)

    for name in CASE_NAMES:
        truth = parse_case(
            json.loads((corpus / name / "case.json").read_text(encoding="utf-8"))
        )
        if name == "python-context-clean-large-v1":
            assert truth.clean
            assert truth.expected == ()
            assert truth.clean_trap
        else:
            assert not truth.clean
            assert len(truth.expected) == BUG_COUNT


def test_size_bands_grow_monotonically(tmp_path: Path) -> None:
    corpus = generate(tmp_path)

    sizes = {
        name: total_changed_lines(corpus / name)
        for name in CASE_NAMES
        if name != "python-context-clean-large-v1"
    }
    ordered = list(CASE_NAMES[:-1])
    assert ordered == [
        "python-context-small-v1",
        "python-context-medium-v1",
        "python-context-large-v1",
        "python-context-xlarge-v1",
    ]
    assert sizes["python-context-small-v1"] < sizes["python-context-medium-v1"]
    assert sizes["python-context-medium-v1"] < sizes["python-context-large-v1"]
    assert sizes["python-context-large-v1"] < sizes["python-context-xlarge-v1"]
    assert 150 <= sizes["python-context-small-v1"] <= 600


def test_bug_positions_follow_target_fractions(tmp_path: Path) -> None:
    corpus = generate(tmp_path)

    for name in CASE_NAMES:
        if name == "python-context-clean-large-v1":
            continue
        truth = parse_case(json.loads((corpus / name / "case.json").read_text(encoding="utf-8")))
        changed_root = corpus / name / "changed"
        files = [
            path.relative_to(changed_root).as_posix()
            for path in changed_python_files(corpus / name)
        ]
        lengths = {
            file: len((changed_root / file).read_text(encoding="utf-8").splitlines())
            for file in files
        }
        total = sum(lengths.values())

        slots = {entry_slot(entry.label) for entry in truth.expected}
        assert slots == {"first-file", "last-file"} | {
            f"{fraction:.0%}" for fraction in TARGET_FRACTIONS
        }

        for entry in truth.expected:
            offset = sum(lengths[file] for file in files if file < entry.file)
            fraction = (offset + entry.line) / total
            slot = entry_slot(entry.label)
            if slot == "first-file":
                assert entry.file == files[0]
                assert fraction <= TARGET_FRACTIONS[0] + 0.05
            elif slot == "last-file":
                assert entry.file == files[-1]
                assert fraction >= TARGET_FRACTIONS[-1] - 0.05
            else:
                target = float(slot.removesuffix("%")) / 100
                assert abs(fraction - target) <= 0.08, f"{name} {slot}: {fraction:.3f}"


def test_base_and_changed_trees_differ_broadly(tmp_path: Path) -> None:
    corpus = generate(tmp_path)
    case = corpus / "python-context-small-v1"

    changed_files = changed_python_files(case)
    differing = 0
    for path in changed_files:
        base = case / "base" / path.relative_to(case / "changed")
        if base.exists() and base.read_text(encoding="utf-8") != path.read_text(encoding="utf-8"):
            differing += 1
    assert differing >= len(changed_files) * 3 // 4


def test_context_profile_uses_one_repeat_full_preset_and_canonical_token_cap() -> None:
    profile = get_profile("context-canonical-v1")

    assert profile.repeats == 1
    assert profile.preset == "full"
    assert profile.max_input_tokens == 100_000
    assert profile.max_tokens is None
    assert not profile.canonical
