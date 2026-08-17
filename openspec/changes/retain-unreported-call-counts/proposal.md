## Why

`parse_review_output()` passes every numeric call column straight to `int()` inside a `try` that ends in `except (KeyError, ValueError): continue`. lgtmaybe renders `-` for a count it never received, so any such row raises and is discarded without a trace. The `findings` column already maps `-` to "unreported", so the parser is inconsistent with itself.

Re-parsing the retained stdout of every stored observation shows 1,910 call rows dropped across 324 of 1,903 observations and 11 models, hiding roughly 136,300 seconds of wall time. Of those rows, 1,651 are successful calls by models that emit no reasoning tokens, and 259 are the only per-call record of a `ProviderTruncated`, `ProviderWallTimeout`, or `RateLimitError` failure.

The affected observations therefore under-count input, output, and reasoning tokens, omit 229 genuinely truncated calls from `truncation_lenses`, and fail to deduct those calls from `wall_excluding_truncation_seconds`.

## What Changes

- Treat `-` in a numeric call column as an unreported count and retain the row, contributing zero to the observation's totals.
- Keep the existing `findings` distinction between a reported zero and an unreported count.
- Keep skipping lines that are not call rows, so profile summary lines are still ignored rather than parsed into bogus calls.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: the profile parser retains call rows whose counts are unreported instead of discarding them.

## Impact

- `src/lgtmaybe_bench/runner.py` gains one column-parsing helper used by `parse_review_output`.
- Future runs store more complete call evidence, more accurate token totals, and more complete truncation lenses.
- Published results are untouched. Reporting reads the token and truncation fields stored on each observation and never re-parses stdout, so every leaderboard metric stays exactly as it is. Whether historical observations should be re-derived from their retained stdout is a separate question and is not proposed here.
- No new runtime dependencies and no corpus change.
