# Grilling — depends_on integrity — 2026-09-06

## Destination
Every YAML plan rejects a `depends_on` reference to a task absent from the same plan before it can be signed or consumed. Valid plans retain their current behavior.

## Settled
- Scope of dependency validation → reject missing task IDs only; self-dependencies, cycles, and task ordering are out of scope.
- Desired outcome → the user confirmed the destination above.

## Not yet specified
- None.

## Out of scope
- Broader DAG policy (self-dependencies, cycles, and task ordering), because the user selected missing IDs only.

## Facts I verified (so pm does not re-derive them)
- `harness_yaml.load_plan()` is the shared plan-loading chokepoint: `check-plan-routes.py`, `check-state.sh`, `factory_claim.py`, `factory_decompose.py`, and `gh-sync.py` all call it.
- `factory_claim.py` currently treats an unresolved `depends_on` entry as an unresolvable blocker through the feature issue map; the requested validation instead concerns references to task IDs absent from the plan.
- `check-plan-routes.py` already validates plan shape before signature but does not validate `depends_on` referential integrity.
- Issue #201 identifies the defect as a dangling entry reaching decomposition and possibly GitHub `blocked_by` handling.
