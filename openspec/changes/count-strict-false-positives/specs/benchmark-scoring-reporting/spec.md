## MODIFIED Requirements

### Requirement: Deterministic expected and forbidden matching
A finding SHALL match a catalogued entry only when its file agrees, its line is within three lines of the catalogue line, one keyword occurs case-insensitively in the finding title or body, and any minimum severity is met using `info < low < medium < high < critical`. The line window SHALL be a named constant. Each expected entry SHALL be consumed by at most one finding. Every finding that does not consume an expected entry SHALL count as a false positive.

#### Scenario: Match an expected finding
- **WHEN** a finding is within the line window, contains an expected keyword, meets minimum severity, and the expected entry is not already caught
- **THEN** that expected entry counts as caught and the finding is not a false positive

#### Scenario: Finding outside line window
- **WHEN** a finding is four lines from the nearest catalogued entry
- **THEN** it does not match and counts as a false positive

#### Scenario: Keyword with insufficient severity
- **WHEN** a finding has the right line and keyword but severity below `severity_at_least`
- **THEN** it does not catch that expected entry and counts as a false positive

#### Scenario: Duplicate expected finding
- **WHEN** more than one finding matches the same expected entry
- **THEN** only the first catches the planted entry and every duplicate counts as a false positive

#### Scenario: Forbidden trap fires
- **WHEN** a finding matches a forbidden entry
- **THEN** the forbidden-hit and false-positive counts increase and the observation is not clean

### Requirement: Recall, precision, and score
Each repeat SHALL report caught and planted counts, overall and per-lens recall, false positives, forbidden hits, unexpected findings, adjudicable findings, precision, clean status, and score. False positives SHALL include every finding that does not match an uncaught expected planted entry, even when the finding may describe a genuine issue that is absent from the benchmark ground truth. Precision SHALL equal `caught / (caught + false positives)`, with precision defined as one when there are no returned findings. Score SHALL be the harmonic mean of recall and precision.

#### Scenario: Score noisy findings
- **WHEN** a repeat catches planted bugs and also produces unmatched findings
- **THEN** every unmatched finding increases false positives and lowers precision and harmonic-mean score

#### Scenario: Plausible uncatalogued issue
- **WHEN** a finding may identify a real issue but does not match an uncaught planted entry
- **THEN** it still counts as a false positive for that immutable benchmark run

### Requirement: Repeat aggregation
Configuration summaries SHALL aggregate recall, precision, score, false-positive count, total wall time, and wall time excluding truncated calls as median with minimum and maximum. They SHALL include truncation count and lenses plus input, output, and reasoning token totals when reported. A single repeat SHALL still render through the same aggregate format.

#### Scenario: Three noisy repeats
- **WHEN** three repeats produce different false-positive counts, recall, or timing values
- **THEN** the report shows their median and full minimum-to-maximum range rather than only one observation or an arithmetic mean

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files, rescore them, and regenerate `RESULTS.md` byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. The generated Markdown SHALL contain one score-descending table for valid completed full-corpus runs with date, lgtmaybe version, provider, model, overall score, false-positive count, every per-lens recall value, and a final settings summary. It SHALL omit incomplete runs, focused runs, the selected-case list, and separate leaderboard, timing, token, precision, clean, truncation, and failure columns. Complete and incomplete data SHALL remain in raw JSON.

The settings summary SHALL list only non-default values among reasoning effort, preset, max output tokens, max input tokens, API base, concurrency, repeats, and execution timeout. It SHALL render `—` when no listed setting differs from its default. Raw results created before the full-corpus marker existed SHALL be treated as full-corpus runs for backward compatibility.

#### Scenario: Regenerate unchanged reports
- **WHEN** `bench report` runs twice without raw-data changes
- **THEN** the second run leaves `RESULTS.md` and the generated README section byte-for-byte unchanged

#### Scenario: Backfill false positives
- **WHEN** existing raw runs are regenerated under the strict scoring rule
- **THEN** every published row contains its recomputed false-positive count and score

#### Scenario: Complete a benchmark run
- **WHEN** `bench run` stores a new full-corpus result successfully
- **THEN** the single generated results table updates through the same renderer used by `bench report`

#### Scenario: Keep an incomplete benchmark checkpoint
- **WHEN** an incomplete raw result exists
- **THEN** its raw evidence is retained but it does not appear in generated Markdown

#### Scenario: Complete a focused diagnostic run
- **WHEN** `bench run` stores a result selected with one or more `--case` values
- **THEN** its raw evidence is retained but it does not appear in the generated comparison table

#### Scenario: Render custom settings
- **WHEN** a full-corpus run uses `max_tokens=512` and one repeat while every other listed setting remains at its default
- **THEN** the settings cell contains `max tokens 512; repeats 1` and no default settings

#### Scenario: Render default settings
- **WHEN** a full-corpus run uses only provider-aware defaults
- **THEN** the settings cell contains `—`
