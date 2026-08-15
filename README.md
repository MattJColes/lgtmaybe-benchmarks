# lgtmaybe-bench

Repeatable recall, precision, noise, token, truncation, and timing benchmarks for [lgtmaybe](https://github.com/MattJColes/lgtmaybe).

## Quick start

```powershell
uv sync --python 3.12
uv run bench run --provider ollama --model qwen3.5:4b
uv run bench report
```

Each run uses `uv` to download and cache the latest stable `lgtmaybe` release before benchmarking, including in a fresh container. Provider credentials stay in the environment and are never written to raw results.

Hosted providers use their usual environment credentials:

```powershell
$env:OPENAI_API_KEY = "..."
uv run bench run --provider openai --model gpt-5.5
```

The default `v2 / canonical-v2` comparison uses three repeats, the fast lgtmaybe preset, a 100,000-token input ceiling, and a bounded 16,384-token output budget per provider call, with the same settings for Python, TypeScript, JavaScript, Rust, Dart, Java, and Go. It also covers GitHub Actions and Terraform. Keep language settings identical: per-language defaults would make the overall result a comparison of configurations rather than models. The output budget bounds runaway generations (issue #25): a call that hits the cap is retained as truncation evidence, not a finding. Results from the earlier provider-resolved `canonical-v1` generation remain stored and comparable within their own generation; the two generations are never ranked against each other.

Use a named diagnostic profile for investigation, not ranking:

```powershell
uv run bench run --provider ollama --model qwen3.5:4b --profile diagnostic-full-v1
uv run bench run --provider ollama --model qwen3.5:4b --profile diagnostic-4k-v1
uv run bench run --provider ollama --model qwen3.5:4b --profile diagnostic-large-diff-v1
```

Repeatable `--case` flags create a focused run. Any command-line setting override creates a `diagnostic-custom-v1` profile so it cannot silently enter the canonical ranking.

## How the benchmark works

Canonical v2 contains 32 paired-revision cases with 72 planted findings and 9 verified-clean changes.

| case type | cases | planted findings | verified clean | probes |
|---|---:|---:|---:|---|
| Runtime safety across seven languages | 7 | 28 | 0 | Security, correctness, tests, and spec alignment |
| Efficiency and design across seven languages | 7 | 21 | 0 | Performance, complexity, and unnecessary indirection |
| Contract evolution across seven languages | 7 | 21 | 0 | Documentation, deprecation, and change intent |
| Clean context across seven languages | 7 | 0 | 7 | Plausible-looking code that should not produce a finding |
| GitHub Actions security and clean context | 2 | 1 | 1 | Cross-cutting workflow security and false positives |
| Terraform security and clean context | 2 | 1 | 1 | Cross-cutting infrastructure security and false positives |
| **Total** | **32** | **72** | **9** | Ten review lenses plus cross-cutting security evidence |

1. Each case is a small Git repository with a clean base revision and a changed revision. The runner invokes lgtmaybe as an external command against the diff, three times per canonical configuration.
2. A final finding matches a planted or forbidden entry only when the file agrees, the line is within three lines, an expected keyword appears in its title or body, and any minimum severity is met. Each planted entry can be caught once; clean-case findings, nearby mismatches, forbidden claims, and duplicates are false positives, while findings outside those rules remain unadjudicated.
3. Human decisions are stored as append-only adjudication events. A result stays provisional while any finding is unadjudicated, and report regeneration applies the latest decisions without changing the raw model output.
4. Each repeat is scored independently, then every reported metric is aggregated as its median with the full minimum–maximum range.

Balanced recall is the arithmetic mean of recall in 70 core cells: seven programming languages × ten review lenses, with one planted finding per cell. The two extra GitHub Actions and Terraform security findings remain in the detailed evidence and pooled precision, but do not give security extra weight in balanced recall. Pooled precision is `true positives / (true positives + false positives)` across classified final findings and is defined as 100% when no classified findings exist; false positives are reported by class. Balanced F1 is `2 × balanced recall × precision / (balanced recall + precision)`.

Legacy-v1 results use a separate historical formula: harmonic recall against perfect precision, followed by a fixed two-percentage-point deduction for each false positive. They are not directly comparable with v2 balanced F1.

## Results

<!-- BENCH_RESULTS_START -->
## Context scaling

Complete `context-v1` runs with profile `context-canonical-v1` only. Cases grow from roughly 3% to 90% of the canonical input-token cap, each planting eight bugs at the same relative positions; the clean case plants none. Model recall covers the 32 planted findings across the four defect-bearing cases.

### Model summary

| date | provider | model | score | recall | precision | true positives | false positives |
|---|---|---|---:|---:|---:|---:|---:|
| 2026-08-15 | openrouter | anthropic/claude-sonnet-5 | 46.0% | 56.2% | 58.1% | 18 | 13 |
| 2026-08-15 | openrouter | openai/gpt-5.6-terra | 43.4% | 53.1% | 56.7% | 17 | 13 |
| 2026-08-15 | openrouter | ~anthropic/claude-fable-latest | 29.8% | 46.9% | 46.9% | 15 | 17 |
| 2026-08-15 | openrouter | openai/gpt-5.6-luna | 19.7% | 78.1% | 42.4% | 25 | 34 |
| 2026-08-15 | openrouter | anthropic/claude-haiku-4.5 | 15.1% | 9.4% | 75.0% | 3 | 1 |
| 2026-08-15 | openrouter | openai/gpt-5.6-sol | 0.0% | 59.4% | 32.2% | 19 | 40 |
| 2026-08-15 | openrouter | anthropic/claude-opus-5 | 0.0% | 0.0% | 100.0% | 0 | 0 |
<!-- BENCH_RESULTS_END -->

See [RESULTS.md](RESULTS.md) for every stored completed run and [dashboard/index.html](dashboard/index.html) for column sorting and filters by suite, profile, model, version, status, audit state, language, and lens. Focused and diagnostic runs remain visible there but do not enter the canonical README ranking.

## Metrics

- V2 balanced recall gives equal weight to each of the 70 language/lens cells, including tests and spec alignment for every programming language. It is not inflated by languages or lenses with more planted findings.
- V2 precision pools true and false positives across the suite. False positives are split into forbidden claims, clean-case findings, unexpected nearby findings, duplicates, and manually adjudicated findings.
- V2 balanced F1 is the harmonic mean of balanced recall and pooled precision. A score is marked provisional while any otherwise-unclassified finding still needs adjudication.
- Legacy-v1 tables retain their published score: harmonic recall with a fixed two-point deduction per false positive. Three-repeat results show the median and min–max range.
- Compare only rows with the same `suite / profile / lgtmaybe version` key. Provider, model, clean pass, timing, tokens, truncations, and changed settings remain visible separately.

## Raw data and recovery

Each configuration run writes an append-only JSON document under `results/raw/` before updating reports. It retains every final model finding, including false-positive candidates, stable evidence IDs, token and truncation diagnostics, and resolved profile settings. Compatible lgtmaybe versions also produce immutable gzip audit traces under `results/audit/`, preserving guessed candidates and later filtering decisions for lens refinement.

Human classifications are append-only events under `results/adjudications/`; later corrections supersede earlier events without changing raw model output. `uv run bench report` reconstructs current adjudications, recalculates scores, and regenerates `README.md`, `RESULTS.md`, and `dashboard/` deterministically. API endpoints are redacted and provider credentials are never stored.

## Contributing cases

Each `corpus/<name>/` case has `base/`, `changed/`, and `case.json`. Expected bugs must be visible in the diff; plausible claims requiring unseen context belong in `forbidden`. Once a raw result names a case, do not edit it—add a versioned replacement such as `<name>-v2`.

Benchmark runs can spend provider money and take hours. Start with `--case` and `--repeats 1`, inspect the raw result, then run the full corpus.
