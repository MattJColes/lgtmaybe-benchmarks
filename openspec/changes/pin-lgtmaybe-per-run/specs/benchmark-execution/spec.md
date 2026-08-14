## ADDED Requirements

### Requirement: Consistent lgtmaybe release
A benchmark configuration run SHALL resolve one concrete lgtmaybe release before its first observation and SHALL use that release for every observation. The runner MUST fail loudly if the executable reports a different release during the run, while retaining completed observations in an `in_progress` checkpoint.

#### Scenario: Latest release changes during a run
- **WHEN** a newer lgtmaybe release becomes available after the benchmark has resolved its command
- **THEN** every observation continues to use the originally resolved release

#### Scenario: Executable reports a different release
- **WHEN** a later observation reports a version different from the run's recorded lgtmaybe version
- **THEN** the run fails before that observation and retains earlier observations in an `in_progress` checkpoint
