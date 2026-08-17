## 1. Behavioral coverage

- [x] 1.1 Add a failing test proving a successful review consumes structured profile JSON when the human profile is on stderr.
- [x] 1.2 Add failing tests for missing, malformed, and unsupported structured profile data failing loudly.
- [x] 1.3 Retain a passing behavioral test for the older stdout-table compatibility path.

## 2. Profile capture

- [x] 2.1 Detect `--profile-json` support and pass an observation-local output path without importing lgtmaybe.
- [x] 2.2 Parse schema-versioned structured calls into `ProfileCall`, retain the exact source, and preserve finding-count and truncation semantics.
- [x] 2.3 Reject successful profiled reviews that yield no usable structured or compatibility telemetry.

## 3. Verification

- [x] 3.1 Run focused tests, the full pytest suite, Ruff, mypy, and strict OpenSpec validation.
- [x] 3.2 Reproduce one live lgtmaybe 2.2.0 observation and confirm non-zero call/token telemetry before restarting canonical runs.
