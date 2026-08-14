## ADDED Requirements

### Requirement: False-positive classification and coverage
Automated scoring SHALL classify expected matches as true positives, forbidden matches as forbidden false positives, every final finding on a verified-clean case as a clean-case false positive, and unmatched findings within the catalogue line window as unexpected-near false positives. Other findings SHALL remain unadjudicated until an append-only adjudication classifies them. Duplicate findings SHALL be reported separately and SHALL count as false positives unless an adjudication marks the case evidence invalid.

#### Scenario: Flag a plausible clean-case guess
- **WHEN** a final finding is emitted for a verified-clean case
- **THEN** clean-case false positives increase and the case does not pass cleanly

#### Scenario: Leave a distant discovery unresolved
- **WHEN** a final finding is outside every expected and forbidden line window on a defect-bearing case
- **THEN** it increases the unadjudicated count without silently changing true positives or false positives

#### Scenario: Apply a later adjudication
- **WHEN** an append-only event classifies an unadjudicated finding
- **THEN** regenerated precision and false-positive metrics use the latest valid classification and retain the prior history

### Requirement: Comparable leaderboard partitions
Generated rankings SHALL compare only complete runs with the same suite ID, profile ID, and lgtmaybe version. The canonical README leaderboard SHALL use the newest comparison key with complete canonical runs. Focused, diagnostic, legacy, incomplete, and incompatible runs SHALL remain explorable but SHALL NOT appear in that ranking.

#### Scenario: Profile settings differ
- **WHEN** two full-suite runs use different profile IDs or lgtmaybe versions
- **THEN** reports place them in different comparison partitions rather than ranking them together

#### Scenario: Publish the current canonical matrix
- **WHEN** complete canonical runs exist for the newest comparison key
- **THEN** the README ranks only those compatible runs and names the suite, profile, and lgtmaybe version

## MODIFIED Requirements

### Requirement: Recall, precision, and score
Each repeat SHALL report caught and planted counts, per-language, per-lens, and language/lens-cell recall, balanced recall, true positives, false positives by class, unadjudicated and duplicate findings, adjudication coverage, precision, clean-pass rate, and balanced F1. Balanced recall SHALL be the arithmetic mean of recall across the suite's 70 primary language/lens cells. Precision SHALL equal `true positives / (true positives + false positives)` for adjudicated final findings and SHALL be one when that denominator is zero. Balanced F1 SHALL be the harmonic mean of balanced recall and precision. A result with unresolved final findings SHALL be labelled provisional.

#### Scenario: Score balanced language coverage
- **WHEN** a model catches every Python target but misses targets in other languages
- **THEN** its balanced recall reflects all 70 language/lens cells rather than the raw Python finding count

#### Scenario: Score noisy findings
- **WHEN** a repeat catches planted bugs and emits forbidden, clean-case, unexpected-near, or adjudicated false-positive findings
- **THEN** its precision and balanced F1 are lower than balanced recall and its false-positive classes remain visible

#### Scenario: Explain the overall percentage
- **WHEN** a report renders the headline percentage
- **THEN** it labels the value balanced F1 and exposes balanced recall, precision, adjudication coverage, and clean-pass rate beside it

### Requirement: Repeat aggregation
Configuration summaries SHALL aggregate balanced recall, precision, balanced F1, clean-pass rate, total wall time, and wall time excluding truncated calls as median with minimum and maximum. They SHALL include true-positive, false-positive, duplicate, unadjudicated, truncation, and lens counts plus input, output, and reasoning token totals when reported. A single repeat SHALL still render through the same aggregate format and SHALL remain diagnostic unless its profile defines one repeat as canonical.

#### Scenario: Three noisy repeats
- **WHEN** three repeats produce different recall, precision, false-positive, or timing values
- **THEN** the report shows metric medians and full minimum-to-maximum ranges plus the underlying counts

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files and adjudication events, rescore them, and regenerate `RESULTS.md`, dashboard data, and the static dashboard byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. The canonical README table SHALL contain date, provider, model, balanced F1, balanced recall, precision, false-positive count, clean-pass rate, adjudication coverage, audit availability, and a compact settings summary, and SHALL name its comparison key. `RESULTS.md` and dashboard data SHALL retain compatible partitions, per-language and per-lens metrics, false-positive classes, trace links, focused and diagnostic runs, truncations, failures, and complete settings.

The settings summary SHALL list only non-profile values among reasoning effort, preset, max output tokens, max input tokens, API base, concurrency, repeats, and execution timeout. It SHALL render `—` when no listed setting differs from the named profile. Raw results created before suite and profile fields existed SHALL be treated as `legacy-v1` for backward compatibility.

#### Scenario: Regenerate unchanged reports
- **WHEN** `bench report` runs twice without evidence or adjudication changes
- **THEN** the second run leaves all generated artifacts byte-for-byte unchanged

#### Scenario: Complete a canonical benchmark run
- **WHEN** `bench run` stores a complete current-suite canonical result successfully
- **THEN** the canonical README table and detailed generated artifacts update through the same scorer and renderer used by `bench report`

#### Scenario: Complete a focused or diagnostic run
- **WHEN** `bench run` stores a selected-case or non-canonical profile result
- **THEN** its evidence is retained in detailed outputs but it does not appear in the canonical README ranking

#### Scenario: Sort and filter detailed results
- **WHEN** a reader opens the generated static dashboard
- **THEN** they can sort and filter results by provider, model, language, lens, suite, profile, lgtmaybe version, score, precision, false positives, clean-pass rate, and audit availability

### Requirement: Behavioural verification
The project SHALL test scoring with hand-written findings for language/lens balancing, line-window boundaries, minimum severity, forbidden hits, clean-case false positives, unexpected-near findings, duplicates, unadjudicated findings, adjudication updates, and provisional status. It SHALL test suite/profile isolation, legacy migration, report and dashboard determinism, corpus matrix validation, and an end-to-end fake-lgtmaybe run containing a complete audit trace and an interrupted partial trace.

#### Scenario: Verify before completion
- **WHEN** the implementation is considered complete
- **THEN** pytest, ruff, mypy, corpus validation, report determinism, and the fake-CLI end-to-end benchmark pass in the Python 3.12 project environment
