# Repository instructions

- Follow the active change under `openspec/changes/`; implement with `/opsx:apply` and mark each verified task complete immediately.
- Use Python 3.12 through `uv`. Write behavioural pytest tests before implementation, then run pytest, ruff, and mypy.
- Published corpus cases are immutable after a raw result references them. Add a versioned replacement instead of editing one.
- Scoring is closed-world: every model finding that does not match an uncaught planted finding is a false positive and lowers precision, even if it may identify a real uncatalogued issue. Never excuse or manually reclassify it in an existing run; add a versioned corpus case for future runs.
- `README.md` result markers and all of `RESULTS.md` are generated from `results/raw/`; never edit their generated tables by hand.
- Invoke lgtmaybe only as an external command. Never store or print provider credentials, API keys, or unrelated environment variables.
- Prefer the standard library and the smallest clear implementation. Do not add runtime dependencies without an approved OpenSpec update.
