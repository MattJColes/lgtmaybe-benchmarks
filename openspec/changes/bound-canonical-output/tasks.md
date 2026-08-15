## 1. Profiles and CLI

- [x] 1.1 Write failing tests: `canonical-v2` resolves as canonical with three repeats and `max_tokens 16384`; `canonical-v1` stays resolvable and unchanged (`max_tokens None`); the CLI default profile is `canonical-v2`; overrides of `canonical-v2` still downgrade to a diagnostic identity.
- [x] 1.2 Implement: register `canonical-v2` in `runner.py`, make it the CLI and resolution default.

## 2. Bounded canonical output evidence

- [x] 2.1 Write failing tests: a canonical-v2 review command carries `--max-tokens 16384`; repeated provider-ceiling calls at the budget are all marked truncated, excluded from `wall_excluding_truncation_seconds`, and the observation stays scoreable; truncation never becomes a finding or failure.
- [x] 2.2 Implement/verify in `run_review` and `_command`; keep truncation marking driven by the resolved profile budget.

## 3. Reporting

- [x] 3.1 Write failing tests: the v2 leaderboard and dashboard canonical eligibility accept both canonical generations; the newest complete canonical generation wins the comparison key and generations never mix in one ranking; existing `canonical-v1` fixtures still render.
- [x] 3.2 Implement eligibility in `reporting.py`; regenerate reports and update hand-authored README profile documentation to name `canonical-v2` as the default.

## 4. Verification

- [x] 4.1 Run pytest, ruff, and mypy in the project environment; confirm report determinism.
- [x] 4.2 Update the change metadata and archive-ready state.
