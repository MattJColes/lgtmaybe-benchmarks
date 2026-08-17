## Why

Publishing the first result under a newer lgtmaybe version replaced the README breadth leaderboard with a single row, making every earlier comparison group disappear from the public summary even though its raw evidence remained stored. A new comparison key must not erase visibility of earlier published results.

## What Changes

- Render each retained breadth comparison key as a separately labelled leaderboard in the README.
- Keep runs ranked only against runs with the same suite, profile, and lgtmaybe version.
- Order comparison groups newest first and continue limiting each group to ten rows.
- Leave raw results and the exhaustive `RESULTS.md` unchanged except for deterministic regeneration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: README reporting retains separately labelled historical comparison groups instead of showing only the newest group.

## Impact

- `src/lgtmaybe_bench/reporting.py` breadth leaderboard selection and rendering.
- Behavioural coverage in `tests/test_reporting.py`.
- Generated `README.md`, `RESULTS.md`, and dashboard artifacts.
- No runtime dependencies, corpus changes, raw-result rewrites, or cross-key rankings.
