## MODIFIED Requirements

### Requirement: Raw observation retention
The runner SHALL write one uniquely named JSON file under `results/raw/` for each configuration run. It SHALL retain each observation's complete final finding objects, raw stdout and stderr, process wall time, parsed provider-call timings, token counts, per-call parsed finding counts when reported, truncation errors, exit status, trace reference and completion state, and a snapshot of case ground truth. Checkpointed observations and final raw documents SHALL preserve stable observation and finding IDs. The profile parser MUST accept both legacy call tables and current tables with reasoning-share and finding-count columns.

#### Scenario: Preserve a successful run
- **WHEN** all selected cases complete
- **THEN** a raw file exists before generated artifacts are updated and contains every repeat and case observation

#### Scenario: Preserve a truncated lens
- **WHEN** lgtmaybe reports a truncated provider call but returns partial findings
- **THEN** the observation remains scoreable and retains the truncation lens, elapsed time, complete partial findings, and available audit events

#### Scenario: Preserve final finding detail
- **WHEN** lgtmaybe emits fields such as category, failure scenario, suggestion, confidence, broad status, or anchoring metadata
- **THEN** the raw observation stores those fields without reducing the finding to title, body, file, line, and severity

#### Scenario: Parse a current profile table
- **WHEN** lgtmaybe emits call rows containing `think_%` and `findings`
- **THEN** the raw observation retains each call and distinguishes zero findings from an unreported finding count

#### Scenario: Parse a legacy profile table
- **WHEN** stored output contains the earlier call columns without `think_%` or `findings`
- **THEN** the raw observation retains the call with no reported finding count
