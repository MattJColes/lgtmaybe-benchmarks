## Why

The published Fable benchmark records a mutable OpenRouter latest-version alias, but the resolved model was exactly `anthropic/claude-fable-5`. The repository should use that exact identity consistently without changing any measured evidence or scores.

## What Changes

- Correct the Fable raw run's model identity, stable IDs, and raw filename from the alias to `anthropic/claude-fable-5`.
- Regenerate README, detailed results, and dashboard artifacts from the corrected raw source.
- Correct the historical OpenSpec task that names the benchmarked model.
- Preserve every observation, finding, metric, token count, timing, and score.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Historical model-identity corrections remain referentially consistent across raw evidence and every generated report.

## Impact

- One raw result filename and its model/run/finding/observation identifiers.
- Generated `README.md`, `RESULTS.md`, and dashboard artifacts.
- One historical OpenSpec task reference and behavioural reporting tests.
- No scoring, corpus, provider, dependency, or benchmark-execution changes.
