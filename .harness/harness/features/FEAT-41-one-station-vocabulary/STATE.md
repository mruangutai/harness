# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: 2026-08-25-05-product returned PASS. All four plan amendments landed and were verified by me
  at source: T-12/D-09 recording form is now a named open dependency, F-1 and F-2 closed with SC-05
  and SC-07 tightened, T-10 skips rather than adds, PB-02 and PB-03 recorded.
- squad: none
- status: Plan
- plan: 13 tasks, 12 decisions, 12 main-session-direct. Parses. check-plan-routes.py exits 0 with
  0 violations across 2 plans.
- approval: pending in BOTH plan.yaml:7 and BRIEF.md:190, and it stays that way — the plan is
  signature-ready and only the main session signs (DEC-120).
- cycles: 7 of 10.
- next: the main session takes the signature to the operator. Nothing else is mine to do.

## Open Questions

- Q1: SIGNATURE CONDITION, non-blocking to the plan. T-12 now carries an external dependency: the
  decisions-authority triage must land a recording form — in-place clause strike under DEC-188, or
  the correction subsumed into the entry in one voice — before T-12 can be fully executed. It STOPs
  and returns the question rather than guessing. Signing the plan accepts that dependency.
- Q2: pm reports DEC-188's own text bears on that triage: DECISIONS.md:5942-5944 says struck
  decisions are not deleted from the file, and :5938-5940 routes a partly-overtaken decision to
  amended. T-12's three cases are clause-level, so form (b) is arguably closer to DEC-188's own
  path. Input for the triage, not grounds to pick here.
- Q3: FEAT-41 carries a live check-state.sh VIOLATION — two validator runs exist but review_sha is
  never pinned (the GAP-7 failure). Pre-existing at cfd8ca7, not caused by this run. It cannot be
  pinned truthfully after the fact: the code-review note records that the panel read plan.yaml from
  an uncommitted working tree while pm was concurrently editing it, so no commit represents what was
  reviewed. Needs an operator decision — re-run the plan review at a pinned sha, or accept the red.
- Q4: the second live VIOLATION is INV-26 FEAT-40 parent (issue #842) — plan derives Review, board
  reads Done. This is the exact defect T-10 exists to close, so it is expected and closes on build.
- Q5: does check-state.sh INV-26 flag issue 223 once T-06 routes the compare through project()?
  223 is a parent card, not a task sub-issue. Not run. T-10 now STOPs and reports rather than adding
  the card, so it fails safe either way. Tracked as PB-03.
