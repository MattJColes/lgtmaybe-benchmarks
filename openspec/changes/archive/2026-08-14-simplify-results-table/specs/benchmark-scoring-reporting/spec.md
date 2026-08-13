## MODIFIED Requirements

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
