## Context

Scoring currently distinguishes nearby unexpected findings from distant unadjudicated findings. Because distant findings do not affect precision, the same noisy output can be scored differently based only on its line location. Existing raw observations already contain every finding needed to apply a stricter closed-world rule retroactively.

## Goals / Non-Goals

**Goals:**

- Treat every finding that does not consume an expected planted entry as a false positive.
- Penalize all false positives through precision and overall score.
- Publish the false-positive count for every historical full-corpus run.
- Make the rule explicit to humans and coding agents.

**Non-Goals:**

- Decide whether an unmatched finding identifies a genuine uncatalogued defect.
- Edit published corpus truth or raw observations.
- Add manual adjudication state.

## Decisions

Use closed-world classification: each finding either matches one still-uncaught expected entry or is a false positive. Forbidden hits remain separately counted for diagnostics but are included in false positives. Duplicate matches count as false positives after the planted entry has been consumed.

Precision is `caught / (caught + false positives)`, with precision one when the model returns no findings. This is equivalent to correct findings divided by all returned findings and makes the penalty easy to explain.

Aggregate false-positive counts across repeats with the same median and min-max representation as other metrics. Regenerate reports from raw JSON so historical rows are backfilled without changing evidence.

Document the closed-world rule in README metrics and AGENTS.md. Agents must not manually excuse plausible unmatched findings; corpus truth changes apply only to future runs through a versioned case.

## Risks / Trade-offs

- A legitimate uncatalogued defect is penalized → this is intentional benchmark behavior; add a versioned corpus case for future runs instead of changing historical truth.
- Historical scores and ordering change → regenerate every row deterministically from immutable raw evidence.
- The label is less nuanced than “unknown positive” → use the user-facing term `false positives` consistently and explain its benchmark-specific meaning.
