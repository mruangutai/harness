# STATE

## Current

- feature: FEAT-09-plan-time-route-check
- phase: build
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-09 (branch feat/FEAT-09-plan-time-route-check)
- head: f823426
- base: 47ed11f (`git merge-base main HEAD`) — re-pinned at the rebase, was ae2443d
- run: none open — no lead dispatched this phase
- status: UNPARKED, in_progress — segment 2

**UNPARKED 2026-08-05. The signal arrived.** FEAT-08 merged (PR #131, main at 47ed11f) and this
worktree is rebased onto it — 7 commits ahead, tree clean, replay verified byte-identical on all
four committed source files. **All seven commit ids were rewritten**; the pre-rebase ids
(685901d, 92d254b, 1185d7f, 06a680f, abddb28, 2a242df) are dangling and must not be cited.

**Both SHA pins were stale, and they failed differently.** `review_sha 1185d7f` is dangling —
`git merge-base --is-ancestor 1185d7f HEAD` returns NO — so it errors loudly and every handoff
claim tagged "verified-at 1185d7f" is unfalsifiable against the branch until re-taken. `base_sha
ae2443d` was the quieter one: a pre-FEAT-08 main commit that still resolves, so `git diff
ae2443d..HEAD` succeeds and simply returns 71 files where the true diff is 14. It is corrected to
47ed11f. SC-11 was re-checked against both and holds at 0 bytes either way.

**review_sha is deliberately NOT_PINNED right now.** User ruling on the timing conflict: INV-6
binds at REVIEWER DISPATCH, not "before anything else", and `validate_panel.timing` requires one
pass against a COMPLETE diff. T-02 still lands a source commit, so pinning now guarantees a second
stale pin. Pin AFTER T-02 and the DECISIONS entry, immediately before the panel.

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

**Segment 2, in this order — the pin has MOVED, do not re-derive from the old note:** T-02 via
eng-lead (APPEND to the 12-entry SCRIPTS array, re-read `run-unit-tests.sh:6` first) → the
DECISIONS entry via product-lead → documentor → **re-pin review_sha to the then-HEAD** → the
four-wide panel → goal-check → distillation → briefing.

## Open Questions

- ~~Q-B BLOCKING — the merge-and-rebase signal.~~ **RESOLVED 2026-08-05.** FEAT-08 merged, this
  tree is rebased, replay verified byte-identical. Unparked.
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
