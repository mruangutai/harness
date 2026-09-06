# STATE

## Current

- feature: BUG-1305-run-state-clobber
- run: .harness/harness/features/BUG-1305-run-state-clobber/runs/goalcheck-build-c4-product/state.yaml
- squad: none
- status: awaiting-user
- station: review; review_sha 154ff2a0; cycles 15/15 exhausted; runs 27 against an informational 20
- gates: qa test_matrix PASS, SIMPLIFY PASS, panel F-1 CLOSED at cycle 15 by a two-mutant probe with zero crosstalk, code grade exit 0. SC-01 restored and met; SC-07 NOT MET.
- held: awaiting Advisor ruling AdviseBug1305Sc07Conflict. Nothing may be amended or under-reported until it returns.

## Open Questions

- SC-07 is not_met at the pin for a criterion-internal conflict, not a delivery gap: the note remedy is correct and both directions are satisfied in substance, but SC-07's final FAILS-if leg fires on the very disclosure direction two requires. Three operator options, none available to any cycle: accept not_met on the record and ship; widen SC-07's disclosure carve-out to name the Advisor-ordered reconstruction-None class; or authorise a one-clause reword that keeps the disclosure but moves it out of the note's BLUF, which demotes a material behaviour change out of the lead sentence.
- Advisor is separately deciding whether permanent in-suite PRE permit coverage is required for the handoff arm: the cited valid-handoff Edit control resolves to a PostToolUse case, and pm measured the PRE permit by hand at the pin (exit 0) with the suite not pinning it.
- Harness defect, fourth occurrence: worktree claims key on persona and on the shared broker pid, so a lead was refused writes into its own BUG-1305 run directory because of a stale harness-product-lead claim on BUG-1308 whose agent had already left the roster. Remedy named by the blocked lead: inflight_registry.py release --agent harness-product-lead --feature BUG-1308-expertise-replace-drop; it is another flow's registry and therefore the main session's act, not mine.
