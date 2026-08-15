## 1. Behavioural Coverage

- [x] 1.1 Add failing tests that context, v2, and legacy README rankings sort by score and render at most ten rows
- [x] 1.2 Add a failing test that detailed outputs retain rows excluded from README and HTML shows true positives

## 2. Reporting

- [x] 2.1 Apply one ten-row limit after sorting in every README ranking renderer
- [x] 2.2 Render true positives in the HTML results table
- [x] 2.3 Regenerate README and dashboard HTML and confirm detailed outputs remain complete

## 3. Verification

- [x] 3.1 Run pytest, ruff, mypy, report determinism, and OpenSpec validation with Python 3.12
