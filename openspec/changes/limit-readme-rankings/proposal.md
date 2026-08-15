## Why

README rankings will keep growing as more models are benchmarked, making the repository landing page harder to scan. It should consistently show only the ten strongest eligible results while detailed outputs retain the full history.

## What Changes

- Sort every generated README ranking by score descending.
- Limit each generated README ranking table to its top ten eligible rows.
- Use deterministic timestamp and run identity tie-breakers when scores match.
- Keep every stored run in `RESULTS.md`, dashboard data, and the HTML dashboard.
- Show true positives in the HTML results table so it exposes every README summary metric.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: README rankings become consistently score-sorted and bounded to ten rows.

## Impact

- README and HTML renderers plus behavioural tests in `src/lgtmaybe_bench/reporting.py` and `tests/test_reporting.py`.
- Regenerated `README.md` and dashboard HTML; detailed generated outputs remain complete.
- No scoring, eligibility, raw evidence, dependency, corpus, or execution changes.
