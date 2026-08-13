## Context

The repository is empty apart from OpenSpec. The benchmark must remain compatible with changing lgtmaybe versions, preserve enough evidence to rescore old runs, and avoid presenting hosted and local execution as directly comparable. The supplied benchmark contract also requires a stable corpus, repeated measurements, profile parsing, deterministic Markdown generation, and tests-first Python development.

## Goals / Non-Goals

**Goals:**

- Exercise lgtmaybe only through its installed command-line interface against real git diffs.
- Preserve complete configuration, findings, profile text, and parsed call data for every case and repeat.
- Produce deterministic recall, precision, clean, score, timing, truncation, token, and per-lens summaries.
- Keep the implementation small and runtime-dependency-free by using the Python standard library.
- Make `bench run` update both the detailed results file and the README leaderboard automatically.

**Non-Goals:**

- Judging findings far from catalogued lines or claiming corpus-wide absolute precision.
- Comparing local and hosted providers on wall time.
- Importing or pinning lgtmaybe internals.
- Editing published corpus cases after results exist; corrections use a versioned case name.
- Running providers concurrently at the benchmark-process level; lgtmaybe owns its internal concurrency.

## Decisions

### Store a clean and changed tree per case

Each case contains `case.json`, `base/`, and `changed/`. The runner copies `base/` into a temporary repository, commits and tags it, overlays `changed/`, and commits again. lgtmaybe receives the tag through `--base`, so the exercised path is a normal committed branch diff. An optional `file` on an expected or forbidden entry supports multi-file cases while retaining compatibility with entries that rely on the case-level `changed_file`.

Alternatives considered: committed nested repositories are awkward to version in this repository, while hand-authored patch files make source inspection and line-number maintenance harder.

### Use a compact standard-library Python package

The implementation uses `argparse`, `subprocess`, `tempfile`, `json`, `statistics`, and `pathlib`. A console-script entry point exposes `bench`. Runtime code is separated only where responsibilities differ: CLI/execution, scoring, and reporting. `pytest`, `ruff`, and `mypy` remain development dependencies.

Alternatives considered: Click, Typer, Pydantic, and GitPython reduce a few lines but add dependencies without improving this two-command interface.

### Persist evidence, derive reports

One raw JSON document represents a configuration run and contains its UTC timestamp, complete resolved configuration, lgtmaybe version, and every case/repeat observation. Each observation retains stdout, stderr, parsed findings, process wall time, parsed profile calls, and command failure details. Reports recompute scores from those observations and embedded case ground truth; no generated score is authoritative.

Raw writes and generated Markdown writes use a temporary sibling followed by replacement so an interrupted run cannot partially corrupt history or documentation. Credentials and environment variables are never written.

### Treat the profile as a versioned text boundary

The runner separates the leading JSON value from stdout with `json.JSONDecoder.raw_decode`, then parses the profile table defensively by header and numeric columns. The original text is always retained. Calls whose error contains a truncation/output-limit marker contribute to truncation counts and lenses. Excluding-truncation time is `max(0, process wall time - summed truncated-call elapsed time)`; the raw call data remains available if a future lgtmaybe profile exposes overlapping-call timelines.

### Aggregate repeats without hiding variation

The default is three complete corpus repeats. Recall, precision, score, total wall time, and wall time excluding truncations render as `median [min–max]`. Counts and tokens render as median plus range where repeated values differ. The combined score is the harmonic mean of recall and precision (F1); `clean` remains a separate hard signal so a forbidden hit cannot disappear inside an aggregate.

The runner passes an explicit concurrency value to lgtmaybe and records it. Defaults are one for `ollama` and `openai-compatible`, and six for hosted providers; users can override it. Ollama rows label effort as `<value> (thinking off)` because lgtmaybe disables thinking on that provider.

### Generate two Markdown surfaces from one renderer

`RESULTS.md` is fully generated. `README.md` contains a documented marker pair around a compact leaderboard and per-lens table; only that bounded section is replaced. `bench run` saves raw data and invokes the same reporting function as `bench report`. Sorting by timestamp and slug, fixed numeric formatting, UTF-8, and LF newlines make repeated generation byte-identical.

## Risks / Trade-offs

- [Profile text changes across lgtmaybe versions] → Keep raw output, tolerate unknown rows, and cover known formats with parser fixtures.
- [Subtracting concurrent truncated-call durations is only an estimate] → Label it as derived, retain call evidence, and prohibit wall-time ranking across provider classes.
- [Twenty-plus corpus cases make default runs expensive] → Support repeatable `--case` selection while keeping three repeats as the comparison default.
- [Case line numbers drift during edits] → Validate every catalogued path and line and require versioned replacement after publication.
- [A partial provider failure could look like low recall] → Retain and surface command failures and truncations rather than dropping the observation.

## Migration Plan

There is no existing runtime data to migrate. Implement the tasks in order, run a fake-lgtmaybe end-to-end check, then run the first real local configuration. Before publishing any row, treat corpus case names and contents as immutable.

Rollback consists of reverting implementation commits; raw result files are append-only evidence and must not be silently deleted.

## Open Questions

- Confirm the initial hosted-provider concurrency default against the lgtmaybe version used for the first published run; the runner will pass and record the resolved value explicitly.
- Decide after the first real run whether the compact README should show every historical row or only the newest rows while `RESULTS.md` remains complete.
