## MODIFIED Requirements

### Requirement: Raw observation retention
The runner SHALL write one uniquely named JSON file under `results/raw/` for each configuration run. It SHALL retain each observation's complete final finding objects, raw stdout and stderr, process wall time, parsed provider-call timings, token counts, per-call parsed finding counts when reported, truncation errors, exit status, trace reference and completion state, and a snapshot of case ground truth. Checkpointed observations and final raw documents SHALL preserve stable observation and finding IDs. The profile parser MUST accept both legacy call tables and current tables with reasoning-share and finding-count columns.

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

#### Scenario: Late case failure
- **WHEN** repository construction or another local boundary fails after earlier observations completed
- **THEN** the run still fails loudly and the reserved raw file retains every completed observation marked in progress

#### Scenario: Classify an unparseable observation
- **WHEN** lgtmaybe exits non-zero and its stdout cannot be parsed as review output
- **THEN** the stored observation is classified `unparseable_output` and retains its raw stdout and stderr

## ADDED Requirements

### Requirement: Canonical runs stop at the first failed observation
A canonical full-corpus run SHALL stop before starting another observation once an observation exits non-zero or times out, because such a run can no longer produce a scoreable result. The failed observation SHALL be checkpointed atomically before the run stops, the run SHALL end with terminal status `ineligible`, and the run SHALL exit non-zero with a concise message rather than reporting success.

The terminal record SHALL carry a structured termination reason naming the repeat, case, observation ID, exit code, whether the observation timed out, and the failure classification. Focused runs and runs resolved to a diagnostic profile SHALL continue through failures so that investigation still collects every observation.

#### Scenario: Abandon a canonical run at its first failure
- **WHEN** an observation of a canonical full-corpus run times out or exits non-zero
- **THEN** no further case or repeat is invoked, the reserved raw file retains that observation with terminal status `ineligible`, and the command exits non-zero

#### Scenario: Record why a canonical run stopped
- **WHEN** a canonical full-corpus run ends as ineligible
- **THEN** the raw record names the repeat, case, observation ID, exit code, timeout flag, and failure classification of the observation that stopped it

#### Scenario: Keep investigating a focused failure
- **WHEN** a focused or diagnostic run observes a failure
- **THEN** the remaining cases and repeats still run and the finished record is marked complete
