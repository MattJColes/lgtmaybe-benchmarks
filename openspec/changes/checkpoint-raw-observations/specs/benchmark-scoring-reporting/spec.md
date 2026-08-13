## MODIFIED Requirements

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files, rescore them, and regenerate `RESULTS.md` byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. Rows SHALL be newest first and include full comparison configuration, score, recall, precision, clean status, truncation data, both wall-time measures, and per-lens recall.

Raw records marked `in_progress` SHALL be excluded from the leaderboard, per-lens recall, and every aggregate metric. They SHALL be listed separately as incomplete runs with their configuration and recorded observation count. Records without a `status` field SHALL be scored as complete.

#### Scenario: Regenerate unchanged reports
- **WHEN** `bench report` runs twice without raw-data changes
- **THEN** the second run leaves `RESULTS.md` and the generated README section byte-for-byte unchanged

#### Scenario: Complete a benchmark run
- **WHEN** `bench run` stores a new raw result successfully
- **THEN** the README leaderboard and score table update through the same report renderer used by `bench report`

#### Scenario: Report an interrupted run
- **WHEN** a raw record is marked in progress
- **THEN** it adds no leaderboard or per-lens row and is named under incomplete runs instead
