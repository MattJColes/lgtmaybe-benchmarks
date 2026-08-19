## Why

The README breadth leaderboard renders one table per `suite / profile / lgtmaybe version` comparison key, so readers must merge partitions by eye to see the overall picture, while the long-horizon table already ranks across versions without saying so. One top-10 table per suite with an explicit lgtmaybe version column shows the whole picture honestly in both sections.

## What Changes

- **BREAKING** Merge each suite's README top-10 into a single table ranked across lgtmaybe versions, capped at ten rows overall, with an `lgtmaybe` column naming each run's version; drop the per-key `Comparison key:` tables and headers.
- Update the hand-authored comparison guidance: suites are never ranked against each other; within a suite the version column identifies what produced each row.
- This supersedes the leaderboard-partitioning behaviour introduced by the unarchived `retain-prior-comparison-leaderboards` change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Rank each suite's canonical leaderboard across lgtmaybe versions with a per-row version column.

## Impact

The README leaderboard renderers, their tests, and the comparison-key prose in README.md and RESULTS.md change. Eligibility rules (complete canonical full-corpus runs only), scores, and the dashboard (already flat with a version filter) are unchanged. `results/raw/` is untouched.
