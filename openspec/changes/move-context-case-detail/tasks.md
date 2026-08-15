## 1. Behavioural Coverage

- [x] 1.1 Add failing tests that README keeps the model summary but omits context case detail
- [x] 1.2 Add failing tests that dashboard data, `RESULTS.md`, and dashboard HTML retain context case detail

## 2. Reporting

- [x] 2.1 Move context case metric calculation into dashboard data and stop rendering it in README
- [x] 2.2 Render context case rows from dashboard data in `RESULTS.md` and dashboard HTML
- [x] 2.3 Regenerate README, RESULTS, and dashboard artefacts from stored raw results

## 3. Verification

- [x] 3.1 Run pytest, ruff, mypy, corpus validation, fake-CLI integration, report determinism, and OpenSpec validation with Python 3.12
