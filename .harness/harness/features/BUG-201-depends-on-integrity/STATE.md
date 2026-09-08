# STATE

## Current

- feature: BUG-201-depends-on-integrity
- mission: ship — build, QA, SIMPLIFY, the reviewer panel and the goal-check are all COMPLETE. The
  remaining acts are the pull request, the merge, and post-merge terminalization.
- status: in_review → shipping, station `review` (plan.yaml `status: review`)
- source ticket: issue #201 · intake `.harness/notes/grilling-depends-on-integrity-2026-09-06.md`
  · operator ruling `notes/answers-plan-c0.md` (2026-09-07, Q-A)
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity
- branch `feat/BUG-201-depends-on-integrity`, base `af859ee8`.
  `review_sha` PINNED at `626bb59934b8801bf1abdc86379aa313e021c77b` (the MF-1 fix commit). Commits
  after the pin add notes and feature.json only; no source file differs from the pin.
- approval: SIGNED 2026-09-07 by mruangutai, both fragments (plan.yaml `approval.status: approved`,
  BRIEF.md `## Approval`).
- budget: cycles_used 3 / 10 · runs 18 / 20 (informational; every run resolved something)
- GitHub mirror: milestone #56, parent #1466, sub-issues #1467–#1472 (T-01..T-06), source issue
  #201. All seven cards written to the `review` station.

**Where the feature stands**

- All six tasks `status: done`; QA matrix PASS (`notes/qa-harness-qa-c1.md`); SIMPLIFY applied its
  one permitted fold-in (`refuse(stream=...)`) and deferred the diagnostic double-path finding.
- Reviewer panel c1 (`runs/2026-09-07-05-validator`) returned FAIL on ONE gating finding: MF-1,
  `_validate_plan_depends_on` was code-risk grade 3 in production code. Fixed by extracting
  `_depends_on_entries` and `_dangling_edges` (`runs/2026-09-07-04-eng`) — grade 5 and 4/4, ten
  hostile inputs byte-identical old vs new, nine suites green.
- Re-validation c2 (`runs/2026-09-07-06-validator`) PASS, `must_fix: []`, `matrix_ok: true`.
  Security and UI were NOT re-dispatched at c2 — the delta touches one file and moves no surface —
  and that carry expires the moment `harness_yaml.py`'s raised text or call surface changes again.
- Ship goal-check (`runs/2026-09-07-05-product`) PASS: SC-01..SC-09 all MET, each by its own
  declared method at the pin. No criterion declares `verify: uat`, so no UAT gate applies.
- CEO briefing written: `notes/ship-review-2026-09-07-ship.md` (+ rendered HTML). It carries a
  twelve-row proposed backlog, B-1..B-12.

**Records reconciled this session**

- `panel.readers` was missing the `goalcheck` row (check-state.sh INV-32). pm appended it through
  `plan-merge.py set-panel`; 19 findings and the signature untouched (`runs/2026-09-07-04-product`).
- The GitHub mirror had never run (INV-26). `gh-sync.py open` then `gh-sync.py status … review`.

**HARNESS DEFECT, re-measured today with the live refusal — the handoff notes.**
`notes/handoff-plan.md` could not be written, and `handoff-build.md` / `handoff-validate.md` cannot
be either, for a feature that exists only in a worktree. `check-domain.sh`'s shape rel (`:1141-1149`)
takes the checkout-relative path from `harness_boundary.checkout_relative` and DISCARDS the worktree
root, then passes that rel with the MAIN root into `handoff_done_when.problems` (`:1748`). Every
Authority pointer resolves through that base, so `.harness/harness/features/BUG-201-.../plan.yaml`
is looked for in the main checkout, where the unmerged feature dir does not exist. Today's refusal
named all three pointers verbatim. **Not worked around**: a pointer bent to satisfy the gate would
be a false authority. The three notes are therefore written AFTER the merge, from the main checkout,
where the feature dir resolves — the same content, one commit later. Filed as backlog B-1.

## Open Questions

- Q-D (non-blocking, harness owner): the handoff-note defect above. Backlog B-1.
- Q-E (non-blocking, dev-ops chore): `plan-merge.py` has no write route to the top-level `lanes`
  key. Advisor-settled for this plan. Backlog B-2.
- Q-H (non-blocking, harness owner): `code-grade.py`'s pre-image lookup grades an unchanged function
  as changed when only its line offset moves. Raised at c1 and again at c2. Backlog B-3.
- Q-I (non-blocking, harness owner): a relative-path `Edit` resolves against the process cwd rather
  than the assigned worktree; one edit leaked into the main checkout twice in this feature and was
  reverted by hand. Backlog B-8.
