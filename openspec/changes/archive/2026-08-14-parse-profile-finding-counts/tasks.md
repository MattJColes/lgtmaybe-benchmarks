## 1. Regression coverage

- [x] 1.1 Add a parser test covering legacy, reasoning-share, and finding-count profile columns.
- [x] 1.2 Verify the current parser reproduces the empty-call defect.

## 2. Profile parsing

- [x] 2.1 Parse call rows from the emitted header and retain optional finding counts.
- [x] 2.2 Preserve existing truncation and token accounting behavior.

## 3. Verification

- [x] 3.1 Run focused and full tests, Ruff, mypy, strict OpenSpec validation, and a stored-profile replay.
