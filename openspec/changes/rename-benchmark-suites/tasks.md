## 1. Behavioural Coverage

- [x] 1.1 Add a failing report test that a run stored under the superseded suite and profile IDs still ranks in the published leaderboard with unchanged metrics
- [x] 1.2 Add a failing dashboard-data test that superseded and current identifiers display one suite name and share one comparison partition
- [x] 1.3 Add a failing test that an unrecognised suite or profile identifier resolves to itself
- [x] 1.4 Add a failing profile test that the removed `canonical-v1` identifier is rejected and that `canonical-long-horizon` and `canonical-breadth` resolve with their published settings
- [x] 1.5 Add a failing corpus test that `long-horizon` and `breadth` load their ordered case membership unchanged

## 2. Corpus And Execution

- [x] 2.1 Rename the suite manifests to `long-horizon` and `breadth` without altering case membership or case directory names
- [x] 2.2 Rename the canonical profiles, remove the unused `canonical-v1` profile, and update command defaults
- [x] 2.3 Update breadth matrix validation and the context suite generator to the renamed identifiers

## 3. Reporting

- [x] 3.1 Add superseded-identifier resolution and apply it to leaderboard eligibility, comparison keys, and generated display
- [x] 3.2 Update the generated context-scaling blurb to name the renamed suite and profile

## 4. Documentation

- [x] 4.1 Rewrite the hand-authored README to describe the two suites as distinct axes, the reproducing command, and only the published scoring formula
- [x] 4.2 Record the suite naming and superseded-identifier rules in `AGENTS.md`

## 5. Verification

- [x] 5.1 Run pytest, ruff, and mypy with Python 3.12
- [x] 5.2 Regenerate reports and confirm the published leaderboard retains the same models and identical score, recall, precision, and finding counts
- [x] 5.3 Confirm `results/raw/` is unchanged and generated artefacts show one resolved suite name
- [x] 5.4 Validate the OpenSpec change
