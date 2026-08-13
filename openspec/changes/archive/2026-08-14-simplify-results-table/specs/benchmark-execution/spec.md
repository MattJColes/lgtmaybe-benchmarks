## MODIFIED Requirements

### Requirement: Complete resolved configuration
Every configuration run SHALL record the UTC time, lgtmaybe version, provider, model, reasoning effort, preset, max output tokens, max input tokens, API base when supplied, repeats, selected cases, whether the run covered the full corpus, explicit concurrency, and execution timeout. Secrets and API credentials MUST NOT be stored.

#### Scenario: Record an Ollama configuration
- **WHEN** the provider is `ollama`
- **THEN** the stored effort states that thinking is disabled and concurrency records the value actually passed to lgtmaybe

#### Scenario: Record benchmark scope
- **WHEN** a user runs the full corpus or supplies focused `--case` values
- **THEN** raw configuration records the selected cases and whether the run covered the full corpus
