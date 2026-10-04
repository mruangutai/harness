# Grilling — repository-scoped factory write grants — 2026-09-15

## Destination
Harness can run concurrent factory work across product repositories while each agent may write only within its assigned repository and assigned worktree. If the agent-to-repository identity cannot be resolved, the write is refused.

## Mission
mission: plan
reason: This adds a fail-closed identity/binding contract across the OMP pre-write adapter and both enforcement routes.
confirmed-by: operator

## Settled
- The boundary applies only to factory-dispatched work for declared product repositories; Harness self-development and the main session retain their existing behavior.
- Independent Kaya features may run concurrently in their own worktrees; repository binding must not prevent this.
- #495 may be planned and built independently while #496 performs its first Kaya proof, but it must ship before concurrent multi-product factory operation is treated as safe.
- The operator confirmed the plan mission and shared understanding before planning began.

## Not yet specified
- None.

## Out of scope
- Changing Harness self-development to factory-dispatched work.
- Delaying or folding #496's first Kaya proof into this feature.
- Broader factory redesign outside repository binding and its necessary enforcement proof.

## Facts I verified (so pm does not re-derive them)
- #495 is open; Units 3 and 5 are shipped, and #496 does not depend on Unit 7.
- `.harness/team-config.yaml` still grants repository-wildcard control-plane paths such as `.harness/*/features/**` and `.harness/*/expertise/**`.
- OMP's `basePayload` supplies `agent_type`, `hook_event_name`, and `cwd` to pre-write checks; it does not include a runtime `agent_id`.
- `ctx.agentId` is already used by the OMP adapter's digest and task-claim lifecycle paths, but the pre-write availability and first-write ordering need direct verification.
- `check-domain.py` governs Write/Edit; `bash-write-guard.py` governs detectable Bash writes; their repository decision must agree.
- The current claim-worktree protection is keyed by agent type and reduces checkout mistakes but does not bind concurrent same-role agents to separate repositories.
