## ADDED Requirements

### Requirement: Immutable candidate audit artifacts
The benchmark SHALL retain every available upstream audit event for an observation in an immutable compressed JSONL artifact. The artifact SHALL preserve schema version, run and call provenance, raw redacted model responses, complete parsed candidates, lifecycle decisions and reasons, reflection and retrieval outcomes, provider usage, and errors. Raw configuration SHALL link the artifact by stable identity and integrity hash.

#### Scenario: Retain candidates removed by reflection
- **WHEN** lgtmaybe emits candidates that reflection later drops
- **THEN** the audit artifact preserves the candidates, reflection verdicts, and drop decisions even though they are absent from final findings

#### Scenario: Retain a provider failure prefix
- **WHEN** a provider call fails after earlier events were emitted
- **THEN** the benchmark preserves the valid event prefix and marks the trace incomplete or failed

### Requirement: Append-only adjudication history
Human or corrected classifications SHALL be stored separately from raw and audit evidence as append-only events. Each event SHALL identify the suite, run, observation, repeat, candidate or final finding, classification, reason, adjudicator, timestamp, and any superseded adjudication. Valid classifications SHALL include true positive, false positive, duplicate, invalid case evidence, and unadjudicated.

#### Scenario: Refine an earlier judgment
- **WHEN** a maintainer changes a candidate's classification
- **THEN** a new event supersedes the earlier event and both remain available in history

#### Scenario: Rebuild current adjudication state
- **WHEN** reports are regenerated
- **THEN** the latest valid event for each evidence identity determines its current classification

### Requirement: Evidence safety and reproducibility
Audit storage MUST NOT contain provider credentials, request headers, unrelated environment variables, or unredacted secrets. The benchmark SHALL retain enough version, profile, case, lens, and hash provenance to reconstruct standard prompts, and SHALL retain explicit custom lens text only when it cannot be reconstructed from versioned inputs.

#### Scenario: Inspect stored evidence
- **WHEN** a maintainer opens raw, audit, or adjudication artifacts
- **THEN** the artifacts contain review evidence and provenance but no credential or unrelated environment data

#### Scenario: Compare a later lens revision
- **WHEN** candidate behavior changes after a lens or prompt revision
- **THEN** stored provenance distinguishes the revisions and links their candidates without mutating earlier evidence
