# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- run: .harness/harness/features/FEAT-31-orchestrator-context-watch/runs/plan2b-product/state.yaml
- squad: product
- status: awaiting-user

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING
SIGNAL, not a note: the orchestrator asks the user, writes the answers to
.harness/harness/features/<FEAT>/notes/answers-<runid>.md, and re-delegates with that path. Clear
each entry when it is answered.>

- Q1, blocking. SC-01 demands a live orchestrator under verify automated, and CI is ubuntu-latest
  with no transcript directory. plan.yaml D-09 splits it: the automated half runs against a fixture
  with the arithmetic re-implemented independently, and the live half moves to SC-10's UAT. That
  narrows an approved criterion, so it needs the operator's word. Blocks the plan's signature.
- Q2, blocking. SC-14's second half cannot go red: check-state.sh only ever opens handoff notes
  whose stem is in the seam table, so a mid-phase stem is accepted by silence, before and after any
  change. The proposed replacement is that INV-17 shape-checks every notes/handoff-*.md it finds
  while the seam table keeps governing which are required. That changes what the criterion asserts,
  so it needs the operator's word. Blocks the relay half of the plan.
