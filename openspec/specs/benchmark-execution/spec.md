# benchmark-execution Specification

## Purpose
TBD - created by archiving change build-lgtmaybe-bench. Update Purpose after archive.
## Requirements
### Requirement: Versioned benchmark profiles
The benchmark SHALL provide versioned named profiles. `canonical-v1` SHALL use lgtmaybe's product-default fast review behavior with provider-resolved output and reasoning settings and SHALL use three repeats. Full-lens, fixed-output-budget, and large-diff settings SHALL use distinct diagnostic profile IDs. A profile SHALL apply consistently across languages.

#### Scenario: Run the canonical profile
- **WHEN** a user runs a provider and model without overriding benchmark settings
- **THEN** the runner selects `canonical-v1`, resolves its product-default settings, and schedules three repeats

#### Scenario: Use a language-specific diagnostic setting
- **WHEN** a user changes settings for one language or selected cases
- **THEN** the run is stored as a focused or diagnostic configuration and is not labelled canonical

### Requirement: Benchmark command interface
The package SHALL expose `bench run` with required `--provider` and `--model`, named `--suite` and `--profile`, repeatable `--case`, `--api-base`, and explicit concurrency options. It SHALL retain explicit diagnostic overrides for reasoning effort, output tokens, input tokens, preset, repeats, and timeout. The default profile SHALL be `canonical-v1`; incompatible overrides SHALL cause the stored run to use a diagnostic profile identity rather than the canonical identity.

#### Scenario: Run one local repeat
- **WHEN** a user runs `bench run --provider ollama --model <local> --profile diagnostic-full-v1 --repeats 1`
- **THEN** the selected suite is reviewed once, raw evidence is stored, and generated reports are updated without adding the run to the canonical leaderboard

#### Scenario: Run selected cases
- **WHEN** a user supplies one or more `--case` values
- **THEN** only those named cases run, unknown names fail before a model call, and the run is marked focused

#### Scenario: Run recommended defaults
- **WHEN** a user supplies only provider and model
- **THEN** the complete current canonical suite runs with the canonical profile's three repeats

### Requirement: Real isolated git diffs
For every case and repeat, the runner SHALL create an isolated temporary git repository with clean and planted revisions, then invoke `lgtmaybe review` as a subprocess using the clean revision as `--base`, JSON output, and profiling. It MUST NOT import lgtmaybe internals.

#### Scenario: Invoke lgtmaybe
- **WHEN** a case repository is prepared
- **THEN** the command receives the resolved provider, model, configuration flags, base revision, `--format json`, and `--profile`

### Requirement: Complete resolved configuration
Every configuration run SHALL record the UTC time, lgtmaybe version, suite ID, profile ID, profile schema version, provider, model, reasoning effort, preset, max output tokens, max input tokens, API base when supplied, repeats, selected cases, whether the run covered the complete suite, explicit concurrency, execution timeout, review-feature switches, and audit availability. Resolved values SHALL be stored even when inherited from product defaults. Secrets and API credentials MUST NOT be stored.

#### Scenario: Record an Ollama configuration
- **WHEN** the provider is `ollama`
- **THEN** the stored effort states that thinking is disabled and concurrency records the value actually passed to lgtmaybe

#### Scenario: Record benchmark scope
- **WHEN** a user runs the complete suite or supplies focused `--case` values
- **THEN** raw configuration records the suite, selected cases, and whether the run covered the complete suite

#### Scenario: Resolve a product default
- **WHEN** a canonical setting is not passed explicitly to lgtmaybe
- **THEN** raw configuration still records the resolved behavior used by the installed lgtmaybe version

### Requirement: Raw observation retention
The runner SHALL write one uniquely named JSON file under `results/raw/` for each configuration run. It SHALL retain each observation's complete final finding objects, raw stdout and stderr, process wall time, parsed provider-call timings, token counts, per-call parsed finding counts when reported, truncation errors, exit status, trace reference and completion state, and a snapshot of case ground truth. Checkpointed observations and final raw documents SHALL preserve stable observation and finding IDs. The profile parser MUST accept both legacy call tables and current tables with reasoning-share and finding-count columns.

#### Scenario: Preserve a successful run
- **WHEN** all selected cases complete
- **THEN** a raw file exists before generated artifacts are updated and contains every repeat and case observation

#### Scenario: Preserve a truncated lens
- **WHEN** lgtmaybe reports a truncated provider call but returns partial findings
- **THEN** the observation remains scoreable and retains the truncation lens, elapsed time, complete partial findings, and available audit events

#### Scenario: Preserve final finding detail
- **WHEN** lgtmaybe emits fields such as category, failure scenario, suggestion, confidence, broad status, or anchoring metadata
- **THEN** the raw observation stores those fields without reducing the finding to title, body, file, line, and severity

#### Scenario: Parse a current profile table
- **WHEN** lgtmaybe emits call rows containing `think_%` and `findings`
- **THEN** the raw observation retains each call and distinguishes zero findings from an unreported finding count

#### Scenario: Parse a legacy profile table
- **WHEN** stored output contains the earlier call columns without `think_%` or `findings`
- **THEN** the raw observation retains the call with no reported finding count

### Requirement: Optional upstream audit capture
When the installed lgtmaybe exposes the benchmark-compatible audit option, the runner SHALL request one explicit trace path per observation and retain the resulting complete or partial trace. If audit output is unsupported or intentionally disabled, final-result scoring SHALL continue and raw evidence SHALL state that candidate audit is unavailable.

#### Scenario: Capture a completed trace
- **WHEN** an audited lgtmaybe observation completes
- **THEN** the raw observation references an immutable compressed trace containing the emitted candidate and pipeline events

#### Scenario: Preserve interrupted audit evidence
- **WHEN** lgtmaybe times out, exits non-zero, or leaves a valid partial trace
- **THEN** the runner retains the partial evidence and records its completion state with the observation

### Requirement: Loud execution failures
The runner SHALL reject missing executables, invalid configuration, malformed JSON, and unusable case repositories with a concise non-zero error. A subprocess timeout or non-zero lgtmaybe exit SHALL be retained in raw evidence and surfaced in the report rather than silently treated as a clean review.

#### Scenario: lgtmaybe is unavailable
- **WHEN** `bench run` cannot resolve the lgtmaybe executable
- **THEN** it exits before creating a misleading leaderboard row and identifies the missing prerequisite
