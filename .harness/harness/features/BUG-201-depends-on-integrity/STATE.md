# STATE

## Current

- feature: BUG-201-depends-on-integrity
- mission: ship — **SHIPPED.** PR #1476 merged to `main` 2026-09-08 as merge commit `a063a738`.
- status: shipped, station `done`
- source ticket: issue #201 (CLOSED COMPLETED) · intake
  `.harness/notes/grilling-depends-on-integrity-2026-09-06.md` · operator ruling
  `notes/answers-plan-c0.md` (2026-09-07, Q-A)
- branch `feat/BUG-201-depends-on-integrity`, base `af859ee8`. **PR #1476 MERGED**, recorded in
  `feature.json` as `pr: 1476`.
- `review_sha` PINNED at `626bb59934b8801bf1abdc86379aa313e021c77b` and UNMOVED — it is an
  ancestor of `origin/main`, and every commit added after it is `notes/`, `STATE.md` or
  `feature.json`. No source file differs from the reviewed tree.
- approval: SIGNED 2026-09-07 by mruangutai, both fragments.
- budget: cycles_used 3 / 10 · runs 18 / 20 (informational; every run resolved something). This
  ship run added NO cycles: nothing was reworked, and both blockers were cleared by other features.
- GitHub: milestone #56 CLOSED (6/6). Parent #1466, sub-issues #1467–#1472 and source #201 all
  CLOSED COMPLETED and all eight cards at board station **Done** (verified individually, not sampled).

**The work — done, verified, and landed**

- All six tasks `status: done`; QA matrix PASS; SIMPLIFY applied its one permitted fold-in.
- Reviewer panel c1 FAILed on ONE gating finding (MF-1: the new validator was itself code-risk
  grade 3). Fixed by extracting `_depends_on_entries` and `_dangling_edges` — grade 5 / 4 / 4, ten
  hostile inputs byte-identical old vs new, nine suites green. Re-validation c2 PASS,
  `must_fix: []`, `matrix_ok: true`.
- Ship goal-check PASS: SC-01..SC-09 all MET at the pin. No `verify: uat` criterion exists.
- The rule lives at exactly one site, `_validate_plan_depends_on` in `harness_yaml.py:343`, inside
  `validate_plan_doc`'s call tree — SC-04's single-implementation requirement, confirmed on `main`.
- CEO briefing: `notes/ship-review-2026-09-07-ship.md` (+ rendered HTML), backlog B-1..B-13.

**How the two merge blockers were cleared — neither was this feature's code**

The `integration` check is required on `main` with `enforce_admins: true`, so no override existed.
It failed on seven record violations, five of them another feature's.

1. **BUG-1290's five rows** — three unrecorded panel readers, two missing handoff notes — were
   reconciled by PR #1503 on `origin/main`. This branch took them by **MERGE, never rebase**:
   `gh pr update-branch` produced merge `69af7582` with parents `202995a1` and `9ec2a037`, so every
   reviewed commit survives by id and the pin still resolves. A rebase would have rewritten them.
2. **BUG-201's own two rows** — `notes/handoff-plan.md` and `notes/handoff-build.md` — could not be
   written from a worktree until BUG-1480 (PR #1497) taught `check-domain.sh` to carry
   `_checkout_root(...)` into `handoff_done_when.problems`. Both are now written, and
   `notes/handoff-validate.md` followed once the `done` station required it. All three are marked
   BACKFILLED in their own comments rather than presented as contemporaneous, and all three are
   `notes/` additions that touch no source.

Integration went **green** on the merged head and PR #1476 merged with a merge commit.

## Open Questions

- Q-D (RESOLVED, was blocking B-1): the handoff-note worktree-root defect — shipped as BUG-1480 /
  PR #1497. No backlog row is needed for it.
- Q-J (RESOLVED, was blocking): the merge. Cleared as above; no operator history decision was
  needed, because the base was reached by merge rather than by rewriting it.
- Q-K (non-blocking, main session): the standing worktree at
  `.claude/worktrees/harness/BUG-201-depends-on-integrity` must be removed now the feature is
  terminal (INV-29). Removal is not an orchestrator's act — it is the main session's or the
  post-merge hook's, from outside the tree.
- Q-E (non-blocking, dev-ops chore): `plan-merge.py` has no write route to the top-level `lanes`
  key. Advisor-settled for this plan. Backlog B-2.
- Q-H (non-blocking, harness owner): `code-grade.py`'s pre-image lookup grades an unchanged function
  as changed when only its line offset moves. Raised at c1 and again at c2. Backlog B-3.
- Q-I (non-blocking, harness owner): a relative-path `Edit` resolves against the process cwd rather
  than the assigned worktree; one edit leaked into the main checkout twice in this feature and was
  reverted by hand. Backlog B-8.
