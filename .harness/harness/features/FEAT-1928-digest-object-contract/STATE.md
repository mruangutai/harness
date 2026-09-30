# STATE

## Current

- feature: FEAT-1928-digest-object-contract
- run: .harness/harness/features/FEAT-1928-digest-object-contract/runs/plan-amend-T03-product/state.yaml
- squad: product
- status: blocked

## Open Questions

- Main session must revoke plan.yaml approval for the authorized DEC-237 T-03 amendment, leaving both BRIEF.md and plan.yaml pending for operator re-signature.
- The post-amendment plan check resolves all six T-03 anchors but fails on T-04's stale `_digest_mapping` and `_fenced_blocks` anchors; T-04 changes were outside this assignment and must be routed separately before re-signature.
