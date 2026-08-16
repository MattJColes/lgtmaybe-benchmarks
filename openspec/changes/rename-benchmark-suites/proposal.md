## Why

The suite IDs `context-v1` and `v2` read as two generations of one benchmark, so the generated and hand-authored documentation implies that `v2` supersedes `context-v1`. The two suites measure orthogonal properties: `context-v1` varies diff size for one language to test recall over a long horizon, while `v2` varies language and review lens at small diff sizes to test breadth. Every published run belongs to `context-v1`; no `v2` run has ever been stored. Readers cannot tell which suite produced the leaderboard, which command reproduces it, or which scoring formula produced its numbers.

The README compounds this by documenting a `canonical-v1` scoring generation and a `legacy-v1` formula that have no stored evidence, and by describing balanced F1 as the published metric when the visible table is produced by the closed-world overall score.

## What Changes

- Rename suite `context-v1` to `long-horizon` and suite `v2` to `breadth` so the ID states the measured axis.
- Rename profile `context-canonical-v1` to `canonical-long-horizon` and `canonical-v2` to `canonical-breadth`.
- Remove the unused `canonical-v1` profile, which no stored result references.
- Resolve superseded suite and profile IDs when reading stored raw results, so published runs stay in the leaderboard without rewriting immutable raw evidence.
- Rewrite the hand-authored README to describe the two suites as distinct axes, the command that reproduces the published leaderboard, and only the scoring formula that produces the published numbers.
- Record the suite naming and alias rules in `AGENTS.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-corpus`: suite manifests are named for the property they measure.
- `benchmark-execution`: profile and suite identifiers are renamed and the unused canonical profile is removed.
- `benchmark-scoring-reporting`: reports resolve superseded identifiers and the README documents the published suite and formula.

## Impact

- Suite manifests under `corpus/suites/`, leaving every case directory name unchanged.
- Profile and command defaults in `src/lgtmaybe_bench/{runner,cli,corpus,context_generator}.py`.
- Identifier resolution and generated output in `src/lgtmaybe_bench/reporting.py`.
- Behavioural tests, `README.md`, `AGENTS.md`, and regenerated `RESULTS.md` and dashboard artefacts.
- No change to stored raw results, the scoring formula, matching rules, corpus case contents, or runtime dependencies.
