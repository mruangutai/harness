# STATE

## Current

- feature: FEAT-2537-registry-record-cleanup
- run: .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-1-plan-product/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- Q1 (signature): accept the fail-closed class as "every non-v2 object" rather than "the extinct v1 shape"? It adds two deltas no writer produces: `{}` reads as no claims today and is refused as unreadable after; a non-v1, non-v2 dict folded by a locked writer gains a stderr warning. Orchestrator recommends accept. Blocks the signature; asked of the signer (fable-advisor, operator's delegate).
