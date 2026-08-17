## 1. Behavioural coverage

- [x] 1.1 Write a failing test for a successful call row whose reasoning count is `-` being retained with its other counts reaching the observation totals.
- [x] 1.2 Write a failing test for a failed call row reporting no counts being retained with its error, elapsed time, truncation mark, and lens.
- [x] 1.3 Write a failing test for a profile summary line that splits into the call table's column count still being skipped.

## 2. Parsing

- [x] 2.1 Parse an unreported numeric call column as zero while keeping the reported-versus-unreported finding count distinction.

## 3. Verification

- [x] 3.1 Run pytest, ruff lint, and mypy in the project virtual environment.
- [x] 3.2 Regenerate README.md and RESULTS.md from existing raw runs and confirm the leaderboard holds the same models with identical metrics.
