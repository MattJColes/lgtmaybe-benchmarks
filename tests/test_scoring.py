from __future__ import annotations

import json
from pathlib import Path

import pytest

from lgtmaybe_bench.scoring import (
    LINE_WINDOW,
    CaseTruth,
    CatalogEntry,
    Finding,
    RepeatMetrics,
    SuiteObservation,
    SuiteRepeatMetrics,
    aggregate_repeats,
    aggregate_suite_repeats,
    append_adjudication,
    effort_label,
    load_adjudications,
    parse_case,
    parse_findings,
    score_case,
    score_suite,
)


def _raw_evidence() -> list[dict[str, object]]:
    return [
        {
            "run_id": "run-1",
            "configuration": {"suite": "v2"},
            "observations": [
                {
                    "observation_id": "obs-1",
                    "repeat": 1,
                    "findings": [{"finding_id": "finding-1"}],
                    "audit": {"path": None},
                }
            ],
        }
    ]


def _adjudication(
    event_id: str,
    classification: str,
    *,
    evidence_id: str = "finding-1",
    supersedes: str | None = None,
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "suite": "v2",
        "run_id": "run-1",
        "observation_id": "obs-1",
        "repeat": 1,
        "evidence_kind": "finding",
        "evidence_id": evidence_id,
        "classification": classification,
        "reason": "manual review",
        "adjudicator": "maintainer",
        "timestamp": "2026-08-14T00:00:00Z",
        "supersedes": supersedes,
    }


def test_adjudication_history_is_append_only_and_latest_supersession_wins(
    tmp_path: Path,
) -> None:
    path = tmp_path / "results" / "adjudications" / "manual.jsonl"
    first = _adjudication("adj-1", "true_positive")
    second = _adjudication("adj-2", "false_positive", supersedes="adj-1")

    append_adjudication(path, first)
    append_adjudication(path, second)
    history = load_adjudications(tmp_path, _raw_evidence())

    assert [event.event_id for event in history.events] == ["adj-1", "adj-2"]
    assert next(iter(history.current.values())).event_id == "adj-2"
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


def test_adjudication_rejects_invalid_evidence_and_supersession(tmp_path: Path) -> None:
    directory = tmp_path / "results" / "adjudications"
    directory.mkdir(parents=True)
    (directory / "invalid.jsonl").write_text(
        json.dumps(_adjudication("adj-1", "false_positive", evidence_id="missing")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown evidence identity"):
        load_adjudications(tmp_path, _raw_evidence())

    (directory / "invalid.jsonl").write_text(
        json.dumps(_adjudication("adj-2", "duplicate", supersedes="missing-event")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown superseded adjudication"):
        load_adjudications(tmp_path, _raw_evidence())


def test_adjudication_current_state_is_deterministic_across_files(tmp_path: Path) -> None:
    directory = tmp_path / "results" / "adjudications"
    directory.mkdir(parents=True)
    (directory / "b.jsonl").write_text(
        json.dumps(_adjudication("adj-2", "duplicate", supersedes="adj-1")) + "\n",
        encoding="utf-8",
    )
    (directory / "a.jsonl").write_text(
        json.dumps(_adjudication("adj-1", "unadjudicated")) + "\n",
        encoding="utf-8",
    )

    first = load_adjudications(tmp_path, _raw_evidence())
    second = load_adjudications(tmp_path, _raw_evidence())

    assert first == second
    assert next(iter(first.current.values())).classification == "duplicate"


def truth(*, severity: str = "medium") -> dict[str, object]:
    return {
        "name": "off-by-one",
        "changed_file": "app.py",
        "expected": [
            {
                "label": "range skips final item",
                "lens": "correctness",
                "line": 10,
                "keywords": ["off-by-one", "final item"],
                "severity_at_least": severity,
            },
            {
                "label": "missing regression test",
                "lens": "tests",
                "line": 20,
                "keywords": ["missing test"],
            },
        ],
        "forbidden": [
            {
                "label": "claims auth is missing",
                "lens": "security",
                "line": 30,
                "keywords": ["missing auth"],
            }
        ],
    }


def finding(line: int, body: str, *, severity: str = "high") -> dict[str, object]:
    return {
        "file": "app.py",
        "line": line,
        "severity": severity,
        "title": body,
        "body": "details",
    }


def test_expected_finding_matches_at_line_window_boundary() -> None:
    case = parse_case(truth())
    findings = parse_findings([finding(10 + LINE_WINDOW, "Off-by-one")])

    result = score_case(case, findings)

    assert result.caught == 1
    assert result.recall == pytest.approx(0.5)
    assert result.precision == 1.0
    assert result.score == pytest.approx(2 / 3)


def test_finding_outside_line_window_is_a_false_positive() -> None:
    result = score_case(
        parse_case(truth()),
        parse_findings([finding(10 + LINE_WINDOW + 1, "Off-by-one")]),
    )

    assert result.caught == 0
    assert result.adjudicable == 1
    assert result.unexpected == 1
    assert result.false_positives == 1
    assert result.precision == 0.0


def test_keyword_with_wrong_severity_is_unexpected() -> None:
    result = score_case(
        parse_case(truth(severity="high")),
        parse_findings([finding(10, "Off-by-one", severity="medium")]),
    )

    assert result.caught == 0
    assert result.unexpected == 1
    assert result.false_positives == 1
    assert result.adjudicable == 1
    assert result.precision == 0.0


def test_forbidden_hit_makes_run_unclean() -> None:
    result = score_case(
        parse_case(truth()),
        parse_findings([finding(30, "Missing auth guard")]),
    )

    assert result.forbidden_hits == 1
    assert result.false_positives == 1
    assert result.clean is False
    assert result.precision == 0.0


def test_duplicate_expected_finding_counts_as_noise() -> None:
    case = parse_case(truth())
    findings = parse_findings([finding(10, "Off-by-one"), finding(11, "Final item is skipped")])

    result = score_case(case, findings)

    assert result.caught == 1
    assert result.unexpected == 1
    assert result.false_positives == 1
    assert result.adjudicable == 2
    assert result.precision == 0.5


def test_each_false_positive_deducts_one_percentage_point() -> None:
    case = parse_case(truth())
    clean = score_case(case, parse_findings([finding(10, "Off-by-one")]))
    noisy = score_case(
        case,
        parse_findings([finding(10, "Off-by-one"), finding(100, "Plausible issue")]),
    )

    assert noisy.score == pytest.approx(clean.score - 0.01)


def test_false_positive_penalty_cannot_reduce_score_below_zero() -> None:
    case = parse_case(truth())
    findings = [finding(10, "Off-by-one")]
    findings.extend(finding(100 + index, f"Noise {index}") for index in range(68))

    result = score_case(case, parse_findings(findings))

    assert result.false_positives == 68
    assert result.score == 0.0


def test_per_lens_recall_includes_zeroes() -> None:
    result = score_case(
        parse_case(truth()),
        parse_findings([finding(10, "Off-by-one")]),
    )

    assert result.per_lens == {"correctness": 1.0, "tests": 0.0}


def test_aggregate_reports_median_min_max_and_tokens() -> None:
    case = parse_case(truth())
    scores = [
        score_case(case, parse_findings([])),
        score_case(
            case,
            parse_findings([finding(10, "Off-by-one"), finding(100, "Plausible issue")]),
        ),
        score_case(
            case,
            parse_findings(
                [
                    finding(10, "Off-by-one"),
                    finding(20, "Missing test"),
                    finding(100, "Plausible issue"),
                    finding(110, "Another plausible issue"),
                ]
            ),
        ),
    ]
    repeats = [
        RepeatMetrics(scores[0], 30.0, 30.0, (), 100, 10, 0, 0),
        RepeatMetrics(scores[1], 90.0, 40.0, ("correctness",), 200, 20, 5, 0),
        RepeatMetrics(scores[2], 60.0, 60.0, (), 300, 30, 10, 1),
    ]

    result = aggregate_repeats(repeats)

    assert (result.recall.median, result.recall.minimum, result.recall.maximum) == (
        0.5,
        0.0,
        1.0,
    )
    assert result.wall_seconds.median == 60.0
    assert (
        result.false_positives.median,
        result.false_positives.minimum,
        result.false_positives.maximum,
    ) == (1.0, 0.0, 2.0)
    assert result.input_tokens.median == 200
    assert result.truncations.maximum == 1
    assert result.truncation_lenses == ("correctness",)
    assert result.failures.maximum == 1


def test_single_repeat_uses_same_aggregate_shape() -> None:
    score = score_case(parse_case(truth()), parse_findings([]))

    result = aggregate_repeats([RepeatMetrics(score, 3.0, 3.0, (), 1, 2, 0, 0)])

    assert result.wall_seconds.median == result.wall_seconds.minimum == result.wall_seconds.maximum


def test_ollama_effort_label_is_explicit() -> None:
    assert effort_label("ollama", "high") == "high (thinking off)"
    assert effort_label("openai", "high") == "high"


def _suite_case(language: str, lens: str, *, clean: bool = False) -> CaseTruth:
    expected = (
        ()
        if clean
        else (CatalogEntry(f"{language}-{lens}", lens, "app.py", 10, (f"{language}-{lens}",)),)
    )
    return CaseTruth(
        f"{language}-{lens}",
        "app.py",
        expected,
        (),
        language=language,
        clean=clean,
        clean_trap="safe" if clean else None,
    )


def _scored_finding(finding_id: str, line: int, title: str) -> Finding:
    return parse_findings(
        [
            {
                "finding_id": finding_id,
                "file": "app.py",
                "line": line,
                "severity": "high",
                "title": title,
                "body": "details",
            }
        ]
    )[0]


def test_balanced_recall_averages_70_cells_and_precision_pools_adjudicated_findings() -> None:
    languages = ("python", "typescript", "javascript", "rust", "dart", "java", "go")
    lenses = (
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
    observations: list[SuiteObservation] = []
    for language in languages:
        for lens in lenses:
            case = _suite_case(language, lens)
            findings = (
                (_scored_finding(f"{language}-{lens}", 10, f"{language}-{lens}"),)
                if language == "python"
                else ()
            )
            observations.append(SuiteObservation(case, findings))
        clean = _suite_case(language, "clean", clean=True)
        noise = (
            ()
            if language == "python"
            else (_scored_finding(f"{language}-noise", 1, "plausible warning"),)
        )
        observations.append(SuiteObservation(clean, noise))

    result = score_suite(observations)

    assert result.language_lens_cells == 70
    assert result.balanced_recall == pytest.approx(1 / 7)
    assert result.true_positives == 10
    assert result.false_positives == 6
    assert result.precision == pytest.approx(10 / 16)
    assert result.clean_pass_rate == pytest.approx(1 / 7)
    assert result.balanced_f1 == pytest.approx(2 * (1 / 7) * (10 / 16) / ((1 / 7) + (10 / 16)))


def test_false_positive_classes_duplicates_unadjudicated_and_later_adjudication() -> None:
    case = CaseTruth(
        "mixed",
        "app.py",
        (CatalogEntry("expected", "security", "app.py", 10, ("expected",)),),
        (CatalogEntry("forbidden", "security", "app.py", 20, ("forbidden",)),),
        language="python",
    )
    clean = _suite_case("python", "clean", clean=True)
    findings = (
        _scored_finding("tp", 10, "expected"),
        _scored_finding("duplicate", 10, "expected"),
        _scored_finding("forbidden", 20, "forbidden"),
        _scored_finding("near", 11, "different concern"),
        _scored_finding("distant", 50, "new discovery"),
    )
    observations = [
        SuiteObservation(case, findings),
        SuiteObservation(clean, (_scored_finding("clean-fp", 1, "guess"),)),
    ]

    provisional = score_suite(observations)
    adjudicated = score_suite(observations, {"distant": "true_positive"})

    assert provisional.true_positives == 1
    assert provisional.false_positive_classes == {
        "forbidden": 1,
        "clean_case": 1,
        "unexpected_near": 1,
        "duplicate": 1,
        "adjudicated": 0,
    }
    assert provisional.duplicates == 1
    assert provisional.unadjudicated == 1
    assert provisional.provisional is True
    assert provisional.precision == pytest.approx(1 / 5)
    assert provisional.clean_pass_rate == 0.0
    assert adjudicated.true_positives == 2
    assert adjudicated.unadjudicated == 0
    assert adjudicated.adjudication_coverage == 1.0
    assert adjudicated.provisional is False
    assert adjudicated.precision == pytest.approx(2 / 6)


def test_suite_repeat_aggregation_reports_medians_and_full_ranges() -> None:
    defect = _suite_case("python", "security")
    clean = _suite_case("python", "clean", clean=True)
    missed = score_suite([SuiteObservation(defect, ()), SuiteObservation(clean, ())])
    noisy = score_suite(
        [
            SuiteObservation(defect, (_scored_finding("tp", 10, "python-security"),)),
            SuiteObservation(clean, (_scored_finding("noise", 1, "guess"),)),
        ]
    )
    clean_hit = score_suite(
        [
            SuiteObservation(defect, (_scored_finding("tp-2", 10, "python-security"),)),
            SuiteObservation(clean, ()),
        ]
    )
    repeats = [
        SuiteRepeatMetrics(missed, 30.0, 30.0, (), 100, 10, 0, 0),
        SuiteRepeatMetrics(noisy, 90.0, 40.0, ("security",), 200, 20, 5, 0),
        SuiteRepeatMetrics(clean_hit, 60.0, 60.0, (), 300, 30, 10, 1),
    ]

    result = aggregate_suite_repeats(repeats)

    assert (result.balanced_recall.median, result.balanced_recall.minimum) == (1.0, 0.0)
    assert result.balanced_f1.median == pytest.approx(2 / 3)
    assert (result.clean_pass_rate.minimum, result.clean_pass_rate.maximum) == (0.0, 1.0)
    assert result.true_positives.maximum == 1
    assert result.false_positives.maximum == 1
    assert result.input_tokens.median == 200
    assert result.truncation_lenses == ("security",)


def test_single_diagnostic_suite_repeat_uses_the_same_aggregate_shape() -> None:
    score = score_suite([SuiteObservation(_suite_case("python", "security"), ())])

    result = aggregate_suite_repeats([SuiteRepeatMetrics(score, 3.0, 3.0, (), 1, 2, 0, 0)])

    assert result.balanced_f1.median == result.balanced_f1.minimum == result.balanced_f1.maximum
    assert result.input_tokens.median == result.input_tokens.minimum == result.input_tokens.maximum
