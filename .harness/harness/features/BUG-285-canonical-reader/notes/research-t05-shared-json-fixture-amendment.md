# T-05 shared JSON fixture amendment

## BLUF

T-05 now owns the existing shared check-state fixture producer so its strict feature.json reader cutover exercises schema-valid JSON while preserving the established outputs of every existing named check-state test. The controlled task amendment reset plan approval to pending; T-05 remains building.

## Narrowly authorized amendment

- Added `tests/integration/check_state_support.py` once to T-05 `files`, preserving the prior file list.
- Added only this requirement to T-05 `intent`: use the existing shared feature.json fixture producer in `tests/integration/check_state_support.py` and change that producer to emit schema-valid JSON rather than YAML-form content, so the strict `load_feature_json` cutover exercises the real artifact contract. Preserve every existing named check-state test's return code and normalized complete stdout and stderr, or any other established output contract for that test. Do not create duplicated test-local fixture wrappers, and do not change unrelated fixtures.

## Unchanged boundaries

- The live record was re-read immediately before mutation and confirmed as T-05, `status: building`, with the binding verify command exactly as dispatched. That verify command was not executed or changed.
- The narrow `plan-merge.py apply` proposal named only T-05 `files` and `intent`; it omitted task status and every other task, decision, panel, lane, brief, and top-level plan field.
- No formatter, linter, test, build, project-wide check, staging, commit, or production/test-file mutation was performed in this PM amendment.

## Evidence

- The control-plane `plan-merge.py apply` receipt reported `REPLACED T-05.files`, `REPLACED T-05.intent`, `APPROVAL-RESET`, and `APPLIED`. The post-apply plan record shows T-05 still building and approval pending with `reset_reason: apply T-05`.
- The required targeted control-plane `plan-merge.py check` exited 0 and reported `OK T-05 21 anchor(s) resolved`; its final summary was `9 task(s), 146 anchor(s) resolved, 0 failure(s)`.
