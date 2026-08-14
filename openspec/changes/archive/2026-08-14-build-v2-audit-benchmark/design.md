## Context

The current corpus has 20 Python findings, one forbidden trap, and no clean repositories. Raw observations preserve final lgtmaybe output, but the reports compare any full-corpus run even when the corpus, lgtmaybe defaults, repeat count, or output budget differs. That makes the table useful for smoke testing but too confounded for model or lens-quality claims.

The v2 benchmark must keep all published v1 cases and evidence immutable, invoke lgtmaybe only through its CLI, remain reproducible from stored evidence, and avoid runtime dependencies. It also needs an optional upstream audit stream because final JSON cannot reveal candidates removed by anchoring, deduplication, rules, or reflection.

## Goals / Non-Goals

**Goals:**

- Measure review quality across seven programming languages, CI/IaC, every existing lens, clean diffs, specs, and tests.
- Make the headline percentage mathematically explicit and comparable only within a frozen suite and profile.
- Preserve final findings, all available model candidates, false-positive classifications, and later human adjudications.
- Recommend one canonical benchmark profile while keeping useful diagnostic variations distinct.
- Generate a compact README table and a sortable/filterable static dashboard from the same evidence.

**Non-Goals:**

- Claim that a finite synthetic corpus represents all real pull requests.
- Tune canonical settings separately by language or model.
- Treat every unmatched finding as a false positive without adjudication.
- Import lgtmaybe internals or make the upstream audit trace mandatory for ordinary scoring.
- Edit historical corpus cases or raw result documents in place.

## Decisions

### Version suites, profiles, and comparison keys

A suite manifest will name an ordered, immutable set of case versions. New `case.json` documents will add `language` and support an explicitly clean case with no expected findings. Existing raw results will be interpreted as `legacy-v1` at read time; their files will not be rewritten.

A profile is a versioned set of benchmark and lgtmaybe settings. Every raw run will store the suite ID, profile ID, resolved profile values, and lgtmaybe version. A comparison key is the tuple of suite ID, profile ID, and lgtmaybe version. Generated leaderboards will never combine different keys.

This is preferred to inferring comparability from individual flags because a newly introduced default would otherwise change semantics without changing an old row.

### Build v2 as a coverage matrix with a stop rule

The core matrix will contain four cases for each of Python, TypeScript, JavaScript, Rust, Dart, Java, and Go: three defect-bearing PRs and one clean-but-plausible PR. Across each language's defect cases, the suite will contain exactly one primary expected finding for each of the ten benchmark lenses. At least one case per language will exercise specification alignment and one will exercise test-review quality. Four additional cases will cover GitHub Actions and Terraform, split between defect-bearing and clean changes.

This produces 32 cases, 70 balanced language/lens targets, seven language clean cases, and four cross-cutting CI/IaC cases. More cases are added only to fill a missing behavior class, remove a demonstrated ambiguity, or replace a published case under a new version. The fixed matrix is preferred to open-ended corpus growth because it keeps cost and weighting legible.

### Use one canonical profile across languages

`canonical-v1` will pass no language-specific tuning and will follow lgtmaybe's product defaults: the fast preset, reflection, recursive review, and matched spec review enabled; static analysis and mid-review retrieval disabled; provider-resolved output and reasoning limits; default input budget and provider-aware concurrency. The benchmark, not lgtmaybe, will repeat the suite three times.

Resolved values are stored so a later product-default change leads to a new profile version. Separate one-repeat profiles will cover full-lens diagnosis, a fixed 4K output budget, and large-diff stress. Diagnostic profiles remain visible but never enter the canonical leaderboard. This tests the experience users receive by default without hiding useful failure analysis.

### Separate automated matching from adjudication

Expected matches are true positives. Forbidden matches, all findings on verified-clean cases, and unmatched findings close to a catalogued location are automated false-positive classes. Findings outside those classes remain `unadjudicated`; they are not silently counted as correct or false.

Maintainers can append an adjudication event that classifies a finding as a true positive, false positive, duplicate, or invalid case evidence, with a reason and superseded event reference. Raw observations and audit traces remain unchanged. A score with unresolved final findings is labelled provisional and reports adjudication coverage.

### Define the headline as balanced F1, not accuracy

Balanced recall is the arithmetic mean of recall for the 70 language/lens cells, so a strong Python result cannot mask a weak Rust or Dart result. Precision is true-positive final findings divided by all adjudicated true- and false-positive final findings. The overall score is the harmonic mean of balanced recall and precision. It is displayed as a percentage but named `balanced F1`, never accuracy.

Clean-pass rate, false-positive counts by class, unadjudicated count, and adjudication coverage are first-class metrics. CI/IaC results and per-language/per-lens metrics are reported separately rather than changing the weight of the core matrix. Repeat summaries retain median and range for comparable per-repeat metrics.

### Retain two linked evidence layers

The existing raw JSON remains the run manifest and stores complete final finding fields, case truth snapshots, resolved configuration, and references to optional trace artifacts. Upstream audit events are copied without semantic rewriting into immutable `results/audit/*.jsonl.gz` files using the standard library. A trace may contain raw redacted model responses, every parsed candidate, stage decisions, usage, and errors.

Append-only `results/adjudications/*.jsonl` files hold evolving human classifications keyed by run, observation, repeat, and candidate or final-finding ID. Prompts are represented by lgtmaybe version, lens identity, and hashes unless a custom lens cannot otherwise be reconstructed. This avoids duplicating large stable prompts while retaining experimental provenance.

### Generate static exploration, keep Markdown compact

GitHub Markdown tables cannot provide reliable client-side sorting or filtering. `bench report` will therefore keep the README to the newest compatible canonical comparison key, retain detailed Markdown in `RESULTS.md`, and generate a deterministic dashboard data file plus a dependency-free static HTML/JavaScript page. The dashboard will sort and filter by model, provider, language, lens, suite, profile, version, score, precision, false positives, clean-pass rate, and audit availability.

The Markdown and dashboard data will be rendered from raw evidence plus adjudication events through the same scoring functions. Generated files are never edited by hand.

## Risks / Trade-offs

- [Synthetic cases overfit lens wording] -> Keep cases idiomatic, use unseen replacements for corrections, and report matrix coverage rather than universal quality claims.
- [Thirty-two cases multiplied by three repeats is expensive] -> Make focused case runs and one-repeat diagnostic profiles available while reserving canonical publication for the full matrix.
- [Product defaults drift] -> Freeze resolved values and increment the profile version before comparing new runs.
- [Human adjudication introduces judgment] -> Keep append-only reasons and provenance, expose coverage, and never overwrite automated classifications.
- [Audit traces contain repository or model text] -> Rely on the upstream redaction contract, retain only explicitly requested traces, and prohibit credentials or unrelated environment data.
- [Active reporting/checkpoint changes overlap this work] -> Apply this change only after those changes are archived or deliberately reconcile their deltas before implementation.

## Migration Plan

1. Add suite/profile loading and classify historical evidence as `legacy-v1` without rewriting it.
2. Add the v2 schema and cases, then validate matrix coverage before making model calls.
3. Add scoring, adjudication, and report/dashboard generation while continuing to render legacy results.
4. Consume the upstream audit option when the installed lgtmaybe supports it and mark older runs as audit-unavailable.
5. Publish canonical v2 rows only after all cases complete three repeats under one comparison key.

Rollback removes v2 from the selected canonical suite and regenerates reports; immutable v2 raw and audit evidence remains available for diagnosis.

## Open Questions

- Which exact issue examples should populate each language/lens cell is an implementation-time corpus review decision; the matrix and acceptance criteria are fixed here.
- Dashboard hosting can use GitHub Pages or be opened locally; generation must not depend on hosting.
