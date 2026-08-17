## MODIFIED Requirements

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files, rescore them, and regenerate `RESULTS.md` byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. The generated Markdown SHALL contain one newest-first table for valid completed full-corpus runs with date, lgtmaybe version, provider, model, overall score, every per-lens recall value, and a final settings summary. It SHALL omit incomplete runs, focused runs, the selected-case list, and separate leaderboard, timing, token, precision, clean, truncation, and failure columns. Complete and incomplete data SHALL remain in raw JSON.

Raw records whose status is not `complete` — including `in_progress` checkpoints and terminal `ineligible` records — SHALL be excluded from every score, ranking, per-lens value, and generated Markdown table. Records without a `status` field SHALL be scored as complete.

The settings summary SHALL list only non-default values among reasoning effort, preset, max output tokens, max input tokens, API base, concurrency, repeats, and execution timeout. It SHALL render `—` when no listed setting differs from its default. Raw results created before the full-corpus marker existed SHALL be treated as full-corpus runs for backward compatibility.

#### Scenario: Regenerate unchanged reports
- **WHEN** `bench report` runs twice without raw-data changes
- **THEN** the second run leaves `RESULTS.md` and the generated README section byte-for-byte unchanged

#### Scenario: Complete a benchmark run
- **WHEN** `bench run` stores a new full-corpus result successfully
- **THEN** the single generated results table updates through the same renderer used by `bench report`

#### Scenario: Keep an incomplete benchmark checkpoint
- **WHEN** an incomplete raw result exists
- **THEN** its raw evidence is retained but it does not appear in generated Markdown

#### Scenario: Keep an ineligible canonical run out of the rankings
- **WHEN** a full-corpus canonical raw record carries terminal status `ineligible`
- **THEN** its raw evidence is retained, it is never scored or ranked, and it adds no row to any generated table

#### Scenario: Complete a focused diagnostic run
- **WHEN** `bench run` stores a result selected with one or more `--case` values
- **THEN** its raw evidence is retained but it does not appear in the generated comparison table

#### Scenario: Render custom settings
- **WHEN** a full-corpus run uses `max_tokens=512` and one repeat while every other listed setting remains at its default
- **THEN** the settings cell contains `max tokens 512; repeats 1` and no default settings

#### Scenario: Render default settings
- **WHEN** a full-corpus run uses only provider-aware defaults
- **THEN** the settings cell contains `—`
