# lgtmaybe-bench

Repeatable benchmarks for [lgtmaybe](https://github.com/MattJColes/lgtmaybe), measuring findings, false positives, token use, truncation, and run time.

## The two benchmarks

The two suites measure different properties. Compare models within a suite, not across suites.

| suite | question | corpus |
|---|---|---|
| `long-horizon-validated` | Does recall hold up as the diff grows? | Five Python cases with increasing diff size. Four plant the same eight bugs; the fifth is clean. |
| `breadth-validated` | Does the review catch different kinds of issues across languages? | 32 runnable changes across seven programming languages, GitHub Actions, and Terraform. They include 70 independent language/lens targets and nine clean changes. |

Published `long-horizon` and `breadth` runs remain visible as historical results. Their cases have known validation problems, so compare new models within the validated suites instead.

Each suite has its own leaderboard below.

## Running the benchmark

Install dependencies and run one canonical long-horizon benchmark:

```sh
uv sync --python 3.12
uv run bench run --provider openrouter --model google/gemini-3.8-flash --suite long-horizon-validated --profile canonical-long-horizon
uv run bench report
```

`canonical-long-horizon` uses lgtmaybe's full preset, one repeat per case, a 100,000-token input cap, and no output-token cap. A new run uses the latest stable lgtmaybe release, so it may differ from historical rows made with older versions.

To run the breadth suite (the default for `bench run`):

```sh
uv run bench run --provider openrouter --model google/gemini-3.8-flash --suite breadth-validated --profile canonical-breadth
```

`canonical-breadth` uses the fast preset, three repeats, a 16,384-token output cap per provider call, and explicit `low` reasoning effort. The output cap and 100,000-token input cap limit oversized calls. A call that hits a cap is recorded as truncation evidence. Setting reasoning effort explicitly avoids provider defaults that can consume the context before the model returns parseable findings.

Historical breadth runs used both provider-resolved reasoning (`profile_schema_version` 1) and explicit `low` reasoning (`profile_schema_version` 2). Their raw results retain the actual setting. They do not share a leaderboard with `breadth-validated`.

Each run uses `uv` to fetch and cache the latest stable lgtmaybe release. Set the provider's usual credentials in your environment; they are not written to raw results. For example, in PowerShell:

```powershell
$env:OPENAI_API_KEY = "..."
uv run bench run --provider openai --model gpt-5.5 --suite long-horizon-validated --profile canonical-long-horizon
```

Full runs can cost provider money and take hours. To try one case first, add `--case <case-name> --repeats 1`, then inspect its raw result before running the full suite.

The `diagnostic-full-v1`, `diagnostic-4k-v1`, and `diagnostic-large-diff-v1` profiles are for investigation. A setting override that changes a named profile is recorded as `diagnostic-custom-v1`. Diagnostic runs do not enter the leaderboards.

To compare review options, run a baseline and a variant with the same lgtmaybe version, model, and cases, changing one of `--preset`, `--reflect`, `--recursive`, `--static-analysis`, `--mid-review-retrieval`, or `--triage-model` at a time. `--suite review-options` provides small cross-file retrieval and triage probes. Then use `uv run bench compare --baseline results/raw/<baseline>.json --variant results/raw/<variant>.json`. The comparison checks pairing and reports recall, false positives, completeness, tokens, time, and cost when the raw runs contain it. These diagnostics never enter either leaderboard.

## Results

Each table shows the ten highest-scoring complete canonical runs for its suite, across lgtmaybe versions. The `lgtmaybe` column identifies the version used. Scores from different suites are not comparable.

<!-- BENCH_RESULTS_START -->
## Validated breadth

No complete `breadth-validated` canonical runs yet. Historical scores below were recalculated from unchanged raw results.

## Historical breadth — top 10

Complete `breadth` runs using `canonical-breadth`, ranked by median score across lgtmaybe versions. Where measured, the score is balanced F0.5 multiplied by `completeness`, the share of review calls that returned parseable findings. Successful reflection and other non-finding stages are excluded. Historical scores were recalculated from unchanged raw evidence. Scores are not comparable with long horizon. Historical breadth cases contain unvalidated targets; their ranking is archival.

| date | provider | model | lgtmaybe | score | completeness | balanced recall | precision | false positives | clean pass | adjudication | audit | settings |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2026-08-17 | openrouter | qwen/qwen3.8-max | lgtmaybe 2.2.0 | 78.9% [76.3–82.2%] provisional | 100.0% | 61.4% [58.6–67.1%] | 84.9% [79.0–91.5%] | 8 [4–13] | 77.8% [66.7–100.0%] | 98.1% [97.9–98.4%] | no | — |
| 2026-09-24 | openrouter | google/gemini-3.8-flash | lgtmaybe 2.8.5 | 75.4% [74.4–77.4%] | 100.0% | 62.9% | 79.3% [78.0–82.1%] | 12 [10–13] | 22.2% [22.2–44.4%] | 100.0% | no | — |
| 2026-09-24 | openrouter | x-ai/grok-4.7 | lgtmaybe 2.8.5 | 68.9% [66.8–69.9%] provisional | 100.0% | 62.9% [60.0–64.3%] | 70.1% [68.8–71.9%] | 20 [18–20] | 11.1% [11.1–22.2%] | 98.5% [98.5–98.5%] | no | — |
| 2026-08-16 | openrouter | openai/gpt-5.6-sol | lgtmaybe 2.1.4 | 68.8% [68.6–70.5%] provisional | 100.0% | 58.6% [55.7–60.0%] | 72.1% [71.7–75.5%] | 17 [13–17] | 33.3% [33.3–44.4%] | 98.4% [98.1–100.0%] | no | — |
| 2026-08-17 | openrouter | google/gemini-3.7-flash | lgtmaybe 2.2.0 | 68.7% [68.1–68.7%] | 100.0% | 54.3% [52.9–57.1%] | 72.7% [72.4–75.0%] | 15 [13–16] | 44.4% [33.3–44.4%] | 100.0% | no | — |
| 2026-09-24 | openrouter | z-ai/glm-5.3-flash | lgtmaybe 2.8.5 | 68.2% [62.8–68.4%] provisional | 98.6% | 62.9% [58.6–67.1%] | 70.0% [65.2–70.3%] | 21 [19–23] | 11.1% [0.0–11.1%] | 98.5% [98.5–98.6%] | no | — |
| 2026-08-16 | openrouter | google/gemini-3.7-flash | lgtmaybe 2.1.4 | 67.9% [67.8–68.1%] provisional | 97.8% | 48.6% [47.1–52.9%] | 77.8% [77.8–78.0%] | 10 [10–11] | 55.6% [44.4–55.6%] | 100.0% [98.0–100.0%] | no | — |
| 2026-08-18 | openrouter | z-ai/glm-5.2 | lgtmaybe 2.2.0 | 65.6% [61.1–68.2%] provisional | 92.7% | 72.9% [72.9–75.7%] | 69.6% [65.4–71.6%] | 24 [21–28] | 11.1% [11.1–22.2%] | 98.8% [98.7–98.8%] | no | — |
| 2026-09-24 | openrouter | moonshotai/kimi-k3 | lgtmaybe 2.8.5 | 64.3% [62.3–65.7%] provisional | 100.0% | 65.7% [61.4–68.6%] | 63.3% [62.5–65.8%] | 27 [25–29] | 0.0% | 98.6% [98.6–98.8%] | no | — |
| 2026-08-16 | openrouter | x-ai/grok-4.6 | lgtmaybe 2.1.4 | 63.7% [60.6–69.0%] provisional | 100.0% | 57.1% [52.9–62.9%] | 65.6% [62.9–70.8%] | 22 [19–23] | 22.2% [22.2–33.3%] | 98.5% [98.4–98.5%] | no | — |

## Validated long horizon

No complete `long-horizon-validated` runs yet.

## Historical long horizon — top 10

Complete `long-horizon` runs using `canonical-long-horizon`, ranked by score across lgtmaybe versions. Recall covers 32 planted bugs in four cases; a fifth case is clean. Where measured, the score is F0.5 multiplied by `completeness`, the share of review calls that returned parseable findings. Historical scores were recalculated from unchanged raw evidence. Scores are not comparable with breadth. Historical cases include unplanted threshold changes; their ranking is archival.

### Model summary

| date | provider | model | lgtmaybe | score | completeness | recall | precision | true positives | false positives |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-09-24 | openrouter | google/gemini-3.8-flash | lgtmaybe 2.8.5 | 77.8% | 100.0% | 87.5% | 75.7% | 28 | 9 |
| 2026-08-18 | openrouter | qwen/qwen3.8-max | lgtmaybe 2.2.0 | 76.9% | 100.0% | 75.0% | 77.4% | 24 | 7 |
| 2026-09-24 | openrouter | openai/gpt-6-luna | lgtmaybe 2.8.5 | 71.8% | 100.0% | 84.4% | 69.2% | 27 | 12 |
| 2026-08-15 | openrouter | google/gemini-3.7-flash | lgtmaybe 2.1.4 | 70.5% | 93.3% | 81.2% | 74.3% | 26 | 9 |
| 2026-08-15 | openrouter | kwaipilot/kat-coder-pro-v2.5 | lgtmaybe 2.1.4 | 66.0% | 93.6% | 68.8% | 71.0% | 22 | 9 |
| 2026-08-15 | openrouter | x-ai/grok-4.6 | lgtmaybe 2.1.4 | 59.2% | 100.0% | 84.4% | 55.1% | 27 | 22 |
| 2026-08-15 | openrouter | anthropic/claude-sonnet-5 | lgtmaybe 2.1.4 | 57.7% | 100.0% | 56.2% | 58.1% | 18 | 13 |
| 2026-08-15 | openrouter | deepseek/deepseek-v4-pro-0813 | lgtmaybe 2.1.4 | 56.6% | 83.0% | 37.5% | 85.7% | 12 | 2 |
| 2026-08-15 | openrouter | openai/gpt-5.6-terra | lgtmaybe 2.1.4 | 55.9% | 100.0% | 53.1% | 56.7% | 17 | 13 |
| 2026-08-15 | openrouter | kwaipilot/kat-coder-air-v2.5 | lgtmaybe 2.1.4 | 55.9% | 89.4% | 62.5% | 62.5% | 20 | 12 |
<!-- BENCH_RESULTS_END -->

## Further results

- [RESULTS.md](RESULTS.md) has every stored completed run and per-case detail.
- [dashboard/index.html](dashboard/index.html) offers sorting and filters for runs, languages, and review lenses.

Focused and diagnostic runs appear in both, but not in the leaderboards.

Each run checkpoints a JSON result under `results/raw/`. It retains final findings (including false positives), evidence IDs, token and truncation data, and the resolved profile. The status is `in_progress` until all cases and repeats finish, then `complete`. A full-corpus canonical run stops at its first failed observation and becomes `ineligible`; its result records where and why it stopped. Focused and diagnostic runs continue collecting failures for investigation.

Compatible lgtmaybe versions also write immutable gzip audit traces under `results/audit/`, showing candidates and later filtering decisions. Human classifications are append-only events under `results/adjudications/`; corrections supersede earlier classifications without changing raw output.

`uv run bench report` reapplies adjudications, recalculates scores, and regenerates the marked README results, `RESULTS.md`, and `dashboard/`. API endpoints are redacted; provider credentials are not stored.

## How the score is calculated

1. Each case has a clean Git revision and a changed revision. The runner asks lgtmaybe to review their diff.
2. A finding catches a planted bug when the file matches, its line is within three lines, an expected keyword appears in the title or body, and it meets any minimum severity. Each bug can be caught once.
3. Every other finding is a false positive, including plausible issues not listed in the corpus. `precision = true positives / (true positives + false positives)`.
4. Both suites use F0.5: `score = 1.25 × precision × recall / (0.25 × precision + recall)`, or 0% when the denominator is zero. It weights precision twice as heavily as recall. Long horizon uses recall over planted bugs; breadth uses balanced recall across language and lens combinations. Where call data is available, the score is also scaled by completeness: the share of provider calls that returned parseable findings.
5. Each repeat is scored separately. Tables show the median and, when repeats differ, the minimum–maximum range.

Long horizon has 32 planted bugs across four cases; findings on its fifth, clean case are false positives. Breadth averages recall across 70 primary language and lens combinations, giving each equal weight. Breadth uses three repeats; long horizon uses one. A breadth run with unresolved findings is marked provisional until classified.

For a closer comparison, use the dashboard to filter to one lgtmaybe version. It also shows timing, tokens, truncations, and settings.

## Contributing cases

Each `corpus/<name>/` case contains `base/`, `changed/`, and `case.json`. Planted bugs must be visible in the diff. Claims requiring unseen context belong in `forbidden`. Once a raw result references a case, keep it unchanged and add a versioned replacement such as `<name>-v2`.
