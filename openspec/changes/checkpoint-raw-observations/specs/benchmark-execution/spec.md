## MODIFIED Requirements

### Requirement: Raw observation retention
The runner SHALL write one uniquely named JSON file under `results/raw/` for each configuration run. It SHALL retain each observation's findings, raw stdout and stderr, process wall time, parsed provider-call timings, token counts, truncation errors, exit status, and a snapshot of case ground truth.

The runner SHALL reserve that file path before the first case runs and rewrite it atomically after every completed observation, recording a `status` of `in_progress` until the final repeat and case complete and `complete` afterwards. A record without a `status` field SHALL be treated as complete. Already recorded observations MUST NOT be altered or removed by a later write, and credentials MUST remain excluded from every write.

#### Scenario: Preserve a successful run
- **WHEN** all selected cases complete
- **THEN** a raw file exists before generated Markdown is updated, is marked complete, and contains every repeat and case observation

#### Scenario: Preserve a truncated lens
- **WHEN** lgtmaybe reports a truncated provider call but returns partial findings
- **THEN** the observation remains scoreable and retains the truncation lens, elapsed time, and partial findings

#### Scenario: Late case failure
- **WHEN** repository construction or another local boundary fails after earlier observations completed
- **THEN** the run still fails loudly and the reserved raw file retains every completed observation marked in progress
