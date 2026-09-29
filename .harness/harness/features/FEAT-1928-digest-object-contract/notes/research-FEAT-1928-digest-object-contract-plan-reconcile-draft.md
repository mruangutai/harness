# FEAT-1928 plan reconciliation at `1f021fa3`

## Conclusion

The signed design was reconciled to merged `main` without changing SC-01–SC-08 or D-01–D-05. `BRIEF.md` and `plan.yaml` are pending operator re-signature because task content changed. The approval history remains in `notes/approval-2026-09-28.md`; `feature.json` retains the historical rework ruling of 2 rounds / 90 minutes.

## Drift incorporated

- T-01 now forbids broad catches and a second `spec_from_file_location` loader, and requires canonical direct-route reader rows plus `scanned_files` entries for both new Python modules.
- T-02 now targets `_inv15_digest_verdict` in `check_state/run_state.py`, includes `ctx.py`, `table.py`, `feature_record.py`, and the structure-lock test, requires exactly one invariant owner and declared INV-15/INV-46 reads, and explicitly deletes the #1960/#1969 string/fallback branch and its two named tests.
- The DEC-174 lane covers `check-state.py and check_state/**`; every enforcement edit remains `main-session-direct`.
- T-04 isolates only the FEAT-70-dependent plan digest-reader slice. Its five current source entries are symbol-anchored. Its pre-start requires FEAT-70 to be merged, re-resolves `_lead_digest`, `_digest_mapping`, `_digest_findings`, `cmd_record_amendments`, and `cmd_record_panel` to package module anchors through the control-plane plan merge command, then reruns plan check. T-01 and T-02 remain runnable while T-04 waits; T-03 follows T-02 and T-04.

## Preserved evidence

- Binding drift: `agent://PlanDrift/report` and `local://feat1928-drift.md`.
- Settled intent and approval: `.harness/notes/grilling-digest-object-contract-2026-09-28.md` and `notes/approval-2026-09-28.md`.
- Panel history was re-recorded through `record-panel`: cycle 0 scope, should-not-exist, and design all `ran`; cycle 1 scope and goalcheck both `ran`.
- All six existing cycle-0 findings retain their exact IDs, severities, kinds, proportionality scopes, resolutions, and `resolved` dispositions; no finding ID was added.

## Mutation and verification receipts

- Approval reset: `APPROVAL-RESET: the plan was approved and its task set or a task field changed; approval.status is pending until the main session signs again`.
- Baseline: `1f021fa3015d721099a87ed840eaf7eaae37db29`.
- Scoped gate: `OK` for T-01 through T-04; `4 task(s), 71 anchor(s) resolved, 0 failure(s)`.
- No implementation, project-wide validation, approval signature, or GitHub/Projects sync was performed.

Principle applied: **Outcome-Oriented Execution** — the FEAT-70 phase boundary gates only the symbols whose module locations are moving, rather than serializing unrelated enforcement work.
