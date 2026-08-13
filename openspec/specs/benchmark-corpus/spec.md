# benchmark-corpus Specification

## Purpose
TBD - created by archiving change build-lgtmaybe-bench. Update Purpose after archive.
## Requirements
### Requirement: Stable self-contained benchmark cases
The corpus SHALL store each case under `corpus/<case-name>/` with `case.json`, a clean `base/` tree, and a planted-bug `changed/` tree. `case.json` SHALL identify the case, default changed file, expected findings, forbidden findings, target lens, catalogued line, matching keywords, and any minimum severity. Entries MAY override the default file for multi-file cases.

#### Scenario: Load a valid case
- **WHEN** the runner loads a case whose metadata and source trees satisfy the schema
- **THEN** it can construct the clean and changed revisions without external case data

#### Scenario: Reject invalid ground truth
- **WHEN** a case references a missing file, an invalid lens, an out-of-range line, or an empty keyword set
- **THEN** corpus validation fails before any model call is made

### Requirement: Complete lens coverage
The published corpus SHALL contain at least two expected findings for each of `security`, `correctness`, `performance`, `complexity`, `tests`, `documentation`, `deprecation`, `intent`, `ponytail`, and `spec`. It SHALL include both single-file and multi-file cases, including input large enough to exercise lgtmaybe batching at a documented token budget.

#### Scenario: Validate corpus coverage
- **WHEN** the full corpus is validated
- **THEN** every required lens has at least two expected findings and both size classes are represented

### Requirement: Adjudicable and forbidden findings
Every expected finding SHALL be discoverable from the changed diff itself. Claims that require unavailable or deliberately unshown context SHALL be represented as forbidden findings instead of expected findings.

#### Scenario: Context-dependent plausible claim
- **WHEN** a changed line looks unsafe but the relevant guard exists outside the reviewed diff
- **THEN** the case catalogues that claim as forbidden and identifies the misleading line and keywords

### Requirement: Published case immutability
Once a case contributes to a stored result, its name and contents SHALL be treated as immutable. A correction SHALL be introduced under a new versioned case name.

#### Scenario: Correct a published case
- **WHEN** maintainers discover invalid ground truth in a case already referenced by raw results
- **THEN** they add a replacement such as `<case-name>-v2` rather than editing the original case
