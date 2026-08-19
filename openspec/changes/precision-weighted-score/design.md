## Context

The long-horizon score is `max(0, 2 × recall / (recall + 1) − 0.01 × false positives)`. Recall is normalised over 32 planted findings while the deduction is a raw count, so one false positive costs a drifting fraction of a true positive and heavy noise floors the score at 0% while recall is still being measured. Breadth already scores a harmonic mean of balanced recall and pooled precision, but weights them equally. The requested rule scores both suites with F0.5.

## Goals / Non-Goals

**Goals:**

- One shared score function: `(1 + 0.25) × precision × recall / (0.25 × precision + recall)`, zero when the denominator is zero, with 0.25 as beta squared for F0.5.
- Long-horizon applies it to planted-finding recall and closed-world precision; breadth applies it to balanced recall and pooled precision.
- No zero cliff: noise damps the score toward zero without erasing nonzero recall.
- Recalculate historical reports from unchanged raw observations.

**Non-Goals:**

- Change recall, balanced recall, precision, false-positive classification, corpus truth, or raw evidence.
- Rank the suites against each other.

## Decisions

Rework `overall_score` in `scoring.py` to take recall and precision and return F0.5, with a named `PRECISION_WEIGHT = 0.25` constant; delete `FALSE_POSITIVE_PENALTY`. `score_case`, combined-repeat scoring, and `score_suite`'s balanced score all call the same function, which is the behavioural guarantee that the suites share one weighting.

Keep stored and internal identifiers (`balanced_f1` metric keys, `legacy_f1` score kind) unchanged so dashboards and stored names stay stable; update only user-facing labels to "balanced F0.5". Regenerate README result markers, RESULTS.md, and the dashboard from unchanged raw JSON. Update README.md and AGENTS.md so humans and coding agents apply the same formula.

## Risks / Trade-offs

- Leaderboard order changes wherever noise previously floored or dominated scores → expected; recall, precision, and false-positive counts stay identical per row for verification.
- Display label "balanced F0.5" over an internal `balanced_f1` key is a naming mismatch → accepted to keep stored keys stable; the label is generated in one place.
