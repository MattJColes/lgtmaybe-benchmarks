## Why

A canonical full-corpus result is publishable only when every observation completes with no failure or timeout. The first failed observation therefore makes the configuration irreversibly ineligible, but `execute_benchmark()` keeps working through every remaining case and repeat and then writes `status: complete`. In the 27-model breadth campaign, `anthropic/claude-haiku-4.5` completed all 96 observations and was marked complete even though its first unparseable observation had already made the result unscorable.

Today the only way to stop the waste is external monitoring that kills the process. That spends provider time and money on a result that can never be scored, and a killed run leaves an `in_progress` record that is indistinguishable from an accidental interruption.

## What Changes

- Stop a canonical full-corpus run before starting another observation once an observation exits non-zero or times out.
- Checkpoint the failed observation atomically before stopping, so it survives as campaign evidence.
- Write the terminal status `ineligible` instead of leaving `in_progress` or reaching `complete`.
- Record a structured `termination` block naming the repeat, case, observation ID, exit code, timeout flag, and classified failure.
- Classify each failed observation as `timeout`, `truncated_output`, `unparseable_output`, or `nonzero_exit` and retain that class on the observation.
- Keep collecting failures for focused and diagnostic runs, whose purpose is investigation rather than leaderboard eligibility.
- Keep `ineligible` records out of every score, ranking, and generated Markdown table.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: canonical full-corpus runs gain first-failure termination, a terminal `ineligible` status, and a structured termination reason.
- `benchmark-scoring-reporting`: report generation states explicitly that terminal ineligible records are never scored or ranked.

## Impact

- `src/lgtmaybe_bench/runner.py` classifies observation failures, stops canonical full-corpus runs at the first failure, and writes the terminal record.
- `src/lgtmaybe_bench/reporting.py` needs no eligibility change; every existing filter already requires `complete`, and behavioural tests pin that for the new status.
- Newly written raw records gain optional `termination` and per-observation `failure_class` fields. Published raw results under `results/raw/` are untouched, and records without the new fields keep reading as before.
- No new runtime dependencies, no corpus change, and no change to any published metric.
