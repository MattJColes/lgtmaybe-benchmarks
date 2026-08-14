## Context

`parse_review_output` matches call rows with a regular expression tied to the original profile columns. Lgtmaybe later appended `think_%`, then `findings`, so otherwise valid rows no longer match and raw observations silently contain `calls: []`.

## Goals / Non-Goals

**Goals:**

- Parse current call rows, including valid zero findings.
- Preserve compatibility with stored legacy profile layouts.
- Keep malformed non-row text ignored as it is today.

**Non-Goals:**

- Reparse or rewrite existing raw result files.
- Change benchmark scoring or infer findings from output-token counts.
- Parse the human-readable profile footer into a second summary model.

## Decisions

Use the table's header as the schema for the following rows and split each row to the header's width, leaving the final error field intact. This removes the version-specific regular expression and naturally tolerates additive columns while keeping the existing typed fields explicit.

Store `findings` as `int | None`: zero means the review lens parsed a valid empty payload, while `None` covers legacy profiles, non-review calls, and parse failures that render a dash.

## Risks / Trade-offs

- Future renames of required columns still stop call parsing → retain focused tests for the supported public column names.
- Human-readable tables are less stable than JSON → keep parsing header-driven and do not infer absent values.
