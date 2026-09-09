# Receipt — harness-backend-dev — T-01 (declare github.build_entry in feature-schema.json)

## BLUF
T-01 done: `github.build_entry` is now declared in `feature-schema.json`'s `properties.github.properties`
mapping — a closed string enum of the four legal values (`opened`, `recovery-required`,
`not-applicable`, `recovered-terminal`), optional (no `required` change), with a description stating
all five states including ABSENT, verbatim from the intent. `github` keeps `additionalProperties: false`
and no `required` list. Nothing else in the file changed. Test-first order was followed: four new
cases were written, run, and observed RED before the schema edit; then GREEN after.

## Failing-first evidence (exact output, before schema edit)
```
FAIL accepted_github_build_entry_opened ["sample.json: undeclared key 'build_entry' at /github. This file holds execution state only. ..."]
FAIL accepted_github_build_entry_recovery-required ["sample.json: undeclared key 'build_entry' at /github. ..."]
FAIL accepted_github_build_entry_not-applicable ["sample.json: undeclared key 'build_entry' at /github. ..."]
FAIL accepted_github_build_entry_recovered-terminal ["sample.json: undeclared key 'build_entry' at /github. ..."]
FAIL rejected_github_build_entry_illegal_value_'opened ' ["sample.json: undeclared key 'build_entry' at /github. ..."]
FAIL rejected_github_build_entry_illegal_value_'reopened' ["sample.json: undeclared key 'build_entry' at /github. ..."]

6 FAILURE(S): ['accepted_github_build_entry_opened', 'accepted_github_build_entry_recovery-required',
'accepted_github_build_entry_not-applicable', 'accepted_github_build_entry_recovered-terminal',
"rejected_github_build_entry_illegal_value_'opened '", "rejected_github_build_entry_illegal_value_'reopened'"]
```
The remaining two new cases (`rejected_github_build_entry_hyphen_misspelling`,
`accepted_github_block_without_build_entry`) passed even pre-edit, correctly — both assert behavior
that already held before `build_entry` existed (an undeclared sibling key is refused; the key's own
absence validates clean), so they carry no new-schema dependency and are not vacuous: they still
exercise real assertions against the post-edit schema on the GREEN run.

## GREEN — verify command (verbatim from plan.yaml, run from worktree root)
```
python3 tests/integration/test-validate-feature-json.py && python3 -c "import json;s=json.load(open('.claude/skills/harness/bin/feature-schema.json'));e=s['properties']['github']['properties']['build_entry']['enum'];assert sorted(e)==['not-applicable','opened','recovered-terminal','recovery-required'],e;print('VERIFY-PASS')"
```
Final lines:
```
     (red proof counts: original 1, mutant 0)

ALL PASS
VERIFY-PASS
```
Runner's own reported case count: 77 named `PASS` lines printed by the script (73 pre-existing +
4 new: `accepted_github_build_entry_each_legal_value` prints one PASS per of its 4 loop values,
`rejected_github_build_entry_illegal_value` prints one PASS per of its 2 loop values,
`rejected_github_build_entry_hyphen_misspelling` and `accepted_github_block_without_build_entry`
one PASS each — 4+2+1+1 = 8 new PASS lines over the 4 new case functions), zero `FAIL` lines,
exit 0, then `VERIFY-PASS` from the second command. `sys.exit(0)` in `main()` is reached only
because `failures` is empty.

## Files touched (exactly T-01's two)
- `.claude/skills/harness/bin/feature-schema.json` — added `build_entry` inside
  `properties.github.properties`, nothing else changed (confirmed: `github` still
  `additionalProperties: false`, still no `required` list; JSON re-parses clean).
- `tests/integration/test-validate-feature-json.py` — added 4 new case functions plus a
  `main()` registration block, following the file's existing case style (loop-over-legal-values,
  loop-over-illegal-values with a `named` message check, single hyphen-misspelling case mirroring
  `case_rejected_undeclared_github_sub_key`, single absence case mirroring
  `case_accepted_github_block_without_source_issues`).

## Observed, not mine
`git status --porcelain` also shows `.harness/harness/features/BUG-1309-mirror-build-entry/feature.json`
and `.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml` as modified. I never opened
either file with a write/edit call; these are outside T-01's `files:` list and are concurrent
orchestrator/panel activity, reported per convention rather than reverted.

## Open questions
None.
