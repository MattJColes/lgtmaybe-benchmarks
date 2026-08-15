## Why

The generated README and dashboard no longer show an aggregate score or incorrect-finding count for each model because the current context-only report path renders case rows and discards aggregate true-positive and false-positive counts. Readers need the model-level outcome alongside the scaling detail to compare published runs without inspecting raw JSON.

## What Changes

- Add a deterministic model-summary table for eligible `context-v1` canonical runs with overall score, recall, precision, true positives, and false positives.
- Retain the existing per-case context-scaling table beneath the summary.
- Preserve computed true-positive and false-positive totals for context runs in dashboard data and `RESULTS.md` instead of emitting missing values.
- Keep the existing closed-world scoring rules and eligibility filters unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: context reporting gains model-level score and correct/incorrect finding totals across generated outputs.

## Impact

- Reporting and dashboard serialization in `src/lgtmaybe_bench/reporting.py`.
- Behavioural report tests and regenerated `README.md`, `RESULTS.md`, and dashboard artefacts.
- No corpus, benchmark execution, scoring formula, public command, or dependency changes.
