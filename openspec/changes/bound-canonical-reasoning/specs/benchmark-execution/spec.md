## MODIFIED Requirements

### Requirement: Versioned benchmark profiles
The benchmark SHALL provide versioned named profiles. `canonical-breadth` SHALL use lgtmaybe's fast review preset with three repeats, a bounded output budget, and an explicit reasoning budget rather than a provider-resolved one. `canonical-long-horizon` SHALL use the full preset with one repeat. Full-lens, fixed-output-budget, and large-diff settings SHALL use distinct diagnostic profile IDs. A profile SHALL apply consistently across languages.

A profile SHALL carry a schema version describing the generation of its own definition, and that version SHALL be recorded with every run. Changing what a profile resolves to SHALL advance that version.

#### Scenario: Run the canonical profile
- **WHEN** a user runs a provider and model without overriding benchmark settings
- **THEN** the runner selects `canonical-breadth`, resolves its bounded output and reasoning budgets, and schedules three repeats

#### Scenario: Bound canonical reasoning explicitly
- **WHEN** a canonical breadth run invokes lgtmaybe
- **THEN** the command carries the profile's reasoning effort and the stored configuration records it, rather than leaving the budget to the provider default

#### Scenario: Supply the budget the profile already sets
- **WHEN** a user passes the reasoning effort that `canonical-breadth` already resolves to
- **THEN** the run keeps its canonical identity and records no diagnostic override

#### Scenario: Use a language-specific diagnostic setting
- **WHEN** a user changes settings for one language or selected cases
- **THEN** the run is stored as a focused or diagnostic configuration and is not labelled canonical
