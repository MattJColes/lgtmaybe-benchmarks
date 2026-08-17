## Context

The runner currently requests `--profile` and parses a human table appended to findings JSON on stdout. `lgtmaybe 2.2.0` correctly keeps machine-readable stdout as JSON, sends the human table to stderr, and adds a versioned `--profile-json PATH` contract. Because findings still parse, the current runner silently produces incomplete observations rather than failing.

## Goals / Non-Goals

**Goals:**

- Consume lgtmaybe's versioned structured profile when supported.
- Preserve complete call, token, reasoning, finding-count, error, and truncation evidence.
- Keep older lgtmaybe releases runnable through the existing stdout-table parser.
- Reject successful observations whose requested profile telemetry is missing or unusable.

**Non-Goals:**

- Change scoring, corpus cases, canonical profile settings, or stored published results.
- Import lgtmaybe internals or add a runtime dependency.
- Parse structured logging lines from stderr as a third telemetry contract.

## Decisions

**Prefer `--profile-json` over human output.** The runner will detect support from `review --help`, allocate an observation-local path, pass `--profile-json`, and parse the resulting JSON. This uses the upstream machine contract and avoids coupling to stream routing or table formatting. Parsing stderr was rejected because it mixes structured logs with a human table and would preserve the same brittle text dependency.

**Retain the existing parser only for older executables.** When `--profile-json` is unsupported, the current JSON-plus-table stdout contract remains the compatibility path. This avoids making the latest release a minimum requirement.

**Validate schema version 1 and required call fields at the boundary.** Structured profile calls are converted into the existing `ProfileCall` type using standard-library JSON validation. Unknown additive fields are ignored; missing or incorrectly typed required fields fail the observation rather than becoming zeros. The exact structured source remains in the raw observation, preserving nullable upstream values, while derived finding counts retain their existing zero-versus-unreported distinction.

**Treat missing telemetry as an execution failure.** A successful subprocess with profiling requested but no usable calls raises a concise error. Silent zero telemetry was rejected because it creates apparently valid but diagnostically incomplete paid runs.

## Risks / Trade-offs

- **Older lgtmaybe help output may not advertise the option** → use the established feature-detection pattern and fall back to stdout parsing.
- **A future profile schema is incompatible** → reject unknown schema versions loudly so support is deliberate.
- **The profile JSON write is best-effort upstream** → surface its absence immediately rather than completing a misleading run.
- **Interrupted 2.2.0 checkpoints remain incomplete** → retain them as unscored evidence and restart affected configurations from observation zero.
