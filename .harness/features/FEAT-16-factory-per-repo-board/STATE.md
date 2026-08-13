# STATE

## Current

- feature: FEAT-16-factory-per-repo-board
- run: .harness/features/FEAT-16-factory-per-repo-board/runs/2026-08-12-01-eng/state.yaml
- squad: eng
- status: in_progress — build wave A COMPLETE, stopped at the T-07 seam
- next: the operator runs T-07 (`main-session-direct`) — the two-board precondition read,
  `notes/board2-capture.md`, then the `fleet.yaml` rewrite. Then T-09 → T-08 → T-10 → qa → panel →
  goal-check. Full detail in `notes/handoff-build.md`.

**Seven of ten team tasks are done, first pass, zero send-backs.** T-01, T-02, T-03, T-04, T-05,
T-06 and T-11 are `status: done` in `plan.yaml`, committed one per task as `b0dd70a`..`353abc3`.
`cycles_used` stays at 3 — a clean first-pass run adds ZERO (DEC-157).

**The stop is structural, not a choice.** T-07 is `main-session-direct` because
`.harness/factory/fleet.yaml` resolves to NOBODY under `check-domain.sh --resolve`, and the three
remaining team tasks all sit behind it: T-09 and T-08 depend on T-07, T-10 depends on T-08 and T-09.
So the ten team tasks split 7/3 across a round-trip the operator owns. There was no reachable path
to the gates from here.

**All four gates run by me at 353abc3, unpiped.** `run-unit-tests.sh --kind unit` → 72 scripts PASS,
exit 0. `--kind integration` → 80 scripts PASS, exit 0. Zero FAIL lines in either.
`check-plan-routes.py` scoped → `0 violation(s) across 1 plan(s)`, exit 0, with T-07 correctly
reading `OK T-07: declared main-session-direct (.harness/factory/fleet.yaml ungranted)` — no
DEVIATION line on this plan, which is what plan decision (d) was written to buy. Tree-wide →
`0 violation(s) across 8 plan(s)`, exit 0. `check-state.sh` → exit 0.

**Two criteria measured mid-flight, so the successor is not guessing.** SC-11's first grep is down
from 18 lines across 7 files to 4 lines across 2, and every survivor is a site T-08's own intent
names. SC-10 holds: the diff `a7c429c..HEAD` intersects none of the four DEC-174 carve-out scripts.
SC-12's four greps are all still 0; T-10 alone moves them.

**The GitHub mirror did not run.** `gh-sync.py open` was blocked by the permission classifier, not
by the environment. Recorded as the one-line SKIP the playbook prescribes — the mirror is never a
gate — and raised to the operator rather than retried.

## Open Questions

- Q1 (non-blocking, relayed for the record): T-05 added an env-gated `GH_CALL_LOG` recorder to the
  fake-gh stub and eng-lead raised it against the task's two-site bound. Assessed IN MANDATE by the
  lead and by me: the case T-05's intent requires cannot assert on recorded gh invocations without a
  recorder, and the recorder is opt-in — read at `test-factory-integration.py:95` via
  `os.environ.get`, with line 1033 the only setter — so no existing case changes behaviour. Recorded
  in the T-05 commit message rather than left in a digest. No decision needed.
