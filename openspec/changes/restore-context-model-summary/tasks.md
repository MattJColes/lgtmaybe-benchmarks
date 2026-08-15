## 1. Behavioural Coverage

- [x] 1.1 Add a failing report test for context model score, recall, precision, true positives, and false positives
- [x] 1.2 Add a failing dashboard-data test that preserves context true-positive and false-positive totals

## 2. Reporting

- [x] 2.1 Render the context model summary from eligible scored runs before the per-case table
- [x] 2.2 Preserve computed context finding totals in dashboard data and regenerate report artefacts

## 3. Verification

- [x] 3.1 Run pytest, ruff, mypy, corpus validation, report determinism, and the fake-CLI end-to-end benchmark with Python 3.12
- [x] 3.2 Validate the OpenSpec change and confirm generated README, RESULTS, and dashboard output contain the model summaries
