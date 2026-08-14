## Why

The benchmark currently ignores model findings that are far from catalogued lines, so a noisy reviewer can avoid a precision penalty. The public results also hide the number of unmatched findings behind the aggregate score.

## What Changes

- **BREAKING** Count every finding that does not match an uncaught planted finding as a false positive, even when it may describe a real uncatalogued issue in the benchmark repository.
- Recalculate precision and overall score from that strict classification.
- Add a `false positives` count to the generated results table and backfill it from existing raw runs.
- Document the scoring contract for contributors and coding agents.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Strictly classify all unmatched findings as false positives and publish their count.

## Impact

This changes scoring, aggregation, report rendering, generated README and RESULTS content, tests, and contributor guidance. Raw observations and planted corpus data remain unchanged.
