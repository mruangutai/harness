# FEAT-64 — red-first receipts

Baseline `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` (detached worktree `.claude/worktrees/harness/feat64-base`).
Digests are `sha256(stream)[:16]` of the suite's stdout / stderr, run as
`HARNESS_PROJECT_DIR=<root> python3 <root>/<suite>` with `cwd=<root>`. `e3b0c44298fc1c14` is the empty stream.

## 1. Baseline (27 suites at a4a3d7f8) vs final head

| Suite | Baseline exit / stdout / stderr | Head exit / stdout / stderr | Verdict |
|---|---|---|---|
| `tests/integration/test-board-station.py` | 0 / `a171319db8ef8248` / `e3b0c44298fc1c14` | 0 / `fbadad1f5f9bbd53` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/integration/test-check-omp-port.py` | 0 / `1e4f62a3c40489e9` / `e3b0c44298fc1c14` | 0 / `716dcdfa0d0b0b2e` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/integration/test-check-plan-routes.py` | 0 / `2cd35b50b598dadb` / `e3b0c44298fc1c14` | 0 / `14e98df79a44a4bb` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/integration/test-check-skill-weight.py` | 0 / `944bd96cf8899fe0` / `b52fd2030bf92de4` | 0 / `944bd96cf8899fe0` / `fd49aba5f35c938b` | additive (ledger A) |
| `tests/integration/test-factory-decompose.py` | 0 / `8aa25728d0e63e67` / `fc2a3cca15b70d98` | 0 / `70501f46d5e84a53` / `9ac42bdb95eeae00` | additive (ledger A) |
| `tests/integration/test-gh-sync-abandon.py` | 0 / `032c0c48770a0662` / `e3b0c44298fc1c14` | 0 / `032c0c48770a0662` / `e3b0c44298fc1c14` | identical |
| `tests/integration/test-gh-sync-open.py` | 0 / `ba2cdd872c4f9fcf` / `e3b0c44298fc1c14` | 0 / `ba2cdd872c4f9fcf` / `e3b0c44298fc1c14` | identical |
| `tests/integration/test-gh-sync-record.py` | 0 / `5567a99547239673` / `e3b0c44298fc1c14` | 0 / `5567a99547239673` / `e3b0c44298fc1c14` | identical |
| `tests/integration/test-gh-sync-ship.py` | 0 / `9807e2b63a5a771a` / `e3b0c44298fc1c14` | 0 / `61240c513bd46074` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/integration/test-gh-sync-start-task.py` | 0 / `ccc5dc0d444cbd3d` / `e3b0c44298fc1c14` | 0 / `ccc5dc0d444cbd3d` / `e3b0c44298fc1c14` | identical |
| `tests/integration/test-harness-yaml.py` | 0 / `b42593b5fd31560e` / `db8ebaba756dcd61` | 0 / `e262cbc6b7063366` / `9a136b682df0904d` | additive (ledger A) |
| `tests/integration/test-inflight-registry.py` | 0 / `5e3306082763c2e0` / `da6f5bfb48f793ec` | 0 / `5e3306082763c2e0` / `da6f5bfb48f793ec` | identical |
| `tests/integration/test-post-merge-sweep.py` | 0 / `65e22b8532744130` / `e3b0c44298fc1c14` | 0 / `5d6a31e470c7c8de` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/integration/test-run-unit-tests-kinds.py` | 0 / `14012b1f44c33112` / `e3b0c44298fc1c14` | 0 / `14012b1f44c33112` / `e3b0c44298fc1c14` | identical |
| `tests/integration/test-run-unit-tests-layout.py` | 0 / `530906cedd80d882` / `e3b0c44298fc1c14` | 0 / `98e449c3f08e36a9` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/integration/test-upgrade-config.py` | 0 / `ca4991d42c768d62` / `e3b0c44298fc1c14` | 0 / `e0cd4b34e37bfa1f` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/integration/test-worktree-terminal.py` | 0 / `09353793cf61612d` / `e3b0c44298fc1c14` | 0 / `bbe2871e0559f19c` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-broad-catch-census.py` | 0 / `0d0f939d88121985` / `e3b0c44298fc1c14` | 0 / `3923dc0227d4d289` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-factory-gh.py` | 0 / `614a527522ba3428` / `e3b0c44298fc1c14` | 0 / `6572bd5120d6e6c1` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-feature-schema-build-entry.py` | 0 / `68bf4792957395f7` / `e3b0c44298fc1c14` | 0 / `7a3adbe52283f9ea` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-gh-cost-log.py` | 0 / `5042a2e6bcbf5ec3` / `e3b0c44298fc1c14` | 0 / `1631045f5dfccaa8` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-gh-sync-build-entry.py` | 0 / `4b1dcfc7047de28c` / `e3b0c44298fc1c14` | 0 / `4b1dcfc7047de28c` / `e3b0c44298fc1c14` | identical |
| `tests/unit/test-handoff-done-when.py` | 0 / `0a84a00634104247` / `e3b0c44298fc1c14` | 0 / `85f8825192a8291d` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-handoff-policy.py` | 0 / `dc914f0ad65e979a` / `e3b0c44298fc1c14` | 0 / `2b28e266c3392b04` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-harness-boundary.py` | 0 / `14859aff778938fb` / `44758db6f3eba2bf` | 0 / `1220be5b7538fdac` / `08d031468a8d4655` | additive (ledger A) |
| `tests/unit/test-harness-yaml-corpus.py` | 0 / `a0c9a0436bb323f6` / `e3b0c44298fc1c14` | 0 / `f2b83c520de73549` / `e3b0c44298fc1c14` | additive (ledger A) |
| `tests/unit/test-run-identity.py` | 0 / `4ccc92f3e4d38cbc` / `e3b0c44298fc1c14` | 0 / `a5a1e9cc8437b76f` / `e3b0c44298fc1c14` | additive (ledger A) |

Seven suites are byte-identical; twenty differ only by the added FEAT-64 case lines, their count lines, one
retitled case, two more YAML files in the corpus, and `tempfile` names on stderr — each ruled in
`build-divergences.md` §A. No suite lost a line; every exit status is 0 on both sides.

## 2. Red executions (each case failing against the pre-change tree, before the production edit)

Every narrowed handler was preceded by a case of the uniform shape "an unrelated `RuntimeError` injected under the
handler must ESCAPE", plus a case pinning the documented outcome for the boundary's real class. Receipts as run,
in build order.

### T-01 (libs) — red at `a4a3d7f8`, green at `8fc213e0` / `c8dd3479`

Re-measured verbatim at the end of the build: the head's ten T-01 suites copied into the `feat64-base` worktree
(bin at `a4a3d7f8`) and run there, `grep`ed to their failing rows. (`test_docs_domain_witness_reddens…` in
test-harness-yaml is the base worktree's own repointed-root control, unrelated to FEAT-64 and green on head;
test-factory-gh's `PermissionError: gh: permission denied` is the suite dying on the very launch failure
`run_gh` now types.)

```
$ python3 tests/integration/test-factory-decompose.py   # head cases against a4a3d7f8 bin
factory: decompose: unexpected failure: RuntimeError: boom, kill before any edge — re-run with FACTORY_DEBUG=1 for a traceback
FAIL  FEAT-64: an unrelated RuntimeError escapes extract_brief
$ python3 tests/unit/test-feature-schema-build-entry.py   # head cases against a4a3d7f8 bin
FAIL FEAT-64 BE-12 an unrelated RuntimeError in the plan loader escapes recovery_command_for 
$ python3 tests/unit/test-gh-cost-log.py   # head cases against a4a3d7f8 bin
FAIL  FEAT-64: an unrelated RuntimeError escapes _read_counter
FAIL  FEAT-64: an unrelated RuntimeError escapes record
$ python3 tests/unit/test-handoff-policy.py   # head cases against a4a3d7f8 bin
FAIL FEAT-64: an unrelated RuntimeError in the plan loader escapes _plan_mapping 
$ python3 tests/unit/test-run-identity.py   # head cases against a4a3d7f8 bin
FAIL an unrelated RuntimeError escapes record_seed 
$ python3 tests/unit/test-handoff-done-when.py   # head cases against a4a3d7f8 bin
FAIL FEAT-64: plan.yaml is parsed once per note across resolution and satisfaction ['/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp0x7qhe88/.harness/harness/features/FEAT-91-satisfaction/plan.ya
FAIL FEAT-64: an unrelated RuntimeError in the plan loader escapes resolution 
FAIL FEAT-64: an unrelated RuntimeError in satisfaction escapes 
$ python3 tests/integration/test-harness-yaml.py   # head cases against a4a3d7f8 bin
FAIL test_docs_domain_witness_reddens_on_addition_removal_and_census_drift: control (unmutated manifest, repointed root) must exit 0:
FAIL test_feat64_load_str_boundary_is_typed: an unrelated RuntimeError must escape load_str, not become YamlParseError
FAIL test_feat64_require_or_die_cleanup_boundary_is_typed: an unrelated RuntimeError must escape require_or_die's cleanup
FAIL test_feat64_load_str_boundary_is_typed: an unrelated RuntimeError must escape load_str, not become YamlParseError
FAIL test_feat64_require_or_die_cleanup_boundary_is_typed: an unrelated RuntimeError must escape require_or_die's cleanup
$ python3 tests/unit/test-harness-boundary.py   # head cases against a4a3d7f8 bin
FAIL case_hook_guard_contract_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'hook_guard'")
FAIL linked_worktrees_lets_an_unrelated_RuntimeError_escape 
FAIL run_dir_grant_globs_lets_an_unrelated_RuntimeError_escape 
$ python3 tests/integration/test-worktree-terminal.py   # head cases against a4a3d7f8 bin
FAIL: (n) an unrelated RuntimeError escapes both git launchers
FAIL: (n) an unrelated RuntimeError escapes _repo_arg_for_segment
FAIL: (n) an unrelated RuntimeError escapes the landed feature.json read
FAIL: (n) an unrelated RuntimeError escapes the landed plan.yaml read
$ python3 tests/unit/test-factory-gh.py   # head cases against a4a3d7f8 bin
PermissionError: gh: permission denied
```

### T-02 (tools) — red committed as `d1a611c7`, green at `94cb7fa0`

```
$ python3 tests/integration/test-board-station.py
FAIL  FEAT-64: an unrelated RuntimeError inside set_station escapes (non-zero, not ERROR/exit 0) — rc=0 stderr='board-station: ERROR - #326 -> plan: unrelated defect\n'
$ python3 tests/integration/test-check-omp-port.py
FAIL  FEAT-64: an unrelated RuntimeError in the config reader escapes check-omp-port (traceback, not 'cannot read') — rc=1 stderr='OMP-PORT: cannot read .omp/config.yml: unrelated defect\n…'
$ python3 tests/integration/test-check-skill-weight.py
FAIL: test_feat64_unrelated_defect_in_frontmatter_escapes (…) AssertionError: RuntimeError not raised
$ python3 tests/integration/test-upgrade-config.py
FAIL  FEAT-64: an unrelated RuntimeError in load_harness_json escapes upgrade-config
$ python3 tests/integration/test-run-unit-tests-layout.py
FAIL FEAT-64: an unrelated RuntimeError in suite_layout.violations escapes the runner as itself, not as 'MISCONFIGURED: layout check crashed' rc=2 … RuntimeError: unrelated defect (rendered inside the crash string)
PASS FEAT-64: a documented layout data-shape failure keeps the 'layout check crashed' rendering at exit 2
$ python3 tests/integration/test-post-merge-sweep.py
FAIL: FEAT-64: an unrelated RuntimeError inside the sweep escapes (traceback, not 'post-merge-sweep: ERROR' + exit 0) — rc=0 stdout='…post-merge-sweep: ERROR: unrelated defect\n' stderr=''
$ python3 tests/integration/test-gh-sync-ship.py
FAIL  FEAT-64: an unrelated RuntimeError inside the audit escapes ship (traceback, not 'the board audit could not run')
      rc=0 stderr=': ERROR - the board audit could not run: unrelated defect\n…'
```

### T-03 — red at `94cb7fa0`, green at `05e48294`

```
$ python3 tests/integration/test-check-plan-routes.py
FAIL feat64_manifest_deviation_unrelated_RuntimeError_escapes the broad catch turned a defect into a DEVIATION line
FAIL feat64_live_plan_loaded_exactly_once_per_execution rc=0 calls={'…/FEAT-A/plan.yaml': 2}
FAIL feat64_shipped_plan_loaded_exactly_once_and_skipped rc=0 calls={'…/FEAT-A/plan.yaml': 2}
FAIL feat64_ceiling_<each of the 16 files>_is_zero ceiling <old count>
FAIL feat64_ceiling_harness_boundary_is_exactly_two ceiling 6
FAIL feat64_census_lib_except_exception_mutant_is_one_finding_naming_handoff_policy.py
FAIL feat64_census_lib_bare_except_mutant_is_one_finding_naming_handoff_policy.py
FAIL feat64_census_tool_except_exception_mutant_is_one_finding_naming_gh-sync.py
FAIL feat64_census_tool_bare_except_mutant_is_one_finding_naming_gh-sync.py
FAIL feat64_census_third_harness_boundary_catch_fails_against_two
PASS feat64_census_reduction_mutant_is_clean
$ python3 tests/unit/test-broad-catch-census.py
FAIL FEAT-64: <each of the 16 files> has a zero ceiling <old count>
FAIL FEAT-64: harness_boundary.py's ceiling is exactly two
```

Independent re-measurement of the reparse (ad-hoc shim counting `artifact_accessors.load_plan` calls over one
shipped plan, `/tmp/feat64-reparse-red.py`): baseline `load_plan calls: 2`; head `load_plan calls: 1`.

## 3. Final receipts at head

```
$ python3 tests/unit/test-broad-catch-census.py && python3 tests/integration/test-check-plan-routes.py \
    && python3 .claude/skills/harness/bin/check-plan-routes.py --consolidation-audit
ALL PASS
ALL PASS
0 consolidation finding(s) under bin/
$ python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit          # exit 0 (the `FAIL` rows inside
                                                                            #  test-factory-claim-mutation.py are its
                                                                            #  own MUTANT ACTIVE reddening, exit 0)
$ python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration   # exit 0 after test-board-lifecycle c4
                                                                            #  (ledger B3)
$ python3 .claude/skills/harness/bin/code-grade.py --base a4a3d7f8 --head HEAD   # exit 0, 0 × RESULT: FAIL
```

AST census at head (handlers typed exactly `Exception` or bare):
`bash-write-guard 6, branch-create-gate 4, check-domain 24, check-plan-routes 0, dispatch-guard 9, feature-record 1,
gh-close-gate 3, harness_boundary 2, inflight_registry 3, inject-expertise 2, merge-gate 5, plan-sign-gate 2,
validate-digest 18` — every FEAT-64 lib and tool at 0; the eleven hook files untouched for FEAT-65.
