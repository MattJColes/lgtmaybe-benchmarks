## ADDED Requirements

### Requirement: Identified result sections
Every generated result section SHALL open with a heading naming the suite it reports, followed by text naming that suite's ID, canonical profile ID, and the property it measures. When a document can contain more than one suite's results, each section SHALL state that suites measure different properties and that scores are not comparable between them. A section SHALL NOT rely on hand-authored prose to identify its suite.

#### Scenario: Identify the breadth section
- **WHEN** complete canonical breadth runs are rendered
- **THEN** their section opens with a heading naming the breadth suite and text naming its suite ID, profile ID, and what it measures

#### Scenario: Identify the long-horizon section
- **WHEN** complete canonical long-horizon runs are rendered
- **THEN** their section opens with a heading naming the long-horizon suite

#### Scenario: Disclaim cross-suite ranking
- **WHEN** both suites' sections are rendered in one document
- **THEN** each section states that the suites measure different properties and that their scores are not comparable

#### Scenario: Keep hand-authored prose durable
- **WHEN** the hand-authored README describes the results section
- **THEN** it makes no claim about which suites currently have stored runs, so no stored result can falsify it
