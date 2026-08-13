## ADDED Requirements

### Requirement: Benchmark command interface
The package SHALL expose `bench run` with `--provider`, `--model`, `--reasoning-effort`, `--max-tokens`, `--max-input-tokens`, `--preset`, `--repeats`, repeatable `--case`, `--api-base`, and explicit concurrency options. Repeats SHALL default to three, and provider and model SHALL be required.

#### Scenario: Run one local repeat
- **WHEN** a user runs `bench run --provider ollama --model <local> --repeats 1`
- **THEN** the selected corpus is reviewed once, raw evidence is stored, and Markdown reports are updated

#### Scenario: Run selected cases
- **WHEN** a user supplies one or more `--case` values
- **THEN** only those named cases run and unknown names fail before a model call

### Requirement: Real isolated git diffs
For every case and repeat, the runner SHALL create an isolated temporary git repository with clean and planted revisions, then invoke `lgtmaybe review` as a subprocess using the clean revision as `--base`, JSON output, and profiling. It MUST NOT import lgtmaybe internals.

#### Scenario: Invoke lgtmaybe
- **WHEN** a case repository is prepared
- **THEN** the command receives the resolved provider, model, configuration flags, base revision, `--format json`, and `--profile`

### Requirement: Complete resolved configuration
Every configuration run SHALL record the UTC time, lgtmaybe version, provider, model, reasoning effort, preset, max output tokens, max input tokens, API base when supplied, repeats, selected cases, explicit concurrency, and execution timeout. Secrets and API credentials MUST NOT be stored.

#### Scenario: Record an Ollama configuration
- **WHEN** the provider is `ollama`
- **THEN** the stored and reported effort states that thinking is disabled and concurrency records the value actually passed to lgtmaybe

### Requirement: Raw observation retention
The runner SHALL write one uniquely named JSON file under `results/raw/` for each configuration run. It SHALL retain each observation's findings, raw stdout and stderr, process wall time, parsed provider-call timings, token counts, truncation errors, exit status, and a snapshot of case ground truth.

#### Scenario: Preserve a successful run
- **WHEN** all selected cases complete
- **THEN** a raw file exists before generated Markdown is updated and contains every repeat and case observation

#### Scenario: Preserve a truncated lens
- **WHEN** lgtmaybe reports a truncated provider call but returns partial findings
- **THEN** the observation remains scoreable and retains the truncation lens, elapsed time, and partial findings

### Requirement: Loud execution failures
The runner SHALL reject missing executables, invalid configuration, malformed JSON, and unusable case repositories with a concise non-zero error. A subprocess timeout or non-zero lgtmaybe exit SHALL be retained in raw evidence and surfaced in the report rather than silently treated as a clean review.

#### Scenario: lgtmaybe is unavailable
- **WHEN** `bench run` cannot resolve the lgtmaybe executable
- **THEN** it exits before creating a misleading leaderboard row and identifies the missing prerequisite
