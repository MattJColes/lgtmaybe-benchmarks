## ADDED Requirements

### Requirement: Review-call completeness
Completeness SHALL count only attempted finding-producing review calls. Successful reflection, triage, and repair stages with no finding count SHALL NOT lower completeness. Stage failures SHALL be reported separately. Historical raw results SHALL be rescored without mutation.

#### Scenario: Successful reflection
- **WHEN** every review lens succeeds and a successful reflection stage reports no finding count
- **THEN** review-call completeness is 100 percent and the reflection stage is not labelled failed

#### Scenario: Failed review lens
- **WHEN** a review lens fails to return parseable findings
- **THEN** completeness falls while successful non-finding stages do not alter the denominator

### Requirement: Separate validated ranking
The current canonical README ranking SHALL use complete `breadth-validated` runs only. Historical `breadth` runs SHALL remain visible in detailed outputs with recalculated scores and an explicit correction note; no raw files SHALL change.

#### Scenario: No paid validated runs yet
- **WHEN** the validated suite has no complete canonical runs
- **THEN** the README states that no validated result is published and does not present a historical breadth run as its leader

### Requirement: Separate long-horizon history
The validated long-horizon suite SHALL be reported separately from the historical `long-horizon` suite, whose numeric threshold drift invalidates its clean case.

#### Scenario: Historical large-diff run
- **WHEN** a stored raw result names `long-horizon`
- **THEN** its score remains visible as archival evidence and is never ranked with `long-horizon-validated`
