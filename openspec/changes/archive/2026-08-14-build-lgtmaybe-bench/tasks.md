## 1. Repository Foundation

- [x] 1.1 Add `pyproject.toml` for Python 3.12, the `bench` console script, uv, pytest, ruff, and mypy configuration; generate `uv.lock` and confirm commands use the project virtual environment.
- [x] 1.2 Add `.gitignore` for Python, uv, editor, coverage, temporary benchmark repositories, and local result scratch files while retaining `results/raw/*.json`.
- [x] 1.3 Add concise root `AGENTS.md` and `CLAUDE.md` instructions covering OpenSpec apply workflow, tests-first development, corpus immutability, generated files, and secret handling.
- [x] 1.4 Add the initial `README.md` quick start and generated-results markers plus an empty generated `RESULTS.md`.

## 2. Scoring Contract

- [x] 2.1 Write failing public-interface tests for expected matching, the ±3-line boundary, wrong severity, forbidden hits, unexpected adjudicable findings, far-line exclusion, clean status, per-lens recall, and harmonic-mean score.
- [x] 2.2 Implement typed ground-truth and finding parsing at the JSON boundary with the named line-window and severity-order constants.
- [x] 2.3 Implement one-to-one expected matching and finding classification, then make the scoring tests pass.
- [x] 2.4 Add repeat aggregation tests for median/min/max metrics, tokens, truncation lenses, and a single-repeat configuration.
- [x] 2.5 Implement repeat and configuration aggregation, including Ollama's explicit thinking-off effort label.

## 3. Runner and Raw Evidence

- [x] 3.1 Write failing tests for CLI defaults and flags, repeatable case selection, provider-aware concurrency defaults, and preflight errors.
- [x] 3.2 Write a fake `lgtmaybe` executable fixture and failing tests for JSON/profile separation, call-table parsing, token capture, command failure retention, and truncated-lens recognition.
- [x] 3.3 Implement `bench run` argument parsing and preflight validation without adding runtime dependencies.
- [x] 3.4 Implement isolated temporary git repository construction from a case's `base/` and `changed/` trees and verify the generated diff in a behavioural test.
- [x] 3.5 Implement timeout-bound lgtmaybe subprocess invocation with complete resolved flags, version capture, and raw stdout/stderr retention.
- [x] 3.6 Implement defensive findings/profile parsing and preserve partial findings when a profiled call truncates.
- [x] 3.7 Implement atomic, uniquely named raw JSON persistence with embedded ground truth and no credentials.

## 4. Corpus

- [x] 4.1 Write failing corpus-validation tests for schema errors, missing paths, invalid lines/lenses, empty keywords, required lens coverage, and single-file/multi-file representation.
- [x] 4.2 Implement corpus discovery, validation, and exact-name selection; ensure validation completes before model execution.
- [x] 4.3 Add two stable security cases and two correctness cases, including at least one forbidden context trap.
- [x] 4.4 Add two stable performance cases and two complexity cases.
- [x] 4.5 Add two stable tests cases and two documentation cases.
- [x] 4.6 Add two stable deprecation cases and two intent cases.
- [x] 4.7 Add two stable ponytail cases and two committed-spec delivery cases.
- [x] 4.8 Add a multi-file case sized to exercise batching at a documented low `--max-input-tokens` value, then run full corpus validation.

## 5. Reports and Acceptance

- [x] 5.1 Write failing golden-file tests for newest-first result ordering, full configuration columns, score/recall/precision/clean data, per-lens recall, and provider-aware timing labels.
- [x] 5.2 Implement the single Markdown renderer used by both `RESULTS.md` and the bounded generated section of `README.md`.
- [x] 5.3 Implement `bench report` to rescore every raw result and atomically regenerate both Markdown surfaces.
- [x] 5.4 Wire successful `bench run` completion through the same report function and prove two unchanged `bench report` runs are byte-identical.
- [x] 5.5 Complete the README with installation, local and hosted examples, metric definitions, cost warning, corpus contribution rules, timing-comparison warning, and raw-data/report recovery instructions.
- [x] 5.6 Run pytest, ruff format/check, mypy, corpus validation, and a fake-CLI end-to-end run; re-open changed files to confirm formatter persistence.
- [x] 5.7 Run `bench run --provider ollama --model <local> --repeats 1` against an available local model and confirm it stores raw evidence, scores truncations visibly, and updates README and RESULTS tables.
