## Context

See proposal.md. The scorer consumes immutable raw results. The runner invokes a released lgtmaybe CLI externally and creates two-commit temporary repositories. Published case directories cannot change.

## Goals / Non-Goals

**Goals:** Correct historical scoring; make the seven-language review matrix runnable and unambiguous; measure optional review settings as diagnostics.

**Non-Goals:** Host posting adapters, paid model runs, edits to raw evidence, new runtime dependencies, or merging the two suites' scores.

## Decisions

- Add `breadth-validated` with versioned replacement case directories. Keep the existing `breadth` ID for historical evidence and do not alias it to the new suite. Reuse the existing canonical profile settings because only case membership changes.
- The long-horizon audit found that random thresholds changed across revisions, including in its clean case. Add `long-horizon-validated` with versioned copies whose unplanted functions retain their numeric constants; keep the original suite and raw scores archival.
- Keep the 32-case matrix shape. Separate spec from correctness and documentation from intent by putting their evidence on different changed behavior; validate exemplars against the scorer. Add minimal fixture-local declarations and build metadata for each language.
- Define completeness over review labels (`security`, `correctness`, `code-health`, `artefacts`, focused lenses, `spec`). Count null findings with a call error as a failed review. Report other stage errors separately. Preserve the legacy stderr parser.
- Add CLI diagnostic switches that resolve to `diagnostic-custom-v1`, plus a triage-model field. Compare each option one at a time against the same suite and model; use small cross-file probes for retrieval and triage.
- Regenerate reports from raw results. Keep historical breadth in detailed outputs and show an explicit empty current leaderboard until an authorised canonical run exists.

## Risks / Trade-offs

- More realistic fixtures may reveal uncatalogued problems. Validate build and behaviour and review all changed lines before freezing a version.
- Product feature flags may change across releases. Record the lgtmaybe version and resolved settings; fail visibly if a requested option is unsupported.
- Historical score corrections change published percentages and ranks. Keep raw evidence and show the correction, with before/after checks in tests.
