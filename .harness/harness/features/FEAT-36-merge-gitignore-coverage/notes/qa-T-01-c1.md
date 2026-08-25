# QA gate — T-01 SC-05 evidence amendment

PASS. The SC-05-only working-tree diff changes `.agents/skills/harness/bin/test-merge-gitignore.py`:117-126, replacing the absence-only caller-CWD assertion with a pre-existing `caller-only-rule` byte-preservation assertion. No other working-tree file is changed.

## Contract and matrix

`plan.yaml:41-57` names T-01, declares `[unit, integration]`, and carries this exact command (including the line break):

```sh
python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
.agents/skills/harness/bin/run-unit-tests.sh --kind all
```

It matches the dispatched command byte-for-byte. `harness.json:40-50` independently requires unit and integration for `change_type: feature`; no UI predicate applies to this non-interaction test-only diff.

## Phase 1 expectation / Phase 2 result

Before inspecting code, expected behavioral coverage was: preserve existing content; complete and incomplete read-only `--check`; absent and partial targets with exact canonical-rule cardinality; byte-identical rerun; and explicit project-root isolation from an unrelated caller directory. Phase 2 found all seven named cases, with no coverage gap. The strengthened SC-05 case at `test-merge-gitignore.py:113-126` creates a caller `.gitignore`, snapshots its bytes, runs the real absolute utility with an explicit project root from that caller, requires the target project change, and requires caller bytes unchanged. This is non-vacuous: a write to an already-present caller file cannot satisfy an absence-only assertion.

## Measured gate evidence

The prescribed command exited 0 (156.44s aggregate). Standalone discovery/execution: 7/7 named cases passed — `preserves_existing_content`, `check_complete_is_read_only`, `check_incomplete_reports_missing_and_is_read_only`, `absent_target_receives_each_rule_once`, `partial_target_retains_present_rule_and_adds_missing_once`, `second_merge_is_byte_identical`, and strengthened `explicit_project_root_ignores_caller_cwd` (SC-05).

`run-unit-tests.sh:17-18` registers 23 unit and 23 integration scripts; `--kind all` selects their union (`run-unit-tests.sh:35-45`). All 46/46 registrations executed successfully in the same aggregate command, including integration registration `test-merge-gitignore.py` (`run-unit-tests.sh:18`). No runner `MISCONFIGURED`, `KIND-DRIFT`, or `FAIL test-` diagnostic occurred. The runner's own kind-check regression test also measured zero live `KIND-DRIFT` lines.

## Success-criterion evidence

- SC-01: `test-merge-gitignore.py:36-47` / named `preserves_existing_content`.
- SC-02: `:50-73` / named complete and incomplete read-only cases.
- SC-03: `:76-98` / named absent and partial cases.
- SC-04: `:101-110` / named `second_merge_is_byte_identical`.
- SC-05: `:113-126` / named `explicit_project_root_ignores_caller_cwd`.
- SC-06: inspection: `run-unit-tests.sh:18` registers the test as integration; this SC-05-only diff does not alter `merge-gitignore.sh`.

must_fix: none.
