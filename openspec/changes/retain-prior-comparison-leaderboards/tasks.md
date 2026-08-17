## 1. Behavioural coverage

- [x] 1.1 Add a failing test proving a newer lgtmaybe comparison key does not remove the earlier canonical breadth leaderboard.
- [x] 1.2 Assert comparison groups are newest-first, independently ranked, and limited to ten rows each.

## 2. Reporting

- [x] 2.1 Partition eligible canonical breadth runs by comparison key and render every partition.
- [x] 2.2 Regenerate README, RESULTS, and dashboard artifacts from stored raw results.

## 3. Verification

- [x] 3.1 Run pytest, Ruff, mypy, OpenSpec validation, and report determinism checks.
- [x] 3.2 Confirm all raw result files remain present and the README shows both lgtmaybe 2.2.0 and 2.1.4 breadth groups.
