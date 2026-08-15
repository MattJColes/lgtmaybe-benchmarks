## 1. Generator

- [x] 1.1 Write failing tests for `scripts/generate_context_cases.py`: deterministic output for a fixed seed, emitted `case.json` files pass `parse_case`, bug positions land within tolerance of their target fractions, the clean case declares no expected findings, and every referenced changed file and line exists.
- [x] 1.2 Implement the generator: seeded realistic multi-module Python base and changed trees, eight planted bugs per defect case at controlled positions, `case.json` emission, and the `corpus/suites/context-v1.json` manifest.
- [x] 1.3 Generate the five cases and verify corpus loading: `load_suite("context-v1")` resolves, `validate_v2_matrix` still passes for `v2` and is not applied to `context-v1`.

## 2. Execution

- [x] 2.1 Write failing tests for the `context-canonical-v1` profile: resolves with one repeat, full preset, and the canonical input-token cap; explicit overrides still downgrade to a diagnostic identity.
- [x] 2.2 Register the profile in `runner.py` and confirm `bench run --suite context-v1 --profile context-canonical-v1` runs without a diagnostic downgrade.

## 3. Reporting

- [x] 3.1 Write failing tests for the context-scaling section: renders from a fixture raw `context-v1` result with per-case recall, precision, findings, tokens, truncation, and wall time; excluded for focused, failed, or non-context runs; deterministic across two renders.
- [x] 3.2 Implement the section in `reporting.py` and wire it into `render_results`/`regenerate_reports` without changing the `v2` leaderboard or legacy sections.

## 4. Verification

- [x] 4.1 Run pytest, ruff, and mypy in the project environment.
- [x] 4.2 Smoke run `python-context-small-v1` and `python-context-medium-v1` against a cheap provider, confirm findings parse and score.
- [x] 4.3 Run the full ladder and regenerate reports with `anthropic/claude-fable-5`.
