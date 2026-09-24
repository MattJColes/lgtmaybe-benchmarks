## ADDED Requirements

### Requirement: Validated breadth cases
The `breadth-validated` suite SHALL have one independently adjudicable expected defect per language and review category across Python, TypeScript, JavaScript, Rust, Dart, Java, and Go. It SHALL have one verified-clean case per language and the GitHub Actions and Terraform cross-cutting cases. Both base and changed revisions SHALL parse or build using their language's normal tooling, and fixture tests SHALL be runnable without external services.

#### Scenario: Validate independent defects
- **WHEN** the validated suite is checked
- **THEN** all 70 language/category cells exist and an exemplar finding for one expected entry does not match another expected entry in that case

#### Scenario: Validate runnable revisions
- **WHEN** each case's base and changed revisions are checked in isolation
- **THEN** both pass syntax or build validation, the intended weak tests pass, and targeted stronger checks expose planted behavioural defects

### Requirement: Historical corpus preservation
The published `breadth` and `long-horizon` manifests and every case already referenced by a raw result SHALL remain unchanged. Validated suites SHALL have distinct identifiers and SHALL NOT alias historical suite identifiers.

#### Scenario: Load historical evidence
- **WHEN** a stored raw result names `breadth`
- **THEN** it retains that suite identity and is never scored as a `breadth-validated` result

### Requirement: Validated long-horizon cases
The `long-horizon-validated` suite SHALL preserve five Python cases with increasing diff size across four defect cases and one clean case. Unplanted functions SHALL preserve their numeric constants across base and changed revisions. Each defect case SHALL retain eight planted targets.

#### Scenario: Check large-diff fixtures
- **WHEN** the validated long-horizon suite is checked
- **THEN** all Python files parse, the four defect cases grow in size, the clean case has no expected findings, and no unplanted function changes a numeric constant
