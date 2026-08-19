## MODIFIED Requirements

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files and adjudication events, rescore them, and regenerate `RESULTS.md`, dashboard data, and the static dashboard byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. The canonical README table SHALL contain date, provider, model, lgtmaybe version, balanced F0.5, balanced recall, precision, false-positive count, clean-pass rate, adjudication coverage, audit availability, and a compact settings summary, and SHALL name its suite and profile. `RESULTS.md` and dashboard data SHALL retain per-language and per-lens metrics, false-positive classes, trace links, focused and diagnostic runs, truncations, failures, and complete settings for every stored run.

The hand-authored README content outside the generated result markers SHALL document the current canonical suite's case types, case counts, planted-finding and clean-case counts, execution and classification process, balanced-recall population, pooled-precision formula, the shared F0.5 formula, provisional status, repeat aggregation, and the long-horizon recall population. The documented counts SHALL agree with the named suite manifest and corpus metadata.

The settings summary SHALL list only non-profile values among reasoning effort, preset, max output tokens, max input tokens, API base, concurrency, repeats, and execution timeout. It SHALL render `—` when no listed setting differs from the named profile. Raw results created before suite and profile fields existed SHALL be treated as `legacy-v1` for backward compatibility.

#### Scenario: Regenerate unchanged reports
- **WHEN** `bench report` runs twice without evidence or adjudication changes
- **THEN** the second run leaves all generated artifacts byte-for-byte unchanged and preserves the hand-authored README methodology outside the result markers

#### Scenario: Complete a canonical benchmark run
- **WHEN** `bench run` stores a complete current-suite canonical result successfully
- **THEN** the canonical README table and detailed generated artifacts update through the same scorer and renderer used by `bench report`

#### Scenario: Complete a focused or diagnostic run
- **WHEN** `bench run` stores a selected-case or non-canonical profile result
- **THEN** its evidence is retained in detailed outputs but it does not appear in the canonical README ranking

#### Scenario: Sort and filter detailed results
- **WHEN** a reader opens the generated static dashboard
- **THEN** they can sort and filter results by provider, model, language, lens, suite, profile, lgtmaybe version, score, precision, false positives, clean-pass rate, and audit availability

#### Scenario: Read the canonical methodology
- **WHEN** a reader consults the README before comparing canonical results
- **THEN** they can identify the suite's test inventory and counts, follow the evaluation process, and understand the shared F0.5 scoring and each suite's recall population without inspecting implementation files

### Requirement: Comparable leaderboard partitions
Generated rankings SHALL compare only complete canonical runs sharing one suite ID and profile ID. Each suite's canonical README leaderboard SHALL rank those runs across lgtmaybe versions in a single table of at most ten rows, displaying each run's lgtmaybe version as a column, and SHALL never rank runs of different suites or profiles together. Focused, diagnostic, legacy, incomplete, and incompatible runs SHALL remain explorable but SHALL NOT appear in that ranking.

#### Scenario: Versions differ
- **WHEN** two complete canonical runs of one suite and profile use different lgtmaybe versions
- **THEN** the README ranks them in the same table and shows each run's version in its row

#### Scenario: More eligible runs than the row limit
- **WHEN** more than ten complete canonical runs exist across lgtmaybe versions
- **THEN** only the ten highest-ranked rows render, whatever versions they come from

#### Scenario: Profile settings differ
- **WHEN** a full-suite run uses a diagnostic or custom profile
- **THEN** it stays out of the canonical ranking while remaining explorable in detailed outputs
