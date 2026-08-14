# benchmark-corpus Specification

## Purpose
TBD - created by archiving change build-lgtmaybe-bench. Update Purpose after archive.
## Requirements
### Requirement: Stable self-contained benchmark cases
The corpus SHALL store each case under `corpus/<case-name>/` with `case.json`, a clean `base/` tree, and a changed `changed/` tree. `case.json` SHALL identify the case, language or cross-cutting technology, cleanliness, default changed file, expected findings, forbidden findings, target lens, catalogued line, matching keywords, and any minimum severity. Entries MAY override the default file for multi-file cases.

#### Scenario: Load a valid case
- **WHEN** the runner loads a case whose metadata and source trees satisfy the schema
- **THEN** it can construct the clean and changed revisions without external case data

#### Scenario: Reject invalid ground truth
- **WHEN** a case references a missing file, an invalid lens, an unknown language, an out-of-range line, or an empty keyword set
- **THEN** corpus validation fails before any model call is made

### Requirement: Versioned suite membership
The corpus SHALL define named suite manifests containing an ordered set of immutable case versions. Every case in a non-legacy suite SHALL declare its programming language or cross-cutting technology, and a suite ID SHALL identify one fixed membership set.

#### Scenario: Load a named suite
- **WHEN** the runner selects a known suite ID
- **THEN** it loads exactly the ordered case versions declared by that suite

#### Scenario: Change suite membership
- **WHEN** a maintainer adds, removes, or replaces a case in a published suite
- **THEN** the maintainer creates a new suite ID rather than changing the published manifest

### Requirement: Explicitly clean cases
A case MAY declare itself clean with no expected findings. A clean case SHALL contain a valid base and changed revision, SHALL identify its language or technology, and SHALL document the plausible review trap it is intended to test.

#### Scenario: Validate a clean case
- **WHEN** corpus validation loads a case declared clean
- **THEN** it accepts an empty expected list and rejects any contradictory expected finding

#### Scenario: Model flags a clean change
- **WHEN** lgtmaybe returns a final finding for a clean case
- **THEN** the finding is eligible for clean-case false-positive scoring

### Requirement: Complete lens coverage
The `v2` suite SHALL contain Python, TypeScript, JavaScript, Rust, Dart, Java, and Go. For each language it SHALL contain exactly one primary expected finding for every one of `security`, `correctness`, `performance`, `complexity`, `tests`, `documentation`, `deprecation`, `intent`, `ponytail`, and `spec`, distributed across three defect-bearing cases, plus one clean case. It SHALL also contain four GitHub Actions or Terraform cases split between defect-bearing and clean changes, and SHALL include single-file, multi-file, spec-alignment, test-quality, and documented large-diff coverage.

#### Scenario: Validate v2 matrix coverage
- **WHEN** the `v2` suite is validated
- **THEN** all 70 language/lens cells have exactly one primary target, all seven languages have a clean case, and all required cross-cutting and size classes are represented

#### Scenario: Detect accidental weighting
- **WHEN** a case addition would give one language/lens cell a second primary target without a new suite ID
- **THEN** corpus validation fails before any model call is made

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
