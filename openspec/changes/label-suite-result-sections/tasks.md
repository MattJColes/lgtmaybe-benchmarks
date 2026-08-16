## 1. Behavioural Coverage

- [x] 1.1 Add a failing test that the breadth section renders a suite-named heading and a blurb naming its suite and profile
- [x] 1.2 Add a failing test that the long-horizon section renders a suite-named heading
- [x] 1.3 Add a failing test that both sections state scores are not comparable across suites when rendered together

## 2. Reporting

- [x] 2.1 Title both result sections by suite and add the breadth blurb
- [x] 2.2 Add the cross-suite non-comparability sentence to each blurb

## 3. Documentation

- [x] 3.1 Rewrite the hand-authored README results paragraph so it stays correct once breadth runs exist

## 4. Verification

- [x] 4.1 Run pytest, ruff, and mypy with Python 3.12
- [x] 4.2 Regenerate reports and confirm ranking order, rows, and metrics are unchanged
- [x] 4.3 Simulate a stored breadth run and confirm both sections are identifiable and disclaimed

## 5. Clarify the per-suite limit

- [x] 5.1 Add behavioural assertions that each generated suite heading says `top 10`
- [x] 5.2 Update both generated suite headings and regenerate the README
- [x] 5.3 Run pytest, Ruff, mypy, and deterministic report generation with Python 3.12

## 6. Clarify breadth ranking order

- [x] 6.1 Add a behavioural assertion that the breadth section explains its ranking order and leader row
- [x] 6.2 Add the generated breadth ranking note and regenerate the README
- [x] 6.3 Run pytest, Ruff, mypy, strict OpenSpec validation, and deterministic report generation with Python 3.12
