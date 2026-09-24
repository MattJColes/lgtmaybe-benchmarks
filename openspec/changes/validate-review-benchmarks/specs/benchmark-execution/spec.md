## ADDED Requirements

### Requirement: Paired review-option diagnostics
The benchmark SHALL support diagnostic runs that change one of preset, reflection, recursion, static analysis, triage, or mid-review retrieval while retaining the same selected corpus, provider, primary model, and measurement fields. Every changed setting and triage model identity SHALL be stored; such runs SHALL never enter canonical rankings.

#### Scenario: Compare a review option
- **WHEN** a baseline and a single-option diagnostic run complete on the same cases
- **THEN** their recall, false positives, completeness, token use, wall time, and available cost can be compared without merging them into the canonical leaderboard

#### Scenario: Disable reflection
- **WHEN** a diagnostic run selects no reflection
- **THEN** the external review command receives the option and the raw configuration records it
