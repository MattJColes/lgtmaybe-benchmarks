## ADDED Requirements

### Requirement: Consistent corrected model identity
When a published run's requested model alias is corrected to its exact resolved model, the raw configuration, raw filename, run ID, observation IDs, finding IDs, generated model labels, and generated raw links SHALL use the corrected identity consistently. The correction SHALL NOT change observations, findings, scoring, token counts, timings, diagnostics, or eligibility.

#### Scenario: Correct a historical model alias
- **WHEN** a maintainer replaces a historical requested alias with the exact resolved model
- **THEN** regenerated reports contain only the exact identity and retain byte-equivalent measurement evidence after identity fields are normalised

#### Scenario: Regenerate corrected links
- **WHEN** the corrected raw filename changes
- **THEN** `RESULTS.md` and dashboard data link to the corrected path and no generated artifact references the obsolete path
