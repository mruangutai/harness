# STATE

## Current

- feature: BUG-2171-task-structured
- run: 2026-11-21-02-patch-product (open; deliverable complete; digest.md holds no fenced record — lead returns arrived as final-message text, #2171 symptom; close-run refused at digest stage; needs operator `close-run --refused-return --verdict BLOCKED --cycles-used 0 --evidence <authorization> --by <operator>`)
- squad: product
- status: awaiting-user
- mission: patch
- station: plan
- approval: pending (BRIEF.md, plan.yaml) — main session signs; operator ruling rework rounds=1,minutes=45
- revision: SC-04 string-`data` yield (real tool_call handler, red b7af829c / green fix); SC-01 hook bound = refusal line + yield-branch parse; T-01 smoke --max-time=10m; T-01 files + harness-hooks.ts#registerHarnessHooks, tests/unit/omp-hooks.test.ts; lanes 5 rows; plan check 0 failures
- lane: T-01 main-session-direct (DEC-174); no build team
- handoff: none
- cycles_used: 0

## Open Questions

- Q-01: operator authorization for the `--refused-return` close of run 2026-11-21-02-patch-product (blocking for the record, not for signature)
