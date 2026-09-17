# STATE

## Current

- feature: FEAT-53-metrics-dashboard
- run: .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-17-03-eng/digest.md
- squad: engineering
- status: awaiting-user

Build entry is open and projected to Building. T-01 through T-09 where dependency-ready, plus T-23, T-24, T-25 and T-30, are recorded done. Engineering run 2026-09-17-03-eng closed PASS after transcribing six eligible stale-path amendments; its two internal send-backs moved the durable cycle total to 19 of 20. T-30 is accepted through BUG-1724's host task-result token stamp rather than transcript summation, with that implementation judgement in the ledger.

Execution stopped on a new constraint conflict. DEC-174 says FEAT-53 must not touch hooks, validators or gate scripts and requires escalation if a task appears to. Main-session-direct T-25 was committed at `c2483f7a` and modifies `.claude/skills/harness/bin/check-state.py` to add INV-45. The commit also contains the task's lifecycle parser, intake transitions, reviewed corpus backfill and tests, so it cannot be accepted or partially removed without an operator scope ruling. A `continue: stop` judgement records the exact conflict. No later dependent task has started.

Historical ledger backfill is recorded for every 2026-09-01 FAIL run, and `notes/handoff-plan.md` carries the required `## Done when` shape. Digest parser defect #1819 remains honestly recorded in the previous run's component close. The current worktree contains the closed-run ledger, amendment record, receipts and observations pending the orchestrator evidence commit.

## Open Questions

- Blocking: DEC-174 forbids validator/gate changes, but signed T-25 requires and commit `c2483f7a` contains an INV-45 change to `check-state.py`. Which authority should govern? Recommendation: keep DEC-174, revert T-25 as one atomic commit, and route T-25 back through product for an approved design that does not alter validator/gate scripts before resuming.
- Blocking before ship: how should the operator-approved historical `max_total_cycles: 20` ceiling be ledgered when `raise-cycles --to 20` refuses a retain ruling? The record must not be hand-edited; retain this as the known INV-39 tool contradiction.
