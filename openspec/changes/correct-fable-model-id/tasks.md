## 1. Behavioural Coverage

- [x] 1.1 Add a failing test that the Fable raw source and dashboard projection use the exact model identity consistently

## 2. Evidence Correction

- [x] 2.1 Rename the Fable raw file and correct its model, run, observation, and finding identifiers
- [x] 2.2 Correct the historical OpenSpec task reference and prove no obsolete alias remains
- [x] 2.3 Regenerate README, RESULTS, and dashboard artifacts from the corrected raw evidence

## 3. Verification

- [x] 3.1 Prove measurements are unchanged after normalising the approved identity strings
- [x] 3.2 Run pytest, Ruff, mypy, report determinism, and OpenSpec validation with Python 3.12
