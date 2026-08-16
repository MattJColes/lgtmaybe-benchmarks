# lgtmaybe-bench

Repeatable recall, precision, noise, token, truncation, and timing benchmarks for [lgtmaybe](https://github.com/MattJColes/lgtmaybe).

## The two benchmarks

The corpus holds two suites. They measure different things and are not two generations of one benchmark — neither replaces the other.

| suite | question it answers | shape | published runs |
|---|---|---|---:|
| `long-horizon` | Does recall survive as the diff grows? | One language (Python), 5 cases whose diffs scale from roughly 3% to 90% of the 100,000-token input cap. Each defect-bearing case plants the same 8 bugs at the same relative positions, so recall differences come from size alone. One clean case at a large size. | **30** |
| `breadth` | Does it catch every kind of issue in every language? | 32 cases across Python, TypeScript, JavaScript, Rust, Dart, Java, Go, GitHub Actions, and Terraform. 72 planted findings spread over ten review lenses, plus 9 verified-clean changes. Small diffs. | **0** |

Every result published below comes from `long-horizon`. **`breadth` has never been run**, so nothing in this repository reports a breadth score yet.

## Running the benchmark

To reproduce the published leaderboard:

```powershell
uv sync --python 3.12
uv run bench run --provider openrouter --model google/gemini-3.7-flash --suite long-horizon --profile canonical-long-horizon
uv run bench report
```

`canonical-long-horizon` runs the full lgtmaybe preset once per case with a 100,000-token input cap and no output-token ceiling.

To run the breadth suite, which is what `bench run` does by default:

```powershell
uv run bench run --provider openrouter --model google/gemini-3.7-flash --suite breadth --profile canonical-breadth
```

`canonical-breadth` uses the fast preset, three repeats, and a 16,384-token output budget per provider call. That budget bounds runaway generations: a call that hits the cap is retained as truncation evidence, not as a finding.

Each run uses `uv` to download and cache the latest stable `lgtmaybe` release before benchmarking, including in a fresh container. Provider credentials stay in the environment and are never written to raw results. Hosted providers use their usual environment credentials:

```powershell
$env:OPENAI_API_KEY = "..."
uv run bench run --provider openai --model gpt-5.5 --suite long-horizon --profile canonical-long-horizon
```

Benchmark runs can spend provider money and take hours. Start with `--case` and `--repeats 1`, inspect the raw result, then run the full suite.

Named diagnostic profiles — `diagnostic-full-v1`, `diagnostic-4k-v1`, `diagnostic-large-diff-v1` — exist for investigation, not ranking. Any command-line setting override produces a `diagnostic-custom-v1` profile, so a changed configuration cannot silently enter the published ranking.

## Results

Top 10 per suite. Each suite gets its own section — **Long horizon** and **Breadth** — headed by the suite it reports and naming its comparison key. Rows are comparable within a section and never across them: the two suites measure different properties and are scored by different formulas. A suite with no runs renders no section.

<!-- BENCH_RESULTS_START -->
## Long horizon

Complete `long-horizon` runs with profile `canonical-long-horizon` only. Cases grow from roughly 3% to 90% of the canonical input-token cap, each planting eight bugs at the same relative positions; the clean case plants none. Model recall covers the 32 planted findings across the four defect-bearing cases. Scored as the closed-world overall score, which is not comparable with the breadth balanced F1.

### Model summary

| date | provider | model | score | recall | precision | true positives | false positives |
|---|---|---|---:|---:|---:|---:|---:|
| 2026-08-15 | openrouter | google/gemini-3.7-flash | 71.7% | 81.2% | 74.3% | 26 | 9 |
| 2026-08-15 | openrouter | kwaipilot/kat-coder-pro-v2.5 | 63.5% | 68.8% | 71.0% | 22 | 9 |
| 2026-08-15 | openrouter | kwaipilot/kat-coder-air-v2.5 | 52.9% | 62.5% | 62.5% | 20 | 12 |
| 2026-08-15 | openrouter | deepseek/deepseek-v4-pro-0813 | 50.5% | 37.5% | 85.7% | 12 | 2 |
| 2026-08-15 | openrouter | x-ai/grok-4.6 | 47.5% | 84.4% | 55.1% | 27 | 22 |
| 2026-08-15 | openai-compatible | nvidia/Qwen3.6-35B-A3B-NVFP4 | 46.5% | 37.5% | 75.0% | 12 | 4 |
| 2026-08-15 | openrouter | anthropic/claude-sonnet-5 | 46.0% | 56.2% | 58.1% | 18 | 13 |
| 2026-08-15 | openrouter | minimax/minimax-m3 | 43.4% | 53.1% | 56.7% | 17 | 13 |
| 2026-08-15 | openrouter | openai/gpt-5.6-terra | 43.4% | 53.1% | 56.7% | 17 | 13 |
| 2026-08-15 | openrouter | z-ai/glm-4.7-flash | 34.9% | 43.8% | 51.9% | 14 | 13 |
<!-- BENCH_RESULTS_END -->

## Further results

- [RESULTS.md](RESULTS.md) — every stored completed run, with per-case detail.
- [dashboard/index.html](dashboard/index.html) — column sorting and filters by suite, profile, model, version, status, audit state, language, and lens.

Focused and diagnostic runs stay visible in both, but do not enter either published ranking.

Each configuration run writes an append-only JSON document under `results/raw/` before reports are updated, retaining every final model finding including false-positive candidates, stable evidence IDs, token and truncation diagnostics, and the resolved profile. Compatible lgtmaybe versions also write immutable gzip audit traces under `results/audit/`, preserving guessed candidates and later filtering decisions. Human classifications are append-only events under `results/adjudications/`, where later corrections supersede earlier ones without changing raw model output.

`uv run bench report` reconstructs adjudications, recalculates scores, and regenerates `README.md`, `RESULTS.md`, and `dashboard/` deterministically. API endpoints are redacted and provider credentials are never stored.

## How the score is calculated

1. **Setup.** Each case is a small Git repository with a clean base revision and a changed revision. The runner invokes lgtmaybe as an external command against the diff.
2. **Matching.** A finding matches a planted entry only when the file agrees, the line is within three lines, an expected keyword appears in its title or body, and any minimum severity is met. Each planted entry can be caught once.
3. **Closed-world precision.** Every finding that does not match an uncaught planted entry is a false positive, even if it may identify a real uncatalogued issue. `precision = true positives / (true positives + false positives)`.
4. **Score.** `score = 2 × recall / (recall + 1) − 0.02 × false positives`, floored at 0%. That is the harmonic mean of recall against 100% precision, less two percentage points per false positive. This is the `score` column in the Long horizon table.
5. **Aggregation.** Each repeat is scored independently, and every reported metric is the median across repeats with the full minimum–maximum range. Published runs use one repeat, so no range is shown.

Recall in the Long horizon table is measured over the 32 planted findings in the four defect-bearing cases. The fifth case is clean and plants none; findings raised against it count as false positives.

Compare only rows sharing a `suite / profile / lgtmaybe version` key. Provider, model, clean pass, timing, tokens, truncations, and changed settings stay visible separately.

## Contributing cases

Each `corpus/<name>/` case has `base/`, `changed/`, and `case.json`. Expected bugs must be visible in the diff; plausible claims that would require unseen context belong in `forbidden`. Once a raw result names a case, do not edit it — add a versioned replacement such as `<name>-v2`.
