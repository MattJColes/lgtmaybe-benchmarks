## ADDED Requirements

### Requirement: Context scaling report section
Generated reports SHALL include a context-scaling section for complete, un-failed runs of suite `context-v1` with profile `context-canonical-v1`. The section SHALL render one row per model and case with recall, precision, findings count, input and output tokens, truncation indicator, and wall time, so recall degradation is visible reading down the size bands within a model. The section SHALL be regenerated deterministically from stored raw results, SHALL exclude focused, failed, incomplete, and non-context runs, and SHALL NOT alter the `v2` leaderboard or legacy sections.

#### Scenario: Render context results
- **WHEN** complete `context-v1` canonical runs exist
- **THEN** the generated results document contains the context-scaling section with one row per model and case including recall, precision, tokens, truncation, and wall time

#### Scenario: Exclude ineligible runs
- **WHEN** a context run is focused, diagnostic, incomplete, or contains observation failures
- **THEN** it remains stored and explorable but does not appear in the context-scaling section

#### Scenario: Regenerate deterministically
- **WHEN** `bench report` runs twice with unchanged evidence
- **THEN** the context-scaling section is byte-for-byte unchanged
