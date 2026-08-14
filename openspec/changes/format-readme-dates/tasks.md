## 1. Report Formatting

- [x] 1.1 Add behavioural coverage for ISO dates in complete and incomplete rows.
- [x] 1.2 Format generated report dates as `YYYY-MM-DD` without changing raw timestamps or sorting.

## 2. Generated Output and Verification

- [x] 2.1 Regenerate `README.md` and `RESULTS.md` from raw evidence.
- [x] 2.2 Run pytest, ruff, mypy, corpus validation, and OpenSpec validation.

## 3. Score Ordering

- [x] 3.1 Add behavioural coverage for score-descending order and newest-first score ties.
- [x] 3.2 Sort complete comparison rows by median overall score descending with timestamp tie-breaking.

## 4. Updated Output and Verification

- [x] 4.1 Regenerate `README.md` and `RESULTS.md` with score ordering.
- [x] 4.2 Run pytest, ruff, mypy, report determinism, and strict OpenSpec validation.

## 5. Failed Run Filtering

- [x] 5.1 Add behavioural coverage that excludes complete runs containing failed observations.
- [x] 5.2 Filter failed runs before scoring while retaining raw evidence.

## 6. Final Output and Verification

- [x] 6.1 Regenerate `README.md` and `RESULTS.md` without failed score rows.
- [x] 6.2 Run pytest, ruff, mypy, report determinism, and strict OpenSpec validation.
