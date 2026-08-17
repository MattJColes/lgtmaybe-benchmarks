## Why

`canonical-breadth` pins `max_tokens` to 16,384 but leaves `reasoning_effort` at `None`, so the output budget is comparable across models and the reasoning budget is whatever each provider defaults to. The benchmark therefore measures review quality under a budget it never set.

The consequence is not only comparability. A model whose provider default spends the context on reasoning can exhaust it before emitting parseable output, which surfaces as a truncation failure rather than a low score. Issue #89 lost three canonical campaign runs that way: `z-ai/glm-4.7-flash` at 21 of 96 observations, `poolside/laguna-s-2.1` at 48, and `nvidia/nemotron-3.5-lightning` at 59.

Truncation is not confined to the runs that failed. Across the 1,632 observations in the 17 stored full-corpus canonical breadth runs, 287 contain at least one `ProviderTruncated` call — 84 for `z-ai/glm-4.7`, 65 for `nvidia/Gemma-4-26B-A4B-NVFP4`, 63 for `kwaipilot/kat-coder-air-v2.5`. Those runs scored, because a truncated call that still exits zero stays scoreable, but their recall was measured under an unset budget.

## What Changes

- Set `reasoning_effort` to `low` on `canonical-breadth`, so every canonical breadth run passes an explicit `--reasoning-effort` to lgtmaybe instead of accepting a provider default.
- Bump the profile's `schema_version` to 2, so a raw record states which generation of the profile definition it ran under.
- Leave the profile ID unchanged, so no leaderboard reset and no re-runs are required.
- Leave `canonical-long-horizon` provider-resolved; the issue is scoped to breadth and the long-horizon budget is a separate question.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: the canonical breadth profile sets an explicit reasoning budget rather than accepting a provider default.
- `benchmark-scoring-reporting`: a diagnostic run's settings summary is derived from its own recorded profile rather than the live profile registry.

## Impact

- `src/lgtmaybe_bench/runner.py` gains two `_profile()` parameters and applies them to `canonical-breadth`.
- `src/lgtmaybe_bench/reporting.py` summarises a diagnostic run's settings against its own recorded resolved profile and overrides. Without this, changing the canonical reasoning budget silently rewrites a published row: the one stored `diagnostic-custom-v1` breadth run lost its `effort low` label, because the summary compared it against today's base profile instead of the profile it actually ran under.
- Hand-authored README profile documentation records the budget and the reason for it.
- No generated table changes until a fresh canonical breadth run lands; regenerating the reports leaves them byte-identical.
- **Accepted trade-off, chosen deliberately by the maintainer over a new profile generation:** the leaderboard partitions by `suite / profile / lgtmaybe version`, so the 17 published runs (provider-resolved reasoning) and future runs (`low`) rank against each other under one comparison key until those models are re-run. The stored `reasoning_effort` and `profile_schema_version` on each raw record keep the two generations distinguishable in evidence even though ranking does not separate them.
- No new runtime dependencies and no corpus change.
