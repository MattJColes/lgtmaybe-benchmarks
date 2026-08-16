## MODIFIED Requirements

### Requirement: Versioned benchmark profiles
The benchmark SHALL provide named profiles whose IDs state the suite they are canonical for. `canonical-breadth` SHALL use lgtmaybe's fast review behavior with a bounded output budget and SHALL use three repeats. `canonical-long-horizon` SHALL use the full review preset with one repeat and no output-token ceiling. Full-lens, fixed-output-budget, and large-diff settings SHALL use distinct diagnostic profile IDs. A profile SHALL apply consistently across languages. The benchmark SHALL NOT define a profile that no suite is canonical for.

#### Scenario: Run the canonical profile
- **WHEN** a user runs a provider and model without overriding benchmark settings
- **THEN** the runner selects `canonical-breadth`, resolves its settings, and schedules three repeats

#### Scenario: Reject a removed profile
- **WHEN** a user names a profile ID that the benchmark no longer defines
- **THEN** profile resolution fails with a concise error before any model call

#### Scenario: Use a language-specific diagnostic setting
- **WHEN** a user changes settings for one language or selected cases
- **THEN** the run is stored as a focused or diagnostic configuration and is not labelled canonical

### Requirement: Benchmark command interface
The package SHALL expose `bench run` with required `--provider` and `--model`, named `--suite` and `--profile`, repeatable `--case`, `--api-base`, and explicit concurrency options. It SHALL retain explicit diagnostic overrides for reasoning effort, output tokens, input tokens, preset, repeats, and timeout. The default suite SHALL be `breadth` and the default profile SHALL be `canonical-breadth`; incompatible overrides SHALL cause the stored run to use a diagnostic profile identity rather than the canonical identity.

#### Scenario: Run one local repeat
- **WHEN** a user runs `bench run --provider ollama --model <local> --profile diagnostic-full-v1 --repeats 1`
- **THEN** the selected suite is reviewed once, raw evidence is stored, and generated reports are updated without adding the run to the canonical leaderboard

#### Scenario: Run selected cases
- **WHEN** a user supplies one or more `--case` values
- **THEN** only those named cases run, unknown names fail before a model call, and the run is marked focused

#### Scenario: Run the long-horizon suite
- **WHEN** a user runs `bench run --provider <provider> --model <model> --suite long-horizon --profile canonical-long-horizon`
- **THEN** the complete long-horizon suite runs once per case with the full preset and the result is eligible for the published leaderboard

#### Scenario: Run recommended defaults
- **WHEN** a user supplies only provider and model
- **THEN** the complete breadth suite runs with the canonical breadth profile's three repeats
