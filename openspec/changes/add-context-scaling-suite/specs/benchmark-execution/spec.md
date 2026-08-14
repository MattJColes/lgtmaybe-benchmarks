## MODIFIED Requirements

### Requirement: Versioned benchmark profiles
The benchmark SHALL provide versioned named profiles. `canonical-v1` SHALL use lgtmaybe's product-default fast review behavior with provider-resolved output and reasoning settings and SHALL use three repeats. Full-lens, fixed-output-budget, and large-diff settings SHALL use distinct diagnostic profile IDs. A profile SHALL apply consistently across languages.

The benchmark SHALL additionally provide `context-canonical-v1` for the `context-v1` suite: one repeat, the full preset, and the canonical input-token cap, so context scaling is measured under full lenses without harness truncation and without paying per-band repeats. It SHALL remain outside the `v2` leaderboard's canonical identity.

#### Scenario: Run the canonical profile
- **WHEN** a user runs a provider and model without overriding benchmark settings
- **THEN** the runner selects `canonical-v1`, resolves its product-default settings, and schedules three repeats

#### Scenario: Use a language-specific diagnostic setting
- **WHEN** a user changes settings for one language or selected cases
- **THEN** the run is stored as a focused or diagnostic configuration and is not labelled canonical

#### Scenario: Run the context scaling profile
- **WHEN** a user runs `bench run --suite context-v1 --profile context-canonical-v1`
- **THEN** the suite runs once per case with full lenses and the canonical input-token cap, and the stored run is labelled with the context profile identity

#### Scenario: Override the context profile
- **WHEN** a user adds explicit settings overrides to `context-canonical-v1`
- **THEN** the stored run downgrades to a diagnostic identity and does not enter context-scaling canonical reporting
