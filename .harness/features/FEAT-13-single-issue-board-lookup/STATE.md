# STATE

## Current

- feature: FEAT-13-single-issue-board-lookup
- run: .harness/features/FEAT-13-single-issue-board-lookup/runs/2026-08-10-03-product/state.yaml
- squad: product
- status: awaiting-user

Mission PLAN is complete and the phase ends here, at the operator's signature. `BRIEF.md` and
`plan.yaml` are on disk, both `pending`. 6 REQs, 10 SCs, 2 tasks, 6 decisions — recounted by me
from the amended files with `safe_load`, not relayed. No blocking question remains. No branch
exists and none was created.

Three runs, two cycles charged, both genuine rework: the lead's send-back of a dangling `SC-19`
pointer inside T-01's dispatch prompt, and the eng review's three `must_fix` routed back to pm.
The eng review itself was first-pass clean and charged zero.

Four questions came up that a measurement could close, and I closed all four myself rather than
returning them: the `resolved_at` SHA (a real ancestor commit carrying only a log and an unrelated
note), the chained `verify:` runtime (6.31s against a 60s bar, both halves green today), the two
artifacts disagreeing about issue #216's board item id (one live query settled it — and confirmed
live that a CLOSED issue's item is still returned, which is the property this whole feature turns
on), and the `grep` false-red hazard in T-01's `verify:` (the one comment mention in decompose is
the bare token and does not match the pattern).

The plan's own contracts check clean: `safe_load` parses it, `feature:` matches the directory,
both `verify:` blocks are literal, all 6 REQs are traced by a task, no dangling SC or REQ
reference survives, and `check-plan-routes.py` returns 0 violations.

## Open Questions

- Q1 (non-blocking, for ratification at signature): the BRIEF's **Goal text changed** during the
  fix cycle. eng found that `claim --issue` will exit `EXIT_REFUSED` (2) instead of
  `EXIT_NOTHING` (1) when the board holds the issue under a repo outside the fleet — a real
  observable delta against the Goal's promise that no tool changes what an operator observes. pm
  amended the Goal and added a Constraint bullet naming the delta rather than leaving the BRIEF
  asserting the opposite of the plan. REQ/SC/task/decision counts are unchanged at 6/10/2/6.
- Q2 (non-blocking, a one-clause option): T-01's receipt is declared in `files:` but nothing in
  its `verify:` checks the receipt exists, unlike T-02 which carries a `test -s` clause. The
  intermediate-green record that mitigates T-01's size is therefore instruction-level, not gated.
  My recommendation is to accept as written — the tests are the gate and the receipt is a process
  artifact — but adding `test -s` costs nothing and is the operator's to call.
