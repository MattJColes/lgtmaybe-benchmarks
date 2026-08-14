## Why

Every `v2` case is 14–34 lines and the `large-diff` coverage tag sits on a 15-line file, so the corpus measures nothing about how recall and precision change as the reviewed diff grows. Real pull requests are hundreds to thousands of lines. Context length currently exists only as a run-profile knob (`max_input_tokens`), and the harness can detect truncation but cannot say at what diff size planted bugs stop being found. A scaling suite answers a question `v2` structurally cannot: at what context size does lgtmaybe stop finding bugs that are plainly visible in the diff, and where in the diff do misses concentrate?

## What Changes

- Add a `context-v1` suite of five generated Python cases: four defect-bearing cases at roughly 3k, 15k, 45k, and 90k input-token diffs (~300, ~1,500, ~4,500, and ~9,000 changed lines), plus one clean case at the large band.
- Each defect-bearing case plants the same eight bugs at controlled relative positions through the diff (~10%, ~25%, ~40%, ~55%, ~70%, ~85%, plus the first and last changed file) so recall is comparable across bands and bug position is a controlled variable.
- Add a deterministic, stdlib-only generator script (`scripts/generate_context_cases.py`) that emits the case directories once; generated cases are immutable corpus artefacts like any other.
- Add a `context-canonical-v1` run profile: one repeat, full preset, canonical 100k input-token cap, so the ladder measures model attention under context pressure rather than harness truncation.
- Add a generated "Context scaling" section to `RESULTS.md` reporting per case and model: recall, precision, findings count, input/output tokens, truncation, and wall time.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-corpus`: gains the `context-v1` suite, the `context-scaling` coverage class, and generator requirements for the new cases.
- `benchmark-execution`: gains the `context-canonical-v1` profile alongside the existing canonical and diagnostic profiles.
- `benchmark-scoring-reporting`: gains a generated context-scaling section rendered from stored raw results.

## Impact

- New files under `corpus/` (`python-context-*-v1` case directories and `suites/context-v1.json`), one new script, and profile/reporting additions in `src/lgtmaybe_bench/`.
- The `v2` suite, its manifest, its matrix validation, and its leaderboard rules are untouched; published case immutability is preserved (the generator is a one-shot builder, not a live dependency of runs).
- No new runtime dependencies; the generator and renderer use the standard library only.
- A full `context-v1` run costs noticeably more than a `v2` run (up to ~90k input tokens per case at the top band), which is why the profile pins one repeat and the implementation smoke-tests the small and medium cases before publishing the ladder.
