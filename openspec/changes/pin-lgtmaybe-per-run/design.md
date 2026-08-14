## Context

The default command uses `uv tool run lgtmaybe@latest` for every subprocess. A long run can therefore cross a release boundary after its initial version is recorded.

## Goals / Non-Goals

**Goals:**

- Resolve the latest release once and execute an exact package version thereafter.
- Detect any runtime version mismatch before recording another observation.
- Preserve the existing in-progress checkpoint on a late mismatch.

**Non-Goals:**

- Change explicit `--lgtmaybe` executable behavior.
- Add a dependency or alter benchmark scoring.

## Decisions

Parse the successful preflight's `--version` output and return an exact `uv tool run --from lgtmaybe==<version> lgtmaybe` command. This keeps uv as the existing installer and avoids managing cache paths. Before each observation, compare the command's reported version with the run's recorded version; raise `ValueError` on mismatch so existing checkpoint behavior is retained.

## Risks / Trade-offs

- Exact uv invocations still perform lightweight environment resolution → the concrete package constraint prevents release drift.
- Extra version checks add one local subprocess per observation → correctness outweighs the small local cost.
