## Why

The benchmark stores current lgtmaybe profiles but parses every provider-call list as empty because its fixed regular expression predates the `think_%` column. The merged finding-flow diagnostic adds a `findings` column, so the harness must understand the table it preserves before new OpenRouter evidence is useful.

## What Changes

- Parse profile call rows from their header instead of one historical fixed column layout.
- Retain each call's parsed finding count when the profile reports one.
- Keep older profiles without reasoning-share or finding-count columns readable.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-execution`: Preserve provider-call evidence from legacy and current lgtmaybe profile tables.

## Impact

The runner's profile parser, stored call shape, and focused parser tests change. Benchmark execution, scoring, reports, and existing raw evidence remain unchanged.
