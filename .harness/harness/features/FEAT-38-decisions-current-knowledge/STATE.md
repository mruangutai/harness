# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: .harness/harness/features/FEAT-38-decisions-current-knowledge/runs/2026-08-29-17-validator/state.yaml
- squad: none — the resume segment is complete and stopped at two operator decisions
- status: Review — awaiting the operator's UAT result and a ruling on the cycle budget

**The briefing is the thing to read**: `notes/ship-review-2026-08-29-18.md` (rendered view alongside
it as `.html`). It SUPERSEDES `notes/ship-review-2026-08-29-16.md`. Working memory for whoever picks
this up is `notes/handoff-ship.md`.

`review_sha` is re-pinned at **`48bbe7e`** (was `2557950`); `base_sha` is `7ebfc9e`. Branch
`feat/FEAT-38-decisions-current-knowledge`. **No PR exists and none was created.**

**Where it stands.** The operator resolved the three carved-out `main-session-direct` tasks and they
landed: T-14 `e88182c`, T-22 `c1d657b`, T-23 `7cb69a9`. All 23 tasks now read `done` in `plan.yaml`,
so `gh-sync.py status Review` ran and succeeded — parent #935 and sub-issues #936–#958 are all at the
`Review` station.

Because the tip moved, `review_sha` was re-pinned at `48bbe7e` and **every automated gate was
re-established there**:

- **qa PASS** — exit 0, 0 `FAIL`, 0 anchored `^KIND-DRIFT:`, index diff-clean, checkers discovering
  20 anchors / 11 claims (`notes/qa-2026-08-29-11-validator.md`).
- **Review panel PASS** — `severity_max: med`, `must_fix` empty; all three reviewers examined the
  named file set rather than self-scoping out, and adjudicated the three citation questions
  (`notes/review-harness-{code,security,ui}-reviewer-c2.md`).
- **Goal-check PASS — 12 of 13 SCs met** (`notes/research-FEAT-38-goalcheck-48bbe7e.md`). **SC-04
  flipped `not_met` → `met`**, its sweeps run per id for all fifteen ids and proved able to report
  red by a positive control. SC-13 remains `unrun`, operator-owned.

**Two things stop this, both the operator's.**

1. **SC-13's UAT is unrun.** `gates.uat` is `blocking_when_uat_criteria_exist`, so the ship decision
   waits on it. `notes/uat-FEAT-38.md` is `status: ready` and its stale `2557950` header was
   repointed to `48bbe7e` this run.
2. **The cycle budget is crossed: `cycles_used` 11 of `max_total_cycles` 10.** Both new cycles were
   lead-internal send-backs during re-verification of already-passing gates — qa's self-caught false
   6-`FAIL` baseline reading, and the ui-reviewer's self-corrected high→med rating. Neither changed a
   line of production code and no fix cycle was routed to a builder. Raising the budget is a user
   decision recorded in `feature.json`.

**Budget: cycles 11 of 10 (CROSSED), runs 19 of an informational 20.** GitHub mirror open:
milestone 31, parent #935, sub-issues #936–#958 at `Review`.

## Open Questions

Twenty-three residual findings are carried as the proposed backlog **B-1 … B-23** in
`notes/ship-review-2026-08-29-18.md`, where the operator can strike them by name. Anything not struck
becomes a backlog issue on ship acceptance; anything not listed dies silently, so they are all listed
there rather than duplicated here. B-5 is now marked RESOLVED. Five rows are new this run: B-19
(the renderer blanking code blocks), B-20 (renderer contrast), B-21 (an imprecise joint citation,
inherited not introduced), B-22 (no guard on `DEC-N` citations in `.claude/**`) and B-23 (a digest
validator that accepted `not_met` on a `verify: uat` criterion).

The four needing the operator's own answer:

- **Q1 (BLOCKING, operator).** SC-13's UAT at `notes/uat-FEAT-38.md` is unrun. ~15 minutes.
- **Q2 (BLOCKING, operator).** The cycle budget is crossed at 11 of 10. Raise it, or accept the
  crossing and ship on the UAT result.
- **Q3 (operator signature).** Three signed `verify:` blocks — T-10, T-15, T-19 — cannot pass as
  written, while the work behind each is correct. Replacement text is preserved verbatim in
  `notes/research-verify-block-defects.md` (briefing row B-1).
- **Q4 (operator, possible data loss).** A T-06 member ran `git checkout -- <path>` on the MAIN
  checkout for two generator files. Ruled unknowable and not to be inferred; recorded so it is not
  silently dropped (briefing row B-4).
