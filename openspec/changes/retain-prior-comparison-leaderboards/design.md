## Context

The breadth renderer currently selects the single newest canonical comparison key before sorting and limiting rows. The first lgtmaybe 2.2.0 result therefore replaced ten visible 2.1.4 rows with one row, while raw evidence and `RESULTS.md` remained intact. Comparison keys must stay isolated because scores from different lgtmaybe versions are not directly rankable.

## Goals / Non-Goals

**Goals:**

- Preserve every published canonical comparison group in the README.
- Keep ordering and the ten-row limit local to each comparison group.
- Keep report generation deterministic.

**Non-Goals:**

- Combine or rank scores across lgtmaybe versions or profile IDs.
- Change scoring, raw evidence, detailed results, or dashboard behavior.
- Add a separate history document or client-side interaction.

## Decisions

**Group before rendering.** Partition eligible canonical breadth runs by the existing `(suite, profile, lgtmaybe_version)` comparison key, sort groups by their newest run, and invoke the existing table renderer once per group. This reuses current ranking logic and avoids a second representation of comparison semantics.

**Use one breadth section with repeated comparison-key blocks.** A single suite heading and methodology blurb precede multiple labelled tables. Repeating the full suite introduction for each version would add noise; omitting the key would make partitions ambiguous.

**Apply the top-ten limit per group.** A global limit would still allow a large new partition to hide historical groups. Per-group limiting preserves the documented bounded summary without mixing results.

## Risks / Trade-offs

- [README grows as comparison keys accumulate] → Bound each partition to ten rows; revisit archival presentation only when real growth makes it necessary.
- [Readers mistake adjacent tables as directly comparable] → Label every table with its full comparison key and retain the explicit cross-suite/key comparability guidance.
- [Ordering changes nondeterministically] → Derive group order from stored timestamps with the existing deterministic tie-break behavior.
