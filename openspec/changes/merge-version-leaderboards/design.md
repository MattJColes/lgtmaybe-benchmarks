## Context

`_render_breadth_canonical` partitions eligible runs by `suite / profile / lgtmaybe version` and renders a labelled top-10 per partition; `_render_context_scaling` ranks long-horizon runs globally with no version shown. Matt wants one overall top-10 per suite with the version as a column, in both README sections.

## Goals / Non-Goals

**Goals:**

- One table per suite section: rank all eligible canonical runs together, cut to ten rows overall, add an `lgtmaybe` column after `model`.
- Keep eligibility unchanged: complete, canonical profile, full corpus, no failures.
- Keep RESULTS.md's flat all-runs table and the dashboard as they are.

**Non-Goals:**

- Rank the two suites against each other.
- Deduplicate models across versions — every eligible run competes.

## Decisions

Delete the partition grouping in `_render_breadth_canonical`; sort once by `(median score desc, timestamp desc, run_id)` — the same ordering previously used within a partition — and slice to the README limit. `_render_context_scaling` only gains the column. Section blurbs name the suite and profile in prose and state that rows span lgtmaybe versions.

Superseding note: the unarchived `retain-prior-comparison-leaderboards` change introduced the per-key tables this removes; its delta is superseded by this change's delta rather than edited, keeping the historical record intact.

## Risks / Trade-offs

- Rows produced under different lgtmaybe versions rank together even though tool behaviour may differ between versions → accepted deliberately; the version column keeps the difference visible, and the dashboard still filters by version for strict comparisons.
- Older-version rows can crowd the ten-row cut → expected: the table answers "best runs overall", not "best per version".
