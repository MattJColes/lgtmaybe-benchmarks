## 1. Document the methodology

- [x] 1.1 Add the v2 case-type inventory, exact case and finding counts, and coverage explanation to `README.md` outside the generated result markers.
- [x] 1.2 Explain the paired-revision run process, finding classification and adjudication, v2 formulas, provisional status, repeat aggregation, and legacy-v1 distinction.

## 2. Verify the documentation

- [x] 2.1 Confirm every documented count against `corpus/suites/v2.json` and the referenced `case.json` files.
- [x] 2.2 Run pytest, ruff, mypy, corpus validation, report determinism, and OpenSpec validation in the Python 3.12 project environment.
