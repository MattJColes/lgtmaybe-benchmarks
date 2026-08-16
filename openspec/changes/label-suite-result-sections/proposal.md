## Why

Generated reports can render two result sections whose scores are produced by different formulas and must never be ranked against each other. Only one of them is labelled. The long-horizon section carries a heading and a blurb naming its suite and profile; the breadth section opens with a bare comparison-key line and a table, so the unlabelled table is the one a reader is least equipped to identify.

No breadth run is stored yet, so the defect is latent: the first stored breadth run would publish two adjacent tables that share a `precision` column, differ in score formula, and give the reader nothing that says so.

The hand-authored README paragraph above the markers compounds this. It states that every published run shares the long-horizon comparison key, which is true only while breadth has no runs, and would sit directly above a breadth table contradicting it.

## What Changes

- Give the breadth result section a heading and a short blurb naming its suite, profile, and what it measures.
- Name the long-horizon section for its suite so both sections are identified the same way.
- State in each section that the two suites measure different properties and that their scores are not comparable.
- Rewrite the hand-authored README paragraph so it stays correct once breadth runs exist.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-scoring-reporting`: every generated result section identifies its suite and disclaims cross-suite ranking.

## Impact

- Section rendering in `src/lgtmaybe_bench/reporting.py`.
- Behavioural report tests, the hand-authored `README.md` prose, and regenerated `README.md`, `RESULTS.md`, and dashboard artefacts.
- No change to stored raw results, suite or profile identifiers, scoring formulas, eligibility filters, or the ranking itself.
