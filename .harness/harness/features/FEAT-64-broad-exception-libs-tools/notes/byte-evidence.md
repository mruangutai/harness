# FEAT-64 — exact byte evidence per suite (validate c0, GC-64-01)

Baseline `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` vs head `220feabb80174c042aff1f9f663cd49a4a57e968`.
Each suite run once per tree, `HARNESS_PROJECT_DIR=<tree> python3 <tree>/<suite>`, cwd `<tree>`.
`raw` digests are sha256[:16] of the untouched stream. `norm` digests are the same stream after exactly two
substitutions: the tree's own absolute path → `<ROOT>`, and any `…/T/tmpXXXXXXXX` tempfile directory → `<TMP>`.
Under `Lines` every differing line of the NORMALISED streams is printed verbatim (unified diff, zero context);
a suite with `norm` digests equal and no lines listed is byte-identical up to those two substitutions.

## `tests/integration/test-board-station.py`

- exit: baseline 0 → head 0
- stdout raw `a171319db8ef8248` → `fbadad1f5f9bbd53`; norm `a171319db8ef8248` → `fbadad1f5f9bbd53`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-PASS  board-station exits 0 when set_station raises a non-BoardError exception
+PASS  board-station exits 0 when set_station's gh returns a body that does not decode (GhError)
+PASS  FEAT-64: an unrelated RuntimeError inside set_station escapes (non-zero, not ERROR/exit 0)
```

## `tests/integration/test-check-omp-port.py`

- exit: baseline 0 → head 0
- stdout raw `1e4f62a3c40489e9` → `716dcdfa0d0b0b2e`; norm `1e4f62a3c40489e9` → `716dcdfa0d0b0b2e`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-64: an unrelated RuntimeError in the config reader escapes check-omp-port (traceback, not 'cannot read')
-26/26 cases passed
+27/27 cases passed
```

## `tests/integration/test-check-plan-routes.py`

- exit: baseline 0 → head 0
- stdout raw `2cd35b50b598dadb` → `14e98df79a44a4bb`; norm `2cd35b50b598dadb` → `14e98df79a44a4bb`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS feat64_manifest_deviation_unrelated_RuntimeError_escapes
+PASS feat64_live_plan_loaded_exactly_once_per_execution
+PASS feat64_shipped_plan_loaded_exactly_once_and_skipped
+PASS feat64_ceiling_factory_decompose.py_is_zero
+PASS feat64_ceiling_feature_schema.py_is_zero
+PASS feat64_ceiling_gh_cost_log.py_is_zero
+PASS feat64_ceiling_handoff_done_when.py_is_zero
+PASS feat64_ceiling_handoff_policy.py_is_zero
+PASS feat64_ceiling_harness_yaml.py_is_zero
+PASS feat64_ceiling_run_identity.py_is_zero
+PASS feat64_ceiling_worktree_terminal.py_is_zero
+PASS feat64_ceiling_board-station.py_is_zero
+PASS feat64_ceiling_check-omp-port.py_is_zero
+PASS feat64_ceiling_check-plan-routes.py_is_zero
+PASS feat64_ceiling_check-skill-weight.py_is_zero
+PASS feat64_ceiling_gh-sync.py_is_zero
+PASS feat64_ceiling_post-merge-sweep.py_is_zero
+PASS feat64_ceiling_run-unit-tests.py_is_zero
+PASS feat64_ceiling_upgrade-config.py_is_zero
+PASS feat64_ceiling_harness_boundary_is_exactly_two
+PASS feat64_census_lib_except_exception_mutant_is_one_finding_naming_handoff_policy.py
+PASS feat64_census_lib_bare_except_mutant_is_one_finding_naming_handoff_policy.py
+PASS feat64_census_tool_except_exception_mutant_is_one_finding_naming_gh-sync.py
+PASS feat64_census_tool_bare_except_mutant_is_one_finding_naming_gh-sync.py
+PASS feat64_census_third_harness_boundary_catch_fails_against_two
+PASS feat64_census_reduction_mutant_is_clean
```

## `tests/integration/test-check-skill-weight.py`

- exit: baseline 0 → head 0
- stdout raw `944bd96cf8899fe0` → `944bd96cf8899fe0`; norm `944bd96cf8899fe0` → `944bd96cf8899fe0` (identical)
- stderr raw `484819fc6115ded4` → `fd49aba5f35c938b`; norm `484819fc6115ded4` → `fd49aba5f35c938b`

Lines (stderr):
```
-......
+.......
-Ran 6 tests in 0.022s
+Ran 7 tests in 0.023s
```

## `tests/integration/test-factory-decompose.py`

- exit: baseline 0 → head 0
- stdout raw `8aa25728d0e63e67` → `70501f46d5e84a53`; norm `8aa25728d0e63e67` → `70501f46d5e84a53`
- stderr raw `5299aeebed71d79b` → `dd09f29da3a74361`; norm `54ea443ca0dad452` → `54ea443ca0dad452` (identical)

Lines (stdout):
```
+ok    FEAT-64: a non-UTF-8 BRIEF is (None, None)
+ok    FEAT-64: a missing BRIEF is (None, None)
+ok    FEAT-64: an unrelated RuntimeError escapes extract_brief
```

## `tests/integration/test-gh-sync-abandon.py`

- exit: baseline 0 → head 0
- stdout raw `032c0c48770a0662` → `032c0c48770a0662`; norm `032c0c48770a0662` → `032c0c48770a0662` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-gh-sync-open.py`

- exit: baseline 0 → head 0
- stdout raw `ba2cdd872c4f9fcf` → `ba2cdd872c4f9fcf`; norm `ba2cdd872c4f9fcf` → `ba2cdd872c4f9fcf` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-gh-sync-record.py`

- exit: baseline 0 → head 0
- stdout raw `5567a99547239673` → `5567a99547239673`; norm `5567a99547239673` → `5567a99547239673` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-gh-sync-ship.py`

- exit: baseline 0 → head 0
- stdout raw `9807e2b63a5a771a` → `61240c513bd46074`; norm `9807e2b63a5a771a` → `61240c513bd46074`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-64: an unrelated RuntimeError inside the audit escapes ship (traceback, not 'the board audit could not run')
```

## `tests/integration/test-gh-sync-start-task.py`

- exit: baseline 0 → head 0
- stdout raw `ccc5dc0d444cbd3d` → `ccc5dc0d444cbd3d`; norm `ccc5dc0d444cbd3d` → `ccc5dc0d444cbd3d` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-harness-yaml.py`

- exit: baseline 0 → head 0
- stdout raw `b42593b5fd31560e` → `e262cbc6b7063366`; norm `b42593b5fd31560e` → `e262cbc6b7063366`
- stderr raw `29f492595035cc15` → `01d0d57ac16f6e08`; norm `baa4f7eeb8769d62` → `baa4f7eeb8769d62` (identical)

Lines (stdout):
```
+ok   test_feat64_load_str_boundary_is_typed
+ok   test_feat64_require_or_die_cleanup_boundary_is_typed
```

## `tests/integration/test-inflight-registry.py`

- exit: baseline 0 → head 0
- stdout raw `5e3306082763c2e0` → `5e3306082763c2e0`; norm `5e3306082763c2e0` → `5e3306082763c2e0` (identical)
- stderr raw `da6f5bfb48f793ec` → `da6f5bfb48f793ec`; norm `da6f5bfb48f793ec` → `da6f5bfb48f793ec` (identical)

## `tests/integration/test-post-merge-sweep.py`

- exit: baseline 0 → head 0
- stdout raw `65e22b8532744130` → `5d6a31e470c7c8de`; norm `65e22b8532744130` → `5d6a31e470c7c8de`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS: FEAT-64: an unrelated RuntimeError inside the sweep escapes (traceback, not 'post-merge-sweep: ERROR' + exit 0)
+PASS: FEAT-64: the worktree is left standing when the sweep dies
```

## `tests/integration/test-run-unit-tests-kinds.py`

- exit: baseline 0 → head 0
- stdout raw `14012b1f44c33112` → `14012b1f44c33112`; norm `14012b1f44c33112` → `14012b1f44c33112` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/integration/test-run-unit-tests-layout.py`

- exit: baseline 0 → head 0
- stdout raw `530906cedd80d882` → `98e449c3f08e36a9`; norm `530906cedd80d882` → `98e449c3f08e36a9`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS FEAT-64: an unrelated RuntimeError in suite_layout.violations escapes the runner as itself, not as 'MISCONFIGURED: layout check crashed' 
+PASS FEAT-64: a documented layout data-shape failure keeps the 'layout check crashed' rendering at exit 2 
```

## `tests/integration/test-upgrade-config.py`

- exit: baseline 0 → head 0
- stdout raw `ca4991d42c768d62` → `e0cd4b34e37bfa1f`; norm `ca4991d42c768d62` → `e0cd4b34e37bfa1f`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-64: an unrelated RuntimeError in load_harness_json escapes upgrade-config
-12/12 cases passed.
+13/13 cases passed.
```

## `tests/integration/test-worktree-terminal.py`

- exit: baseline 0 → head 0
- stdout raw `09353793cf61612d` → `bbe2871e0559f19c`; norm `09353793cf61612d` → `bbe2871e0559f19c`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS: (n) a git that cannot launch is None from _run_git
+PASS: (n) a git that cannot launch is (False, '') from _worktree_list_raw
+PASS: (n) an unrelated RuntimeError escapes both git launchers
+PASS: (n) an unrelated RuntimeError escapes _repo_arg_for_segment
+PASS: (n) an unrelated RuntimeError escapes the landed feature.json read
+PASS: (n) a FeatureJsonError from the landed read is 'unparseable'
+PASS: (n) an unrelated RuntimeError escapes the landed plan.yaml read
+PASS: (n) MissingDependency (by class) falls back to the top-level status scan
```

## `tests/unit/test-broad-catch-census.py`

- exit: baseline 0 → head 0
- stdout raw `0d0f939d88121985` → `3923dc0227d4d289`; norm `0d0f939d88121985` → `3923dc0227d4d289`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS FEAT-64: factory_decompose.py has a zero ceiling
+PASS FEAT-64: feature_schema.py has a zero ceiling
+PASS FEAT-64: gh_cost_log.py has a zero ceiling
+PASS FEAT-64: handoff_done_when.py has a zero ceiling
+PASS FEAT-64: handoff_policy.py has a zero ceiling
+PASS FEAT-64: harness_yaml.py has a zero ceiling
+PASS FEAT-64: run_identity.py has a zero ceiling
+PASS FEAT-64: worktree_terminal.py has a zero ceiling
+PASS FEAT-64: board-station.py has a zero ceiling
+PASS FEAT-64: check-omp-port.py has a zero ceiling
+PASS FEAT-64: check-plan-routes.py has a zero ceiling
+PASS FEAT-64: check-skill-weight.py has a zero ceiling
+PASS FEAT-64: gh-sync.py has a zero ceiling
+PASS FEAT-64: post-merge-sweep.py has a zero ceiling
+PASS FEAT-64: run-unit-tests.py has a zero ceiling
+PASS FEAT-64: upgrade-config.py has a zero ceiling
+PASS FEAT-64: harness_boundary.py's ceiling is exactly two
+PASS FEAT-64: a third harness_boundary.py broad catch is a finding against two
```

## `tests/unit/test-factory-gh.py`

- exit: baseline 0 → head 0
- stdout raw `614a527522ba3428` → `6572bd5120d6e6c1`; norm `614a527522ba3428` → `6572bd5120d6e6c1`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+ok    FEAT-64 run_gh: a launch PermissionError is GhError
+ok    FEAT-64 run_gh: the launch failure is chained as the cause
+ok    FEAT-64 run_gh: a non-JSON body under json_out is GhError
+ok    FEAT-64 run_gh: the decode failure names the argv and keeps the stdout
+ok    FEAT-64 run_gh: an unrelated RuntimeError escapes
```

## `tests/unit/test-feature-schema-build-entry.py`

- exit: baseline 0 → head 0
- stdout raw `68bf4792957395f7` → `7a3adbe52283f9ea`; norm `68bf4792957395f7` → `7a3adbe52283f9ea`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS FEAT-64 BE-11 a plan.yaml that does not parse is recover-terminal 
+PASS FEAT-64 BE-12 an unrelated RuntimeError in the plan loader escapes recovery_command_for 
```

## `tests/unit/test-gh-cost-log.py`

- exit: baseline 0 → head 0
- stdout raw `5042a2e6bcbf5ec3` → `1631045f5dfccaa8`; norm `5042a2e6bcbf5ec3` → `1631045f5dfccaa8`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS  FEAT-64: an absent counter binary reads None
+PASS  FEAT-64: a counter that prints junk reads None
+PASS  FEAT-64: an unrelated RuntimeError escapes _read_counter
+PASS  FEAT-64: an unrelated RuntimeError escapes record
-39/39 checks passed
+43/43 checks passed
```

## `tests/unit/test-gh-sync-build-entry.py`

- exit: baseline 0 → head 0
- stdout raw `4b1dcfc7047de28c` → `4b1dcfc7047de28c`; norm `4b1dcfc7047de28c` → `4b1dcfc7047de28c` (identical)
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

## `tests/unit/test-handoff-done-when.py`

- exit: baseline 0 → head 0
- stdout raw `0a84a00634104247` → `85f8825192a8291d`; norm `0a84a00634104247` → `85f8825192a8291d`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS FEAT-64: plan.yaml is parsed once per note across resolution and satisfaction 
+PASS FEAT-64: an unrelated RuntimeError in the plan loader escapes resolution 
+PASS FEAT-64: an unrelated RuntimeError in satisfaction escapes 
+PASS FEAT-64: a FleetError from the station vocabulary is indeterminate, not a refusal 
```

## `tests/unit/test-handoff-policy.py`

- exit: baseline 0 → head 0
- stdout raw `dc914f0ad65e979a` → `2b28e266c3392b04`; norm `dc914f0ad65e979a` → `2b28e266c3392b04`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-20 passed, 0 failed
+PASS FEAT-64: an unrelated RuntimeError in the plan loader escapes _plan_mapping 
+21 passed, 0 failed
```

## `tests/unit/test-harness-boundary.py`

- exit: baseline 0 → head 0
- stdout raw `14859aff778938fb` → `1220be5b7538fdac`; norm `14859aff778938fb` → `1220be5b7538fdac`
- stderr raw `7c553e93229b3335` → `2caa1109707dcb8b`; norm `179f949873782ae8` → `179f949873782ae8` (identical)

Lines (stdout):
```
+PASS hook_guard_returns_mains_result
+PASS hook_guard_open_returns_0_on_exception
+PASS hook_guard_open_names_hook_and_failure_and_passing_through
+PASS hook_guard_closed_returns_2_on_exception
+PASS hook_guard_closed_says_BLOCKED
+PASS hook_guard_lets_KeyboardInterrupt_escape
+PASS hook_guard_lets_SystemExit_escape
+PASS hook_guard_is_called_by_no_hook_in_FEAT-64
+PASS linked_worktrees_skips_a_non_utf8_pointer
+PASS linked_worktrees_lets_an_unrelated_RuntimeError_escape
+PASS run_dir_grant_globs_lets_an_unrelated_RuntimeError_escape
+PASS resolve_fleet_blocks_exit_2_on_a_fleet_that_does_not_load
+PASS resolve_fleet_lets_an_unrelated_RuntimeError_escape
```

## `tests/unit/test-harness-yaml-corpus.py`

- exit: baseline 0 → head 0
- stdout raw `a0c9a0436bb323f6` → `3a1860010aa8ff56`; norm `a0c9a0436bb323f6` → `3a1860010aa8ff56`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
-ok    every shipped YAML parses (101 files across 2 roots: .harness=97, .claude/skills/harness/teams=4)
+ok    every shipped YAML parses (104 files across 2 roots: .harness=100, .claude/skills/harness/teams=4)
```

## `tests/unit/test-run-identity.py`

- exit: baseline 0 → head 0
- stdout raw `4ccc92f3e4d38cbc` → `a5a1e9cc8437b76f`; norm `4ccc92f3e4d38cbc` → `a5a1e9cc8437b76f`
- stderr raw `e3b0c44298fc1c14` → `e3b0c44298fc1c14`; norm `e3b0c44298fc1c14` → `e3b0c44298fc1c14` (identical)

Lines (stdout):
```
+PASS an unwritable run dir is False, not a raise
+PASS an unrelated RuntimeError escapes record_seed
+PASS the temp file is still cleaned up after the escape
```

## Summary

| Suite | exit | stdout norm-identical | stderr norm-identical | `-` lines |
|---|---|---|---|---|
| `tests/integration/test-board-station.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-check-omp-port.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-check-plan-routes.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-check-skill-weight.py` | 0→0 | yes | no | 2 |
| `tests/integration/test-factory-decompose.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-gh-sync-abandon.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-gh-sync-open.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-gh-sync-record.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-gh-sync-ship.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-gh-sync-start-task.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-harness-yaml.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-inflight-registry.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-post-merge-sweep.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-run-unit-tests-kinds.py` | 0→0 | yes | yes | 0 |
| `tests/integration/test-run-unit-tests-layout.py` | 0→0 | no | yes | 0 |
| `tests/integration/test-upgrade-config.py` | 0→0 | no | yes | 1 |
| `tests/integration/test-worktree-terminal.py` | 0→0 | no | yes | 0 |
| `tests/unit/test-broad-catch-census.py` | 0→0 | no | yes | 0 |
| `tests/unit/test-factory-gh.py` | 0→0 | no | yes | 0 |
| `tests/unit/test-feature-schema-build-entry.py` | 0→0 | no | yes | 0 |
| `tests/unit/test-gh-cost-log.py` | 0→0 | no | yes | 1 |
| `tests/unit/test-gh-sync-build-entry.py` | 0→0 | yes | yes | 0 |
| `tests/unit/test-handoff-done-when.py` | 0→0 | no | yes | 0 |
| `tests/unit/test-handoff-policy.py` | 0→0 | no | yes | 1 |
| `tests/unit/test-harness-boundary.py` | 0→0 | no | yes | 0 |
| `tests/unit/test-harness-yaml-corpus.py` | 0→0 | no | yes | 1 |
| `tests/unit/test-run-identity.py` | 0→0 | no | yes | 0 |
