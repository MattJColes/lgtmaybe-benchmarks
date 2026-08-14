## Why

The current corpus is a useful Python-heavy lens smoke test, but its two findings per lens, single forbidden trap, one-repeat published runs, and unversioned leaderboard cannot support a durable claim about review quality across languages or benchmark configurations. A versioned v2 suite should measure balanced recall, false positives, spec alignment, test-review quality, and retained audit evidence while keeping unlike runs out of the same ranking.

## What Changes

- Introduce named, immutable benchmark suites and profiles so corpus or configuration changes never silently mix with historical results.
- Add a balanced v2 corpus for Python, TypeScript, JavaScript, Rust, Dart, Java, and Go, plus CI/IaC coverage, clean false-positive cases, spec-alignment scenarios, and test-quality scenarios.
- Make the canonical profile follow lgtmaybe's product defaults with three repeats; retain full-lens, constrained-output, and large-diff runs as separately identified diagnostic profiles.
- Retain complete final finding fields and ingest an optional upstream lgtmaybe candidate audit trace, preserving every candidate and pipeline decision in append-only compressed evidence.
- Add append-only adjudications for true positives, forbidden and clean-case false positives, duplicates, unexpected-near findings, and unadjudicated findings.
- Replace the micro-only headline with balanced language/lens recall, precision, false-positive counts, clean-pass rate, and an F1 score computed only within one suite and profile.
- Keep a compact canonical README leaderboard and generate detailed sortable/filterable result data and a static dashboard from the same raw evidence.

## Capabilities

### New Capabilities

- `benchmark-audit-evidence`: Immutable candidate-level audit traces and separately evolving adjudications for lens and pipeline research.

### Modified Capabilities

- `benchmark-corpus`: Add versioned suite membership, language metadata, balanced v2 coverage, and explicitly clean cases.
- `benchmark-execution`: Add named profiles, canonical defaults, upstream audit-trace capture, and configuration provenance.
- `benchmark-scoring-reporting`: Add balanced aggregation, explicit false-positive metrics, suite/profile isolation, and generated dashboard data.

## Impact

The change affects corpus discovery and validation, runner configuration and raw schemas, scoring and report generation, behavioural tests, generated README/RESULTS output, and new generated audit/dashboard artifacts. It depends on lgtmaybe exposing the opt-in structured trace proposed by `emit-review-audit-trace`; normal runs remain usable without that trace. Published v1 cases and raw results remain immutable and are labelled as the legacy suite during migration.
