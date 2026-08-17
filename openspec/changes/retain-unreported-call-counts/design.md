## Context

`parse_review_output()` reads the profile call table by splitting each line against the header columns, then building a `ProfileCall`. Every count goes through `int()`, and the one guard is a blanket `except (KeyError, ValueError): continue` that serves double duty: it skips lines that merely happen to split into the right number of fields — profile summary lines such as `reasoning: 1,296 of ...` — and, unintentionally, it discards genuine call rows carrying an unreported count.

The two cases are easy to tell apart. A summary line fails on a column that is prose or a thousands-separated number; a genuine row fails only on a column rendered as `-`.

## Goals / Non-Goals

**Goals:**

- Retain every genuine call row, including rows whose provider never reported a count.
- Keep observation token totals, truncation lenses, and truncation-adjusted wall time complete.
- Keep the parser rejecting lines that are not call rows.

**Non-Goals:**

- Re-derive historical observations from their retained stdout.
- Change any published metric, score, or ranking.
- Distinguish an unreported reasoning count from a reported zero in observation totals.

## Decisions

**An unreported numeric column parses as zero.** `-` means the count never arrived, and every consumer of these fields sums them. Modelling the distinction would make `ProfileCall.reasoning_tokens` optional and push a `None` case into every sum and every stored record, for no question anyone asks of the data. Zero is what the sums already assume for a call that reported nothing.

`findings` keeps its separate `None` treatment, because the execution spec explicitly requires a reported zero to stay distinguishable from an unreported count — that field answers "did this lens find anything", where the difference is real.

**Non-call lines are still rejected by the same guard.** The blanket `except` stays. Only the meaning of `-` changes, so a summary line whose columns contain prose or `1,296` still raises and is still skipped. This keeps the fix to the one behaviour that is wrong and leaves the line-filtering behaviour that is right.

**Every numeric column is treated alike.** Only `think_tok` is rendered as `-` anywhere in the stored corpus, but handling all numeric columns the same way costs nothing, needs no per-column reasoning, and does not break the first time lgtmaybe leaves a different count unreported.

**Published results stay untouched.** Reporting reads the token and truncation fields stored on each observation and never re-parses stdout, so this fix reaches future runs only. That is verified by regenerating the reports and confirming the leaderboard holds the same models with identical metrics.

## Risks / Trade-offs

- Future token totals rise for models whose rows were dropped, so their figures are not comparable with the same model's published runs → the published runs remain correct evidence of what the old parser recorded, and comparability across a parser fix is a property no stored run ever had.
- An unreported reasoning count becomes indistinguishable from a reported zero → the raw stdout is retained on every observation, so the distinction is recoverable if a question ever needs it.
