# STATE

## Current

- feature: FEAT-09-plan-time-route-check
- phase: build
- worktree: /Users/molchairuangutai/GitHub/harness-FEAT-09 (branch feat/FEAT-09-plan-time-route-check)
- head: 2a242df
- run: none open — no lead dispatched this phase
- status: PARKED, awaiting-user

**PARKED BY USER RULING. Dispatch nothing until the merge-and-rebase signal arrives.**

Three of four tasks are DONE and committed. I verified every `verify:` myself rather than
relaying the report: the resolve probe prints `OK`, the domain test exits 0, the unit suite is
13/13, `check-docs.sh` and `check-state.sh` both exit 0. The load-bearing claim holds — both
matcher functions hash IDENTICALLY either side of the change, so exactly one matcher survives.
The stdin read now sits in the `else` branch; an open pipe that hung past 10s answers in 0.21s.
The hook path is unchanged, checked with my own payload files.

**Three rulings received and recorded.** The review panel waits for ONE post-rebase pass rather
than running now — the panel must re-run after the last task regardless, and a pin taken now
goes stale at the rebase. The accepted cost is on the record: the write-permission guard stays
committed with zero independent review until the concurrent feature merges. That is a window
that existed, and the briefing must name it as such.

**There is no cost line any more.** I verified the mandate is gone from the main checkout's
playbook (grep returns nothing) rather than accepting it. The budget field is removed here. My
own copy of the playbook still carries the old mandate, so until the rebase I am governed by
text that is already superseded — a seam worth naming rather than assuming.

On resuming, in order: re-pin the review SHA to post-rebase HEAD before anything else, re-check
that the three task commits replayed byte-identical, then the last task, the decisions entry,
the four-wide panel, the goal-check, distillation and the briefing.

## Open Questions

- Q-B BLOCKING — the merge-and-rebase signal. Nothing proceeds without it; I am parked, not
  working. Segment 1 is committed, so the rebase has nothing uncommitted to collide with.
- Q-G NON-BLOCKING, HARNESS DEFECT — the documented 200-line cap on this file is **not
  mechanically enforced**. A 205-line write succeeded, no registered hook implements a
  state-file shape gate, and the invariant checker has no such check. The rule is prose-only,
  which is the exact enforcement shape this feature's own brief rejected. I trimmed to 186 by
  hand; the next agent may not know to.
- Q3 NON-BLOCKING — promote the route checker to a state-check invariant once the concurrent
  feature releases that file?
- Q4 NON-BLOCKING — the checker copies the state checker's task-block regex rather than sharing
  it. Consolidate later, or accept two copies?
- Q5 NON-BLOCKING — two historical plans use a token this feature retires. Leave them as
  history, or normalise them?
