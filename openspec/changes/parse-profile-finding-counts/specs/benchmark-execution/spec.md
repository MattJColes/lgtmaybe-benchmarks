## MODIFIED Requirements

### Requirement: Raw diagnostic evidence
The runner SHALL write one uniquely named JSON file under `results/raw/` for each configuration run. It SHALL retain each observation's findings, raw stdout and stderr, process wall time, parsed provider-call timings, token counts, per-call parsed finding counts when reported, truncation errors, exit status, and a snapshot of case ground truth. The profile parser MUST accept both legacy call tables and current tables with reasoning-share and finding-count columns.

#### Scenario: Parse a current profile table
- **WHEN** lgtmaybe emits call rows containing `think_%` and `findings`
- **THEN** the raw observation retains each call and distinguishes zero findings from an unreported finding count

#### Scenario: Parse a legacy profile table
- **WHEN** stored output contains the earlier call columns without `think_%` or `findings`
- **THEN** the raw observation retains the call with no reported finding count

#### Scenario: Interrupt a run
- **WHEN** a run is interrupted after one or more observations finish
- **THEN** the same reserved raw file contains those completed observations with `status: in_progress`

#### Scenario: Finish a run
- **WHEN** every selected case and repeat completes
- **THEN** the reserved raw file is atomically replaced with `status: complete` and its final summary

#### Scenario: Provider response truncates
- **WHEN** lgtmaybe reports a truncated provider call but returns partial findings
- **THEN** raw evidence retains both the partial findings and the truncation marker

#### Scenario: Provider response fails
- **WHEN** lgtmaybe exits non-zero for an observation
- **THEN** raw evidence retains stdout, stderr, exit status, and the failed observation without treating it as a clean review
