# Repository instructions

- Follow the active change under `openspec/changes/`; implement with `/opsx:apply` and mark each verified task complete immediately.
- Use Python 3.12 through `uv`. Write behavioural pytest tests before implementation, then run pytest, ruff, and mypy.
- Two suites exist and measure orthogonal properties; neither supersedes the other, and their scores are never ranked against each other even though both use the F0.5 formula. `long-horizon` varies diff size for one language to test whether recall survives a growing diff. `breadth` varies language and review lens at small diff sizes to test coverage. Both have published runs. Name a suite for the property it measures, never for a release sequence.
- Published corpus cases are immutable after a raw result references them. Add a versioned replacement instead of editing one.
- Stored raw results keep the suite and profile ID recorded at run time. A rename adds an entry to `SUITE_ALIASES` or `PROFILE_ALIASES` in `reporting.py` so published runs keep ranking and display one name; it never rewrites `results/raw/`. After any rename, confirm the leaderboard still holds the same models with identical metrics.
- Scoring is closed-world: every model finding that does not match an uncaught planted finding is a false positive, even if it may identify a real uncatalogued issue. Overall score is F0.5 — `1.25 × precision × recall / (0.25 × precision + recall)`, zero when the denominator is zero — weighting precision twice as heavily as recall; breadth applies it to balanced recall as balanced F0.5. Never excuse or manually reclassify a false positive in an existing run; add a versioned corpus case for future runs.
- `README.md` result markers and all of `RESULTS.md` are generated from `results/raw/`; never edit their generated tables by hand.
- Invoke lgtmaybe only as an external command. Never store or print provider credentials, API keys, or unrelated environment variables.
- Prefer the standard library and the smallest clear implementation. Do not add runtime dependencies without an approved OpenSpec update.
