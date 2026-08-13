# lgtmaybe-bench

Repeatable recall, precision, noise, token, truncation, and timing benchmarks for [lgtmaybe](https://github.com/MattJColes/lgtmaybe).

## Quick start

```powershell
uv sync
uv run bench run --provider ollama --model qwen3.5:4b --repeats 1
uv run bench report
```

`lgtmaybe` must already be available on `PATH`. Provider credentials stay in the environment and are never written to raw results.

Hosted providers use their usual environment credentials:

```powershell
$env:OPENAI_API_KEY = "..."
uv run bench run --provider openai --model gpt-5.5 --reasoning-effort medium
```

The default is three repeats. Use repeatable `--case` flags for a focused run. The `spec-batched-export` case contains a deliberately large multi-file diff; `--max-input-tokens 500` forces it through the batching path on small-context models.

## Results

<!-- BENCH_RESULTS_START -->
> Local and hosted wall times are not comparable; provider concurrency differs. Wall-ex-trunc is derived by subtracting truncated call durations.

## Leaderboard

| date | lgtmaybe | provider | model | cases | effort | preset | max_tok | max_in | api | conc | timeout | repeats | score | recall | precision | clean | trunc | failures | wall (med) | wall-ex-trunc | in_tok | out_tok | reason_tok |
|---|---|---|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-13T13:38:59Z | lgtmaybe 1.14.1 | ollama | qwen2.5-coder:3b | deep-nesting, deprecated-imp-module, deprecated-utcnow, duplicate-branches, intent-out-of-scope-delete, intent-promised-pagination, missing-boundary-test, n-plus-one-orders, nullable-owner, off-by-one-page, path-traversal-download, ponytail-custom-chunks, ponytail-single-factory, quadratic-membership, spec-batched-export, spec-timeout-undelivered, sql-injection-basic, stale-readme-default, undocumented-public-api, weak-exception-test | default (thinking off) | full | 512 | - | - | 1 | 7200 | 1 | 21.4% | 14.3% | 42.9% | yes | 2.00 | 0.00 | 1198.88 | 1160.41 | 548864.00 | 24471.00 | 0.00 |

## Per-lens recall

| date | provider | model | security | correctness | performance | complexity | tests | documentation | deprecation | intent | ponytail | spec |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-13T13:38:59Z | ollama | qwen2.5-coder:3b | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | 50.0% | 0.0% | 0.0% |
<!-- BENCH_RESULTS_END -->

See [RESULTS.md](RESULTS.md) for the generated leaderboard and per-lens detail.

## Metrics

- Recall is the share of planted findings caught. Precision discounts forbidden traps and unexpected findings near catalogued lines; distant findings are not adjudicated.
- Score is the harmonic mean of recall and precision. Clean means no forbidden trap fired.
- Every repeated metric is shown as median and min–max. Truncations remain visible and wall-ex-trunc subtracts their recorded call time.
- Local and hosted wall times are not comparable because their actual concurrency differs.

## Raw data and recovery

Each configuration run writes an append-only JSON document under `results/raw/` before updating Markdown. `uv run bench report` rescans those files and regenerates `RESULTS.md` and the marked README section byte-identically. Raw data contains the API base but never credentials.

## Contributing cases

Each `corpus/<name>/` case has `base/`, `changed/`, and `case.json`. Expected bugs must be visible in the diff; plausible claims requiring unseen context belong in `forbidden`. Once a raw result names a case, do not edit it—add a versioned replacement such as `<name>-v2`.

Benchmark runs can spend provider money and take hours. Start with `--case` and `--repeats 1`, inspect the raw result, then run the full corpus.
