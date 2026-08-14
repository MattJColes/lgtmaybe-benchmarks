## 1. Behavioural coverage

- [x] 1.1 Add tests proving each false positive deducts exactly two percentage points from the same base score.
- [x] 1.2 Add a test proving deductions cannot reduce score below zero.
- [x] 1.3 Verify the revised tests fail against the variable-penalty implementation.

## 2. Scoring and documentation

- [x] 2.1 Implement one shared fixed-penalty score function and use it for case and combined scoring.
- [x] 2.2 Update README.md and AGENTS.md with the fixed formula and zero floor.

## 3. Historical reports and verification

- [x] 3.1 Regenerate README.md and RESULTS.md twice and verify byte-identical adjusted scores.
- [x] 3.2 Run pytest, ruff format check, ruff lint, mypy, strict OpenSpec validation, and git diff checks.
