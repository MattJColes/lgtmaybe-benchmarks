## Why

The strict false-positive score currently applies a variable penalty through precision, so the cost of one false positive changes with the number of planted findings caught. A fixed two percentage-point deduction is easier to understand and compare while retaining the strict false-positive count.

## What Changes

- **BREAKING** Replace the variable precision-derived score penalty with a fixed two percentage-point deduction per false positive.
- Calculate the base score at perfect precision, then clamp the penalized score to a minimum of zero.
- Retain precision and false-positive counts as diagnostic metrics.
- Recalculate every historical score and document the fixed formula for humans and coding agents.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Apply a fixed false-positive deduction to overall score with a zero floor.

## Impact

Scoring, aggregation, tests, generated README and RESULTS rows, and scoring documentation change. Raw observations, false-positive classification, and corpus truth remain unchanged.
