## MODIFIED Requirements

### Requirement: Versioned benchmark profiles
The benchmark SHALL provide versioned named profiles. `canonical-v1` SHALL use lgtmaybe's product-default fast review behavior with provider-resolved output and reasoning settings and SHALL use three repeats; it is retained unchanged as a versioned predecessor. `canonical-v2` SHALL be the current canonical profile: the `canonical-v1` behaviour with an explicit bounded canonical output budget of `max_tokens 16384` passed to every lgtmaybe review call, so a canonical observation cannot consume repeated provider-ceiling generations. Full-lens, fixed-output-budget, and large-diff settings SHALL use distinct diagnostic profile IDs. A profile SHALL apply consistently across languages.

#### Scenario: Run the canonical profile
- **WHEN** a user runs a provider and model without overriding benchmark settings
- **THEN** the runner selects `canonical-v2`, resolves its bounded-output settings, and schedules three repeats

#### Scenario: Use a language-specific diagnostic setting
- **WHEN** a user changes settings for one language or selected cases
- **THEN** the run is stored as a focused or diagnostic configuration and is not labelled canonical

#### Scenario: Bound a runaway generation
- **WHEN** a provider would otherwise generate up to its own output ceiling under the current canonical profile
- **THEN** each review call is capped at the profile's 16,384-token output budget, calls that hit the cap are retained as truncated evidence, and the observation remains scoreable

#### Scenario: Preserve the versioned predecessor
- **WHEN** a stored raw result references `canonical-v1`
- **THEN** the profile stays resolvable and the run keeps its original canonical identity within its own generation

### Requirement: Benchmark command interface
The package SHALL expose `bench run` with required `--provider` and `--model`, named `--suite` and `--profile`, repeatable `--case`, `--api-base`, and explicit concurrency options. It SHALL retain explicit diagnostic overrides for reasoning effort, output tokens, input tokens, preset, repeats, and timeout. The default profile SHALL be `canonical-v2`; incompatible overrides SHALL cause the stored run to use a diagnostic profile identity rather than the canonical identity.

#### Scenario: Run one local repeat
- **WHEN** a user runs `bench run --provider ollama --model <local> --profile diagnostic-full-v1 --repeats 1`
- **THEN** the selected suite is reviewed once, raw evidence is stored, and generated reports are updated without adding the run to the canonical leaderboard

#### Scenario: Run selected cases
- **WHEN** a user supplies one or more `--case` values
- **THEN** only those named cases run, unknown names fail before a model call, and the run is marked focused

#### Scenario: Run recommended defaults
- **WHEN** a user supplies only provider and model
- **THEN** the complete current canonical suite runs with the current canonical profile's three repeats and bounded output budget
