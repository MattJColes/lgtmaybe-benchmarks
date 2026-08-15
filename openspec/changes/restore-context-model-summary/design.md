## Context

The `v2` renderer has a model-level leaderboard, while the context renderer emits only per-case rows. When no eligible `v2` results remain, README generation therefore has no aggregate model scores. Dashboard serialization also calculates context scores but replaces their true-positive and false-positive totals with missing values.

## Goals / Non-Goals

**Goals:**

- Render one aggregate row per eligible context model from the existing scorer output.
- Preserve context true-positive and false-positive totals in detailed generated data.
- Keep generated output deterministic and covered by behavioural tests.

**Non-Goals:**

- Change the scoring formula, matching, eligibility, corpus, or run profiles.
- Combine context models with the `v2` canonical leaderboard.
- Reclassify any stored finding.

## Decisions

The context renderer will derive its summary rows from the same eligible result objects and scoring functions used for its case rows. This keeps one closed-world score source and avoids a second aggregation path. An alternative was to recover counts from rendered case text, but that would duplicate scoring logic and lose typed values.

The README will show the compact model summary before the existing case table. `RESULTS.md` receives the same generated section through the existing report pipeline. Dashboard serialization will expose the already-computed aggregate counts instead of overwriting them with `None`.

Behavioural tests will assert summary values, count preservation, eligibility filtering, and deterministic regeneration before generated artefacts are refreshed from raw results.

## Risks / Trade-offs

- [Context score labels could be confused with the `v2` balanced-F1 leaderboard] → Keep the section explicitly named context scaling and do not merge its rows into the canonical leaderboard.
- [Summary and case rows could drift] → Generate both from the same eligible results and scorer output in one render pass.
