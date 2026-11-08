# Fail-first receipt — FEAT-2206 T-01

Baseline = `git archive b7af829c .claude/skills/harness/bin` exported to /private/tmp/f2206-baseline (plus a .harness/team-config.yaml marker so its root resolves). The NEW tests run against it via CHECK_STATE_BIN_DIR (unit) and CHECK_STATE_BIN (integration). Env: CLAUDE_PROJECT_DIR, HARNESS_PROJECT_DIR, HARNESS_AGENT_TYPE unset.

## Unit — `CHECK_STATE_BIN_DIR=<baseline bin> python3 tests/unit/test-check-state-shipped-ctx.py` → exit 1 (10 failures)

```
PASS  precondition: the shipped fixture plan fails the strict loader
FAIL  subjects are exactly the unshipped features (missing, unreadable, nested, non-mapping, ambiguous and non-done status stay checked) — features=['FEAT-1-shipped', 'FEAT-2-shipped-quoted', 'FEAT-3-building', 'FEAT-4-no-status', 'FEAT-5-nested-status', 'FEAT-6-no-plan', 'FEAT-7-not-utf8', 'FEAT-8-list-document', 'FEAT-9-two-statuses']
FAIL  the context records which discovered features shipped — shipped=None
FAIL  a strict-invalid shipped plan produces no loading finding — .harness/harness/features/FEAT-1-shipped/plan.yaml does not load, so INV-3/4/5 cannot be checked for it: failed to parse YAML in /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpvf75umw0/.harness/harness/features/FEAT-1-shipped/plan.yaml: `tasks:` is missing or not a list; .harness/harness/features/FEAT-2-shipped-quoted/plan.yaml does not load, so INV-3/4/5 cannot be checked for it: failed to parse YAML in /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpvf75umw0/.harness/harness/features/FEAT-2-shipped-quoted/plan.yaml: `tasks:` is empty, so this must be a station-only record and must SAY so: it needs `station_only: true` and a top-level `status:`. An emptied plan is not a station-only record.
FAIL  FEAT-1-shipped: context construction opens only its plan.yaml — opened=['BRIEF.md', 'STATE.md', 'plan.yaml']
FAIL  FEAT-2-shipped-quoted: context construction opens only its plan.yaml — opened=['BRIEF.md', 'STATE.md', 'plan.yaml']
PASS  control: an unshipped feature's BRIEF and plan are still read up front
FAIL  keep={shipped} leaves no audit subject — features=['FEAT-1-shipped']
PASS  control: keep={unshipped} keeps it
PASS  no shipped feature.json is opened while the context is built
FAIL  population entries carry (feature, document, shipped) — [('FEAT-1-shipped', {'feature_id': 'FEAT-1-shipped', 'factory': {'repo': 'acme/widget', 'issues': {'T-01': 11}}}), ('FEAT-2-shipped-quoted', None), ('FEAT-3-building', {'feature_id': 'FEAT-3-building', 'factory': {'repo': 'acme/widget', 'issues': {'T-01': 11}}})]
FAIL  a readable shipped record is in the population, flagged shipped — None
PASS  an unparseable shipped record contributes no claim
FAIL  an unshipped record is in the population, not flagged shipped — {}
FAIL  an unparseable shipped record is never reported — .harness/harness/features/FEAT-2-shipped-quoted/plan.yaml does not load, so INV-3/4/5 cannot be checked for it: failed to parse YAML in /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmplcwnteex/.harness/harness/features/FEAT-2-shipped-quoted/plan.yaml: `tasks:` is missing or not a list

10 failure(s)
```

## Integration — `CHECK_STATE_BIN=<baseline bin>/check-state.py python3 tests/integration/test-check-state-shipped.py -v` → exit 1 (8 failures)

Already correct at baseline, so not claimed newly red: INV-24 shipped/active and shipped/shipped collisions, INV-29 standing worktree, INV-52 shared branch, missing-selector refusal, unreadable-status control.

```
test_inv24_does_not_grade_a_shipped_claim_itself ... FAIL
test_inv24_sees_a_collision_between_a_shipped_and_an_active_claim ... ok
test_inv24_sees_a_collision_between_two_shipped_claims ... ok
test_inv29_sees_a_standing_worktree_of_a_shipped_feature ... ok
test_inv52_sees_two_shipped_features_on_one_branch ... ok
test_inv28_and_inv30_are_retired ... FAIL
test_no_milestone_or_pull_request_check_runs_for_a_shipped_feature ... FAIL
test_selecting_a_retired_number_runs_nothing ... FAIL
test_a_changed_audit_names_no_shipped_feature ... FAIL
test_a_full_audit_names_no_shipped_feature ... FAIL
test_a_missing_selected_feature_still_refuses ... ok
test_a_shipped_directory_is_read_only_for_status_and_comparison ... FAIL
test_an_unreadable_status_keeps_every_check ... ok
test_selecting_a_shipped_feature_prints_one_note_and_exits_clean ... FAIL
Ran 14 tests in 8.071s
FAILED (failures=8)
```

## After the change

- unit: 0 failure(s); integration: Ran 14 tests, OK.
- `--real-corpus /Users/molchairuangutai/GitHub/harness`: 9 landed, 7 shipped, every shipped record excluded, open-confined and one-note on explicit selection; 0 failure(s).
- full suite (`run-unit-tests.py --kind all`): 146 files, all exit 0 after the DEC-252 index ruling was shortened to the 30-word cap.

## Rework round 1 (validate FAIL at fe49c8df; two must-fixes)

Baseline = the reviewed pin `fe49c8df` bin exported to /private/tmp/f2206-pin (plus
`.harness/team-config.yaml` so the unit import resolves a root).

| Regression | At pin fe49c8df | After rework |
|---|---|---|
| unit: FEAT-10..13 duplicate status keys (list, empty, number-first, quoted key) stay subjects | FAIL (2 assertions: subjects, shipped set) | PASS |
| integration `test_a_duplicate_status_key_keeps_every_check` (full audit + `--feature`) | FAIL | PASS |
| integration `test_inv24_skips_unusable_shipped_numbers_and_keeps_usable_ones` ("²" parent, "x" issue, usable 11 collision) | FAIL (ValueError traceback in INV-24) | PASS |

Fixing INV-24's coercion alone exposed the same crash one layer down: the census strict-loads every
landed record for INV-52 and `feature_json_write.opt_int` (the shared coercion, documented to
return None for junk) raised on "²". Fixed there (ASCII digits only); INV-24's
`_inv24_issue_number` now delegates to it instead of carrying a second copy.
