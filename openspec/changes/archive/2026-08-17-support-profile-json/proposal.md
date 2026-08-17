## Why

`lgtmaybe 2.2.0` sends profiles for machine-readable findings formats to stderr and exposes `--profile-json` for structured consumption, while the benchmark still parses a human table appended to stdout. Successful runs therefore silently record zero calls, tokens, reasoning, and truncations, making their evidence incomplete while provider spend continues.

## What Changes

- Request a per-observation structured profile JSON file when the installed lgtmaybe supports it.
- Parse and validate structured call telemetry at the subprocess boundary.
- Retain the stdout table parser as a compatibility fallback for older lgtmaybe releases.
- Fail loudly when profiling was requested but a successful review yields no usable profile telemetry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: Define version-compatible structured profile capture, legacy fallback, and missing-telemetry failure behavior.

## Impact

The change is limited to `src/lgtmaybe_bench/runner.py`, its behavioral tests, and benchmark-execution specification artifacts. It adds no runtime dependency and does not change corpus, scoring, or published raw results.
