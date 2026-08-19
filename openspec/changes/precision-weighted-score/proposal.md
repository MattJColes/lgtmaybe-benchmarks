## Why

The long-horizon overall score deducts a fixed percentage per false positive. The deduction is an unbounded absolute count set against a normalised recall base, so the marginal cost of a false positive is arbitrary relative to the value of a caught finding, and enough noise floors any run at 0% regardless of recall. The breadth suite meanwhile scores balanced F1, which weights precision and recall equally. Both suites should encourage recall and precision together through one scale-free formula that still says noise hurts more than misses.

## What Changes

- **BREAKING** Replace the long-horizon fixed-deduction score with F0.5: `1.25 × precision × recall / (0.25 × precision + recall)`, weighting precision twice as heavily as recall, zero only when the denominator is zero.
- **BREAKING** Align the breadth suite to the same weighting: balanced F1 becomes balanced F0.5 over the same balanced recall, pooled precision, and median-across-repeats aggregation.
- Share one scoring function between the suites; recalculate every historical score from unchanged raw observations and update the documentation for humans and coding agents.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: Score both suites with precision-weighted F0.5.

## Impact

The shared score function, penalty tests, breadth expected values, generated README and RESULTS rows, dashboard labels, and scoring documentation change. Raw observations, false-positive classification, recall, precision, balanced recall, and corpus truth remain unchanged. The suites still measure orthogonal properties and are never ranked against each other; they now share a formula family, not a leaderboard.
