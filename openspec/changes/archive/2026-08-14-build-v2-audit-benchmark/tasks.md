## 1. Reconcile foundation changes

- [x] 1.1 Archive or deliberately reconcile `checkpoint-raw-observations` and `format-readme-dates`, then confirm their accepted behavior is present before editing shared runner/reporting code
- [x] 1.2 Add failing corpus tests for suite manifests, language and clean metadata, immutable membership, and `legacy-v1` inference
- [x] 1.3 Implement suite loading and legacy inference in the existing corpus module until the corpus tests pass
- [x] 1.4 Add failing runner tests for versioned profiles, canonical defaults, diagnostic overrides, and language-independent settings
- [x] 1.5 Implement the smallest profile definitions and resolved-profile model in the existing runner/config path until those tests pass
- [x] 1.6 Add failing CLI tests for `--suite`, `--profile`, focused cases, and canonical-versus-diagnostic identity
- [x] 1.7 Implement the CLI options and fail-fast validation without adding a runtime dependency

## 2. Validate the v2 coverage matrix

- [x] 2.1 Add failing validator tests for 70 unique language/lens cells, seven clean language cases, four CI/IaC cases, and required spec, test, multi-file, and large-diff coverage
- [x] 2.2 Implement matrix validation and clear duplicate, missing-cell, contradictory-clean, and unknown-language errors
- [x] 2.3 Add the immutable `v2` suite manifest with the planned 32 case IDs and confirm it fails validation until all cases exist

## 3. Add Python and TypeScript cases

- [x] 3.1 Add the idiomatic Python runtime-safety case covering security, correctness, tests, and spec, then run corpus validation
- [x] 3.2 Add the idiomatic Python efficiency-design case covering performance, complexity, and ponytail, then run corpus validation
- [x] 3.3 Add the idiomatic Python contract-evolution case covering documentation, deprecation, and intent, then run corpus validation
- [x] 3.4 Add the Python clean-context trap case with no expected findings, then run corpus validation
- [x] 3.5 Add the idiomatic TypeScript runtime-safety case covering security, correctness, tests, and spec, then run corpus validation
- [x] 3.6 Add the idiomatic TypeScript efficiency-design case covering performance, complexity, and ponytail, then run corpus validation
- [x] 3.7 Add the idiomatic TypeScript contract-evolution case covering documentation, deprecation, and intent, then run corpus validation
- [x] 3.8 Add the TypeScript clean-context trap case with no expected findings, then run corpus validation

## 4. Add JavaScript and Rust cases

- [x] 4.1 Add the idiomatic JavaScript runtime-safety case covering security, correctness, tests, and spec, then run corpus validation
- [x] 4.2 Add the idiomatic JavaScript efficiency-design case covering performance, complexity, and ponytail, then run corpus validation
- [x] 4.3 Add the idiomatic JavaScript contract-evolution case covering documentation, deprecation, and intent, then run corpus validation
- [x] 4.4 Add the JavaScript clean-context trap case with no expected findings, then run corpus validation
- [x] 4.5 Add the idiomatic Rust runtime-safety case covering security, correctness, tests, and spec, then run corpus validation
- [x] 4.6 Add the idiomatic Rust efficiency-design case covering performance, complexity, and ponytail, then run corpus validation
- [x] 4.7 Add the idiomatic Rust contract-evolution case covering documentation, deprecation, and intent, then run corpus validation
- [x] 4.8 Add the Rust clean-context trap case with no expected findings, then run corpus validation

## 5. Add Dart and Java cases

- [x] 5.1 Add the idiomatic Dart runtime-safety case covering security, correctness, tests, and spec, then run corpus validation
- [x] 5.2 Add the idiomatic Dart efficiency-design case covering performance, complexity, and ponytail, then run corpus validation
- [x] 5.3 Add the idiomatic Dart contract-evolution case covering documentation, deprecation, and intent, then run corpus validation
- [x] 5.4 Add the Dart clean-context trap case with no expected findings, then run corpus validation
- [x] 5.5 Add the idiomatic Java runtime-safety case covering security, correctness, tests, and spec, then run corpus validation
- [x] 5.6 Add the idiomatic Java efficiency-design case covering performance, complexity, and ponytail, then run corpus validation
- [x] 5.7 Add the idiomatic Java contract-evolution case covering documentation, deprecation, and intent, then run corpus validation
- [x] 5.8 Add the Java clean-context trap case with no expected findings, then run corpus validation

## 6. Add Go and CI/IaC cases

- [x] 6.1 Add the idiomatic Go runtime-safety case covering security, correctness, tests, and spec, then run corpus validation
- [x] 6.2 Add the idiomatic Go efficiency-design case covering performance, complexity, and ponytail, then run corpus validation
- [x] 6.3 Add the idiomatic Go contract-evolution case covering documentation, deprecation, and intent, then run corpus validation
- [x] 6.4 Add the Go clean-context trap case with no expected findings, then run corpus validation
- [x] 6.5 Add one defect-bearing GitHub Actions case and validate its diff-visible ground truth
- [x] 6.6 Add one clean GitHub Actions trap case and validate that its expected list is empty
- [x] 6.7 Add one defect-bearing Terraform case and validate its diff-visible ground truth
- [x] 6.8 Add one clean Terraform trap case and run the complete v2 matrix validator successfully

## 7. Preserve complete evidence

- [x] 7.1 Add failing runner tests for complete final finding fields, stable observation/finding IDs, resolved provenance, and checkpoint-to-final identity
- [x] 7.2 Extend raw observation retention minimally until the complete-evidence runner tests pass
- [x] 7.3 Add failing tests for complete, interrupted, malformed, unavailable, and unsupported upstream audit JSONL
- [x] 7.4 Invoke compatible lgtmaybe versions with one explicit audit path per observation and retain immutable standard-library-gzipped trace artifacts with hashes
- [x] 7.5 Add failing tests for append-only adjudication events, supersession, invalid identities, and deterministic current-state reconstruction
- [x] 7.6 Parse current and legacy lgtmaybe profile rows and retain token and truncation diagnostics
- [x] 7.7 Implement adjudication loading and validation separately from immutable raw and audit files

## 8. Score balanced quality and false positives

- [x] 8.1 Add failing scoring tests for 70-cell balanced recall and pooled adjudicated precision across uneven language results
- [x] 8.2 Add failing scoring tests for forbidden, clean-case, unexpected-near, duplicate, unadjudicated, and later-adjudicated findings
- [x] 8.3 Implement false-positive classification, adjudication coverage, provisional status, clean-pass rate, and balanced F1 in the existing scoring module
- [x] 8.4 Add failing aggregation tests for three-repeat medians/ranges and one-repeat diagnostic summaries
- [x] 8.5 Implement repeat aggregation while preserving provider-aware timing and token diagnostics

## 9. Generate comparable reports and dashboard

- [x] 9.1 Add failing reporting tests that partition by suite, profile, and lgtmaybe version and select only the newest complete canonical key for README
- [x] 9.2 Update the shared report model and Markdown renderers with balanced F1, recall, precision, false positives, clean-pass, adjudication, and audit columns
- [x] 9.3 Add failing determinism tests for detailed dashboard data containing legacy, focused, diagnostic, incomplete, and canonical runs
- [x] 9.4 Generate deterministic dashboard data and a dependency-free static sortable/filterable page from the shared scored model
- [x] 9.5 Add an accessibility and behavior test for keyboard-usable table headers, labels, empty filters, numeric sorting, and a no-JavaScript fallback link to `RESULTS.md`
- [x] 9.6 Regenerate `README.md`, `RESULTS.md`, and dashboard artifacts through `bench report` without hand-editing generated sections

## 10. Verify the external workflow

- [x] 10.1 Extend the fake-lgtmaybe acceptance executable to emit complete findings, a completed audit trace, an interrupted partial trace, and a truncation
- [x] 10.2 Run the end-to-end canonical fixture and verify raw, audit, adjudication, score, Markdown, and dashboard links from the external CLI boundary
- [x] 10.3 Update README guidance for canonical defaults, diagnostic profiles, comparison keys, score interpretation, false positives, audit retention, and dashboard use
- [x] 10.4 Run `uv sync --python 3.12`, pytest, ruff, mypy, corpus validation, report determinism, and the fake-CLI end-to-end benchmark; mark each task complete only after its check passes
- [x] 10.5 Reject an invalid v2 coverage matrix before invoking lgtmaybe
