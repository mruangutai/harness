# STATE

## Current

- feature: FEAT-16-factory-per-repo-board
- run: .harness/features/FEAT-16-factory-per-repo-board/runs/2026-08-11-02-plan-product/state.yaml
- squad: product
- status: in_review — signature-ready, signature NOT taken
- next: the operator's signature on `BRIEF.md ## Approval` and `plan.yaml approval.status`. Nothing
  else blocks the build phase.

Plan phase COMPLETE and re-baselined on the six-value board. `BRIEF.md` (`## Approval` status
pending, line 352) and `plan.yaml` (11 tasks, 6 REQs, **13 SCs**, **11 decisions**,
`approval.status: pending`) are signature-ready. Both gates re-run by me at `a29ad06`, unpiped:
`check-plan-routes.py` scoped → `0 violation(s) across 1 plan(s)`, exit 0; tree-wide →
`0 violation(s) across 12 plan(s)`, exit 0.

**The board contradiction is resolved, and six is the intended end state.** Both boards now carry
`Backlog → Plan → Ready → Building → Review → Done`. Measured by me on 2026-08-11 via
`gh api graphql`: board 2 items are 211 total — `Done` 118, `Backlog` 82, `Building` 11, with
`Plan`/`Ready`/`Review` at 0. The three ids SC-03 pins all survive (`f75ad846` now `Backlog`,
`47fc9ee4` now `Building`, `98236657` still `Done`), which is what proves the change was a rename
and not a delete-and-recreate. `Backlog`/`Building`/`Done` share ids across both boards — GitHub
default template ids — so every cross-board assertion in the plan compares names, never ids.

**All four of T-07's revised verify clauses PASS live, run read-only by me just now.** T-07 no
longer edits a board: the board work is done, and what remains is a precondition read, one capture,
and the fleet declaration. `.harness/factory/fleet.yaml` is still untouched at `a29ad06` — top-level
`board:` on number 3 — so the declaration rewrite is entirely remaining work.

**An empty `Ready` is CORRECT, not a defect** (D-08). The factory's `ready` station stays pointed at
`Ready`; the 82 unstarted kaya issues are correctly in `Backlog`. The consequence is recorded rather
than absorbed: promotion from `Backlog` to `Ready` is a human decision with no recorded step
anywhere, it is OUT OF SCOPE here, and the only thing this feature owes it is SC-13.

**I was wrong about one thing and the squad caught it.** I told pm that `check-plan-routes.py`
contains no budget logic. It does — `MACHINE_LINES_PER_TASK = 50` at line 280, emitted as a DEC-182
`VIOLATION` at 322-327. I asserted that negative from a truncated grep. The research note's FEAT-14
claim still fails, for the narrower and stronger reason pm found: `BUDGETED_FIELDS` (lines 282-287)
excludes `intent:`, so intent length can never produce a budget violation.

## Open Questions

None outstanding. All six from the previous run are closed — Q1, Q2 and Q3 by the operator's answers
file, Q4/Q5/Q6 by this revision, recorded as D-09, D-10 and D-11. **The question ids below use the
answers file's scheme; the previous STATE.md numbered the last three one lower and that collision is
now removed.**

- Q1 (closed, operator): six IS the intended end state; the main session mutated board 2 mid-plan.
- Q2 (closed, operator): SC-06's live run stays the operator's, `not_met`, and its issue must not be
  one of the 118 in `Done`.
- Q3 (closed, operator): the research note is corrected, not struck.
- Q4 (closed, D-09): T-10 appends DEC-174 am.2 — a closure belongs in the entry that opened the
  loose end.
- Q5 (closed, D-10): DEC-186 is amended, forced by DEC-188's own text — partly overtaken is amended,
  and a strike would remove its live three-purpose read-back bound.
- Q6 (closed, D-11): no prototype gate fires; every literal `files:` entry is `.py`, `.yaml` or
  `.md`, so there is no rendered surface to prototype. Overridable in either direction.
