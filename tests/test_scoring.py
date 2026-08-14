from __future__ import annotations

import pytest

from lgtmaybe_bench.scoring import (
    LINE_WINDOW,
    RepeatMetrics,
    aggregate_repeats,
    effort_label,
    parse_case,
    parse_findings,
    score_case,
)


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
