# FEAT-61 fail-first receipts (validate c1, VAL-01)

Method: a disposable `git worktree` at the plan baseline `066638e8` (pre-T-01 source) with HEAD `170b2032`'s `tests/unit` and `tests/integration` overlaid, so each new or changed test runs against the code it was written to redden. Every file below exits non-zero on the baseline and exits 0 at HEAD (the signed verify chains, recorded in `review-harness-qa-c1.md`). Captured 2026-09-20 by the main session; the worktree was removed afterwards.

## SC-02

### `tests/unit/test-factory-config.py` — baseline exit 1

    FAIL  (FEAT-61) STATION_ROWS is an ordered tuple of (name, has_board_column, bucket) rows
    FAIL  (FEAT-61) STATION_ROWS names are plain strings in lifecycle order
    FAIL  (FEAT-61) MANDATED_STATIONS is derived: exactly the rows with a board column, in order
    FAIL  (FEAT-61) TERMINAL_STATIONS is derived: exactly the rows without a board column, in order
    FAIL  (FEAT-61) ACTIVE_STATIONS is the four in-progress stations, in order
    FAIL  (FEAT-61) FINISHED_STATIONS is done then the terminal names — the old concatenation order
    FAIL  (FEAT-61) not_started | active | finished partition the eight names with no overlap
    FAIL  (FEAT-61) is_active/is_finished('backlog') == (False, False)
    FAIL  (FEAT-61) is_active/is_finished('plan') == (True, False)
    FAIL  (FEAT-61) is_active/is_finished('ready') == (True, False)
    FAIL  (FEAT-61) is_active/is_finished('building') == (True, False)
    FAIL  (FEAT-61) is_active/is_finished('review') == (True, False)

## SC-06

### `tests/unit/test-artifact-accessors.py` — baseline exit 1

    ERROR: test_load_run_step_contract_is_strict_about_the_schema_file_itself (__main__.JsonContracts.test_load_run_step_contract_is_strict_about_the_schema_file_itself)
    ERROR: test_load_run_step_contract_preserves_natural_failures_for_malformed_shapes (__main__.JsonContracts.test_load_run_step_contract_preserves_natural_failures_for_malformed_shapes) (text='{"properties": {}}')
    ERROR: test_load_run_step_contract_preserves_natural_failures_for_malformed_shapes (__main__.JsonContracts.test_load_run_step_contract_preserves_natural_failures_for_malformed_shapes) (text='{"properties": {"steps": []}}')
    ERROR: test_load_run_step_contract_preserves_natural_failures_for_malformed_shapes (__main__.JsonContracts.test_load_run_step_contract_preserves_natural_failures_for_malformed_shapes) (text='{"properties": {"steps": {"items": {"properties": {}}}}}')
    ERROR: test_load_run_step_contract_returns_step_schema_declared_keys_and_evidence_pattern (__main__.JsonContracts.test_load_run_step_contract_returns_step_schema_declared_keys_and_evidence_pattern)
    ERROR: test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror (__main__.JsonContracts.test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror) (text='{"outer": {"key": 1, "key": 2}}')
    ERROR: test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror (__main__.JsonContracts.test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror) (text='[{"a": 1, "a": 2}]')
    ERROR: test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror (__main__.JsonContracts.test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror) (text='{"value": NaN}')
    ERROR: test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror (__main__.JsonContracts.test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror) (text='{"value": Infinity}')
    ERROR: test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror (__main__.JsonContracts.test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror) (text='{"value": -Infinity}')
    ERROR: test_strict_json_loads_returns_any_json_value_untouched (__main__.JsonContracts.test_strict_json_loads_returns_any_json_value_untouched) (text='{"nested": {"value": 7}}')
    ERROR: test_strict_json_loads_returns_any_json_value_untouched (__main__.JsonContracts.test_strict_json_loads_returns_any_json_value_untouched) (text='[{"value": 7}, 2]')

### `tests/unit/test-feature-json-reader.py` — baseline exit 1

    FAIL: test_private_hook_twins_are_gone (__main__.ParseDocTest.test_private_hook_twins_are_gone)
    FAILED (failures=1)

### `tests/unit/test-harness-boundary.py` — baseline exit 1

    FAIL case_feature_artifact_checkout_mismatch_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'feature_artifact_checkout_mismatch'")
    FAIL case_feature_artifact_checkout_mismatch_ambiguous_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'feature_artifact_checkout_mismatch'")
    FAIL case_load_repo_module_registration_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'load_repo_module'")
    FAIL case_load_repo_module_failures_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'load_repo_module'")

### `tests/integration/test-check-state-feat59.py` — baseline exit 1

    FAIL - case (61.b) the failed exec leaves no check_skill_weight entry in sys.modules
    FAIL - case (61.c) a null module spec is INV-42 CANNOT RUN as an ImportError naming the path
    FAIL - case (61.e) a duplicate key in run-state-schema.json is INV-16 CANNOT be checked, never last-wins

### `tests/integration/test-check-domain.py` — baseline exit 1

    FAIL  a duplicate key in run-state-schema.json is refused as unreadable, never last-wins

## SC-03

### `tests/integration/test-plan-merge.py` — baseline exit 1

    FAIL  resume/review: reset records the classified resume station
    FAIL  resume/ready/'Building': a task station outside the vocabulary raises rather than classifies
    FAIL  resume/ready/'Building': the refused mutation leaves the plan byte-identical
    FAIL  resume/building/'': a task station outside the vocabulary raises rather than classifies
    FAIL  resume/building/'': the refused mutation leaves the plan byte-identical
    FAIL test-plan-merge.py

### `tests/integration/test-gh-sync-record.py` — baseline exit 1

    FAIL  status Review, task station outside the vocabulary: names the value, no traceback

### `tests/integration/test-worktree-terminal.py` — baseline exit 1

    FAIL: landed station outside the vocabulary -> unresolved, naming the value, never omitted

## SC-04

### `tests/unit/test-gate-policy.py` — baseline exit 1

    Traceback (most recent call last):
    KeyError: 'qa_gate'
    Traceback (most recent call last):
        raise GatePolicyError(gate, None) from error
    gate_policy.GatePolicyError: invalid gate policy for qa_gate: None

### `tests/integration/test-validate-digest.py` — baseline exit 1

    ok    [bug919] BUG-1756 SC-04: a spawn OSError fails OPEN, loudly
    Traceback (most recent call last):
    KeyError: 'qa_gate'
    Traceback (most recent call last):
        raise GatePolicyError(gate, None) from error
    gate_policy.GatePolicyError: invalid gate policy for qa_gate: None

## SC-05

### `tests/integration/test-check-domain-worktree.py` — baseline exit 1

    FAIL  [feat61] an unexpected core failure is absorbed and the allowance stands

### `tests/integration/test-bash-write-guard.py` — baseline exit 1

    FAIL  mandated commit trailer (angle brackets in a quoted string)
    FAIL  an arrow inside a quoted string
    FAIL  an HTML comment inside a quoted string
    FAIL  a heredoc delimiter is not a redirect target
    FAIL  input redirection is a READ, not a write
    FAIL  a quoted string mentioning a redirect
    FAIL  stderr redirection is not the cp destination
    FAIL  stderr redirection is not an rm target
    FAIL  rm -f in-domain passes
    FAIL  sed -i -f in-domain passes
    FAIL  plain read commands pass
    FAIL  a comparison operator inside a python heredoc body

## SC-01/SC-07

HEAD's `check-plan-routes.consolidation_findings` over the baseline `bin/` reports **16 findings** (0 at HEAD) — the pre-migration sites, by name:

- `.claude/skills/harness/bin/board_lifecycle.py::<module>:459`
- `.claude/skills/harness/bin/check-plan-routes.py::finished_stations:525`
- `.claude/skills/harness/bin/check-state.py::<module>:107`
- `.claude/skills/harness/bin/check-state.py::<module>:2426`
- `.claude/skills/harness/bin/check-state.py::<module>:2728`
- `.claude/skills/harness/bin/check-state.py::<module>:1314`
- `.claude/skills/harness/bin/gh-sync.py::_apply_parent_rule:345`
- `.claude/skills/harness/bin/gh-sync.py::finished_stations:955`
- `.claude/skills/harness/bin/gh-sync.py::cmd_status:1525`
- `.claude/skills/harness/bin/gh_board.py::_active_lifecycle_station:146`
- `.claude/skills/harness/bin/handoff_done_when.py::_satisfied_plan:277`
- `.claude/skills/harness/bin/plan-merge.py::_approval_reset_context:894`
- `.claude/skills/harness/bin/plan-merge.py::_approval_resume_station:2037`
- `.claude/skills/harness/bin/plan-merge.py::_feature_record_module:2254`
- `.claude/skills/harness/bin/plan-merge.py::_check_plan_routes_module:3405`
- `.claude/skills/harness/bin/worktree_terminal.py::_import_feature_worktree:44`

SC-01's byte receipt (`tests/integration/fixtures/feat61-check-plan-routes-lifecycle.receipt.json`) was captured from the pre-T-05 script and is compared whole at HEAD; the lock above is the red half of that pair.

