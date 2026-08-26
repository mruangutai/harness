# QA gate — FAIL

**Review SHA:** `ce29a059e37af5133ae5b4f87df6f622ed966a92` (base `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`).

## Scope and matrix

Assessed changed files: `.agents/skills/harness/bin/test-merge-gitignore.py`, `.agents/skills/harness/bin/run-unit-tests.sh`, `.harness/harness.json`. Inspected intentionally unchanged `.agents/skills/harness/bin/merge-gitignore.sh` for the behavioral contract.

T-01 is `change_type: feature` (`plan.yaml:41-57`), so `test_matrix.feature.always` requires **unit** and **integration** (`.harness/harness.json:40-44`); no UI interaction-flow predicate is present and AI evals are not required. The task verify command exactly matches the dispatched command (`plan.yaml:55-57`):

`python3 .agents/skills/harness/bin/test-merge-gitignore.py && .agents/skills/harness/bin/run-unit-tests.sh --kind all`

## Gate evidence

| Kind | Command / discovery | Result |
|---|---|---|
| unit | `run-unit-tests.sh --kind all`; 23 listed unit scripts (`run-unit-tests.sh:17,36-38`) | Satisfied: no unit-script failure reported. |
| integration | direct behavioral program, then `--kind all`; 24 listed integration scripts (`run-unit-tests.sh:18,36-38`) | Changed test is explicitly registered only here and passes twice: 7/7 direct cases and `PASS test-merge-gitignore.py`. However the bucket contains one failed named assertion, so the required integration gate fails. |

The changed test is actually bound, not merely discoverable: it is in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`), its exact path is in `test_kinds.integration.detect` (`.harness/harness.json:119`), and the runner's drift/kind cross-check runs before all selected scripts (`run-unit-tests.sh:42-127`). The all-kinds run emitted `PASS test-merge-gitignore.py`; no `MISCONFIGURED` or `KIND-DRIFT` output appeared. The direct program passed all seven named cases (test list at `test-merge-gitignore.py:126-134`), covering SC-01 through SC-05 at the corresponding case bodies (`:36-123`).

**Observed exact outcome:** the prescribed command exited **1** after 152.85s. Its direct first leg passed 7/7. The all-kinds leg failed `test-bash-write-guard.py`, whose named assertion reported: `ONE IMPLEMENTATION: mutating WORKTREES_SEGMENT flips BOTH routes 0 -> 2` with observed `bash=0, write=0, want (2, 2)`; it reported `26/27 worktree-boundary cases passed`. The changed merge-gitignore integration program itself passed in the all-kinds leg.

## Finding

- **reviewer:** harness-qa
  **severity:** high
  **failure scenario:** A mandatory feature matrix rerun cannot pass because `test-bash-write-guard.py`'s one-implementation mutation proof leaves both guarded routes allowed (`0`) instead of refusing (`2`). This blocks the integration kind even though the changed behavioral test passes.
  **evidence:** prescribed-gate output; failing assertion named above; runner invocation at `.agents/skills/harness/bin/run-unit-tests.sh:134-148` aggregates failures into exit 1.
  **recommendation/disposition candidate:** return to the owner of the bash-write-guard regression, repair or establish its environmental cause, then rerun the verbatim T-01 command. Do not waive the required integration gate.

## Phase-1 coverage delta

Before source inspection, expected independent real-process cases for preservation, complete/incomplete read-only check behavior and missing-rule reporting, absent/partial targets with per-rule uniqueness, rerun byte identity, and explicit-root/caller-CWD isolation. The seven changed-test cases cover each expectation. No coverage gap for REQ-01 through REQ-05 / SC-01 through SC-05 was found. SC-06 is inspection-only and is supported by the unchanged utility in the diff plus integration registration above.
