# STATE

## Current

- feature: BUG-1308-expertise-replace-drop
- run: .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-panel-record-c1-product/state.yaml
- squad: product
- status: awaiting-user

Plan phase COMPLETE at the operator signature gate. BRIEF.md and plan.yaml are drafted, goal-checked
against stated intent (PASS at cycle 1), read by the full adversarial plan panel (both readers ran),
and the panel is transcribed into plan.yaml `panel` with all seven findings `disposition: open`.
Approval is `pending` in both artifacts by design — only the main session signs. Station: plan.
Cycles used 1 of 8. Worktree: .claude/worktrees/harness/BUG-1308-expertise-replace-drop.

Log:
- 2026-09-05: plan phase opened; feature.json and STATE.md instantiated; station -> plan.
- 2026-09-05: BRIEF + plan drafted (run 2026-09-05-01-product, PASS).
- 2026-09-05: plan goal-check c0 FAIL, 3 must_fix + 3 advisory; routed back — cycle 1.
- 2026-09-05: plan repaired (plan-fix-c1-product, PASS); goal-check c1 PASS, all six closed.
- 2026-09-05: plan panel c1 FAIL, severity_max high, 7 findings; Advisor answered A1/A2/A3.
- 2026-09-05: panel transcribed to plan.yaml, D-14 records the Advisor's rulings; handoff written.

## Open Questions

- PF-f4d258f365f54f04d9cc976baf0ad981 (high, gating, scope reader): T-01 Step D never reconciles
  original-index resolution with in-place mutation, and no case exercises two ops on different
  original indices in one section. Blocked on: the operator's signature ruling — sign with
  `--overrule`, or send one consolidated revision. Neither the orchestrator nor pm may accept this
  risk (DEC-176).
- Contract-shape call for the operator at signature: A3 keeps `merge` as a contract verb the tool
  refuses, while PF-3f8a11143ba40f67b0f326d532381d5e (med) proposes deleting D-02's optional
  `section` the tool accepts. The panel states it cannot settle this; it is not a squad question.
- Harness defect, non-blocking, for the harness owner: the plan panel's `scope` step returned host
  status `failed (exit 1)` while emitting a well-formed digest and a complete artifact, after a
  digest re-submission over the reviewer `reviewed` field on a plan-only cycle with no `review_sha`.
  A valid return that exits 1 is indistinguishable from a real failure to the tier above.
