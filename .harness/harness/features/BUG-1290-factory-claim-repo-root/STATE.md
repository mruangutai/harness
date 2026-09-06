# STATE

## Current

- feature: BUG-1290-factory-claim-repo-root
- run: none in flight — B-16 fix cycle complete, back at the operator ship decision
- squad: none
- status: awaiting-user

The operator struck briefing row **B-16** and directed the committed test before the ship decision
(`notes/answers-2026-09-06-b16.md`). **B-16 is closed.** `tests/unit/test-factory-claim.py` case
`5b` now runs through a shared scenario builder (`_run_5b_scenario`) and a shared predicate
(`_5b_property_holds`); new case **`5g`** reuses both under a mutant `_BlockerCache` SUBCLASS whose
issue-map lookup routes every repository through the first repository seen for a feature id — the
`feature`-only key — and asserts `5b`'s property is FALSE under it. Test-only: production
byte-identical to the previous pin `7104aa43`, +57/-8 in one file.

Orchestrator's own four-arm control, measured independently of every squad on an out-of-tree
scaffold copy (`/tmp/b16-orch-control.py`): intact 125/125; harness fixture's `depends_on=["T-99"]`
deleted → `5b` ok but **`5g` FAIL** (the directive, discharged — that deletion used to leave 124/124
green); harness fixture's issue map emptied → **`5b` FAIL**, `5g` ok (the two cases defend DIFFERENT
fragments); the mutant's delegating call replaced by a bare `raise` → both green, which is briefing
row **B-27**, a non-live fail-open in `5g`'s negation.

Gates: eng PASS (0 send-backs, second persona re-measured); qa test-matrix **PASS**
(`matrix_ok: true`, `must_fix: []`) after its lead sent it back once for inheriting eng's
measurement; simplify an **empty pass** over four angles, nothing applied; validation panel **PASS**,
`must_fix: []`, four reviewers ran and none skipped; goal-check **9 SC MET, 0 unmet**, SC-02
re-graded from scratch and its residue recorded **DISCHARGED**. `review_sha` re-pinned at
**`c488218e`** (the commit carrying the fix). Plan station `review`, all five tasks `done`; mirror
re-synced at review (milestone #51, parent #1359, tasks #1360..#1364).

Briefing: `notes/ship-review-2026-09-06-13-ship.md`. Handoff: `notes/handoff-ship.md` (seq-3). No
PR, no merge, nothing shipped — the operator's ship/fix/re-scope/stop decision is the next act.

**Budgets, both surfaced in the briefing.** 9 rework cycles of a hard 10 — one spent this cycle, on
the qa send-back. **23 runs of an informational 20.** My read: today's four runs each earned their
place, unlike the previous cycle's.

Housekeeping done this cycle: removed `/private/tmp/qa-b16-proof-worktree`, a qa scratch worktree
outside the segment layout that tripped INV-25 and an INV-29 the invariant could not compose a
removal command for. Clean, nothing unlanded. Row B-26 records the recurrence.

## Open Questions

- Q1 (**operator ruling, non-blocking, in the briefing**): the directive said the test "must fail
  case `5b`"; as delivered, `5b` never runs under the mutant — new case `5g` does. The code reviewer
  and the validation lead both graded this faithful delivery of the operative clause, and I agree:
  the file is order-dependent over one shared fixture tree, so mutating in place around `5b` would
  leak the mutant into `5c`-`5f`. The operator may still want the literal form.
- Q2 (**operator decision, non-blocking, briefing row B-27**): `5g` asserts a negation, so a mutant
  that merely RAISES leaves both cases green at 125/125 while proving nothing. Not live; reproduced
  by me, ranked first by the panel, raised independently by pm. Remedy is a two-line tightening.
- Q3 (RESOLVED, rung 1, carried from the previous cycle): T-01's approved `verify:` exits 1 and is a
  settled test-first RED gate, unsatisfiable after T-03 landed the seam. Not a defect, no amendment
  owed. Re-confirmed unchanged this cycle: the pin moved but production did not.
- Q4 (non-blocking, operator only, row B-10): the REQ-05 wording correction, carried unchanged. The
  operator declined to rule twice and directed that approved artifacts stay unchanged.
- Q5 (non-blocking, harness defects, rows B-11..B-15, B-18..B-22, B-26, B-31): `check-domain` claim
  scoping; lead digest clobber; hardlink edit desync; **null-yield returns, which recurred a third
  consecutive panel — the security reviewer exited 1 after its note had landed**; main-checkout
  leakage (no recurrence, re-checked); the test matrix keying a required kind on a directory label
  (**re-raised by qa unprompted**); the write-guard's two write routes disagreeing; reviewer
  `files_touched` under-reporting; scratch worktrees outside the layout; and the permanently inert
  `match_bug_class` matrix leg.
- Q6 (pre-existing, NOT introduced by this cycle, and NOT fabricated closed, row B-24):
  `check-state.sh` still reports no `notes/handoff-build.md` — the build seam was crossed without one
  by a predecessor. Writing a "working memory" note now for a phase nobody ran would falsify the
  record, so it stays open and reported.
