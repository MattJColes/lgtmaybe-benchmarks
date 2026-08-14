## Why

A benchmark configuration can currently resolve `lgtmaybe@latest` to different releases between observations while recording only the first version. Mixed-version raw results are internally incomparable and can be mistaken for valid canonical evidence.

## What Changes

- Pin the latest lgtmaybe release to one concrete version before a benchmark starts.
- Use that pinned release for every observation in the configuration.
- Fail on a version mismatch while retaining completed observations in the in-progress checkpoint.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: Require one consistent lgtmaybe release for every observation in a configuration run.

## Impact

The benchmark command resolver, execution runner, and behavioural runner tests change. No dependency or public CLI change is required.
