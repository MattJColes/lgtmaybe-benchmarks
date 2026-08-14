## MODIFIED Requirements

### Requirement: Recall, precision, and score
Each repeat SHALL report caught and planted counts, overall and per-lens recall, false positives, forbidden hits, unexpected findings, adjudicable findings, precision, clean status, and score. False positives SHALL include every finding that does not match an uncaught expected planted entry, even when the finding may describe a genuine issue that is absent from the benchmark ground truth. Precision SHALL equal `caught / (caught + false positives)`, with precision defined as one when there are no returned findings, and SHALL remain a diagnostic metric.

The base score SHALL be the harmonic mean of recall and perfect precision. The final score SHALL deduct exactly `0.02` for each false positive and SHALL be clamped to a minimum of zero: `max(0, base score - 0.02 * false positives)`.

#### Scenario: Apply one fixed false-positive penalty
- **WHEN** two otherwise identical repeats differ by one false positive and neither score reaches the zero floor
- **THEN** the noisy repeat's score is exactly two percentage points lower

#### Scenario: Floor a noisy score at zero
- **WHEN** false-positive deductions exceed the base score
- **THEN** the final score is zero rather than negative

#### Scenario: Preserve diagnostic precision
- **WHEN** a repeat catches planted bugs and produces false positives
- **THEN** precision still describes the share of returned findings that matched planted findings while the fixed deduction determines overall score

#### Scenario: Plausible uncatalogued issue
- **WHEN** a finding may identify a real issue but does not match an uncaught planted entry
- **THEN** it still counts as a false positive and deducts two percentage points for that immutable benchmark run
