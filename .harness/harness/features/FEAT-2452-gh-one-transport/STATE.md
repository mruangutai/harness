# STATE

## Current

- feature: FEAT-2452-gh-one-transport
- run: .harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-3-simplify-apply-product/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- OQ-1 (non-blocking, for the operator/fable-advisor at signature): DEC-138's shared-code clause (DECISIONS.md "Shared code, and migration scope") states gh_bin() lives in gh_issues.py and each caller keeps its own runner; after T-02/T-04 that implementation sentence is stale while its policy holds. Keep (as drafted, keep row + BRIEF constraint) or amend (amend row + DECISIONS.md owned by T-05)? pm and orchestrator recommend amend. Plan is signable either way.
