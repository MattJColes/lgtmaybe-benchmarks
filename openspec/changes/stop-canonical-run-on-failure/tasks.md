## 1. Behavioural coverage

- [x] 1.1 Write failing tests for a canonical full-corpus run stopping at its first failed observation, invoking no later case, and storing terminal status `ineligible`.
- [x] 1.2 Write failing tests for the stored termination reason naming repeat, case, observation ID, exit code, timeout flag, and failure classification.
- [x] 1.3 Write failing tests for observation failure classification covering timeout, truncated output, unparseable output, non-zero exit, and a truncated but scoreable observation.
- [x] 1.4 Write failing tests for focused and diagnostic runs still collecting failures and finishing as complete.
- [x] 1.5 Write failing tests for an `ineligible` record being excluded from scoring, rankings, generated Markdown, and the canonical dashboard flag while existing `complete` and `in_progress` records still render.

## 2. Execution

- [x] 2.1 Classify failed observations in `run_review` and retain the class on the stored observation.
- [x] 2.2 Stop canonical full-corpus runs after the first failed observation and write the terminal `ineligible` record with its structured termination reason.
- [x] 2.3 Exit non-zero with a concise, credential-free message naming the case, repeat, and classification.

## 3. Documentation

- [x] 3.1 Document the fail-fast rule and the `ineligible` status where run statuses are already described for humans and coding agents.

## 4. Verification

- [x] 4.1 Run pytest, ruff format check, ruff lint, and mypy in the project virtual environment.
- [x] 4.2 Regenerate README.md and RESULTS.md from existing raw runs and confirm the leaderboard holds the same models with identical metrics.
