# Sign-off — FEAT-2340 (2026-11-22)

Decided by the advisor (fable-advisor), standing in for the operator under goal mode. The operator delegated questions, plan changes and approvals.

- **Signed as written.** BRIEF SC set and plan T-01 → T-02, both main-session-direct: T-01 because its guidance paths are owned by nobody (DEC-179), T-02 under DEC-174. The advisor verified that the plan faithfully carries the grilling, checking each point against the worktree at 62f608fa.
- **Rework ruling:** 2 rounds / 90 min, the propose-rework default.
- **Overrule:** none. All six panel findings are resolved, severity_max med.
- **Verify-runtime gap (55 s):** T-02's mandated pre-edit baseline run is the measurement.
  - If the unmodified baseline exceeds 55 s, the main session is authorized to raise the supervised aggregate deadline to 300 s for both the baseline and post-edit runs, recording the measured baseline and this authorization in run evidence.
  - If the baseline fits but the post-edit run times out or FAILs, that is a refactor failure: fix the code, with no test rewrites and no further budget movement.
- **Executor notes:**
  - The frozen fixture is at tests/integration/fixtures/prior-check-domain.fixture.
  - Only the comment at check-domain.py:1483-1484 is stale; the test-check-domain.py reference at :124 stays.
