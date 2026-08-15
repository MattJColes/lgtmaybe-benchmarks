## MODIFIED Requirements

### Requirement: Context scaling report section
Generated reports SHALL include a context-scaling section for complete, un-failed runs of suite `context-v1` with profile `context-canonical-v1`. The section SHALL render a model summary with overall score, recall, precision, true-positive count, and false-positive count, followed by one row per model and case with recall, precision, findings count, input and output tokens, truncation indicator, and wall time, so both the aggregate outcome and recall degradation are visible. Dashboard data and `RESULTS.md` SHALL preserve the same computed true-positive and false-positive totals rather than representing them as missing. The section SHALL be regenerated deterministically from stored raw results, SHALL exclude focused, failed, incomplete, and non-context runs, and SHALL NOT alter the `v2` leaderboard or legacy sections.

#### Scenario: Render context model summaries
- **WHEN** complete `context-v1` canonical runs exist
- **THEN** the generated README and results document contain one summary row per model with overall score, recall, precision, true positives, and false positives

#### Scenario: Render context case results
- **WHEN** complete `context-v1` canonical runs exist
- **THEN** the generated results document contains one row per model and case including recall, precision, tokens, truncation, and wall time

#### Scenario: Preserve dashboard finding totals
- **WHEN** dashboard data is generated for a complete context run
- **THEN** its metrics contain the computed true-positive and false-positive totals

#### Scenario: Exclude ineligible runs
- **WHEN** a context run is focused, diagnostic, incomplete, or contains observation failures
- **THEN** it remains stored and explorable but does not appear in the context-scaling section

#### Scenario: Regenerate deterministically
- **WHEN** `bench report` runs twice with unchanged evidence
- **THEN** the context-scaling section is byte-for-byte unchanged
