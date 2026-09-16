# STATE

## Current

- feature: BUG-1723-orchestrator-closeout
- run: .harness/harness/features/BUG-1723-orchestrator-closeout/runs/fix-c2-validator/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- C1-V01 (blocking, unowned scope change, high): Approve adding the BUG-1723 DEC-159 clause in `.harness/harness/docs/DECISIONS.md` (and regenerated index if required) to scope, then reconcile its terminal-note exemption with the approved all-stations INV-43 contract.
- C2-QA01 (blocking, validator infrastructure): Decide whether return validation must execute at pinned `review_sha` or whether the later-checkout `run-unit-tests.py` failure must be repaired outside this feature gate.
