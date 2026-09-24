## 1. Scoring correction

- [x] 1.1 Add failing tests for successful non-finding stages and failed review lenses; verify they fail before the fix.
- [x] 1.2 Correct completeness and stage-failure reporting; verify scoring tests pass.
- [x] 1.3 Regenerate historical reports and verify raw results are unchanged and recalculated scores are labelled.

## 2. Runnable breadth corpus

- [x] 2.1 Add versioned Python, TypeScript, and JavaScript cases with distinct targets; verify both revisions parse or build and the matrix is complete for these languages.
- [x] 2.2 Add versioned Rust and Dart cases with distinct targets; verify both revisions parse or build and weak tests run.
- [x] 2.3 Add versioned Java and Go cases with distinct targets; verify both revisions compile and weak tests run.
- [x] 2.4 Add valid versioned Terraform cases and review Actions cases; verify syntax and intended security/clean outcomes.
- [x] 2.5 Add `breadth-validated` manifest and exemplar collision checks; verify 70 independent cells, nine clean cases, and immutable historical files.

## 3. Diagnostic review options

- [x] 3.1 Add CLI/profile support for paired diagnostic feature switches and triage model; verify commands and raw settings with fake CLI tests.
- [x] 3.2 Add small retrieval and triage probes plus paired comparison output; verify differences report recall, noise, completeness, tokens, time, and available cost without canonical ranking.

## 4. Rollout and verification

- [x] 4.1 Set validated breadth as the default and keep historical breadth separate in generated reports; verify no validated leader is shown without a complete run.
- [x] 4.2 Audit all long-horizon Python cases for syntax, intended planted findings, and size order; verify the five-case suite is unchanged unless versioned replacements are necessary.
- [x] 4.3 Run fixture checks, full pytest, Ruff, mypy, strict OpenSpec validation, report determinism, and focused external CLI smoke tests; record no paid runs and no raw-result edits.
