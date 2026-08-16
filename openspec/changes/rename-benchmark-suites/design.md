## Context

Thirty stored raw results record suite `context-v1` and profile `context-canonical-v1`. Published raw evidence is append-only, so the rename cannot rewrite them. Reporting filters compare these identifiers by exact string, so an unaliased rename would silently empty the published leaderboard while every check still passed.

A second collision exists in the profile table: `canonical-v1` is already defined with three repeats and the fast preset, left over from a scoring generation whose results were deleted. The published profile has one repeat and the full preset. No stored result names profile `canonical-v1`.

## Goals / Non-Goals

**Goals:**

- Name each suite and canonical profile for the property it measures.
- Keep every published run in the leaderboard with unchanged scores.
- Leave stored raw results byte-identical.
- Present one name per suite across README, `RESULTS.md`, and the dashboard.

**Non-Goals:**

- Change the scoring formula, matching rules, eligibility filters, or repeat aggregation.
- Rename corpus case directories, which stored observations reference by name.
- Rename diagnostic profile identifiers.
- Run the breadth suite or add results.

## Decisions

Superseded identifiers are resolved at read time through a table mapping each old identifier to its current name, applied wherever reporting reads a stored suite or profile. Resolution is one-way and total: an unknown identifier resolves to itself, so focused, diagnostic, and legacy runs keep their stored identity. The alternative, migrating raw files, was rejected because published raw evidence is immutable.

Generated output displays the resolved name rather than the stored one. Without this, the same suite would appear under two names in `RESULTS.md` and the dashboard once a run is stored under the new identifier, splitting a single comparison key across two labels. Raw evidence keeps the original value, so no history is lost.

The unused `canonical-v1` profile is removed rather than kept alongside the renamed profile. Retaining it would preserve a profile that no result uses and that names a generation with no stored evidence. Its removal is observable only through `get_profile`, which will reject the identifier.

Corpus case names such as `python-context-small-v1` are retained. They appear inside stored observations, and the repository treats a referenced case as immutable. Only the manifest identifier that groups them changes.

Behavioural tests assert that a run stored under a superseded identifier still ranks, that stored and renamed runs share one displayed name, and that the removed profile is rejected, before any identifier is renamed in the implementation.

## Risks / Trade-offs

- [An unaliased comparison would drop all published runs from the leaderboard without failing a test] → Add the alias test first, and verify after regeneration that the leaderboard still holds the same models and identical score, recall, precision, and finding counts.
- [Displaying a resolved name could be read as altering stored evidence] → Resolve only at render time and leave `results/raw/` untouched, verified by diffing the tree.
- [Future renames could accumulate alias entries indefinitely] → Keep the table small and explicit, one entry per superseded identifier, so a stale entry is visible in review.
