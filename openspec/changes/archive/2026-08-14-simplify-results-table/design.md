## Context

The renderer currently emits a 24-column leaderboard followed by a 13-column per-lens table. Both are generated from the same scored raw runs, and the leaderboard repeats the entire case list even though public comparisons are intended to be full-corpus only. See `proposal.md` for motivation and the two delta specs for observable behavior.

## Goals / Non-Goals

**Goals:**

- Make the generated report useful in one scan without losing the overall score or lens breakdown.
- Keep focused diagnostic runs and complete operational evidence in raw JSON.
- Make configuration differences visible without repeating defaults.
- Preserve deterministic regeneration and compatibility with the existing raw result.

**Non-Goals:**

- Change scoring, aggregation, corpus cases, or CLI flags.
- Delete timings, tokens, findings, failures, or selected cases from raw evidence.
- Add expandable Markdown, a second details table, or a new dependency.

## Decisions

### Emit one comparison table

The table columns will be `date`, `lgtmaybe`, `provider`, `model`, `score`, the ten lens names, and `settings`. This preserves the useful per-lens shape and adds only the identity and score needed to compare historical rows.

Alternative: keep a shortened leaderboard above the lens table. Rejected because it retains two visual surfaces and forces readers to correlate rows.

### Public comparisons are full-corpus only

New raw configurations will store `full_corpus`, derived from whether `--case` was omitted. The renderer will exclude records explicitly marked false. A missing marker means true so the existing committed raw result remains visible.

Alternative: compare stored case names with the current corpus. Rejected because adding a future case would make an honest historical full run disappear retroactively.

### Settings are a default-diff summary

The renderer will compare stored values with benchmark defaults and join deviations in a fixed order: effort, preset, max tokens, max input tokens, API base, concurrency, repeats, timeout. Provider-aware concurrency uses the same resolver as the CLI. Null optional values and Ollama's normal thinking-off behavior are not custom settings.

Alternative: serialize the whole configuration into one cell. Rejected because it recreates the current visual noise in a less readable form.

### Raw JSON remains the detail surface

Precision, recall, clean status, truncations, failures, timing, and token totals remain scored and stored but are not rendered as dedicated columns. This keeps the comparison table focused without destroying evidence or future reporting options.

## Risks / Trade-offs

- [The single table remains wide because there are ten lenses] → Keep every lens because this is the useful comparison the user selected; remove all nonessential columns around it.
- [Focused runs are less discoverable] → Document that they remain under `results/raw/` and are intentionally excluded from comparisons.
- [A custom concurrency equal to the provider default cannot be distinguished] → Treat equivalent resolved behavior as default; the report describes effective configuration, not how the flag was typed.
- [Legacy records lack scope metadata] → Treat missing `full_corpus` as true; all future records carry the explicit marker.

## Migration Plan

1. Add the scope marker to newly written raw configurations without rewriting existing evidence.
2. Replace the golden renderer expectations and add focused-run/settings cases.
3. Regenerate `README.md` and `RESULTS.md` from the committed raw result.
4. Roll back by reverting the renderer and generated Markdown; raw files remain compatible in either direction.
