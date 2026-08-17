## Context

`execute_benchmark()` already reserves one raw path per configuration run and rewrites it atomically after every observation, marking it `in_progress` until the final observation flips it to `complete`. Every eligibility check in `reporting.py` — breadth canonical, long-horizon canonical, the dashboard `canonical` flag, and the generated Markdown tables — additionally requires that no observation reported a failure. So the information needed to abandon a run early already exists at the moment the failure is recorded; nothing consumes it.

## Goals / Non-Goals

**Goals:**

- Stop spending provider budget on a configuration that can no longer be scored.
- Make an abandoned canonical run distinguishable from an accidental interruption.
- Retain the failed observation and enough structure to explain why the run stopped.
- Prove by test that no further case is invoked after the first canonical failure.

**Non-Goals:**

- Retry, resume, or repair a failed observation.
- Change scoring, eligibility rules, or any published metric.
- Rewrite `results/raw/` records already published.
- Add a leaderboard or Markdown surface for ineligible runs.

## Decisions

**Scope fail-fast to canonical full-corpus runs.** A run stops at its first failure when its resolved profile ID is `canonical-breadth` or `canonical-long-horizon` and the run covers the complete suite. Both suites publish a result only when every observation is failure-free, so both waste budget identically after the first failure. The issue's evidence is a breadth campaign; covering long-horizon is the same rule applied to the other suite that shares the property, not a new one.

Focused and diagnostic runs keep collecting failures, which the issue permits as a default. No opt-out flag is added because the existing interface already provides two: any `--case` selection makes the run focused, and any profile override resolves to `diagnostic-custom-v1`. Either identity is already excluded from the leaderboard, so investigating a failure never needs new surface area.

**Terminal status is `ineligible`.** `in_progress` means "may still finish" and `complete` means "every observation was attempted"; neither describes a run deliberately abandoned as unscorable. A third terminal value keeps all three readable and, because every reporting filter tests for equality with `complete`, needs no reporting change to stay out of scores and rankings. Behavioural tests pin that so a future filter cannot silently admit it.

**Classify the failure where the evidence exists.** `run_review()` is the only place that knows whether stdout failed to parse, so the classification lives on `Observation` as `failure_class`, in precedence order `timeout`, `truncated_output`, `unparseable_output`, `nonzero_exit`, and `None` for an observation that did not fail. A truncated call with a zero exit stays unclassified because the spec already treats it as scoreable.

**Terminate loudly.** After the terminal record is written, the run raises with a concise message naming the case, repeat, and classification, so `bench run` exits non-zero. A silent zero exit would tell automation the configuration succeeded. The message carries no credentials, and `_redact_api_base` still governs the stored configuration.

**Write the record before raising.** The terminal write reuses the existing reserved path and `write_raw_result`, so the failed observation and the `ineligible` status land atomically in the same rewrite that already preserves every earlier observation.

## Risks / Trade-offs

- An intermittent provider error now ends a canonical run that might have recovered → the result was already unscorable the moment it failed, and rerunning the configuration is the existing remedy.
- Long-horizon canonical runs change behaviour although the issue cited breadth → the eligibility rule is identical for both, and focused or diagnostic runs remain unaffected.
- Newly written raw records gain two fields → both are optional and additive; readers use `.get`, published records stay byte-identical, and no generated table reads either field.
