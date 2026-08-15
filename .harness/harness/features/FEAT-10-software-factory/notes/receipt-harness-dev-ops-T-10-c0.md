# Receipt — harness-dev-ops — T-10 (c0)

## Task
Widen `test_kinds.integration.detect` in `.harness/harness.json` so the integration kind
resolves (matches at least one file) instead of "no test files matched", and delete the
stale `_reason` key that claims detection has not been run.

## Edit — before / after

Before (verbatim, `_reason` value quoted for the record — superseded, marked stale):
```
"integration": {
  "detect": "tests/integration/**",
  <!-- ok-stale -->
  "exclude": ".claude/worktrees/**|node_modules/**|vendor/**|.venv/**",
  "cmd": ".claude/skills/harness/bin/run-unit-tests.sh --kind integration",
  <!-- ok-stale -->
  "_reason": "unset — dev-ops has not run detection yet"
}
```

After:
```
"integration": {
  "detect": "tests/integration/**|.claude/skills/harness/bin/test-check-state.py|.claude/skills/harness/bin/test-factory-integration.py",
  "exclude": ".claude/worktrees/**|node_modules/**|vendor/**|.venv/**",
  "cmd": ".claude/skills/harness/bin/run-unit-tests.sh --kind integration"
}
```

No other kind's `detect`, `exclude`, `cmd` or `_reason` was touched. File confirmed valid
JSON after the edit (`python3 -c "import json; json.load(open('.harness/harness.json'))"`
exits 0).

## `verify:` — run verbatim from the repo root, output verbatim

Command (cross-checked byte-for-byte against plan.yaml T-10 `verify:` at line 1588 before
running — matched exactly):

```
python3 -c "import json,glob; k=json.load(open('.harness/harness.json'))['test_kinds']['integration']; pats=k['detect'].split('|'); assert k['cmd']; assert '_reason' not in k, 'stale _reason left beside a filled cmd'; assert '.claude/skills/harness/bin/test-factory-integration.py' in pats, pats; hits=[f for p in pats for f in glob.glob(p, recursive=True)]; assert '.claude/skills/harness/bin/test-check-state.py' in hits, hits; print('integration detects', len(hits), 'file(s)')"
```

Output:
```
integration detects 1 file(s)
```

(1 hit: `.claude/skills/harness/bin/test-check-state.py` exists today; `test-factory-integration.py`
is present in the `detect` string, per the task's intent, but does not yet exist on disk — T-12's
job, not this task's.)

## Second measurement — `run-unit-tests.sh --kind integration`

Command:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```

**Exit status: 0**

**Complete list of PASS/FAIL lines printed (76 total, 0 FAIL):**
```
PASS test-validate-digest.py
PASS test-gh-sync.py
PASS test-check-state.py
PASS test-check-expertise.py
PASS test-gen-decisions-index.py
PASS test-bash-write-guard.py
PASS test-check-domain.py
PASS test-harness-yaml.py
PASS test-upgrade-config.py
PASS case_01_ungranted_undeclared_exits_nonzero
PASS case_02_output_has_task_id
PASS case_03_output_has_offending_path
PASS case_04_all_granted_exits_0
PASS case_05_ungranted_declared_main_session_exits_0
PASS case_06_wildcard_produces_unresolved_glob
PASS case_07_wildcard_exit_status_matches_task_removed
PASS case_08_source_mentions_check_domain_sh
PASS case_09_source_has_no_fnmatch
PASS case_16_source_has_no_glob_to_re
PASS case_10_template_has_lanes_section
PASS case_11_template_has_team_token
PASS case_12_template_has_main_session_direct_token
PASS case_13_runner_lists_this_test
PASS case_14_granted_but_main_session_produces_deviation
PASS case_15_deviation_plan_still_exits_0
PASS case_17_midpattern_wildcard_grant_no_violation
PASS case_17_midpattern_wildcard_grant_reports_ok
PASS case_17_midpattern_wildcard_grant_exits_0
PASS case_17b_ok_line_names_the_exact_granting_set
PASS case_19a_argvless_output_is_independent_of_cwd
PASS case_19a3_argvless_actually_finds_the_plans
PASS case_19a2_argvless_names_the_root_it_scanned
PASS case_19b_unresolvable_root_exits_2_not_0
PASS case_19b2_unresolvable_root_says_why_on_stderr
PASS case_19b3_unusable_project_dir_is_reported_not_silently_replaced
PASS case_19b4_a_valid_project_dir_is_not_warned_about
PASS case_19b5_an_unset_project_dir_is_not_warned_about
PASS case_19a4_discovery_finds_exactly_the_feature_plans
PASS case_19a5_the_scan_line_matches_the_glob_that_ran
PASS case_19c_zero_feature_project_is_not_an_error
PASS case_19c2_zero_feature_project_scans_the_declared_root
PASS case_19d_explicit_path_unaffected_by_the_root_guard
PASS case_19d2_explicit_path_with_no_tasks_still_exits_0
PASS case_20_bash_write_guard_sh_probes_the_manifest
PASS case_20_check_domain_sh_probes_the_manifest
PASS case_20_check_plan_routes_py_probes_the_manifest
PASS case_20_the_detector_is_not_blind
PASS case_21_a_bare_harness_dir_is_not_a_project_root
PASS case_22a_unreadable_feature_dir_exits_2
PASS case_22b_unreadable_plan_file_exits_2
PASS case_22c_broken_symlink_plan_is_reported_not_skipped
PASS case_22d_a_readable_tree_is_not_flagged
PASS case_23a_plan_yaml_granted_path_is_OK
PASS case_23b_plan_yaml_ungranted_path_is_a_VIOLATION
PASS case_23c_an_annotated_path_resolves_to_NOBODY_not_silently_cleaned
PASS case_23d_a_malformed_plan_yaml_exits_2_not_1
PASS case_23e_the_per_task_machine_budget_fires
PASS case_23f_the_budget_stays_silent_on_a_normal_task
PASS case_23h_an_over_budget_task_sets_the_EXIT_CODE_not_just_stdout
PASS case_23i_the_budget_boundary_is_exact
PASS case_23j_every_budgeted_field_counts_exactly_once
PASS case_23j2_BUDGETED_FIELDS_is_still_the_eleven_this_case_pins
PASS case_23g_both_plan_yaml_and_PLAN_md_is_refused
PASS case_24_shipped_is_skipped
PASS case_24_abandoned_is_skipped
PASS case_24_in_review_is_checked
PASS case_24_awaiting_user_is_checked
PASS case_24_no_feature_yaml_is_checked_not_skipped
PASS case_24_feature_yaml_a_sequence_is_checked_not_crashed
PASS case_24_feature_yaml_a_bare_scalar_is_checked_not_crashed
PASS case_24_feature_yaml_status_is_a_list_is_checked_not_crashed
PASS case_24_feature_yaml_a_mapping_with_no_status_is_checked_not_crashed
PASS test-check-plan-routes.py
PASS test-merge-settings.py
PASS test-gen-omp-agents.py
PASS test-omp-reviewer-guard.py
```

Note (mechanism, stated after the measured output per instructions): the executed list is
driven by `run-unit-tests.sh`'s own `INTEGRATION_SCRIPTS` list (unmodified by this task —
T-11 owns that file), not by the widened `detect` glob in `harness.json`. `detect` feeds the
qa gate's kind-resolution check (SC-06), separate from what this runner executes. This T-10
edit did not add or remove any test from the executed set; it only made the kind resolvable.
`test-factory-integration.py` does not yet appear in the executed list because it does not
yet exist (T-12).

## Bounds observed

- Did not touch `.claude/skills/harness/bin/check-state.sh` or
  `.claude/skills/harness/bin/test-check-state.py` (DEC-174 carve-out; T-10 only names the
  file in the `detect` glob).
- Did not touch `.claude/skills/harness/bin/run-unit-tests.sh` (T-11's file).
- Only file written: `.harness/harness.json`, plus this receipt.
- Pre-existing `check-state.sh` VIOLATIONs (FEAT-04/FEAT-07) were not touched or repaired.

## Verdict

PASS. Both the task `verify:` and the second integration-run measurement succeeded with the
expected shapes; the edit is minimal and scoped exactly as specified.
