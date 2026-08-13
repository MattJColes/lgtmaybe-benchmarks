## 1. Scope Metadata

- [x] 1.1 Add failing runner tests proving full runs store `full_corpus: true` and repeatable `--case` runs store `full_corpus: false` without changing selected-case evidence.
- [x] 1.2 Implement the backward-compatible raw configuration marker and make the runner tests pass.

## 2. Consolidated Results

- [x] 2.1 Replace the report golden expectations with one table containing run identity, score, all lens recall columns, and final settings; assert the old leaderboard, cases, timing, token, precision, clean, truncation, and failure columns are absent.
- [x] 2.2 Add behavioural tests for focused-run exclusion, legacy raw results defaulting to full corpus, default settings rendering as `—`, and fixed-order non-default settings rendering.
- [x] 2.3 Implement the full-corpus filter, deterministic settings summarizer, and single-table renderer using existing scoring and provider-aware defaults.

## 3. Generated Documentation and Verification

- [x] 3.1 Regenerate `README.md` and `RESULTS.md` from committed raw evidence and update surrounding prose to describe one full-corpus results table and raw diagnostic detail.
- [x] 3.2 Run two unchanged reports and confirm byte identity, then run pytest, ruff format/check, mypy, strict OpenSpec validation, and `git diff --check`.
