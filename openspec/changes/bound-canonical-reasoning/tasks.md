## 1. Behavioural coverage

- [x] 1.1 Write a failing test for `canonical-breadth` resolving an explicit reasoning effort at profile schema version 2, with long-horizon and the diagnostic profiles unchanged.
- [x] 1.2 Write a failing test for a canonical breadth run passing `--reasoning-effort` to lgtmaybe and storing it in the resolved profile.
- [x] 1.3 Write a failing test for supplying the canonical reasoning effort explicitly keeping canonical identity, and any other effort still resolving to a diagnostic identity.

## 2. Profiles

- [x] 2.1 Give `_profile()` reasoning-effort and schema-version parameters and apply the canonical breadth reasoning budget.

## 2a. Settings summary

- [x] 2a.1 Write a failing test for a published diagnostic run keeping its recorded override in the settings summary after its base profile's definition changes.
- [x] 2a.2 Summarise a diagnostic run's settings against its own recorded resolved profile and overrides rather than the live profile registry.

## 3. Documentation

- [x] 3.1 Record the canonical reasoning budget, why it was chosen, and that published runs ran provider-resolved, where profiles are described for humans and coding agents.

## 4. Verification

- [x] 4.1 Run pytest, ruff lint, and mypy in the project virtual environment.
- [x] 4.2 Regenerate README.md and RESULTS.md from existing raw runs and confirm the leaderboard holds the same models with identical metrics.
