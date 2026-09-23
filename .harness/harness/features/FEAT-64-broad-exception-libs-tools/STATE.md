# STATE

## Current

- feature: FEAT-64-broad-exception-libs-tools
- run: .harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/validate-validator/state.yaml
- squad: validator
- status: awaiting_user

## Open Questions

- Q1 (blocking): Resolve CR-64-01 through the main-session-direct lane: remove the out-of-plan `board_lifecycle.py` and `test-board-lifecycle.py` B2 repair, or obtain an explicit signed scope and behavior amendment before rebuilding.
- Q2 (blocking): After Q1, record exact old and new bytes for every deliberate A1/A5 divergence, regenerate affected baseline-to-pin receipts, and ensure no unlisted byte difference remains.
- Q3 (blocking): Align SC-03 and SC-06 evidence-kind declarations with all carrying tests through the approved plan/brief record path, without weakening or dropping assertions.
