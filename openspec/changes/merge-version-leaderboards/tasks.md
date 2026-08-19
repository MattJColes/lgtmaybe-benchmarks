## 1. Behavioural coverage

- [x] 1.1 Rewrite the comparison-key retention and per-key ranking tests: one merged table, older-version rows shown with their version value, ten rows overall, no `Comparison key:` lines.
- [x] 1.2 Update header and blurb assertions for the `lgtmaybe` column in both suite sections.
- [x] 1.3 Verify the revised tests fail against the per-key renderer.

## 2. Rendering and documentation

- [x] 2.1 Merge `_render_breadth_canonical` into one ranked table with an `lgtmaybe` column; add the column to `_render_context_scaling`.
- [x] 2.2 Update README.md and RESULTS.md comparison prose for cross-version ranking with a per-row version.

## 3. Regeneration and verification

- [x] 3.1 Regenerate README.md, RESULTS.md, and the dashboard via `uv run bench report`.
- [x] 3.2 Run pytest, ruff lint, mypy, and verify via git diff that surviving rows keep identical metrics and `results/raw/` is untouched.
