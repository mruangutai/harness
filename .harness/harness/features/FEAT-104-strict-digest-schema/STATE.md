# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: .harness/harness/features/FEAT-104-strict-digest-schema/runs/sigfix-c2-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase complete; operator rulings from the signature review APPLIED. OD-1 (hermetic inert
fixture remedy, closing the high panel finding), OD-2 (three passthrough rows dropped), OD-3 and
OD-4 (precision corrections) all landed and verified on disk by the orchestrator; OD-6 was already
carried by T-09. All four `PF-` findings now read `disposition: resolved` with ids, severities,
readers and evidence unchanged. Backlog rows B-1..B-6 all struck by the operator and recorded
nowhere.

OD-5 (strike T-02) is BLOCKED: `plan-merge.py` has no delete verb — `apply` adds and never deletes,
`amend` replaces one field of one named item. Nothing was hand-edited and no route was invented.

BRIEF.md and plan.yaml remain `pending`; only the main session signs. Corrected packet:
`notes/ship-review-plan-signature-c2.md`, superseding the c1 packet. cycles_used 3/10, runs 7/20.

## Open Questions

- OD-5: no legal route to remove a task. Amend T-02's title/intent to record the strike in place
  (recommended — one command, reversible), or add a guarded delete verb to `plan-merge.py` as its
  own feature. Operator's call.
- The passthrough table: the ruling named three rows to drop; with D-02's bar repaired,
  `matrix_ok` and `coverage_gaps` are grounded only by a commented line T-01 will create
  (`plan.yaml:205-213`). Accept, or strike those two as well.
- The signature itself. Two `check-state.sh` violations stand at the gate: BRIEF not approved (the
  gate working), and the INV-26 false positive the struck B-1 leaves in place.
