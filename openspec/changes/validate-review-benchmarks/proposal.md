## Why

Published breadth scores count successful reflection calls as failed reviews, and many corpus cases cannot build or count the same defect in two lenses. The benchmark needs trustworthy historical scoring and a new runnable corpus before it can guide model choice.

## What Changes

- Rescore historical raw evidence using finding-producing review calls for completeness; expose non-review stage failures separately.
- Add immutable `breadth-validated` cases with runnable revisions and distinct defects across seven languages, plus valid Actions and Terraform cases.
- Replace the long-horizon cases with a versioned validated suite after the audit found unplanted numeric threshold changes in its historical clean case.
- Add diagnostic paired comparisons for optional review settings without adding them to canonical rankings.
- Make the new suite the default after offline validation while retaining historical suites and results unchanged.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `benchmark-corpus`: Require independently adjudicable, runnable cases in the new validated breadth suite.
- `benchmark-scoring-reporting`: Correct call completeness and keep new and historical suite rankings separate.
- `benchmark-execution`: Support paired diagnostic review-option runs and the new default suite.

## Impact

Corpus fixtures and suite manifests, scorer, runner, reporting, CLI, tests, and generated documentation change. Published case directories and raw result files remain immutable. No paid model run or runtime dependency is added.
