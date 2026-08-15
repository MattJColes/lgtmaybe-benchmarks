## Context

The context renderer currently builds both the compact model summary and a long per-case table for README. Detailed Markdown and dashboard data retain run-level metrics but do not carry the case rows, so deleting the README table directly would discard the only generated case-level view.

## Goals / Non-Goals

**Goals:**

- Keep README limited to the ranked context model summary.
- Move the existing context case metrics into shared dashboard data.
- Render those metrics in both `RESULTS.md` and the HTML dashboard.
- Preserve deterministic regeneration and existing eligibility rules.

**Non-Goals:**

- Change scoring, model ordering, matching, corpus, or run profiles.
- Add interactive charts or a new frontend dependency.
- Reclassify or mutate stored benchmark evidence.

## Decisions

Extract the current per-case calculation into one reporting helper that returns JSON-compatible records. `build_dashboard_data` will attach those records only to eligible context runs. This makes dashboard data the shared detailed representation consumed by both `RESULTS.md` and the static dashboard while the README renderer stops after the model summary.

The HTML dashboard will add a dependency-free context case table populated from the already-filtered run records. This reuses the existing filters and HTML escaping. An alternative was to keep separately calculating Markdown and HTML case rows from raw results, but that would create three implementations of the same metrics.

## Risks / Trade-offs

- [Detailed values drift between outputs] → Generate Markdown and HTML from the same dashboard case records.
- [README links no longer expose case metrics inline] → Keep the existing links to `RESULTS.md` and the dashboard immediately below the generated section.
- [Case data enlarges embedded dashboard JSON] → The context suite has five cases per model, so the added payload is bounded and small.
