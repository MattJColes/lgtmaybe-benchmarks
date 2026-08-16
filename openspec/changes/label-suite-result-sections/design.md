## Context

`render_results` can emit two sections in one document: the breadth leaderboard and the long-horizon scaling section. The breadth renderer returns a comparison-key line followed by its table, with no heading. The long-horizon renderer returns a `## Context scaling` heading, a blurb naming its suite and profile, and a `### Model summary` subheading.

The two sections are scored differently. Breadth reports balanced F1 over 70 language/lens cells. Long-horizon reports the closed-world overall score, the harmonic mean of recall against perfect precision less two points per false positive. Both tables expose a `precision` column, so adjacent rendering invites a comparison the scoring rules forbid.

## Goals / Non-Goals

**Goals:**

- Let a reader name the suite behind any published table without leaving the page.
- Say, in the generated output itself, that the two suites are not comparable.
- Keep the hand-authored README paragraph true regardless of which suites have runs.

**Non-Goals:**

- Change scores, eligibility, ranking order, table columns, or suite and profile identifiers.
- Merge the two sections or introduce a combined score.
- Add a breadth run.

## Decisions

Both sections are titled by suite: `## Long horizon` and `## Breadth`. Titling one by suite and the other by phenomenon is what made the current output asymmetric, and the reader's question is which suite a table belongs to. Each section keeps its existing blurb, which already names the suite and profile in its first sentence, so the heading and body agree.

Each suite heading also says `top 10`. The hand-authored results paragraph already states the limit, but repeating it in both generated headings keeps the scope visible beside either table and removes ambiguity when a reader follows a deep link directly to one section.

This supersedes the earlier decision to leave `## Context scaling` untouched. That decision was taken when only one section could ever render, so asymmetry cost nothing; it costs a mislabelled table as soon as breadth runs.

Each blurb carries one sentence stating that the other suite measures a different property and that scores are not comparable across suites. Placing it in generated text rather than hand-authored prose keeps it adjacent to the table it qualifies and regenerates with it.

The hand-authored README paragraph drops its claim that every published run shares the long-horizon key, and instead names both sections and points at the per-section blurbs for the current comparison key.

## Risks / Trade-offs

- [Renaming a published heading breaks a deep link to `#context-scaling`] → Accepted: the anchor is internal to a generated section, and a mislabelled table is the worse outcome.
- [A hand-authored paragraph can drift from generated content again] → Keep the paragraph free of any claim about which suites currently have runs, so no stored result can falsify it.
