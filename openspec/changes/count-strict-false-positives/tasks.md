## 1. Behavioural coverage

- [x] 1.1 Update scoring tests so distant, duplicate, forbidden, and otherwise unmatched findings count as false positives and lower precision.
- [x] 1.2 Update aggregation and report tests to require a `false positives` count.
- [x] 1.3 Verify the revised tests fail against the current implementation.

## 2. Scoring and reporting

- [x] 2.1 Implement strict closed-world false-positive classification and aggregation.
- [x] 2.2 Render false-positive counts in the generated full-corpus table.

## 3. Documentation and historical results

- [x] 3.1 Document the strict rule in README.md and AGENTS.md, including treatment of plausible uncatalogued issues.
- [x] 3.2 Regenerate README.md and RESULTS.md twice from existing raw runs and verify byte-identical output.

## 4. Verification

- [x] 4.1 Run pytest, ruff format check, ruff lint, mypy, strict OpenSpec validation, and git diff checks.
