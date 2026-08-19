## 1. Behavioural coverage

- [x] 1.1 Replace the fixed-deduction tests with F0.5 tests: exact value, precision weighted above recall, heavy noise damping without a zero cliff, zero score for no findings.
- [x] 1.2 Update breadth balanced-score expected values to F0.5 and add a test that both suites share the precision-weighted formula.
- [x] 1.3 Verify the revised tests fail against the fixed-deduction and balanced-F1 implementation.

## 2. Scoring and documentation

- [x] 2.1 Implement one shared F0.5 score function used by case, combined, and suite scoring; delete the fixed penalty constant.
- [x] 2.2 Update README.md and AGENTS.md with the F0.5 formula and update generated report labels to balanced F0.5.

## 3. Historical reports and verification

- [x] 3.1 Regenerate README.md, RESULTS.md, and the dashboard from unchanged raw results via `uv run bench report`.
- [x] 3.2 Run pytest, ruff lint, mypy, and verify via git diff that only scores, labels, and ordering changed with `results/raw/` untouched.
