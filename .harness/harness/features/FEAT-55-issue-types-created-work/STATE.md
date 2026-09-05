# STATE

## Current

- feature: FEAT-55-issue-types-created-work
- run: .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-04-15-product/state.yaml
- squad: product
- status: awaiting_user
- station: plan (plan.yaml `status: plan`, `approval.status: pending`, BRIEF `## Approval` pending)
- mission: plan — the operator's FIRST batched ruling pass is discharged. Both rulings of
  `notes/answers-plan-panel-20260904.md` are applied in ONE consolidated revision (T-05 case G,
  T-07 case I, `REQ-07` in both `traces:`, both verify loops updated, BRIEF SC-08 reworded to name
  all three creation commands; D-19's `because` rewritten to record the granted opt-in live write).
  The re-run goal-check (c3) answers YES with the eleven baseline findings still closed. The
  adversarial panel re-ran at cycle 2, both readers ran, none skipped, and returned FAIL with four
  new findings — `severity_max: high`. plan.yaml `panel:` now records NINE findings: cycle 2's four
  plus cycle 1's five unruled ones carried verbatim; the two the operator ruled on dropped.
- next: the main session takes a SECOND batched signature pass (DEC-176). One high finding gates it
  and neither pm nor the orchestrator may accept its risk — only
  `sign-approval --overrule PF-60f3544bd486fe9d3541a26658e5fa9f:<reason>`, or a directed fix in the
  next consolidated revision.
- intake: .harness/notes/grilling-issue-types-2026-09-04.md (source ticket #1289)
- handoff: .harness/harness/features/FEAT-55-issue-types-created-work/notes/handoff-plan.md
- cycles: 5 of 10 used; 15 runs of 20.

## Open Questions

- Q1 (BLOCKING, operator): `PF-60f3544bd486fe9d3541a26658e5fa9f` (scope, high) — T-03 case F omits
  the ZERO-`updateIssue` assertion that the new T-05 case G and T-07 case I both carry, so SC-08's
  per-command zero-type-assignment requirement is unproven on the open route. Direct the one-line
  fix (folding low finding `PF-8b5853220e5f2768339090bdbc44b1a5` into the same edit, per the panel's
  `fix_order`), or accept the risk by overrule.
- Q2 (operator): `PF-08da208931348b8cb200b34e8e7a1d31` (should-not-exist, med) — T-10 §6 binds
  `--create-in` to EQUAL the configured `github.repo`, which the plan records as not
  Issue-Type-enabled, so the live create the operator just granted is unreachable and BRIEF.md
  :183-184 promises the opposite. Does the equality binding stand — accepting that SC-10 can never
  report LIVE PASS here — or may the flag name a foreign enabled repository under its own guard?
  This is the delivery half of a granted ruling, so it is the operator's, not a fix cycle.
- Q3 (operator): `PF-56a2ce7a053111a3aff62a4b97c5902e` (should-not-exist, low) — rule on the
  batched `PF-0c12a033f69bb6bc60b8f96134f94fd0` (the `adopted` marker is behaviourally inert)
  BEFORE BRIEF SC-12's wording is signed, since signing first multiplies the surfaces to unwind.
- Q4 (harness defect, not FEAT-55): `panel.readers[]` is written with a `step:` key while
  `check-state.sh` INV-32 keys those entries by `reader:` (`:534-546`), and its `expected_readers`
  set includes a `goalcheck` reader no panel writes at all. INV-32 therefore fails closed the
  moment a plan carrying a panel is signed. Verified at HEAD by direct read.
- Q5 (harness defect, not FEAT-55): `harness-spec-driven` names `apply`, `set-task-station`,
  `set-feature-station` and `sign-approval` as the plan-writing verbs, but `apply` is add-only
  (CONFLICT exit 7) and cannot revise an existing task or decision. The verb that can is `amend`
  (BUG-1128). Every revision cycle after the first needs it; the skill's verb list omits it.
