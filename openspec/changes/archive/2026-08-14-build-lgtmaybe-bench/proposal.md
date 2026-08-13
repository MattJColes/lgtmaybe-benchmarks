## Why

Model and configuration choices for lgtmaybe cannot be compared reliably from isolated review runs: recall can be gamed by noisy findings, generation truncations distort wall time, and incomplete configuration records make historical results incomparable. A repeatable benchmark with stable ground truth and regenerable reports makes those trade-offs visible before a reviewer configuration is adopted.

## What Changes

- Add a versioned corpus of self-contained cases covering every lgtmaybe review lens, including planted findings and forbidden false-positive traps.
- Add a `bench run` command that builds each case as a real git diff, invokes the public lgtmaybe CLI, repeats configurations three times by default, and retains every raw result.
- Add deterministic scoring for recall, precision, clean runs, truncations, timing, token usage, and a combined score.
- Add a `bench report` command that regenerates `RESULTS.md` and the bounded results tables in `README.md` from raw data, newest first.
- Add Python packaging, focused behavioural tests, `.gitignore`, `README.md`, `AGENTS.md`, and `CLAUDE.md` so humans and coding agents can run and extend the benchmark consistently.

## Capabilities

### New Capabilities

- `benchmark-corpus`: Stable case layout, ground-truth schema, lens coverage, and case selection.
- `benchmark-execution`: Repeated subprocess execution against isolated git diffs with full configuration and profile capture.
- `benchmark-scoring-reporting`: Deterministic adjudication, aggregate metrics, raw-result persistence, and reproducible Markdown reports.

### Modified Capabilities

None.

## Impact

- Introduces a Python 3.12 package managed by `uv`, with `pytest`, `ruff`, and `mypy` development tooling.
- Depends on the installed `lgtmaybe` executable at benchmark runtime but does not import lgtmaybe internals.
- Adds corpus fixtures under `corpus/`, immutable run data under `results/raw/`, and generated tables in `RESULTS.md` and `README.md`.
- Benchmark runs can consume model-provider time and money; the runner exposes all cost- and behaviour-relevant configuration flags without storing credentials.
