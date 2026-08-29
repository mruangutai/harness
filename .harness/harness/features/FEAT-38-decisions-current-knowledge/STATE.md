# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: .harness/harness/features/FEAT-38-decisions-current-knowledge/runs/2026-08-29-15-validator/state.yaml
- squad: none — the ship phase ended at its user gate
- status: Review — awaiting the operator's UAT result and ship decision

**The briefing is written and is the thing to read**:
`notes/ship-review-2026-08-29-16.md` (rendered view alongside it as `.html`). The working memory for
whoever picks this up is `notes/handoff-ship.md`.

`review_sha` is pinned at **`2557950`**; `base_sha` is `7ebfc9e`. Branch
`feat/FEAT-38-decisions-current-knowledge`. **No PR exists and none was created.**

**Where it stands.** All 20 team tasks are `done` and committed. The blocking qa gate PASSED. The
review panel returned FAIL at cycle 0 on a HIGH — a document-to-shell RCE in the claims checker,
reachable from CI on every pull request — which was fixed, re-pinned, and confirmed closed at cycle 1
by a reviewer that probed for BYPASSES rather than re-running the known vectors. `severity_max` is
now `med` and nothing gates. The goal-check grades **11 of 13 criteria met** at the pin.

**The two open criteria belong to tiers above the squad, which is why no rework is routable and the
last cycle is unspent.** SC-04 is `not_met` pending T-14; SC-13 is `unrun` pending the operator's UAT.

**Three tasks remain, all `main-session-direct` by construction.** T-14 (18 citations across 13
files; the per-line list is in `notes/research-FEAT-38-goalcheck-2557950.md`), T-22 (the per-entry
read-back, REQ-09's evidence) and T-23 (close issue 448). All 13 of T-14's paths return `NOBODY` from
`check-domain.sh --resolve`, re-measured this run — no squad can be given them.

**Budget: cycles 9 of 10, runs 16 of an informational 20.** The last cycle is unspent; both final
grading runs returned clean at zero cost. GitHub mirror open: milestone 31, parent #935, sub-issues
#936–#958. The board is still at `Building` — `gh-sync.py status Review` refused because it requires
every task `done`, which is the mirror working correctly, and the mirror is never a gate.

## Open Questions

All eighteen residual findings are carried as the proposed backlog **B-1 … B-18** in the briefing,
where the operator can strike them by name. Anything not struck becomes a backlog issue on ship
acceptance; anything not listed dies silently, so they are all listed there rather than duplicated
here. The four that need the operator's own answer:

- **Q1 (BLOCKING, operator).** SC-13's UAT at `notes/uat-FEAT-38.md` is unrun. `gates.uat` is
  `blocking_when_uat_criteria_exist`, so the ship decision waits on it. ~15 minutes.
- **Q2 (BLOCKING, main session).** T-14, T-22 and T-23 cannot be dispatched to any squad. SC-04
  closes when T-14 lands.
- **Q3 (operator signature).** Three signed `verify:` blocks — T-10, T-15, T-19 — cannot pass as
  written, while the work behind each is correct. Replacement text is ready in
  `notes/research-verify-block-defects.md` (briefing row B-1).
- **Q4 (operator, possible data loss).** A T-06 member ran `git checkout -- <path>` on the MAIN
  checkout for two generator files. Both are confirmed back at committed content and no stash exists,
  but uncommitted edits held there before 2026-08-29 would have been destroyed. Not knowable from
  inside the worktree (briefing row B-4).

Two harness defects worth the owner's attention, both hit repeatedly this run: the edit/write tool
family resolving worktree-relative paths against the MAIN checkout while reporting success (B-2, one
artifact actually landed there and needs deleting), and a member returning an empty `{}` result that
the `SubagentStop` digest validator did not block (B-3).
