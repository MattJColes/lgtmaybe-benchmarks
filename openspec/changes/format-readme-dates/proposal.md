## Why

Generated report tables currently show full UTC timestamps and order runs by time, which adds visual noise and makes model quality harder to compare. The README should show compact ISO dates and put the highest overall scores first while retaining exact timestamps in raw JSON.

## What Changes

- Render benchmark dates as `YYYY-MM-DD` in generated Markdown tables.
- Sort complete result rows by overall score descending, using newest timestamp as the deterministic tie-breaker.
- Preserve full timestamps in raw result files and use them for incomplete-run ordering and score ties.
- Cover date formatting and score ordering with behavioural tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Generated report dates use ISO calendar dates and complete rows are ordered by overall score.

## Impact

The report renderer, its behavioural tests, and generated `README.md` and `RESULTS.md` output change. Raw result schema, dependencies, and command interfaces remain unchanged.
