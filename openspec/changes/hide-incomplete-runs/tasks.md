## 1. Behavioural coverage

- [x] 1.1 Update report tests to require incomplete runs to be absent from generated Markdown.
- [x] 1.2 Verify the revised tests fail against the current renderer.

## 2. Report rendering

- [x] 2.1 Remove incomplete-run Markdown rendering while retaining completed-run filtering.
- [x] 2.2 Regenerate README.md and RESULTS.md from raw results twice and verify deterministic output.

## 3. Verification

- [x] 3.1 Run pytest, ruff format check, ruff lint, mypy, and strict OpenSpec validation.
