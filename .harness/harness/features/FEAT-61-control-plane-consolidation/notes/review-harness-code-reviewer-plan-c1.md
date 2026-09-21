# Code review — FEAT-61 plan c1

**VERDICT: FAIL**

The plan covers every SC id and its dependency DAG correctly places shared primitives before consumers and the final lock after all migrations. The selected seams are generally deep: station meaning is concentrated in `factory_config`, parsing/schema access in `artifact_accessors`, checkout policy in `harness_boundary` with route-specific adapters, and module loading behind one small interface. Two verification omissions can nevertheless ship changed gate behavior without the proof required by SC-01.

## Findings

1. **T-02 does not execute one of its own changed integration surfaces**
   - summary: Add `python3 tests/integration/test-gh-sync-open.py` to T-02's `verify` chain.
   - severity: high
   - kind: substance
   - scope: task
   - ref: SC-01
   - why: T-02 names `tests/integration/test-gh-sync-open.py` among the files changed for the `gh-sync.py` lifecycle migration, but its verify command runs only `test-gh-sync-start-task.py` for that module. A migration that changes the open/sync route's exit code or output can therefore pass T-02 and every successor gate without that integration surface running, contrary to SC-01's fail-first byte-equivalence requirement.

2. **T-05 migrates another gate without requiring SC-01's fail-first byte comparison**
   - summary: Specify and verify a before/after exit-code and stdout/stderr comparison for the `check-plan-routes.py` lifecycle migration.
   - severity: high
   - kind: substance
   - scope: task
   - ref: SC-01
   - why: T-05 changes `check-plan-routes.py` from a local finished-station definition to the strict shared predicate, but unlike T-02 and T-03 it asks only for unchanged legal-station output and runs the ordinary integration file. If the migrated gate changes an existing fixture's stderr, stdout, or exit code, the new AST-lock cases can remain green while the preservation contract fails.

## Non-findings checked

- All SC-01 through SC-08 are cited by at least one task; no task cites an absent SC.
- T-01 precedes every consumer of its shared interfaces; T-05 follows T-02, T-03, and T-04, so the lock and documentation land after the complete cutover.
- T-04 is proportional to the live requirement: policy code, live config, install template, example, and consumer fixtures move atomically; no bin-wide detector is introduced.
- The `ArtifactAccessError FleetError` wording in T-01 is malformed, but D-03 and the explicit `station_column` precedent uniquely resolve the required public error as `FleetError`; it is not independently classified as a shipped-behavior finding.

## Open questions

None.
