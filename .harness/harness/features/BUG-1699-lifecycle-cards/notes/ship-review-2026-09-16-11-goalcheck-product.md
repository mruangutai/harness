# Ship review — BUG-1699-lifecycle-cards

## Decision

**PASS — ready for the operator's ship action at pinned SHA `d29899ad3be07bc4999f202cacee7db58c4e8865`.** All three BRIEF perspectives and SC-01 through SC-16 are met. There are no open questions or unresolved findings. The feature remains in Review; this run did not merge, open a pull request, deploy, or mark it Done.

## What completed

- The lifecycle now projects every eligible recorded source, parent, and non-abandoned task card to the canonical Plan, Ready, Building, Review, or Done station at the signed transition boundaries.
- Signature, ordinary build, validation, bounded rework, approval reset/resume, ship, and one-time reconciliation all consume the shared projection policy rather than reconstructing card eligibility.
- Local lifecycle authority remains first; outbound GitHub writes are per-card, best effort, and non-gating. Existing abandonment, open-child, and workflow-owned issue-closing behavior is preserved.
- Current decisions and their generated index describe the delivered lifecycle contract.

## Verification

- Final canonical goalcheck: PASS at `d29899ad`; operator, orchestrator, and code-maintainer perspectives met; SC-01 through SC-16 met; no open questions — `notes/research-BUG-1699-lifecycle-cards-goalcheck-validate-c2.md`.
- Signed T-01 seven-runner command: PASS.
- Configured unit matrix: 40 files, 0 failures.
- Configured integration matrix after the authorized manifest reconciliation: 72 files, 0 failures, 92.93 seconds.
- SC-11 regression proof: the old late false assertion printed failure but exited 0; the repaired equivalent exits 1; the restored focused runner exits 0 and reports all pass.
- Final review evidence: code grade 4, security PASS, UI PASS. The c0/c1 findings are superseded by their evidenced repairs.

## Bounded rework

The original 2-round/90-minute ruling was exhausted. The operator authorized one narrow additional round and 30 minutes solely for the external `.harness/team-config.yaml` reconciliation, one integration-matrix rerun, and this final goalcheck. The final ledger reports 113 rework minutes against the extended 120-minute ceiling. No additional feature scope was introduced.

## Remaining risk

No known release-blocking risk remains. GitHub board writes are intentionally best effort and can leave remote cards stale when GitHub is unavailable; the local record remains authoritative and the bounded reconciliation path repairs drift. Shipping still requires the operator's normal merge/release action.

## Run record

Eleven runs completed with four engineering cycles consumed against the ten-cycle feature cap. The final run, `2026-09-16-11-goalcheck-product`, passed with zero additional cycles. The review pin is `d29899ad3be07bc4999f202cacee7db58c4e8865`.
