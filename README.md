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
Full-corpus runs only. Complete configuration and diagnostic evidence remain in `results/raw/`.

## Per-lens recall

| date | lgtmaybe version | provider | model | score | security | correctness | performance | complexity | tests | documentation | deprecation | intent | ponytail | spec | settings |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2026-08-13T13:38:59Z | lgtmaybe 1.14.1 | ollama | qwen2.5-coder:3b | 21.4% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | 50.0% | 0.0% | 0.0% | max tokens 512; repeats 1 |
<!-- BENCH_RESULTS_END -->

See [RESULTS.md](RESULTS.md) for the full historical results. Focused `--case` runs remain in raw data and do not appear in the public table.

## Metrics

- Recall is the share of planted findings caught. Precision discounts forbidden traps and unexpected findings near catalogued lines; distant findings are not adjudicated.
- Score is the harmonic mean of recall and precision. Clean means no forbidden trap fired.
- The results table shows full-corpus score and per-lens recall. Repeated scores are shown as median and min–max.
- Settings lists only values changed from the benchmark defaults. Timing, tokens, precision, clean status, truncation, and failures remain in raw data.

## Raw data and recovery

Each configuration run writes an append-only JSON document under `results/raw/` before updating Markdown. `uv run bench report` rescans those files and regenerates `RESULTS.md` and the marked README section byte-identically. Raw data retains focused runs and complete diagnostic evidence. It contains the API base but never credentials.

## Contributing cases

Each `corpus/<name>/` case has `base/`, `changed/`, and `case.json`. Expected bugs must be visible in the diff; plausible claims requiring unseen context belong in `forbidden`. Once a raw result names a case, do not edit it—add a versioned replacement such as `<name>-v2`.

Benchmark runs can spend provider money and take hours. Start with `--case` and `--repeats 1`, inspect the raw result, then run the full corpus.
