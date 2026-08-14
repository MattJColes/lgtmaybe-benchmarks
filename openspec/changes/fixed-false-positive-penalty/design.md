## Context

The published score currently uses the harmonic mean of recall and observed precision. This makes the marginal score cost of a false positive depend on how many planted findings the model caught and how much noise it already produced. The requested rule is a predictable two percentage-point deduction with a zero floor.

## Goals / Non-Goals

**Goals:**

- Deduct exactly `0.02` from overall score for each false positive while the score remains above zero.
- Preserve the no-noise score scale by calculating the base at perfect precision.
- Guarantee that overall score cannot become negative.
- Recalculate historical reports from raw observations.

**Non-Goals:**

- Change strict false-positive classification.
- Remove precision as a diagnostic metric.
- Change recall, corpus truth, or raw evidence.

## Decisions

Define a named `FALSE_POSITIVE_PENALTY = 0.02` constant. Calculate `base_score = harmonic_mean(recall, 1.0)`, then `score = max(0.0, base_score - false_positives * FALSE_POSITIVE_PENALTY)`. Using perfect precision for the base replaces the prior variable false-positive effect instead of charging both penalties.

Put the formula in one scoring function used by both per-case and combined-repeat scoring. Precision remains `caught / (caught + false positives)` for diagnosis but no longer feeds overall score.

Regenerate README.md and RESULTS.md from unchanged raw JSON. Update README.md and AGENTS.md so humans and coding agents apply the same fixed deduction and zero floor.

## Risks / Trade-offs

- Precision and score are no longer a direct harmonic pair → document precision as diagnostic and the score formula explicitly.
- A sufficiently noisy run reaches zero and additional false positives have no visible score effect → retain the uncapped false-positive count beside score.
- Historical ordering changes → regenerate deterministically and preserve all raw inputs.
