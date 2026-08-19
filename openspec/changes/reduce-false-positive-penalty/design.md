## Context

The published overall score is `max(0, 2 × recall / (recall + 1) − 0.02 × false positives)`. The two-point deduction was chosen for predictability, but at that rate a handful of false positives can dominate the score and floor mid-recall runs at 0%. The requested rule halves the deduction to one percentage point per false positive.

## Goals / Non-Goals

**Goals:**

- Deduct exactly `0.01` from overall score for each false positive while the score remains above zero.
- Keep the base score at perfect precision and the zero floor.
- Recalculate historical reports from unchanged raw observations.

**Non-Goals:**

- Change strict false-positive classification, recall, precision, corpus truth, or raw evidence.
- Change the breadth suite's balanced-F1 scoring, which never applies this penalty.

## Decisions

Change the single `FALSE_POSITIVE_PENALTY` constant in `scoring.py` from `0.02` to `0.01`. The shared `overall_score()` function and both call sites (per-case and combined-repeat scoring) pick it up unchanged.

Regenerate `README.md` result markers, `RESULTS.md`, and `dashboard/` from unchanged raw JSON via `uv run bench report`. Update the hand-authored README formula section and AGENTS.md so humans and coding agents apply the same one-point deduction.

## Risks / Trade-offs

- Leaderboard rows are ordered by median score, so relative ranking can change where false-positive counts differ → expected and correct under the new rule; recall, precision, and false-positive counts stay identical for verification.
- The live spec documents only the balanced-F1 formula and requires the README to describe the legacy formula accurately, so no spec delta is needed; the README edit satisfies the obligation.
