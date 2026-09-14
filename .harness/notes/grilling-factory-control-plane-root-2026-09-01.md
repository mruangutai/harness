# Grilling — factory control-plane path — 2026-09-01

## Destination

A factory worker operating in a product checkout can reliably use Harness’s control plane, so the real kaya proof in #496 can run without reading or writing the wrong repository.

## Settled

- How does a factory worker locate the control plane? → Harness injects the absolute control-plane root into the worker’s preamble.
- May the worker read Harness-owned skills through that root? → Yes, read-only access is allowed; product writes remain constrained by the existing grants.
- How is path drift prevented? → Both a static lint over factory-reachable instructions and a spawn-time assertion enforce the contract.

## Not yet specified

None. The planner may choose the narrowest provider-neutral implementation that satisfies the settled contract.

## Out of scope

- Running or testing kaya-ai product code; #496 exercises the factory and its control plane only.
- Expanding product-checkout write permissions for control-plane records.

## Facts I verified (so pm does not re-derive them)

- #496 identifies #356 as required before the first real factory run; four #498 destination criteria depend on that run.
- #356 establishes that relative Harness paths resolve against a factory worker’s product checkout, not the Harness control plane.
- #356’s recorded measurement says `CLAUDE_PROJECT_DIR` is session-scoped and unavailable in an agent tool shell, so the worker needs an explicit agent-visible path.
- PR #899 merged the distinct `check-state.sh` root-resolution repair, which closed #156; it does not resolve #356’s factory instruction-path contract.
