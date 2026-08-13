## Why

Observations currently live only in process memory until every repeat and case of a configuration run completes. A single late failure — in the observed run, case 18 of 20 failing during its second Git commit — raises before `save_raw_result` is ever called, so every completed model call and profile is discarded and has to be paid for again.

## What Changes

- Persist an atomic in-progress raw record after every completed observation, using one reserved file path for the whole configuration run.
- Mark the record `in_progress` while the run is unfinished and finalize it as `complete` once every repeat and case has been observed.
- Exclude in-progress records from leaderboard and per-lens scoring, and render them in a separate incomplete-runs section so partial evidence is visible without being ranked.
- Treat raw records without a status field as complete, so existing published results keep rendering unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: raw observation retention gains incremental checkpointing and an explicit run status.
- `benchmark-scoring-reporting`: report generation ignores in-progress records for the leaderboard.

## Impact

- `src/lgtmaybe_bench/runner.py` reserves the raw path up front and writes after each observation; `save_raw_result` keeps its current signature.
- `src/lgtmaybe_bench/reporting.py` partitions raw runs by status before scoring.
- Adds a `status` field to newly written raw records; the existing schema version is unchanged because the field is optional and defaults to complete.
- No new runtime dependencies. Credentials remain excluded and completed observations stay append-only — each checkpoint rewrites the same file atomically with the previous observations untouched.
