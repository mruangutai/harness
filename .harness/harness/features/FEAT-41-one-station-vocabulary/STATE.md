# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: 2026-08-26-01-product. ONE pm cycle spent closing the three advisory MED findings plus the
  T-10 twin, on the operator's instruction, before signature. product-lead PASS, 0 send-backs.
- squad: none
- status: Plan
- fixes, all four verified BY ME at source in the working tree, not taken from the digest:
  M-1 (T-07 verify, now :663-670) - closed BEHAVIOURALLY, not by grep. pm rejected the grep with
  evidence that status/Done/Review occur legitimately in those files. Five reader tests each gain
  a case DEMONSTRATED FAILING BEFORE THE REPOINTING, and the verify now runs all five, so a
  half-applied migration reds.
  M-2 (:867) - the refusal names "plan-merge.py (plan-write.py after T-13)", correct BOTH before
  and after the rename. Closes the live window AND keeps T-13 separately strikeable, whose clause
  at :1224 therefore stays true untouched. Better than either option I offered.
  M-3 (:400-405) - the one-line multi-file grep is now a per-file loop with explicit exit 1, and
  the stale-Edit negative check was extended to both files.
  T-10 twin (:967-974) - the ship refusal now STATES THE REASON FIRST, then the path, matching
  F-1's form at :866-870.
- gate: check-plan-routes.py exit 0, 0 violations across 2 plans - I ran it myself. plan.yaml
  parses: 13 tasks, 12 decisions.
- approval: pending in BOTH plan.yaml:7 and BRIEF.md:190. BRIEF.md is byte-identical to its
  pre-run checksum, so no SC moved and nothing was signed.
- PIN IS NOW STALE: plan.yaml was 9cb78adb (byte-identical to e5afc19) before the run and is
  2bfd3a77 after. review_sha still reads e5afc19, deliberately untouched - the operator decides
  whether to re-pin.
- cycles: 7 of 10 - UNCHANGED, 0 send-backs reported.
- runs: 12 of 20.
- next: the operator's signature decision, then gh-sync.py status (the operator's, not mine).

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
