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
    call_completeness,
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
    assert result.score == pytest.approx(1.25 * 0.5 / (0.25 + 0.5))


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


def test_score_is_f_half_of_precision_and_recall() -> None:
    case = parse_case(truth())

    result = score_case(
        case,
        parse_findings([finding(10, "Off-by-one"), finding(100, "Plausible issue")]),
    )

    assert result.recall == pytest.approx(0.5)
    assert result.precision == pytest.approx(0.5)
    assert result.score == pytest.approx(1.25 * 0.5 * 0.5 / (0.25 * 0.5 + 0.5))


def test_score_weights_precision_more_than_recall() -> None:
    case = parse_case(truth())
    precise_but_partial = score_case(case, parse_findings([finding(10, "Off-by-one")]))
    complete_but_noisy = score_case(
        case,
        parse_findings(
            [
                finding(10, "Off-by-one"),
                finding(20, "Missing test"),
                finding(100, "Noise a"),
                finding(200, "Noise b"),
            ]
        ),
    )

    assert precise_but_partial.recall == complete_but_noisy.precision == 0.5
    assert precise_but_partial.score > complete_but_noisy.score


def test_heavy_noise_dampens_score_without_erasing_recall() -> None:
    case = parse_case(truth())
    findings = [finding(10, "Off-by-one")]
    findings.extend(finding(100 + index, f"Noise {index}") for index in range(68))

    result = score_case(case, parse_findings(findings))

    assert result.false_positives == 68
    assert 0.0 < result.score < 0.05


def test_no_findings_scores_zero() -> None:
    result = score_case(parse_case(truth()), parse_findings([]))

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
        RepeatMetrics(scores[0], 1.0, 30.0, 30.0, (), 100, 10, 0, 0),
        RepeatMetrics(scores[1], 1.0, 90.0, 40.0, ("correctness",), 200, 20, 5, 0),
        RepeatMetrics(scores[2], 1.0, 60.0, 60.0, (), 300, 30, 10, 1),
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

    result = aggregate_repeats([RepeatMetrics(score, 1.0, 3.0, 3.0, (), 1, 2, 0, 0)])

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
    assert result.balanced_f1 == pytest.approx(
        1.25 * (10 / 16) * (1 / 7) / (0.25 * (10 / 16) + (1 / 7))
    )


def test_both_suites_share_the_precision_weighted_formula() -> None:
    case_score = score_case(
        parse_case(truth()),
        parse_findings(
            [
                finding(10, "Off-by-one"),
                finding(20, "Missing test"),
                finding(100, "Noise a"),
                finding(200, "Noise b"),
            ]
        ),
    )
    suite_score = score_suite(
        [
            SuiteObservation(
                _suite_case("python", "security"),
                (
                    _scored_finding("tp", 10, "python-security"),
                    _scored_finding("near-noise", 11, "different concern"),
                ),
            )
        ]
    )

    assert case_score.recall == suite_score.balanced_recall == 1.0
    assert case_score.precision == suite_score.precision == 0.5
    assert case_score.score == pytest.approx(suite_score.balanced_f1)


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
    assert result.balanced_f1.median == pytest.approx(1.25 * 0.5 / (0.25 * 0.5 + 1.0))
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


class TestCallCompleteness:
    """A lens call that returned nothing is invisible to precision.

    Precision is computed only over findings that exist, so a run whose calls
    mostly failed is scored on the handful that survived. Recall does see the
    loss, but F0.5 weights recall at half, so the failure is under-counted.
    Measured on the stored corpus: `z-ai/glm-4.7-flash` failed to parse 73.8% of
    its lens calls and still scored 50.0%, above a run that found 24 planted
    bugs to its 14.
    """

    def test_a_failed_call_is_one_that_returned_no_parseable_findings(self) -> None:
        observations = [
            {"calls": [{"findings": 3}, {"findings": 0}, {"findings": None}, {"findings": 1}]}
        ]
        assert call_completeness(observations) == pytest.approx(3 / 4)

    def test_zero_findings_is_an_answer_not_a_failure(self) -> None:
        """A lens is entitled to find nothing; that is `[]`, not a failure."""
        assert call_completeness([{"calls": [{"findings": 0}, {"findings": 0}]}]) == 1.0

    def test_it_falls_back_to_the_provider_call_log(self) -> None:
        """Nine stored runs predate the structured `calls` array. Their stderr
        still carries one `provider call` line per call, so the factor is
        derived rather than assumed."""
        stderr = "\n".join(
            [
                '{"message": "provider call", "label": "security", "findings": 2}',
                '{"message": "provider call", "label": "tests", "findings": null}',
                '{"message": "stage completed", "stage": "dedupe"}',
            ]
        )
        assert call_completeness([{"calls": [], "stderr": stderr}]) == pytest.approx(1 / 2)

    def test_completeness_is_unknown_when_nothing_reports_calls(self) -> None:
        """None, not 1.0: an unmeasured run must not be scored as a complete one."""
        assert call_completeness([{"calls": [], "stderr": ""}]) is None

    def test_the_score_is_scaled_by_completeness(self) -> None:
        observations = [
            SuiteObservation(
                _suite_case("python", "security"),
                (_scored_finding("tp", 10, "python-security"),),
            )
        ]
        whole = score_suite(observations)
        half = score_suite(observations, completeness=0.5)
        assert half.balanced_f1 == pytest.approx(whole.balanced_f1 * 0.5)
        assert half.completeness == pytest.approx(0.5)

    def test_unknown_completeness_leaves_the_score_alone(self) -> None:
        """A run that cannot report its calls keeps its score and says so, so a
        reader can tell an unmeasured run from a complete one."""
        observations = [
            SuiteObservation(
                _suite_case("python", "security"),
                (_scored_finding("tp", 10, "python-security"),),
            )
        ]
        unknown = score_suite(observations, completeness=None)
        assert unknown.balanced_f1 == pytest.approx(score_suite(observations).balanced_f1)
        assert unknown.completeness is None
