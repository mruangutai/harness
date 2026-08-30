# Receipt — harness-backend-dev — T-24 — 2026-08-29-01

## BLUF
T-24 landed atomically: array entry removed, both retired claims-checker files `git rm`'d, both
retained anchor files untouched (hash-verified against `99bb52c`). Full `verify:` block, run
verbatim from the worktree root, exits 0. `must_fix: []`.

## 1. verify: block — exit status
Ran verbatim (worktree root confirmed as
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge`
via `git rev-parse --show-toplevel` inside the block). Output tail:
```
ok - test_in_range_anchor_reports_nothing_and_exits_zero
ok - test_missing_file_is_reported_and_exits_one
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_malformed_anchor_extension_reports_line_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
ok - test_live_authority_anchors_all_resolve
EXIT_STATUS=0
```
**exit 0.**

## 2. git status --porcelain
```
D  .claude/skills/harness/bin/check-decision-claims.py
 M .claude/skills/harness/bin/run-unit-tests.sh
D  .claude/skills/harness/bin/test-check-decision-claims.py
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml
?? .harness/logs/2026-08-29.md
```
The two `M`/`D`/`D` entries for `run-unit-tests.sh` and the two deleted files are mine, as
required. The `plan.yaml` modification (T-27's DECISIONS.md task status flipped `pending`→`done`)
and the untracked `.harness/logs/2026-08-29.md` are NOT mine — I never opened either path; they are
concurrent sibling/tooling activity in the shared worktree, out of my `files:` scope, left
untouched. This receipt file and the observations-log entry are the only other paths I write, both
allowed.

## 3. numstat on run-unit-tests.sh
```
1	1	.claude/skills/harness/bin/run-unit-tests.sh
```
1 insertion + 1 deletion (whole-array-line replace, since the array is one physical line). Removed
line ended in:
```
-...  "test-check-decision-anchors.py" "test-check-decision-claims.py")
```
New line ends in:
```
+...  "test-check-decision-anchors.py")
```
Only the trailing `"test-check-decision-claims.py"` array element was removed; every other element,
`UNIT_SCRIPTS`, the kind dispatch, and both detectors are byte-identical.

## 4. Anchor-file hash check against 99bb52c
```
adb9a648cfd167e30c66b34e40e4efd0dfb89ed9958ac21f62a84282299ccb77  check-decision-anchors.py (working tree)
adb9a648cfd167e30c66b34e40e4efd0dfb89ed9958ac21f62a84282299ccb77  check-decision-anchors.py (git show 99bb52c)
7a4e0ba1afcb20b4b2dad6bad297441535fe3ca96284ebad7ded941b363674fa  test-check-decision-anchors.py (working tree)
7a4e0ba1afcb20b4b2dad6bad297441535fe3ca96284ebad7ded941b363674fa  test-check-decision-anchors.py (git show 99bb52c)
```
Both retained files match `99bb52c` exactly — untouched.

## 5. Retained registration
`run-unit-tests.sh:31` `INTEGRATION_SCRIPTS` array still ends `... "test-check-decision-anchors.py")`
— `test-check-decision-anchors.py` remains registered; `test-check-decision-claims.py` is gone from
the array.

## Sweep clause
The `git grep -l check-decision-claims` step (excluding the four pathspecs, `.harness/harness.json`
included per the structural exclusion) returned nothing and did not trip `references survive` —
consistent with the plan's account that the only remaining live reference at this point in the
dependency order is `.harness/harness.json`, owned by T-25. No sixth reference site found.

## must_fix
`[]`
