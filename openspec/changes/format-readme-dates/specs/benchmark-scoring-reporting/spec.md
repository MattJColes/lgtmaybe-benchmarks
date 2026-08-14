## MODIFIED Requirements

### Requirement: Reproducible generated reports
`bench report` SHALL read all valid raw result files, rescore them, and regenerate `RESULTS.md` byte-identically for unchanged inputs. It SHALL also replace only the marked generated section of `README.md`. The generated Markdown SHALL contain one newest-first table for full-corpus runs with ISO calendar date (`YYYY-MM-DD`), lgtmaybe version, provider, model, overall score, every per-lens recall value, and a final settings summary. Incomplete-run rows SHALL use the same ISO calendar date format. It SHALL omit focused runs, the selected-case list, and separate leaderboard, timing, token, precision, clean, truncation, and failure columns. Complete timestamps and data SHALL remain in raw JSON, and newest-first ordering SHALL continue to use the complete timestamp.

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

#### Scenario: Render report dates
- **WHEN** a raw result timestamp is `2026-08-14T01:44:23Z`
- **THEN** its generated complete or incomplete result row shows `2026-08-14` while retaining the full raw timestamp for ordering and evidence

#### Scenario: Render custom settings
- **WHEN** a full-corpus run uses `max_tokens=512` and one repeat while every other listed setting remains at its default
- **THEN** the settings cell contains `max tokens 512; repeats 1` and no default settings

#### Scenario: Render default settings
- **WHEN** a full-corpus run uses only provider-aware defaults
- **THEN** the settings cell contains `—`
