# Design: context scaling suite

## Size bands are token-anchored

The canonical profile caps input at 100k tokens. The ladder targets fractions of that cap so the largest case stresses attention without auto-truncating: ~3%, ~15%, ~45%, and ~90% of the cap, using ~10 tokens per changed line of Python as the planning heuristic. Line counts (~300, ~1,500, ~4,500, ~9,000 changed lines) are the generator's control variable; token fractions are the interpretation.

## Same bug count, controlled positions

Every defect-bearing case plants exactly eight bugs so per-case recall is directly comparable across bands. Bug positions are pinned to relative fractions of the changed-file ordering (~10%, ~25%, ~40%, ~55%, ~70%, ~85%, plus one in the first and one in the last changed file), giving a needle-in-haystack dimension: misses concentrated at high fractions indicate late-context inattention, not general blindness.

## Generated, deterministic, one-shot

`scripts/generate_context_cases.py` generates realistic multi-module Python from a fixed seed: varied domain vocabulary, type hints, docstrings, and non-trivial control flow, with a broad refactor-style `changed/` tree per case. The script is deterministic (same seed, byte-identical output) and is a one-shot builder: once a raw result references a case, the case is immutable like every published case and corrections require a new versioned case name. Runs never invoke the generator.

## Scoring reuses the existing machinery

`parse_case`, `score_case`, and the suite loader are unchanged; the new `case.json` files use the existing schema with a new `context-scaling` coverage tag. Matrix validation stays `v2`-only, so the context suite needs no balanced-cell invariant.

## Profile

`context-canonical-v1` pins one repeat (cost control), the full preset (lenses must not be throttled exactly as context grows), and the canonical 100k input-token cap. It is canonical for the context suite's own report section but must never enter the `v2` leaderboard, which already partitions by suite and profile ID.

## Reporting

A dedicated section in `RESULTS.md`, generated from `results/raw/` like every other section, filters complete, un-failed `context-v1` / `context-canonical-v1` runs and renders one row per model and case: recall, precision, findings, input/output tokens, truncation flag, and wall time. The degradation curve is visible reading down the size bands within a model; no charting dependency.

## Risks

- **Synthetic-code transfer**: absolute recall on generated code is not recall on real PRs; the suite's claim is the relative degradation trend across bands.
- **Statistical coarseness**: eight findings give 12.5% recall steps; interpretation relies on the cross-band trend, and cheap bands can be re-run with more repeats as diagnostic runs.
- **Cost**: the top band can multiply the diff across lenses inside lgtmaybe; the smoke run on small and medium bands gates the full ladder.
