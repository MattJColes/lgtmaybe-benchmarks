## ADDED Requirements

### Requirement: Superseded identifier resolution
Reporting SHALL resolve superseded suite and profile identifiers recorded in stored raw results to their current names when selecting, partitioning, and displaying runs. Resolution SHALL map each superseded identifier to exactly one current identifier and SHALL leave every unrecognised identifier unchanged, so focused, diagnostic, and legacy identities survive. Stored raw result files MUST NOT be rewritten by a rename.

#### Scenario: Rank a run stored under a superseded suite ID
- **WHEN** a complete canonical run recorded a suite and profile ID that a later rename superseded
- **THEN** it remains eligible for the published leaderboard and its score, recall, precision, and finding counts are unchanged

#### Scenario: Display one name per suite
- **WHEN** runs stored under a superseded identifier and its current name are reported together
- **THEN** generated output shows the current name for both and places them in one comparison partition

#### Scenario: Preserve an unrecognised identifier
- **WHEN** a stored run records a focused, diagnostic, or legacy identifier with no superseding entry
- **THEN** reporting retains that identifier unchanged

#### Scenario: Leave raw evidence unchanged
- **WHEN** reports are regenerated after a rename
- **THEN** every file under `results/raw/` is byte-identical and retains the identifier recorded at run time

## MODIFIED Requirements

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files and adjudication events, rescore them, and regenerate `RESULTS.md`, dashboard data, and the static dashboard byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. The canonical README table SHALL contain date, provider, model, balanced F1, balanced recall, precision, false-positive count, clean-pass rate, adjudication coverage, audit availability, and a compact settings summary, and SHALL name its comparison key. `RESULTS.md` and dashboard data SHALL retain compatible partitions, per-language and per-lens metrics, false-positive classes, trace links, focused and diagnostic runs, truncations, failures, and complete settings.

The hand-authored README content outside the generated result markers SHALL identify each published suite by the property it measures, state which suite produced the published leaderboard and the command that reproduces it, and document that suite's case count, planted-finding and clean-case counts, execution and classification process, scoring formula, and repeat aggregation. It SHALL NOT document a scoring generation or suite for which no result is stored as though it were published, and SHALL mark an unrun suite as unrun. The documented counts SHALL agree with the named suite manifest and corpus metadata.

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
- **WHEN** a reader consults the README before comparing published results
- **THEN** they can tell which suite produced the leaderboard, what it measures, how to reproduce it, and which formula produced its numbers, without inspecting implementation files

#### Scenario: Distinguish an unrun suite
- **WHEN** the README describes a suite that has no stored result
- **THEN** it states that the suite has no published runs rather than presenting it as the current comparison

### Requirement: Context scaling report section
Generated reports SHALL include a context-scaling section for complete, un-failed runs of the long-horizon suite with its canonical profile, resolving superseded identifiers when selecting them. The section SHALL render a model summary with overall score, recall, precision, true-positive count, and false-positive count, followed by one row per model and case with recall, precision, findings count, input and output tokens, truncation indicator, and wall time, so both the aggregate outcome and recall degradation are visible. Dashboard data and `RESULTS.md` SHALL preserve the same computed true-positive and false-positive totals rather than representing them as missing. The section SHALL be regenerated deterministically from stored raw results, SHALL exclude focused, failed, incomplete, and non-long-horizon runs, and SHALL NOT alter the breadth leaderboard or legacy sections.

#### Scenario: Render context model summaries
- **WHEN** complete canonical long-horizon runs exist
- **THEN** the generated README and results document contain one summary row per model with overall score, recall, precision, true positives, and false positives

#### Scenario: Render context case results
- **WHEN** complete canonical long-horizon runs exist
- **THEN** the generated results document contains one row per model and case including recall, precision, tokens, truncation, and wall time

#### Scenario: Preserve dashboard finding totals
- **WHEN** dashboard data is generated for a complete long-horizon run
- **THEN** its metrics contain the computed true-positive and false-positive totals

#### Scenario: Exclude ineligible runs
- **WHEN** a long-horizon run is focused, diagnostic, incomplete, or contains observation failures
- **THEN** it remains stored and explorable but does not appear in the context-scaling section

#### Scenario: Regenerate deterministically
- **WHEN** `bench report` runs twice with unchanged evidence
- **THEN** the context-scaling section is byte-for-byte unchanged
