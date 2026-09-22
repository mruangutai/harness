# FEAT-63 red-first receipts

Every new case run against the PINNED tree 804d68b8 (a detached worktree at /tmp/feat63/pin
with only the four test files copied in from the build tree), then against the build tree.
Command, then the case lines verbatim. Captured 2026-09-21 by the main session.

## RED at 804d68b8

```
$ python3 tests/integration/test-check-state-entry.py | grep FEAT-63
FAIL - FEAT-63: gh auth status is probed exactly once per run (probes: 2; INV-30 still fired: True)

$ python3 tests/integration/test-check-state-feat59.py | grep "(63\."
FAIL - case (63.a) an unimportable feature_schema is INV-23 CANNOT RUN naming the failure
FAIL - case (63.b) the 300-line fallback is gone — nothing is graded against a guessed budget

$ python3 tests/unit/test-harness-boundary.py | grep -E "^FAIL"
FAIL case_load_repo_module_failures_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'RepoModuleError'")

$ python3 tests/integration/test-check-plan-routes.py | grep -E "^FAIL feat63"
FAIL feat63_reparse_load_feature_json_mutant_fails_for_its_own_finding .claude/skills/harness/bin/check-state.py::inv_2:4449 INV-2 opens 'feature.json' but its row declares no path: read covering it (
FAIL feat63_reparse_load_harness_json_mutant_fails_for_its_own_finding .claude/skills/harness/bin/check-state.py::inv_2:4449 INV-2 opens 'harness.json' but its row declares no path: read covering it (
FAIL feat63_census_checker_except_exception_mutant_is_one_finding_naming_check_state 
FAIL feat63_census_checker_bare_except_mutant_is_one_finding_naming_check_state 
FAIL feat63_census_frozen_script_plus_one_is_one_finding_naming_it 
FAIL feat63_census_allowance_never_transfers_between_files 
FAIL feat63_census_unlisted_script_has_a_zero_ceiling 
```

## GREEN on the build tree

```
$ python3 tests/integration/test-check-state-entry.py | grep FEAT-63
ok - FEAT-63: gh auth status is probed exactly once per run (probes: 1; INV-30 still fired: True)
$ python3 tests/integration/test-check-state-feat59.py | grep "(63\."
ok - case (63.a) an unimportable feature_schema is INV-23 CANNOT RUN naming the failure
ok - case (63.b) the 300-line fallback is gone — nothing is graded against a guessed budget
$ python3 tests/unit/test-harness-boundary.py | tail -1
ALL PASS
$ python3 tests/integration/test-check-plan-routes.py | grep -cE "^PASS feat63"
9
```

## Fix round 2 (QA-C1-01) — unit kind

```
$ CHECK_PLAN_ROUTES_BIN=<804d68b8 bin>/check-plan-routes.py python3 tests/unit/test-broad-catch-census.py   # RED at the pin
AttributeError: module '_census_under_test' has no attribute '_broad_catch_count'
$ python3 tests/unit/test-broad-catch-census.py | tail -1   # GREEN on the build
ALL PASS
```
