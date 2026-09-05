# STATE

## Current

- feature: BUG-1308-expertise-replace-drop
- run: .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-01-plan-polish-c3-product/state.yaml
- squad: product
- status: awaiting-user

Plan phase COMPLETE and SIGNATURE-READY. BRIEF.md carries REQ-01..09 and SC-01..12; plan.yaml carries
15 decisions and 4 tasks. The operator read cycle 1's panel and ruled REVISE rather than overrule; the
revision was applied, then goal-checked PASS, then re-read by the full panel at cycle 2, which returned
severity_max med with no gating finding and confirmed the cycle-1 HIGH closed. All fourteen findings
across both cycles are recorded: 13 resolved, 1 open — PF-12c69147 (low, u10), left standing on the
validator lead's own recommendation and the operator's ruling. NO OPEN HIGH OR CRITICAL FINDING.
Approval is `pending` in both artifacts by design — only the main session signs. Station: plan.
Cycles used 3 of 8. Worktree: .claude/worktrees/harness/BUG-1308-expertise-replace-drop.

Log:
- 2026-09-05: plan opened; feature.json and STATE.md instantiated; station -> plan.
- 2026-09-05: BRIEF + plan drafted (PASS).
- 2026-09-05: goal-check c0 FAIL, 3 must_fix + 3 advisory; routed back — cycle 1.
- 2026-09-05: plan repaired; goal-check c1 PASS, all six closed.
- 2026-09-05: plan panel c1 FAIL, severity_max high, 7 findings; Advisor answered A1/A2/A3; panel
  transcribed, D-14 records the rulings; returned to the operator for signature.
- 2026-09-05: operator ruled REVISE not overrule; consolidated revision applied — cycle 2.
- 2026-09-05: goal-check c2 PASS (R1-R4 all met); plan panel c2 PASS, severity_max med, no gating
  finding, cycle-1 HIGH confirmed closed.
- 2026-09-05: cycle-2 meds closed and both cycles' dispositions recorded — cycle 3; INV-32's third
  reader recorded; goal-check c3 PASS; three intent imprecisions closed.

## Open Questions

- Harness defect, non-blocking, for the harness owner — CONFIRMED THREE TIMES (plan panel c1, plan
  panel c2, and the c2 revision dispatch): a subagent returns host status `failed (exit 1)` while
  emitting a well-formed digest and a complete artifact, after a digest re-submission over the
  reviewer `reviewed` / `code_grade` fields on a plan-only cycle that has no `review_sha`. A valid
  return that exits 1 is indistinguishable from a real failure to the tier above.
- Harness defect, non-blocking: `check-state.sh` INV-32 (`:533`) requires a `goalcheck` entry in
  `panel.readers`, but `plan-panel.yaml` defines only `should-not-exist` and `scope` — the goal-check
  runs in the PRODUCT segment. Nothing in the team file or the playbook tells the recorder to add the
  third entry, so the honest record fails the invariant until someone measures it. Recorded here as
  `ran`, persona harness-pm, because it did run.
