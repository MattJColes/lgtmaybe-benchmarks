# lgtmaybe-bench

Repeatable recall, precision, noise, token, truncation, and timing benchmarks for [lgtmaybe](https://github.com/MattJColes/lgtmaybe).

## The two benchmarks

The corpus holds two suites. They measure different things and are not two generations of one benchmark — neither replaces the other.

| suite | question it answers | shape | published runs |
|---|---|---|---:|
| `long-horizon` | Does recall survive as the diff grows? | One language (Python), 5 cases whose diffs scale from roughly 3% to 90% of the 100,000-token input cap. Each defect-bearing case plants the same 8 bugs at the same relative positions, so recall differences come from size alone. One clean case at a large size. | **34** |
| `breadth` | Does it catch every kind of issue in every language? | 32 cases across Python, TypeScript, JavaScript, Rust, Dart, Java, Go, GitHub Actions, and Terraform. 72 planted findings spread over ten review lenses, plus 9 verified-clean changes. Small diffs. | **30** |

Both suites have published runs below; each gets its own leaderboard section, and their scores are never ranked against each other.

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

`canonical-breadth` uses the fast preset, three repeats, a 16,384-token output budget per provider call, and `low` reasoning effort. Both budgets bound runaway generations: a call that hits either cap is retained as truncation evidence, not as a finding. The reasoning budget is set explicitly so every model reviews under the same one — left to the provider default, a model that spends its context on reasoning can exhaust it before emitting parseable output, which reads as a truncation failure rather than a low score. `low` is the cheapest explicit bound and the only rung this repository has stored evidence for.

Runs published before that budget existed ran with provider-resolved reasoning, and their `profile_schema_version` is 1 where later runs record 2. The profile ID was deliberately kept stable rather than versioned, so those runs still rank in the same breadth leaderboard; until each model is re-run, the breadth ranking mixes the two reasoning budgets. Every run's own `reasoning_effort` is stored in its raw record.

Each run uses `uv` to download and cache the latest stable `lgtmaybe` release before benchmarking, including in a fresh container. Provider credentials stay in the environment and are never written to raw results. Hosted providers use their usual environment credentials:

```powershell
$env:OPENAI_API_KEY = "..."
uv run bench run --provider openai --model gpt-5.5 --suite long-horizon --profile canonical-long-horizon
```

Benchmark runs can spend provider money and take hours. Start with `--case` and `--repeats 1`, inspect the raw result, then run the full suite.

Named diagnostic profiles — `diagnostic-full-v1`, `diagnostic-4k-v1`, `diagnostic-large-diff-v1` — exist for investigation, not ranking. Any command-line setting override produces a `diagnostic-custom-v1` profile, so a changed configuration cannot silently enter the published ranking.

## Results

Top 10 per suite. Each suite gets its own section — **Long horizon** and **Breadth** — headed by the suite it reports. Each section ranks its complete canonical runs across lgtmaybe versions in one table, and the `lgtmaybe` column names the version each run used. Rows are never compared across sections: the two suites measure different properties over different corpora. A suite with no runs renders no section.

<!-- BENCH_RESULTS_START -->
## Breadth — top 10

Complete `breadth` runs with profile `canonical-breadth` only. Cases span seven programming languages plus GitHub Actions and Terraform, planting one finding per language and review lens, so the score measures coverage across kinds of issue rather than diff size. The score is balanced F0.5 scaled by `completeness`, the share of lens calls that returned parseable findings: precision counts only findings that exist, so without that factor a run whose calls mostly failed is scored on the few that survived. It is not comparable with the long-horizon score, which measures a different corpus. Rows rank runs across lgtmaybe versions; the `lgtmaybe` column names the version each run used. Rows are ranked highest to lowest by median score. The first row is the current leader.

| date | provider | model | lgtmaybe | score | completeness | balanced recall | precision | false positives | clean pass | adjudication | audit | settings |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2026-08-17 | openrouter | qwen/qwen3.8-max | lgtmaybe 2.2.0 | 67.0% [64.0–71.2%] provisional | 84.9% | 61.4% [58.6–67.1%] | 84.9% [79.0–91.5%] | 8 [4–13] | 77.8% [66.7–100.0%] | 98.1% [97.9–98.4%] | no | — |
| 2026-08-16 | openrouter | openai/gpt-5.6-sol | lgtmaybe 2.1.4 | 55.8% [55.5–57.0%] provisional | 80.8% | 58.6% [55.7–60.0%] | 72.1% [71.7–75.5%] | 17 [13–17] | 33.3% [33.3–44.4%] | 98.4% [98.1–100.0%] | no | — |
| 2026-08-17 | openrouter | google/gemini-3.7-flash | lgtmaybe 2.2.0 | 55.5% [55.1–55.6%] | 80.8% | 54.3% [52.9–57.1%] | 72.7% [72.4–75.0%] | 15 [13–16] | 44.4% [33.3–44.4%] | 100.0% | no | — |
| 2026-08-16 | openrouter | google/gemini-3.7-flash | lgtmaybe 2.1.4 | 54.8% [54.7–55.5%] provisional | 79.6% | 48.6% [47.1–52.9%] | 77.8% [77.8–78.0%] | 10 [10–11] | 55.6% [44.4–55.6%] | 100.0% [98.0–100.0%] | no | — |
| 2026-08-18 | openrouter | z-ai/glm-5.2 | lgtmaybe 2.2.0 | 53.2% [49.8–55.2%] provisional | 75.1% | 72.9% [72.9–75.7%] | 69.6% [65.4–71.6%] | 24 [21–28] | 11.1% [11.1–22.2%] | 98.8% [98.7–98.8%] | no | — |
| 2026-08-17 | openrouter | openai/gpt-5.4-nano | lgtmaybe 2.2.0 | 51.6% [50.5–52.8%] provisional | 80.2% | 52.9% [48.6–52.9%] | 68.4% [66.1–72.0%] | 18 [14–20] | 22.2% [22.2–44.4%] | 98.3% [96.2–98.3%] | no | — |
| 2026-08-18 | openrouter | minimax/minimax-m3 | lgtmaybe 2.2.0 | 51.6% [44.9–54.1%] provisional | 78.6% | 58.6% [54.3–60.0%] | 67.7% [63.9–71.0%] | 20 [18–22] | 33.3% [22.2–44.4%] | 98.4% [96.9–98.4%] | no | — |
| 2026-08-16 | openrouter | x-ai/grok-4.6 | lgtmaybe 2.1.4 | 51.5% [49.0–55.8%] provisional | 80.8% | 57.1% [52.9–62.9%] | 65.6% [62.9–70.8%] | 22 [19–23] | 22.2% [22.2–33.3%] | 98.5% [98.4–98.5%] | no | — |
| 2026-08-16 | openrouter | openai/gpt-5.6-luna | lgtmaybe 2.1.4 | 51.4% [43.0–52.3%] provisional | 77.5% | 58.6% [47.1–62.9%] | 66.2% [58.3–68.7%] | 22 [21–25] | 22.2% [11.1–22.2%] | 100.0% [98.4–100.0%] | no | — |
| 2026-08-16 | openrouter | openai/gpt-5.6-terra | lgtmaybe 2.1.4 | 50.9% [48.9–56.8%] provisional | 80.8% | 48.6% [45.7–60.0%] | 67.9% [66.7–73.3%] | 17 [16–17] | 33.3% [22.2–33.3%] | 98.4% [98.1–100.0%] | no | — |

## Long horizon — top 10

Complete `long-horizon` runs with profile `canonical-long-horizon` only. Cases grow from roughly 3% to 90% of the canonical input-token cap, each planting eight bugs at the same relative positions; the clean case plants none. Model recall covers the 32 planted findings across the four defect-bearing cases. Scored as the closed-world F0.5 overall score scaled by `completeness` (the share of lens calls that returned parseable findings), which is not comparable with the breadth balanced F0.5. Rows rank runs across lgtmaybe versions; the `lgtmaybe` column names the version each run used.

### Model summary

| date | provider | model | lgtmaybe | score | completeness | recall | precision | true positives | false positives |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-08-18 | openrouter | qwen/qwen3.8-max | lgtmaybe 2.2.0 | 70.6% | 91.8% | 75.0% | 77.4% | 24 | 7 |
| 2026-08-15 | openrouter | google/gemini-3.7-flash | lgtmaybe 2.1.4 | 64.8% | 85.7% | 81.2% | 74.3% | 26 | 9 |
| 2026-08-15 | openrouter | kwaipilot/kat-coder-pro-v2.5 | lgtmaybe 2.1.4 | 59.7% | 84.6% | 68.8% | 71.0% | 22 | 9 |
| 2026-08-15 | openrouter | anthropic/claude-sonnet-5 | lgtmaybe 2.1.4 | 54.1% | 93.8% | 56.2% | 58.1% | 18 | 13 |
| 2026-08-15 | openrouter | x-ai/grok-4.6 | lgtmaybe 2.1.4 | 53.3% | 90.0% | 84.4% | 55.1% | 27 | 22 |
| 2026-08-15 | openrouter | deepseek/deepseek-v4-pro-0813 | lgtmaybe 2.1.4 | 51.1% | 75.0% | 37.5% | 85.7% | 12 | 2 |
| 2026-08-15 | openrouter | kwaipilot/kat-coder-air-v2.5 | lgtmaybe 2.1.4 | 50.5% | 80.8% | 62.5% | 62.5% | 20 | 12 |
| 2026-08-15 | openrouter | openai/gpt-5.6-terra | lgtmaybe 2.1.4 | 50.3% | 90.0% | 53.1% | 56.7% | 17 | 13 |
| 2026-08-15 | openrouter | google/gemini-3.1-pro-preview | lgtmaybe 2.1.4 | 45.7% | 90.0% | 81.2% | 46.4% | 26 | 30 |
| 2026-08-15 | openrouter | z-ai/glm-5.2 | lgtmaybe 2.1.4 | 44.6% | 87.0% | 78.1% | 47.2% | 25 | 28 |
<!-- BENCH_RESULTS_END -->

## Further results

- [RESULTS.md](RESULTS.md) — every stored completed run, with per-case detail.
- [dashboard/index.html](dashboard/index.html) — column sorting and filters by suite, profile, model, version, status, audit state, language, and lens.

Focused and diagnostic runs stay visible in both, but do not enter either published ranking.

Each configuration run writes an append-only JSON document under `results/raw/` before reports are updated, retaining every final model finding including false-positive candidates, stable evidence IDs, token and truncation diagnostics, and the resolved profile. Its `status` is `in_progress` while the run is unfinished, `complete` once every repeat and case has been observed, and `ineligible` when a full-corpus canonical run was abandoned at its first failed observation. Because such a run can no longer be scored, it stops rather than paying for the remaining cases, and records the repeat, case, exit code, and failure classification that stopped it. Focused and diagnostic runs keep collecting failures instead, so a failure can still be investigated in full. Compatible lgtmaybe versions also write immutable gzip audit traces under `results/audit/`, preserving guessed candidates and later filtering decisions. Human classifications are append-only events under `results/adjudications/`, where later corrections supersede earlier ones without changing raw model output.

`uv run bench report` reconstructs adjudications, recalculates scores, and regenerates `README.md`, `RESULTS.md`, and `dashboard/` deterministically. API endpoints are redacted and provider credentials are never stored.

## How the score is calculated

1. **Setup.** Each case is a small Git repository with a clean base revision and a changed revision. The runner invokes lgtmaybe as an external command against the diff.
2. **Matching.** A finding matches a planted entry only when the file agrees, the line is within three lines, an expected keyword appears in its title or body, and any minimum severity is met. Each planted entry can be caught once.
3. **Closed-world precision.** Every finding that does not match an uncaught planted entry is a false positive, even if it may identify a real uncatalogued issue. `precision = true positives / (true positives + false positives)`.
4. **Score.** `score = 1.25 × precision × recall / (0.25 × precision + recall)`, and 0% when that denominator is zero. That is the F0.5 measure: a harmonic-family mean of precision and recall that weights precision twice as heavily, so noise costs more than misses without ever erasing nonzero recall. Both suites share this formula — the Long horizon `score` column applies it to planted-finding recall and closed-world precision, and the Breadth `balanced F0.5` column applies it to balanced recall and pooled precision. The suites are still never ranked against each other.
5. **Aggregation.** Each repeat is scored independently, and every reported metric is the median across repeats with the full minimum–maximum range. Published runs use one repeat, so no range is shown.

Recall in the Long horizon table is measured over the 32 planted findings in the four defect-bearing cases. The fifth case is clean and plants none; findings raised against it count as false positives. Balanced recall in the Breadth table is the arithmetic mean of recall across the suite's 70 primary language/lens cells, so every language and lens counts equally; published runs use three repeats, and each metric is the median with its full range. A breadth run with unresolved findings is marked provisional until adjudicated.

Compare only rows within one suite's table; the `lgtmaybe` column identifies the version behind each row, and the dashboard can filter to a single version for strict like-for-like comparisons. Provider, model, clean pass, timing, tokens, truncations, and changed settings stay visible separately.

## Contributing cases

Each `corpus/<name>/` case has `base/`, `changed/`, and `case.json`. Expected bugs must be visible in the diff; plausible claims that would require unseen context belong in `forbidden`. Once a raw result names a case, do not edit it — add a versioned replacement such as `<name>-v2`.
