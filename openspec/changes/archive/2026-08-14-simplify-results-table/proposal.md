## Why

The generated leaderboard duplicates the per-lens table, is too wide to scan, and spends most of its space repeating full-corpus case names and default configuration. Results should make model quality obvious first and surface configuration only when a run actually differs from the benchmark defaults.

## What Changes

- **BREAKING** Replace the separate leaderboard and per-lens tables with one historical results table.
- Keep run identity, overall score, and every per-lens recall value in the consolidated table.
- Remove the `cases` column and exclude focused `--case` runs from generated comparison tables; their raw evidence remains available.
- Add a final `settings` column containing only meaningful non-default configuration, such as reasoning effort, token limits, non-full preset, custom API base, concurrency override, repeat count, or timeout.
- Keep complete metrics, configuration, timings, tokens, failures, and findings in the raw JSON rather than repeating them across the Markdown table.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: Record whether a run covers the full corpus so reports can exclude focused diagnostic runs deterministically.
- `benchmark-scoring-reporting`: Consolidate generated results into the per-lens-oriented table and summarize only non-default settings.

## Impact

- Changes the generated section of `README.md` and all of `RESULTS.md`.
- Updates raw run configuration with a backward-compatible full-corpus marker.
- Updates `src/lgtmaybe_bench/runner.py`, `src/lgtmaybe_bench/reporting.py`, and their behavioural/golden tests.
- Adds no runtime dependency and does not alter scoring or existing raw observations.
