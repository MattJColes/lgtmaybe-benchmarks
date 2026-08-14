## ADDED Requirements

### Requirement: Context scaling suite
The corpus SHALL provide a `context-v1` suite of Python cases whose changed diffs grow across four size bands targeting approximately 3%, 15%, 45%, and 90% of the canonical input-token cap, plus one clean case at the large band. Every defect-bearing case SHALL plant the same number of expected findings (eight) at controlled relative positions through the changed-file ordering, and every case SHALL carry the `context-scaling` coverage tag. The cases SHALL be generated once by a deterministic, seed-fixed, standard-library-only script stored in the repository, and SHALL be immutable corpus artefacts afterwards like every published case.

#### Scenario: Load the context suite
- **WHEN** the runner selects suite `context-v1`
- **THEN** it loads exactly the five declared cases and validates them with the same case schema as `v2`, without applying `v2` matrix validation

#### Scenario: Regenerate a case deterministically
- **WHEN** the generator script runs twice with the same seed and no case yet has a stored result
- **THEN** it produces byte-identical case directories and suite manifest

#### Scenario: Compare recall across bands
- **WHEN** a reviewer reads context-scaling results for one model
- **THEN** each defect-bearing case contributes recall over exactly eight planted findings at the same relative positions, making the bands directly comparable

#### Scenario: Correct a published context case
- **WHEN** a context case needs fixing after a raw result references it
- **THEN** the correction ships as a new versioned case name in a new suite manifest, leaving the published case unchanged
