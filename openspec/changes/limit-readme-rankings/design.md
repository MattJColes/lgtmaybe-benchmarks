## Context

The v2, context, and legacy README renderers already sort their rows by score, but each independently renders every eligible result. Detailed Markdown and dashboard outputs use separate renderers and must remain unbounded.

## Goals / Non-Goals

**Goals:**

- Apply one explicit ten-row limit to every README ranking.
- Preserve descending score order and deterministic tie-breaking.
- Keep all detailed outputs complete.
- Expose the already-stored true-positive metric in the HTML results table.

**Non-Goals:**

- Change scoring, eligibility, comparison partitions, or dashboard ordering.
- Add pagination or a configurable limit.
- Remove or mutate raw evidence.

## Decisions

Define one module-level README result limit and slice each already-sorted README run sequence before rendering rows. Applying the limit after eligibility, comparison partitioning, and scoring preserves the existing semantics while keeping the ranking change local to README rendering. An alternative shared ranking abstraction would add indirection without reducing meaningful duplication.

`RESULTS.md` and dashboard data already retain true positives for every complete run. Add one HTML header and cell that render the existing `metrics.true_positives` value; no data-model change is needed. Behavioural tests will exercise more than ten inputs for context, v2, and legacy paths and confirm lower-ranked results remain in detailed outputs with true positives visible.

## Risks / Trade-offs

- [A renderer omits the limit] → Cover all three README paths with behavioural tests using eleven or more eligible runs.
- [Tied scores produce unstable membership] → Keep the existing timestamp and run-identity tie-breakers before slicing.
