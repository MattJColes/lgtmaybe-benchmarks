## Why

The generated README should stay focused on the model-level comparison, but it currently includes a long context case-detail table. The same evidence belongs in the detailed `RESULTS.md` and HTML dashboard, where readers can inspect it without overwhelming the repository landing page.

## What Changes

- Keep the score-ranked context model summary in the generated README.
- Remove the context case-detail table from the README generated section.
- Preserve the case-level recall, precision, findings, token, truncation, and timing data in dashboard data.
- Render the context case detail in `RESULTS.md` and the HTML dashboard.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: context case detail moves from the README to detailed Markdown and HTML outputs.

## Impact

- Context report rendering, dashboard data, detailed Markdown, and dashboard HTML in `src/lgtmaybe_bench/reporting.py`.
- Behavioural report tests and regenerated `README.md`, `RESULTS.md`, and dashboard artefacts.
- No scoring, eligibility, corpus, execution, dependency, or raw-result changes.
