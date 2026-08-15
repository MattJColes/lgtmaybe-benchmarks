## ADDED Requirements

### Requirement: Bounded README rankings
Every generated score-ranked table in the README SHALL order eligible rows by score descending and SHALL render no more than the ten highest-scoring rows. Equal scores SHALL use deterministic timestamp and run-identity tie-breakers. `RESULTS.md`, dashboard data, and the static HTML dashboard SHALL retain every stored eligible and diagnostic run without applying the README limit. The visible HTML results table SHALL show true positives alongside score, recall, precision, and false positives so every README summary metric remains visible for lower-ranked runs.

#### Scenario: More than ten eligible results
- **WHEN** a generated README ranking has eleven or more eligible results
- **THEN** it contains exactly the ten highest-scoring rows in descending order

#### Scenario: Ten or fewer eligible results
- **WHEN** a generated README ranking has ten or fewer eligible results
- **THEN** it contains every eligible row in descending score order

#### Scenario: Preserve detailed history
- **WHEN** README excludes lower-ranked rows because of the limit
- **THEN** those rows and their score, recall, precision, true-positive, and false-positive metrics remain visible in `RESULTS.md` and dashboard HTML and present in dashboard data

#### Scenario: Regenerate deterministically
- **WHEN** reports are regenerated twice from unchanged raw evidence
- **THEN** all generated outputs are byte-for-byte unchanged
