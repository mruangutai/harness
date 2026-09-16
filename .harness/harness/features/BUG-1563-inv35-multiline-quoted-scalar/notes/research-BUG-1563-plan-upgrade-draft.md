# Research — BUG-1563 plan upgrade draft

The approval-pending plan now adds only the unit-kind behavioral coverage required by QA finding V-01; the delivered T-01 checker behavior and integration coverage remain unchanged.

- Operator authority: `notes/answers-upgrade-plan.md` authorizes the patch-to-plan upgrade solely to satisfy the configured hard matrix, with no waiver or broader coverage.
- Matrix basis: `.harness/harness.json` requires `unit` for a `bugfix` that touches runtime code, and the `unit` kind is active with detection under `tests/unit/**`.
- Added scope: SC-03 and T-02 create `tests/unit/test-check-state-inv35.py`, covering the two multiline quoted outcomes and the exact unquoted positive control through the real checker.
- Ordering: T-02 depends on completed T-01. T-01 remains `done` with its original files, traces, verify command, and intent.
- Routing: T-02 and its new test surface are `main-session-direct`; DEC-174 includes every test that vouches for an enforcement gate, and DEC-179 requires declaring that carve-out at plan time.
- Approval: `plan-merge.py apply` reset the prior plan approval to `pending`; the BRIEF is also pending. No approval was signed in this run.
- Verification: the required `plan-merge.py check` resolved both T-01 anchors and the prospective T-02 file anchor, resolved all traces/routes, and exited 0 with 0 failures.

Open questions: none.
