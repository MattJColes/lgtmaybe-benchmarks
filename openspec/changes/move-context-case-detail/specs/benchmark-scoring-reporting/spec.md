## MODIFIED Requirements

### Requirement: Context scaling report section
Generated reports SHALL include context model summaries for complete, un-failed runs of suite `context-v1` with profile `context-canonical-v1`. The README generated section SHALL render only a score-ranked model summary with overall score, recall, precision, true-positive count, and false-positive count; it SHALL NOT render per-case rows. Dashboard data SHALL preserve per-case recall, precision, findings count, input and output tokens, truncation indicator, and wall time. `RESULTS.md` and the static HTML dashboard SHALL render that case detail so recall degradation remains explorable outside the README. Dashboard data and `RESULTS.md` SHALL preserve computed true-positive and false-positive totals rather than representing them as missing. All outputs SHALL be regenerated deterministically from stored raw results, SHALL exclude focused, failed, incomplete, and non-context runs from published context comparison tables, and SHALL NOT alter the `v2` leaderboard or legacy sections.

#### Scenario: Render a compact README summary
- **WHEN** complete `context-v1` canonical runs exist
- **THEN** the generated README contains one score-ranked summary row per model and no context case-detail table

#### Scenario: Render detailed context cases
- **WHEN** complete `context-v1` canonical runs exist
- **THEN** `RESULTS.md` and the static HTML dashboard contain one row per model and case with recall, precision, findings, tokens, truncation, and wall time

#### Scenario: Preserve dashboard case data
- **WHEN** dashboard data is generated for a complete canonical context run
- **THEN** its run record contains deterministic case metrics and computed true-positive and false-positive totals

#### Scenario: Exclude ineligible runs
- **WHEN** a context run is focused, diagnostic, incomplete, or contains observation failures
- **THEN** it remains stored and explorable but does not appear in the published context comparison tables

#### Scenario: Regenerate deterministically
- **WHEN** `bench report` runs twice with unchanged evidence
- **THEN** README, detailed Markdown, dashboard data, and dashboard HTML are byte-for-byte unchanged
