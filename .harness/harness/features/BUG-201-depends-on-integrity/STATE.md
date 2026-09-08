# STATE

## Current

- feature: BUG-201-depends-on-integrity
- mission: ship — build, QA, SIMPLIFY, the reviewer panel and the goal-check are COMPLETE and the
  pull request is open. **The merge is BLOCKED on two record conditions, neither of them this
  feature's code and neither inside this feature's authority.**
- status: blocked (awaiting the operator's decision on the merge), station `review`
- source ticket: issue #201 · intake `.harness/notes/grilling-depends-on-integrity-2026-09-06.md`
  · operator ruling `notes/answers-plan-c0.md` (2026-09-07, Q-A)
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity
- branch `feat/BUG-201-depends-on-integrity`, base `af859ee8`, pushed. **PR #1476** (base `main`).
  `review_sha` PINNED at `626bb59934b8801bf1abdc86379aa313e021c77b` (the MF-1 fix commit); commits
  after it add notes and feature.json only, no source file differs from the pin.
- approval: SIGNED 2026-09-07 by mruangutai, both fragments.
- budget: cycles_used 3 / 10 · runs 18 / 20 (informational; every run resolved something)
- GitHub mirror: milestone #56, parent #1466, sub-issues #1467–#1472, source issue #201 — all seven
  cards at the `review` station. `pr` stays null in feature.json: `record-pr` derives from a MERGED
  pull request and this one has not merged.

**Where the feature stands — the work is done and verified**

- All six tasks `status: done`; QA matrix PASS; SIMPLIFY applied its one permitted fold-in.
- Reviewer panel c1 FAILed on ONE gating finding (MF-1: the new validator was itself code-risk
  grade 3). Fixed by extracting `_depends_on_entries` and `_dangling_edges` — grade 5 / 4 / 4, ten
  hostile inputs byte-identical old vs new, nine suites green. Re-validation c2 PASS,
  `must_fix: []`, `matrix_ok: true`.
- Ship goal-check PASS: SC-01..SC-09 all MET at the pin. No `verify: uat` criterion exists.
- CEO briefing: `notes/ship-review-2026-09-07-ship.md` (+ rendered HTML), backlog B-1..B-13.

**THE MERGE BLOCKER — measured, not inferred**

`main` requires the `integration` check and `enforce_admins` is true, so no override path exists.
The check fails with seven violations, five of which are another feature's.

1. **The branch base never reached `origin/main`.** `af859ee8` is not an ancestor of `origin/main`
   (merge-base `41c16c73`), so PR #1476 carries 40 commits of which only 12 are BUG-201's; the
   other 28 are BUG-1290-factory-claim-repo-root, merged into local `main` and never pushed, with
   no PR recorded (INV-28). Its five record violations — INV-32 for readers `goalcheck`, `scope`,
   `should-not-exist`, plus missing `handoff-build.md` and `handoff-validate.md` — enter this PR's
   CI. Not touched: recording a reader that did not run would falsify the record, and they belong
   to a feature this run was not dispatched against.
2. **BUG-201's own two rows are the harness defect below.** `notes/handoff-plan.md` and
   `notes/handoff-build.md` cannot be written for a feature that exists only in a worktree.
   `check-domain.sh`'s shape rel (`:1141-1149`) takes the checkout-relative path from
   `harness_boundary.checkout_relative` and DISCARDS the worktree root, then passes that rel with
   the MAIN root into `handoff_done_when.problems` (`:1748`), so every Authority pointer is looked
   for in a checkout where the unmerged feature directory does not exist. Re-measured today: the
   live guard refused the write and named all three pointers. **Not worked around** — a pointer
   bent to satisfy the gate would be a false authority. Filed as backlog B-1; the fix is one line
   (carry `_ck[0]` as the root for the handoff check) and it is a harness change, not a BUG-201
   change, so this run did not make it: it is unplanned, unreviewed, and would not clear CI anyway
   while condition 1 stands.

Fixing B-1 unblocks BUG-201's two rows and every future worktree feature. Condition 1 needs an
operator decision about BUG-1290's unpushed work; it will redden the first PR that pushes local
`main`'s backlog whatever else changes.

## Open Questions

- Q-J (BLOCKING, operator): the merge. Fix B-1, and decide what happens to BUG-1290's five record
  violations — or give BUG-201 a base that is on `origin/main`, which is a history decision no agent
  here has the authority to make.
- Q-D (non-blocking, harness owner): the handoff-note defect. Backlog B-1.
- Q-E (non-blocking, dev-ops chore): `plan-merge.py` has no write route to the top-level `lanes`
  key. Advisor-settled for this plan. Backlog B-2.
- Q-H (non-blocking, harness owner): `code-grade.py`'s pre-image lookup grades an unchanged function
  as changed when only its line offset moves. Raised at c1 and again at c2. Backlog B-3.
- Q-I (non-blocking, harness owner): a relative-path `Edit` resolves against the process cwd rather
  than the assigned worktree; one edit leaked into the main checkout twice in this feature and was
  reverted by hand. Backlog B-8.
