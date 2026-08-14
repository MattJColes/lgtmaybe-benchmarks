## Why

Incomplete checkpoints are diagnostic evidence, not comparable benchmark results. Publishing them beside completed runs adds noise and can make an interrupted model look like a scored result.

## What Changes

- Omit incomplete runs from generated README and RESULTS Markdown.
- Keep incomplete checkpoint JSON unchanged under `results/raw/` for diagnosis or resumption.
- Render the existing empty-state message when no publishable completed runs exist.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Generated reports publish only valid completed full-corpus runs.

## Impact

This changes the report renderer, its behavioural tests, and generated README and RESULTS content. Raw result storage and benchmark execution are unchanged.
