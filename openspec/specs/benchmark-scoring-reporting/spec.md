# benchmark-scoring-reporting Specification

## Purpose
TBD - created by archiving change build-lgtmaybe-bench. Update Purpose after archive.
## Requirements
### Requirement: Deterministic expected and forbidden matching
A finding SHALL match a catalogued entry only when its file agrees, its line is within three lines of the catalogue line, one keyword occurs case-insensitively in the finding title or body, and any minimum severity is met using `info < low < medium < high < critical`. The line window SHALL be a named constant.

#### Scenario: Match an expected finding
- **WHEN** a finding is within the line window, contains an expected keyword, and meets minimum severity
- **THEN** that expected entry counts as caught

#### Scenario: Finding outside line window
- **WHEN** a finding is four lines from the nearest catalogued entry
- **THEN** it does not match and is excluded from adjudicable precision

#### Scenario: Keyword with insufficient severity
- **WHEN** a finding has the right line and keyword but severity below `severity_at_least`
- **THEN** it does not catch that expected entry and is classified as unexpected if otherwise adjudicable

#### Scenario: Forbidden trap fires
- **WHEN** a finding matches a forbidden entry
- **THEN** the forbidden-hit count increases and the observation is not clean

### Requirement: Recall, precision, and score
Each repeat SHALL report caught and planted counts, overall and per-lens recall, forbidden hits, unexpected findings, adjudicable findings, precision, clean status, and score. Precision SHALL equal `1 - (forbidden hits + unexpected findings) / adjudicable findings`, with precision defined as one when there are no adjudicable findings. Findings far from every catalogued line SHALL be excluded from precision. Score SHALL be the harmonic mean of recall and precision.

#### Scenario: Score noisy findings
- **WHEN** a repeat catches planted bugs but also produces adjudicable forbidden or unexpected findings
- **THEN** its precision and harmonic-mean score are lower than its recall and clean is false when any forbidden trap fired

### Requirement: Repeat aggregation
Configuration summaries SHALL aggregate recall, precision, score, total wall time, and wall time excluding truncated calls as median with minimum and maximum. They SHALL include truncation count and lenses plus input, output, and reasoning token totals when reported. A single repeat SHALL still render through the same aggregate format.

#### Scenario: Three noisy repeats
- **WHEN** three repeats produce different recall or timing values
- **THEN** the report shows their median and full minimum-to-maximum range rather than only one observation or an arithmetic mean

### Requirement: Provider-aware timing
Each scored raw summary SHALL retain total process wall time, derived wall time excluding truncated provider calls, truncation count and lenses, and explicit concurrency. Generated comparison tables SHALL omit timing because local and hosted providers are not directly comparable, while the raw evidence remains available for diagnosis.

#### Scenario: Truncated call dominates a repeat
- **WHEN** one provider call truncates after consuming most of a repeat's elapsed time
- **THEN** the scored raw summary retains both total and excluding-truncation time and names the affected lens without promoting incomparable timing into the generated table

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files, rescore them, and regenerate `RESULTS.md` byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. The generated Markdown SHALL contain one newest-first table for full-corpus runs with date, lgtmaybe version, provider, model, overall score, every per-lens recall value, and a final settings summary. It SHALL omit focused runs, the selected-case list, and separate leaderboard, timing, token, precision, clean, truncation, and failure columns. Complete data SHALL remain in raw JSON.

The settings summary SHALL list only non-default values among reasoning effort, preset, max output tokens, max input tokens, API base, concurrency, repeats, and execution timeout. It SHALL render `—` when no listed setting differs from its default. Raw results created before the full-corpus marker existed SHALL be treated as full-corpus runs for backward compatibility.

#### Scenario: Regenerate unchanged reports
- **WHEN** `bench report` runs twice without raw-data changes
- **THEN** the second run leaves `RESULTS.md` and the generated README section byte-for-byte unchanged

#### Scenario: Complete a benchmark run
- **WHEN** `bench run` stores a new full-corpus result successfully
- **THEN** the single generated results table updates through the same renderer used by `bench report`

#### Scenario: Complete a focused diagnostic run
- **WHEN** `bench run` stores a result selected with one or more `--case` values
- **THEN** its raw evidence is retained but it does not appear in the generated comparison table

#### Scenario: Render custom settings
- **WHEN** a full-corpus run uses `max_tokens=512` and one repeat while every other listed setting remains at its default
- **THEN** the settings cell contains `max tokens 512; repeats 1` and no default settings

#### Scenario: Render default settings
- **WHEN** a full-corpus run uses only provider-aware defaults
- **THEN** the settings cell contains `—`

### Requirement: Behavioural verification
The project SHALL test scoring with hand-written findings for the line-window boundary, minimum severity, forbidden hit, unexpected finding, and clean status. It SHALL include report determinism and an end-to-end test using a fake lgtmaybe executable, including a truncated lens that still produces a scored row.

#### Scenario: Verify before completion
- **WHEN** the implementation is considered complete
- **THEN** pytest, ruff, mypy, corpus validation, and the fake-CLI end-to-end benchmark all pass in the project virtual environment
