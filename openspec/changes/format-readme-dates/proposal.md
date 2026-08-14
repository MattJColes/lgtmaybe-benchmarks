## Why

Generated report tables currently show full UTC timestamps, which adds visual noise when comparing runs by day. The README should show compact ISO dates while retaining exact timestamps in raw JSON.

## What Changes

- Render benchmark dates as `YYYY-MM-DD` in generated Markdown tables.
- Preserve full timestamps in raw result files and use them for newest-first sorting.
- Cover complete and incomplete result rows with behavioural tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Generated report dates use ISO calendar dates instead of full timestamps.

## Impact

The report renderer, its behavioural tests, and generated `README.md` and `RESULTS.md` output change. Raw result schema, sorting, dependencies, and command interfaces remain unchanged.
