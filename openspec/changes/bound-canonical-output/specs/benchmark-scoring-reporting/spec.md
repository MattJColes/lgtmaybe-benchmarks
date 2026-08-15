## MODIFIED Requirements

### Requirement: Comparable leaderboard partitions
Generated rankings SHALL compare only complete runs with the same suite ID, profile ID, and lgtmaybe version. The canonical README leaderboard SHALL use the newest comparison key with complete canonical runs, where canonical identity is membership of a canonical profile generation (`canonical-v1`, `canonical-v2`) rather than a single profile ID; because the partition key includes the profile ID, different canonical generations SHALL never be ranked against each other, and the leaderboard SHALL move to a newer generation only once that generation has complete canonical runs. Focused, diagnostic, legacy, incomplete, and incompatible runs SHALL remain explorable but SHALL NOT appear in that ranking.

#### Scenario: Profile settings differ
- **WHEN** two full-suite runs use different profile IDs or lgtmaybe versions
- **THEN** reports place them in different comparison partitions rather than ranking them together

#### Scenario: Publish the current canonical matrix
- **WHEN** complete canonical runs exist for the newest comparison key
- **THEN** the README ranks only those compatible runs and names the suite, profile, and lgtmaybe version

#### Scenario: Rank across canonical generations
- **WHEN** complete `canonical-v1` runs exist and no complete `canonical-v2` matrix exists yet
- **THEN** the leaderboard keeps ranking the `canonical-v1` generation, and a later complete `canonical-v2` matrix replaces it as the newest canonical comparison key without ever mixing generations in one ranking
