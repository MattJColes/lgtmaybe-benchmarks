## 1. Behavioural coverage

- [x] 1.1 Update tests to prove each false positive deducts exactly one percentage point from the same base score.
- [x] 1.2 Update the zero-floor test so its noise volume still floors the score under the halved penalty.
- [x] 1.3 Verify the revised tests fail against the two-point implementation.

## 2. Scoring and documentation

- [x] 2.1 Change `FALSE_POSITIVE_PENALTY` to `0.01` in the shared scoring constant.
- [x] 2.2 Update README.md and AGENTS.md with the one-point deduction.

## 3. Historical reports and verification

- [x] 3.1 Regenerate README.md, RESULTS.md, and dashboard from unchanged raw results via `uv run bench report`.
- [x] 3.2 Run pytest, ruff format check, ruff lint, mypy, and verify via git diff that only scores and ordering changed with `results/raw/` untouched.
