## Context

The Fable run was requested through an OpenRouter alias but resolved to Claude Fable 5. Its raw configuration, filename, stable IDs, and every generated report still expose the alias. Generated artifacts must continue to come exclusively from `results/raw/`.

## Goals / Non-Goals

**Goals:**

- Make `anthropic/claude-fable-5` the only Fable model identity in the repository.
- Keep the raw filename, run ID, observation IDs, and finding IDs referentially consistent.
- Preserve all measured output, scoring, timings, and diagnostics.
- Regenerate every report from the corrected raw source.

**Non-Goals:**

- Rerun the benchmark or alter any finding classification.
- Add alias-resolution logic to the harness.
- Change scoring, corpus cases, or comparison eligibility.

## Decisions

Rename the raw file and replace the old model slug in its configuration and stable identifiers. Keeping the old run ID or raw path would leave the obsolete alias visible and break the user's request for a repository-wide correction. Adding a separate resolved-model field would preserve two competing identities and require renderer changes for a one-off historical correction.

Regenerate README, RESULTS, and both dashboard artifacts with `bench report`; do not edit generated content directly. Update the historical context-suite task because it is the remaining hand-authored reference. Add a focused behavioural test that loads the corrected raw file and verifies its model, run, observation, finding, dashboard model, and dashboard path identities.

## Risks / Trade-offs

- [External links to the old raw filename stop resolving] → Land the corrected generated links atomically in the same commit.
- [A partial replacement leaves mixed identities] → Test every identifier layer and require repository-wide search to find no obsolete alias.
- [Measurements change accidentally] → Compare the pre/post raw document after normalising only the approved identity strings.
