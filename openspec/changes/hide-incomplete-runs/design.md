## Context

The report renderer currently separates completed and incomplete raw results, then publishes incomplete checkpoints in their own Markdown section. Checkpoints are useful diagnostic state under `results/raw/`, but they are not benchmark outcomes.

## Goals / Non-Goals

**Goals:**

- Publish only comparable, completed full-corpus runs.
- Preserve incomplete raw checkpoints unchanged.
- Keep report generation deterministic.

**Non-Goals:**

- Delete, resume, or score incomplete checkpoints.
- Change failure filtering or benchmark execution.

## Decisions

Remove incomplete-run rendering from the existing report path. Filtering at render time is sufficient because raw storage already preserves every checkpoint and no additional data migration is needed.

When no publishable completed run remains, reuse the existing `No benchmark runs recorded.` output. A separate incomplete-only state would reintroduce the distinction the public report is removing.

## Risks / Trade-offs

- Diagnostic progress is no longer visible in README or RESULTS → retain raw checkpoints in version control for inspection.
- Users may confuse an empty report with no raw evidence → document the raw evidence location in the specification and PR.
