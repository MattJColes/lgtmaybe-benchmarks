## MODIFIED Requirements

### Requirement: Raw observation retention
The runner SHALL write one uniquely named JSON file under `results/raw/` for each configuration run. It SHALL retain each observation's complete final finding objects, raw stdout and stderr, process wall time, parsed provider-call timings, token counts, per-call parsed finding counts when reported, truncation errors, exit status, trace reference and completion state, and a snapshot of case ground truth. Checkpointed observations and final raw documents SHALL preserve stable observation and finding IDs. The profile parser MUST accept both legacy call tables and current tables with reasoning-share and finding-count columns.

The profile parser SHALL retain a call row whose provider reported no value for a numeric column, treating that count as unreported and contributing zero to the observation's totals. It SHALL still distinguish a reported zero finding count from an unreported one, and it SHALL still skip lines that are not call rows.

The runner SHALL reserve that file path before the first case runs and rewrite it atomically after every completed observation, recording a `status` of `in_progress` until the run reaches a terminal state. A finished run SHALL be recorded as `complete` and a canonical run abandoned at its first failed observation SHALL be recorded as `ineligible`. A record without a `status` field SHALL be treated as complete. Already recorded observations MUST NOT be altered or removed by a later write, and credentials MUST remain excluded from every write.

Every observation SHALL record a failure classification of `timeout`, `truncated_output`, `unparseable_output`, or `nonzero_exit` when it failed, and no classification when it did not. A truncated provider call that still exits zero SHALL NOT be classified as a failure.

#### Scenario: Preserve a successful run
- **WHEN** all selected cases complete
- **THEN** a raw file exists before generated artifacts are updated, is marked complete, and contains every repeat and case observation

#### Scenario: Preserve a truncated lens
- **WHEN** lgtmaybe reports a truncated provider call but returns partial findings
- **THEN** the observation remains scoreable, carries no failure classification, and retains the truncation lens, elapsed time, complete partial findings, and available audit events

#### Scenario: Preserve final finding detail
- **WHEN** lgtmaybe emits fields such as category, failure scenario, suggestion, confidence, broad status, or anchoring metadata
- **THEN** the raw observation stores those fields without reducing the finding to title, body, file, line, and severity

#### Scenario: Parse a current profile table
- **WHEN** lgtmaybe emits call rows containing `think_%` and `findings`
- **THEN** the raw observation retains each call and distinguishes zero findings from an unreported finding count

#### Scenario: Parse a legacy profile table
- **WHEN** stored output contains the earlier call columns without `think_%` or `findings`
- **THEN** the raw observation retains the call with no reported finding count

#### Scenario: Retain a call with no reported reasoning count
- **WHEN** a successful call row renders its reasoning count as `-`
- **THEN** the call is retained, its reasoning count contributes zero, and its other counts still reach the observation totals

#### Scenario: Retain a failed call with no reported counts
- **WHEN** a call row fails with a truncation, wall-timeout, or rate-limit error and reports no counts
- **THEN** the call is retained with its error text and elapsed time, and a truncation error still marks it truncated and adds its lens

#### Scenario: Skip a profile summary line
- **WHEN** a non-call line in the profile output splits into as many fields as the call table has columns
- **THEN** it is skipped rather than stored as a call

#### Scenario: Late case failure
- **WHEN** repository construction or another local boundary fails after earlier observations completed
- **THEN** the run still fails loudly and the reserved raw file retains every completed observation marked in progress

#### Scenario: Classify an unparseable observation
- **WHEN** lgtmaybe exits non-zero and its stdout cannot be parsed as review output
- **THEN** the stored observation is classified `unparseable_output` and retains its raw stdout and stderr
