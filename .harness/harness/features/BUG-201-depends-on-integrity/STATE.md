# STATE

## Current

- feature: BUG-201-depends-on-integrity
- mission: ship — build, QA, SIMPLIFY, the reviewer panel and the goal-check are COMPLETE.
  Both merge blockers are now CLEARED; the feature is merging.
- status: in_review → shipping, station `review`
- source ticket: issue #201 · intake `.harness/notes/grilling-depends-on-integrity-2026-09-06.md`
  · operator ruling `notes/answers-plan-c0.md` (2026-09-07, Q-A)
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity
- branch `feat/BUG-201-depends-on-integrity`, base `af859ee8`. **PR #1476** (base `main`).
  `review_sha` PINNED at `626bb59934b8801bf1abdc86379aa313e021c77b` (the MF-1 fix commit). The
  pin is UNMOVED: everything added after it is `notes/` and `feature.json`, no source file
  differs from the pin.
- approval: SIGNED 2026-09-07 by mruangutai, both fragments.
- budget: cycles_used 3 / 10 · runs 18 / 20 (informational; every run resolved something)
- GitHub mirror: milestone #56, parent #1466, sub-issues #1467–#1472, source issue #201.

**The work — done and verified, unchanged by this run**

- All six tasks `status: done`; QA matrix PASS; SIMPLIFY applied its one permitted fold-in.
- Reviewer panel c1 FAILed on ONE gating finding (MF-1: the new validator was itself code-risk
  grade 3). Fixed by extracting `_depends_on_entries` and `_dangling_edges` — grade 5 / 4 / 4, ten
  hostile inputs byte-identical old vs new, nine suites green. Re-validation c2 PASS,
  `must_fix: []`, `matrix_ok: true`.
- Ship goal-check PASS: SC-01..SC-09 all MET at the pin. No `verify: uat` criterion exists.
- CEO briefing: `notes/ship-review-2026-09-07-ship.md` (+ rendered HTML), backlog B-1..B-13.

**BOTH MERGE BLOCKERS CLEARED — measured, not inferred**

The `integration` check is required on `main` with `enforce_admins: true`, so no override path
exists. It failed on seven record violations, five of them another feature's. Both causes are now
resolved by work that landed on `origin/main`, not by any change to this feature's source.

1. **BUG-1290's five rows** — its three unrecorded panel readers and its two missing handoff
   notes — were reconciled by PR #1503, merged to `origin/main`. Verified at `origin/main`:
   all four `notes/handoff-*.md` present, all three readers `status: ran` in its `plan.yaml`.
   This branch takes them by MERGING `origin/main`, never by rebasing (binding strategy: the
   pinned source review must survive, and a rebase rewrites every reviewed commit).
2. **BUG-201's own two rows** — `notes/handoff-plan.md` and `notes/handoff-build.md` — could not
   be written from a worktree: `check-domain.sh` discarded the worktree root and looked for every
   Authority pointer in the main checkout, where an unmerged feature dir does not exist. That was
   backlog B-1, shipped as BUG-1480 in PR #1497. The guard now carries `_checkout_root(...)` into
   `handoff_done_when.problems`, and both notes are written and pass the shape gate. They are
   marked BACKFILLED in their own comments rather than presented as contemporaneous: they are
   post-pin `notes/` additions only, which the ship strategy permits, and they touch no source.

`check-state.sh` from this worktree now reports ZERO BUG-201 violations. The BUG-1290 rows still
appear here only because this branch has not yet taken the `origin/main` merge; they are absent
from `origin/main` itself. The remaining INV-25/INV-29 rows are standing local worktrees and a
stray `/private/tmp` checkout — workspace conditions, invisible to CI, none of them this feature's.

## Open Questions

- Q-D (RESOLVED, was non-blocking): the handoff-note worktree-root defect. Shipped as BUG-1480 /
  PR #1497. Backlog B-1 is discharged.
- Q-J (RESOLVED, was blocking): the merge. BUG-1290's record violations reconciled by PR #1503;
  BUG-201's two rows written under the BUG-1480 fix. No operator history decision was needed —
  the base is reached by merge, not by rewriting it.
- Q-E (non-blocking, dev-ops chore): `plan-merge.py` has no write route to the top-level `lanes`
  key. Advisor-settled for this plan. Backlog B-2.
- Q-H (non-blocking, harness owner): `code-grade.py`'s pre-image lookup grades an unchanged function
  as changed when only its line offset moves. Raised at c1 and again at c2. Backlog B-3.
- Q-I (non-blocking, harness owner): a relative-path `Edit` resolves against the process cwd rather
  than the assigned worktree; one edit leaked into the main checkout twice in this feature and was
  reverted by hand. Backlog B-8.
