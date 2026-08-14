## Why

The README publishes benchmark results without giving readers enough detail to understand what the suite tests, how many cases and planted findings it contains, or how the headline score is calculated. Readers need that methodology beside the results so they can interpret comparisons correctly.

## What Changes

- Add a compact README methodology section describing the canonical v2 case types and their counts.
- Explain the benchmark process from paired revisions through finding classification and repeat aggregation.
- Define balanced recall, pooled precision, balanced F1, provisional results, and the legacy-v1 scoring distinction in plain language.
- Keep the hand-authored methodology outside the generated results markers.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Require the public README to document the current canonical suite composition, execution process, and scoring interpretation alongside generated results.

## Impact

The change updates `README.md` and the benchmark scoring/reporting specification. It does not change the corpus, scorer, runner, generated result tables, command interfaces, or dependencies.
