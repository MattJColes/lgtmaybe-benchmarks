## 1. Checkpointed Raw Evidence

- [x] 1.1 Write failing tests for a late case failure retaining completed observations as an in-progress record, and for a finished run being marked complete.
- [x] 1.2 Reserve one raw result path per configuration run and write it atomically after every completed observation.
- [x] 1.3 Finalize the reserved record as complete after the last repeat and case, before reports are regenerated.

## 2. Reporting

- [x] 2.1 Write failing tests for in-progress records being excluded from the leaderboard, rendered as incomplete, and for status-free records still scoring.
- [x] 2.2 Partition raw runs by status in the report renderer and add the incomplete-runs section.

## 3. Verification

- [x] 3.1 Run pytest, ruff, and mypy in the project virtual environment.
