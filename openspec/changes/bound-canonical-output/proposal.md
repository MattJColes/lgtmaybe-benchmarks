## Why

`canonical-v1` leaves `max_tokens` provider-resolved. Against OpenRouter's qwen3.6-27b that resolves to the 65,536-token provider ceiling, and one observation burned 3,980 s on four `ProviderTruncated` calls of 65,536 output tokens each (issue #25). A fresh 32-case, three-repeat matrix can spend hours on runaway generations, so wall time and cost measure generation excess rather than review quality. `diagnostic-4k-v1` cannot help because diagnostic runs are excluded from canonical ranking by design.

## What Changes

- Add `canonical-v2`: the `canonical-v1` behaviour (fast preset, three repeats, 100k input-token cap) plus an explicit bounded output budget of `max_tokens 16384`, so every provider call is capped an order of magnitude below the 65k ceiling while leaving ample room for full review output.
- `canonical-v1` remains registered and unchanged; published raw results that reference it stay comparable within their own generation.
- Make `canonical-v2` the default profile for `bench run`, so fresh canonical matrices use the bounded policy without extra flags.
- Canonical leaderboard and dashboard eligibility accept both canonical generations; the existing newest-comparison-key partition keeps generations from ever being ranked against each other, and the leaderboard flips to `canonical-v2` once a complete `canonical-v2` matrix exists.
- Provider truncations remain raw evidence: calls at or beyond the 16,384-token budget keep the existing `truncated` marking, truncation-lens, and `wall_excluding_truncation_seconds` accounting, and are never reclassified as findings.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: gains the `canonical-v2` profile with a bounded canonical output budget; the default profile becomes `canonical-v2`; `canonical-v1` is retained as a versioned predecessor.
- `benchmark-scoring-reporting`: canonical ranking eligibility widens from the single `canonical-v1` ID to canonical profile generations, still partitioned so only one generation is ranked at a time.

## Impact

- Profile registration, CLI default, and reporting eligibility filters in `src/lgtmaybe_bench/` (`runner.py`, `cli.py`, `reporting.py`).
- Hand-authored README profile documentation updates to name `canonical-v2` as the default; generated tables change only if a `canonical-v2` run lands.
- No new runtime dependencies; standard library only.
- `canonical-v1` and `canonical-v2` results are not comparable, which is the point: the bounded output budget is a new comparison contract. The first complete `canonical-v2` matrix establishes the new baseline.
