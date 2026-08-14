## 1. Regression coverage

- [x] 1.1 Add a behavioural test proving default resolution pins the initially reported release.
- [x] 1.2 Add a behavioural test proving a late version mismatch retains an in-progress checkpoint.

## 2. Implementation

- [x] 2.1 Return a concrete uv package command from the latest-release preflight.
- [x] 2.2 Verify the pinned version before each observation.

## 3. Verification

- [x] 3.1 Run pytest, ruff, mypy, and an end-to-end CLI check.
- [x] 3.2 Validate the OpenSpec change.
