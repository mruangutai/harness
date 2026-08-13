# Receipt — harness-backend-dev — T-01 (task-status enum in check-plan-routes)

## Invocation (exact, verbatim from plan.yaml's `verify:`)

```
python3 .claude/skills/harness/bin/test-check-plan-routes.py && python3 .claude/skills/harness/bin/check-plan-routes.py
```

Cross-checked against `plan.yaml` T-01's `verify:` block — identical, no discrepancy.
Run from repo root `/Users/molchairuangutai/GitHub/harness`.

## Observed output, verbatim

### Half 1 — `python3 .claude/skills/harness/bin/test-check-plan-routes.py`

Tail of stdout (full run is ~75 case lines, all `PASS`/`ok`, including the five new
T-01 cases):

```
PASS case_25a_status_building_is_CLEAN
PASS case_25b_status_Building_capital_B_is_a_VIOLATION_naming_the_three_legal_values
PASS case_25c_status_in_progress_is_a_VIOLATION
PASS case_25d_no_status_at_all_is_CLEAN
PASS case_25e_status_done_and_status_pending_are_both_CLEAN

ALL PASS
```

Exit code: `0`

### Half 2 — `python3 .claude/skills/harness/bin/check-plan-routes.py` (live corpus, unargumented)

```
scanning /Users/molchairuangutai/GitHub/harness/.harness/features/*/{plan.yaml,PLAN.md}
OK T-01 granted to harness-backend-dev, harness-dev-ops
OK T-02: declared main-session-direct (.claude/skills/harness/templates/harness.json ungranted)
OK T-03 granted to harness-backend-dev, harness-dev-ops
DEVIATION T-04 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/test-check-state.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
OK T-05 granted to harness-backend-dev, harness-dev-ops
OK T-06: declared main-session-direct (.claude/skills/harness/SKILL.md ungranted)
0 violation(s) across 1 plan(s)
```

Exit code: `0`

**Note on "across 1 plan(s)":** all 17 other feature directories carry `feature.json`
`status: Done` and are excluded by `_is_shipped` (unrelated pre-existing behaviour, not
touched by this task); only FEAT-18 itself (`status: Building`) is currently unshipped and
gets checked. This matches the intent's expectation that the enum "turns nothing red" on
the live corpus — 0 violations, exit 0.

## Combined run (both halves chained with `&&`, exactly as the plan's `verify:` string)

Also run chained, exit code `0` for the combined pipeline (second half only runs because
the first exited 0).

## TDD cycle

- RED: added `case_25` to `test-check-plan-routes.py` (5 sub-cases) before touching
  `check-plan-routes.py`. Ran the suite — `case_25a` passed vacuously (no check existed yet
  but "building" alone triggers no other finding), `case_25b` failed with
  `AttributeError: module '_cpr_under_test' has no attribute 'LEGAL_TASK_STATUSES'` —
  confirmed RED for the right reason.
- GREEN: added `LEGAL_TASK_STATUSES = ("pending", "building", "done")` beside
  `FINISHED_STATUSES` (production line ~407) and the per-task status check inside
  `process_plan_yaml` (before the `files:`/globs handling). Suite went green.
- Mutant check (P-07): swapped the comparison to `status.lower() not in
  LEGAL_TASK_STATUSES` — `case_25b` correctly reddened
  (`exit 0` instead of nonzero, no `VIOLATION T-01` in stdout). Reverted; post-revert diff
  against the working tree contains only the two intended production hunks (confirmed via
  `git diff`).

## Scope discipline

Only `.claude/skills/harness/bin/check-plan-routes.py` and
`.claude/skills/harness/bin/test-check-plan-routes.py` were written.
`harness_yaml.py`'s `REQUIRED_TASK_FIELDS` was not touched — `status` stays absent from it,
so an absent status remains legal. No commit was made.
