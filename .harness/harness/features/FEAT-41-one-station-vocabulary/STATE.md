# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: plan-surface RE-REVIEW at the pinned commit e5afc19. Both squads returned PASS with 0
  send-backs. review_sha is now pinned to e5afc19 in feature.json, closing the GAP-7 violation.
- squad: none
- status: Plan
- panel: harness-eng-lead (architecture) PASS, 0 high / 3 med / 5 low / 2 info.
  harness-validator-lead (harness-code-reviewer + harness-ui-reviewer) PASS, severity_max low.
  F-1 (was high, gating) and F-2 (was info) are both CLOSED at e5afc19, quoted at plan.yaml:834-836
  and 768-773, matched by SC-05 (112-116) and SC-07 (121-124). ui-reviewer self-scoped out.
- gate: gates.review is advisory_unless_high and NO finding is high, so review does not gate. The
  plan is not returned to pm and is signature-ready.
- residual: three MED plan-quality findings, verified by me at e5afc19 rather than taken from the
  digest - T-09 names plan-write.py while T-13's rename is separately strikeable (835-836, 1185);
  T-07's verify cannot see a half-applied station migration (655-660); T-05's multi-file grep
  exits 0 on either file (400). Advisory, the operator's cost call.
- approval: pending in BOTH plan.yaml:7 and BRIEF.md:190, unchanged. Only the main session signs.
- cycles: 7 of 10 - unchanged, because both leads reported ZERO send-backs and only rework counts.
- runs: 11 of 20.
- next: the main session takes the signature to the operator, then gh-sync.py status.


## Open Questions

- Q1: SIGNATURE CONDITION, non-blocking to the plan. T-12 now carries an external dependency: the
  decisions-authority triage must land a recording form — in-place clause strike under DEC-188, or
  the correction subsumed into the entry in one voice — before T-12 can be fully executed. It STOPs
  and returns the question rather than guessing. Signing the plan accepts that dependency.
- Q2: pm reports DEC-188's own text bears on that triage: DECISIONS.md:5942-5944 says struck
  decisions are not deleted from the file, and :5938-5940 routes a partly-overtaken decision to
  amended. T-12's three cases are clause-level, so form (b) is arguably closer to DEC-188's own
  path. Input for the triage, not grounds to pick here.
- Q3: RESOLVED 2026-08-26. The GAP-7 violation is closed. The operator ruled the review be re-run
  against the committed plan; the panel read plan.yaml and BRIEF.md only via `git show e5afc19:...`
  with no working-tree copy opened and no concurrent pm edit, so review_sha is now pinned to
  e5afc19 truthfully rather than after the fact. check-state.sh no longer emits the GAP-7 line for
  FEAT-41.

- Q4: the second live VIOLATION is INV-26 FEAT-40 parent (issue #842) — plan derives Review, board
  reads Done. This is the exact defect T-10 exists to close, so it is expected and closes on build.
- Q5: does check-state.sh INV-26 flag issue 223 once T-06 routes the compare through project()?
  223 is a parent card, not a task sub-issue. Not run. T-10 now STOPs and reports rather than adding
  the card, so it fails safe either way. Tracked as PB-03.
