# T-04 receipt — mechanical reader relocation

## Result

PASS. All 21 classified T-04 dispatchable correct-reader rows now call `artifact_accessors.load_plan` or `artifact_accessors.load_fleet`; caller behavior remains a relocation-only change.

## Pre-edit classification gate

- Matrix: `tests/integration/canonical-reader-classification.json`, `.rows[] | select(.task == "T-04")`; 21 rows (the complete row matrix is the JSON rows at that pointer).
- Every filtered row had a current source, a T-04-listed production source, `remedy: artifact_accessors.load_plan` or `artifact_accessors.load_fleet`, `disposition: migrate`, and `execution_route: team`.
- The T-04 plan files list includes all 11 classified source files and the corresponding 11 listed consumer-test paths where applicable. Predicate passed before the first edit.

## Change boundary

- Repointed only classified T-04 `load_plan` / `load_fleet` calls in: `board_lifecycle.py`, `factory_claim.py`, `factory_config.py`, `factory_decompose.py`, `factory_land.py`, `factory_workspace.py`, `feature-record.py`, `feature-worktree.py`, `gh-sync.py`, `harness_boundary.py`, and `worktree_terminal.py`.
- No test path required a seam update; no semantic expectation was added.
- No accessor body, raw parser, classification machinery, `tests/integration/test-check-plan-routes.py`, documentation, T-03 semantic row, or T-05–T-07 path was edited. `git diff --stat` for the listed sources: 11 files, 17 insertions, 15 deletions.
- Where legacy calls used `factory_config.load_fleet()` with its default, the relocated call passes the same `factory_config.FLEET_PATH` (or local `FLEET_PATH`) explicitly because the public accessor requires a path; this preserves the legacy default resolution and error behavior.

## Discovery and verification evidence

- Post-edit source sweep found no executable `factory_config.load_fleet(` or `harness_yaml.load_plan(` call in the T-04 sources; the sole match was prose in `feature-worktree.py`.
- Post-edit accessor sweep found the canonical accessor seam at every classified T-04 call site. Existing T-03 canonical calls remained unchanged.
- Signed `verify:` cross-check matched `plan.yaml` byte-for-byte and executed from this worktree:

```sh
python3 tests/unit/test-factory-config.py && python3 tests/unit/test-factory-claim.py && python3 tests/unit/test-plan-depends-on.py && python3 tests/integration/test-board-lifecycle.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-feature-worktree.py
```

All nine scripts executed and exited zero: `test-factory-config.py` (116/116), `test-factory-claim.py` (133/133), `test-plan-depends-on.py` (12/12), `test-board-lifecycle.py` (all passed), `test-factory-decompose.py` (179/179), `test-gh-sync-open.py` (ALL PASSED), `test-gh-sync-start-task.py` (ALL PASSED), `test-worktree-terminal.py` (all PASS), and `test-feature-worktree.py` (PASS).
