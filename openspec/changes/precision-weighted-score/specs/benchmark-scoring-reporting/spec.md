## MODIFIED Requirements

### Requirement: Recall, precision, and score
Each repeat SHALL report caught and planted counts, per-language, per-lens, and language/lens-cell recall, balanced recall, true positives, false positives by class, unadjudicated and duplicate findings, adjudication coverage, precision, clean-pass rate, and balanced F0.5. Balanced recall SHALL be the arithmetic mean of recall across the suite's 70 primary language/lens cells. Precision SHALL equal `true positives / (true positives + false positives)` for adjudicated final findings and SHALL be one when that denominator is zero.

The overall score for every suite SHALL be the F0.5 measure `1.25 × precision × recall / (0.25 × precision + recall)`, zero when the denominator is zero, weighting precision twice as heavily as recall through one shared score function. The breadth suite SHALL apply it to balanced recall and pooled precision as balanced F0.5; the long-horizon suite SHALL apply it to planted-finding recall and closed-world precision. A result with unresolved final findings SHALL be labelled provisional.

#### Scenario: Score balanced language coverage
- **WHEN** a model catches every Python target but misses targets in other languages
- **THEN** its balanced recall reflects all 70 language/lens cells rather than the raw Python finding count

#### Scenario: Score noisy findings
- **WHEN** a repeat catches planted bugs and emits forbidden, clean-case, unexpected-near, or adjudicated false-positive findings
- **THEN** its precision and balanced F0.5 are lower than balanced recall and its false-positive classes remain visible

#### Scenario: Weight precision above recall
- **WHEN** one run has precision one half and recall one, and another has precision one and recall one half
- **THEN** the more precise run scores higher

#### Scenario: Damp noise without a zero cliff
- **WHEN** heavy noise drives precision near zero while recall stays positive
- **THEN** the score approaches zero but remains positive

#### Scenario: Explain the overall percentage
- **WHEN** a report renders the headline percentage
- **THEN** it labels the value balanced F0.5 and exposes balanced recall, precision, adjudication coverage, and clean-pass rate beside it

### Requirement: Repeat aggregation
Configuration summaries SHALL aggregate balanced recall, precision, balanced F0.5, clean-pass rate, total wall time, and wall time excluding truncated calls as median with minimum and maximum. They SHALL include true-positive, false-positive, duplicate, unadjudicated, truncation, and lens counts plus input, output, and reasoning token totals when reported. A single repeat SHALL still render through the same aggregate format and SHALL remain diagnostic unless its profile defines one repeat as canonical.

#### Scenario: Three noisy repeats
- **WHEN** three repeats produce different recall, precision, false-positive, or timing values
- **THEN** the report shows metric medians and full minimum-to-maximum ranges plus the underlying counts
