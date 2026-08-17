## Context

`_profile()` builds every registered profile and hardcodes `reasoning_effort=None` and `schema_version=1`. `canonical-breadth` therefore inherits a provider-resolved reasoning budget, while its sibling setting — the output budget — is pinned at 16,384 by an explicit argument. `_command()` already emits `--reasoning-effort` whenever the resolved config carries one, so the plumbing to set a budget exists and is simply unused by the canonical profile.

## Goals / Non-Goals

**Goals:**

- Make the canonical breadth reasoning budget explicit and recorded in the resolved profile.
- Keep the profile ID stable so no leaderboard reset or re-run campaign is required.
- Keep the two profile generations distinguishable in raw evidence.

**Non-Goals:**

- Rescore, reinterpret, or exclude the 17 published canonical breadth runs.
- Separate the generations in ranking — the maintainer chose mutation in place over a new generation precisely to avoid that.
- Change the long-horizon reasoning budget.
- Add a reasoning-token ceiling; only `--reasoning-effort` is plumbed, and nothing confirms the installed lgtmaybe exposes a token-based flag.

## Decisions

**The budget is `reasoning_effort: "low"`.** It is the cheapest explicit bound and the only rung with any stored evidence in this repository — one diagnostic run each on breadth and long-horizon. Anything higher would be chosen blind, since no stored run exercises `medium` or `high`. The trade-off is that a strong reasoning model may now score below what its provider default would have produced; that is the cost of measuring every model under the same budget, and it is symmetrical rather than arbitrary.

**Mutate in place, do not add a generation.** The precedent for the output budget was a new profile ID, which reset the leaderboard. The maintainer chose the opposite here after seeing that consequence stated: no reset, no re-runs, and published and future runs ranking under one comparison key with two different reasoning budgets. That is recorded in the proposal as an accepted trade-off rather than resolved in code, because resolving it — by adding the profile schema version to the comparison key, say — would reset the leaderboard and contradict the decision.

**Bump `schema_version` to 2.** The field means "version of this profile's definition", so leaving it at 1 after changing what the profile does would make it wrong. Bumping it is additive: reporting never reads it, so nothing about ranking or rendering moves, and a raw record gains an unambiguous statement of which generation it ran under. The stored `configuration.reasoning_effort` already distinguishes the generations in practice; the bump makes the field itself honest.

**An explicit `--reasoning-effort low` keeps canonical identity.** `resolve_profile()` compares each override against the base and only assigns a diagnostic identity when a value actually differs, so passing the budget the profile already sets is a no-op. Any other effort still resolves to `diagnostic-custom-v1`, unchanged.

**A diagnostic run's settings summary must come from its own record.** `_settings()` compared a `diagnostic-custom-v1` run against `get_profile(base_profile)` — the live registry — so changing the canonical reasoning budget rewrote a published row, dropping `effort low` from the one stored diagnostic breadth run because the base profile now sets it. The raw record already names exactly what the run overrode in `diagnostic_overrides`, so the summary now compares against the run's own `resolved_profile` with those fields removed: an overridden field always renders, a non-overridden field never does, and no later edit to a profile definition can reach a published run. That also fixes the mirror-image fault, where a base profile that has since changed made the summary invent an override the run never made.

## Risks / Trade-offs

- Published and future runs mix two reasoning budgets under one comparison key → stated in the proposal as the maintainer's accepted trade-off; the per-run `reasoning_effort` and `profile_schema_version` keep the distinction recoverable from evidence.
- `low` may understate models that reason well at their provider default → the alternative is an unset budget that flatters whichever model the provider happens to favour, and no stored evidence supports a higher rung.
- Long-horizon keeps a provider-resolved reasoning budget → out of scope for this issue and left explicit rather than silently generalised.
