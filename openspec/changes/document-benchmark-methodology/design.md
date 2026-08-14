## Context

The README explains how to run the benchmark and gives short metric definitions, but readers must inspect the suite manifest, case metadata, and scorer to learn the test inventory and full evaluation process. The v2 suite currently contains 32 paired-revision cases, 72 planted findings, and 9 verified-clean cases. Its balanced recall deliberately covers only the 70 primary language/lens cells; the two cross-cutting security findings still contribute to pooled precision and detailed evidence.

The generated results section is replaced by `bench report`, so methodology prose must remain outside `BENCH_RESULTS_START` and `BENCH_RESULTS_END`.

## Goals / Non-Goals

**Goals:**

- Make the canonical suite's case types, counts, and coverage visible at a glance.
- Explain the run, classification, adjudication, scoring, and repeat-aggregation process in plain language.
- State enough of each formula for readers to reproduce its interpretation.
- Preserve generated-report ownership of the results table.

**Non-Goals:**

- Change the suite, runner, scorer, profile defaults, or generated table.
- Generate the methodology section from corpus metadata.
- Rewrite the quick start or detailed result artifacts.

## Decisions

### Put methodology before results

Add a `How the benchmark works` section immediately before `## Results`. Readers encounter the evidence model and scoring rules before interpreting a ranking, and report regeneration cannot overwrite it. Putting this detail after the large generated table would make it difficult to discover.

### Use one inventory table and a short process sequence

The inventory table will group the seven core languages by four repeated case types, then list GitHub Actions and Terraform coverage separately. It will show cases, planted findings, and what each type probes. A short numbered sequence will explain paired revisions, external lgtmaybe execution, deterministic classification plus adjudication, and aggregation.

### Distinguish the 72 total targets from the 70 balanced cells

The README will state both figures explicitly. The 70 core targets form one target for every combination of seven languages and ten lenses. The two cross-cutting security targets remain part of suite evidence but do not add extra weight to balanced recall. Pooled precision uses classified final findings across the whole suite.

### Keep legacy scoring visibly separate

The current v2 headline score is balanced F1, the harmonic mean of balanced recall and pooled precision. Legacy-v1 uses harmonic recall against perfect precision and then deducts two percentage points per false positive. The README will avoid describing the legacy penalty as the current v2 formula.

## Risks / Trade-offs

- [Counts can become stale when a new suite is introduced] -> Name v2 explicitly and require the README methodology to be updated with suite membership changes.
- [Readers may confuse planted findings with balanced cells] -> Present both counts and explain why they differ.
- [Generated reports may overwrite prose placed inside their markers] -> Keep all new prose before the generated section and run report determinism checks.
