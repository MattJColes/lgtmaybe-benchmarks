## MODIFIED Requirements

### Requirement: Comparable leaderboard partitions
Generated rankings SHALL compare only complete runs with the same suite ID, profile ID, and lgtmaybe version. The canonical README SHALL render each comparison key that has complete canonical runs as a separately labelled leaderboard, ordered by the newest run in each partition descending, with at most ten ranked rows per partition. Focused, diagnostic, legacy, incomplete, and incompatible runs SHALL remain explorable but SHALL NOT appear in those rankings.

#### Scenario: Profile settings differ
- **WHEN** two full-suite runs use different profile IDs or lgtmaybe versions
- **THEN** reports place them in separately labelled comparison partitions rather than ranking them together

#### Scenario: Publish the current canonical matrix
- **WHEN** a complete canonical run introduces a newer comparison key
- **THEN** the README renders the newer partition first and retains every earlier canonical comparison partition below it

#### Scenario: Limit a comparison partition
- **WHEN** more than ten complete canonical runs share one comparison key
- **THEN** that partition renders only its ten highest-ranked runs without affecting any other partition
