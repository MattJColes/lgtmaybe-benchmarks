## Why

The fixed false-positive deduction is currently two percentage points per false positive. That penalty is judged too harsh relative to the value of each caught finding: a moderately noisy run can floor at 0% while still catching most planted findings. Halving the deduction to one percentage point keeps the fixed, predictable penalty while letting recall differences stay visible in the published score.

## What Changes

- **BREAKING** Reduce the fixed score deduction from two percentage points to one percentage point per false positive.
- Keep the base score at perfect precision and the zero floor unchanged.
- Recalculate every historical score from unchanged raw observations and update the scoring documentation for humans and coding agents.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Apply a one percentage-point false-positive deduction to overall score with a zero floor.

## Impact

The `FALSE_POSITIVE_PENALTY` constant, penalty tests, generated README and RESULTS rows, dashboard data, and scoring documentation change. Raw observations, false-positive classification, recall, precision, and corpus truth remain unchanged. Only the legacy-v1 / long-horizon score moves; the breadth suite's balanced F1 never applies this penalty.
