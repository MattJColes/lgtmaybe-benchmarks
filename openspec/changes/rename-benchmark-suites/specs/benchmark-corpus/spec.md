## MODIFIED Requirements

### Requirement: Versioned suite membership
The corpus SHALL define named suite manifests containing an ordered set of immutable case versions. A suite ID SHALL name the property the suite measures rather than a release sequence, and SHALL identify one fixed membership set. Every case in a non-legacy suite SHALL declare its programming language or cross-cutting technology. Renaming a suite manifest SHALL NOT rename or alter the case versions it lists.

#### Scenario: Load a named suite
- **WHEN** the runner selects a known suite ID
- **THEN** it loads exactly the ordered case versions declared by that suite

#### Scenario: Change suite membership
- **WHEN** a maintainer adds, removes, or replaces a case in a published suite
- **THEN** the maintainer creates a new suite ID rather than changing the published manifest

#### Scenario: Rename a published suite
- **WHEN** a published suite manifest is renamed
- **THEN** its ordered case membership and every case directory name are unchanged, and stored results referencing the superseded suite ID remain scoreable

### Requirement: Breadth matrix coverage
The `breadth` suite SHALL contain Python, TypeScript, JavaScript, Rust, Dart, Java, and Go. For each language it SHALL contain exactly one primary expected finding for every one of `security`, `correctness`, `performance`, `complexity`, `tests`, `documentation`, `deprecation`, `intent`, `ponytail`, and `spec`, distributed across three defect-bearing cases, plus one clean case. It SHALL also contain four GitHub Actions or Terraform cases split between defect-bearing and clean changes, and SHALL include single-file, multi-file, spec-alignment, test-quality, and documented large-diff coverage.

#### Scenario: Validate breadth matrix coverage
- **WHEN** the `breadth` suite is validated
- **THEN** validation confirms every language/lens cell has exactly one primary target and rejects the suite otherwise

#### Scenario: Reject accidental lens weighting
- **WHEN** a case addition would give one language/lens cell a second primary target without a new suite ID
- **THEN** validation rejects the change

### Requirement: Long-horizon suite membership
The `long-horizon` suite SHALL contain one language and SHALL vary diff size across its defect-bearing cases from a small fraction to near the canonical input-token ceiling. Each defect-bearing case SHALL plant the same number of findings at the same relative positions so that recall differences reflect diff size rather than defect selection, and the suite SHALL contain one clean case at a large size.

#### Scenario: Compare recall across diff sizes
- **WHEN** the `long-horizon` suite is scored
- **THEN** each defect-bearing case contributes an equal planted-finding count, so recall is comparable across sizes
