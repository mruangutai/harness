# Receipt — harness-dev-ops — T-03 (FEAT-33)

**Result: PASS.** All six primitives implemented in `factory_gh.py`, unit-covered in
`test-factory-gh.py`, integration-covered in `test-factory-integration.py`. Verify green twice
(independent full runs), zero FAIL lines, zero MISCONFIGURED.

## The six primitives (factory_gh.py)

1. `project_resolve(owner, number)` — reads `repositoryOwner(login:){__typename ...
   projectV2(number:){id title}}`, the SAME shape `_project_field_resolve` uses, minus the field
   selection. Returns `None` (never raises) when the owner resolves but the project number does
   not; raises `GhError` for an unresolvable owner or a non-User `__typename`.
2. `project_create(owner, title)` — resolves the owner node id (`user(login:){id}`), then
   `createProjectV2`. Raises naming owner+title when `projectV2` resolves null.
3. `project_link_repository(project_id, repo)` — resolves the repo node id, then
   `linkProjectV2ToRepository`; an "already linked" failure is swallowed and returns `None`
   (mirrors `create_ref`'s measured-conflict shape at line 639); any other failure still raises.
4. `project_single_select_create(project_id, field_name, option_names)` — `createProjectV2Field`
   with every option carrying `name`, `color: GRAY`, `description: ""` explicitly.
5. `project_single_select_extend(project_id, field_id, option_names)` — `updateProjectV2Field`,
   documented as a REPLACEMENT: sends exactly the list it is given, in order; does not compute
   the union (T-04's job).
6. `project_workflows(owner, number)` — `user(login:){projectV2(number:){workflows(first:50){
   nodes{name enabled number}}}}`. Raises (never returns `[]`) when user, projectV2, or workflows
   resolves null.

`_project_field_resolve` and `project_field_options` are unchanged and reused, not duplicated.
Since `gh api graphql`'s `-f`/`-F` flags have no syntax for an array of input objects, the
`singleSelectOptions` list is rendered as a GraphQL literal (`_options_literal`, `json.dumps`-
escaped) embedded in the mutation text — testable on the recorded `query=` argv string, same as
every other primitive here.

## Unit cases (test-factory-gh.py) and how each was red-proved

Every case asserts on argv/GraphQL variables, not only the return value. Fixtures: 244/244 pass.

- **project_resolve**: ok case, absent-project→None (mutated the `return None` to `raise` —
  reddened), owner-absent→raise (asserts `raised`, distinguishing branch), organization→raise
  with no mutation sent, message-distinctness across the three raising branches.
- **project_create**: happy path (two calls, argv order asserted), owner-absent raises before any
  create call, null `projectV2` in response raises naming owner+title.
- **project_link_repository**: happy path, repo-absent raises before linking, already-linked
  swallowed to `None`, and an UNRELATED failure (auth) still raises — proved red-capable by
  mutating the swallow to a blanket `except GhError: return None` (reddened the "unrelated still
  raises" case).
- **project_single_select_create**: returns field id; sends every option **in order** with
  `color: GRAY` and `description: ""` on all six (asserted by count, not just presence); null
  field raises naming the field.
- **project_single_select_extend**: THE PLAN'S NAMED CASE — sends every option including the
  leading existing ones, in order; proved red-capable by mutating the function to
  `option_names[-1:]` (drops leading options) — reddened both the ordering and the
  count-of-6 assertions.
- **project_workflows**: happy path returns the three fields; three separate cases for
  user/projectV2/workflows resolving null, each asserting `raise`, never `[]` — proved
  red-capable by mutating the three raises into `.get(...) or {}` defaulting: all three cases
  reddened.

## Integration cases (test-factory-integration.py), D-12

`factory_gh.py` is a library with no `__main__`, so "forking a real process" means a real
`python3 -c "import factory_gh; ..."` subprocess (cwd=BIN_DIR), with the stub `gh`'s argv surface
extended (new `elif`-style dispatches for `createProjectV2Field`, `updateProjectV2Field`,
`linkProjectV2ToRepository`, `createProjectV2(`, the repo-id query, `workflows(first:`, the
owner-id query, and `project_resolve`'s own query — ordered longest-substring-first so none
shadows another). One forking case per WRITE primitive (D-12: reads don't need one):

- **project_create**: asserts forked exit 0, that the owner-id call and the `createProjectV2(`
  mutation (not `createProjectV2Field`) both occurred, and the title argv value.
- **project_link_repository**: asserts exit 0, repo-id query then `linkProjectV2ToRepository`
  both occurred, owner/name split sent verbatim.
- **project_single_select_create**: asserts exit 0, mutation text carries `createProjectV2Field`
  and exactly six `color: GRAY` / `description: ""` pairs.
- **project_single_select_extend**: asserts exit 0, mutation text carries `updateProjectV2Field`
  (never `createProjectV2Field`), options in the given order.

All four exit-status assertions proved to have teeth: renaming `project_create` (simulating a
broken import/dispatch) reddened all three of its checks including the exit-0 assertion; the same
`option_names[-1:]` mutation used for the unit RED proof also reddened the extend forking case.
116/116 pass in this file.

## Verify

`.claude/skills/harness/bin/run-unit-tests.sh --kind all` — run twice independently (each several
minutes, backgrounded). Both exited 0. `grep -c '^FAIL\b\|MISCONFIGURED'` on both full logs is 0.
Logs: `/tmp/verify-t03.log`, `/tmp/verify-t03-2.log` (scratch, not committed).

## Notes / plan fidelity

- `_STATION_KEYS` widening and the six-key board declaration (T-01/T-02) were already done and
  committed at `7f6e3d9`; every new fixture here was written with all six station keys from the
  start (backlog/plan/ready/building/review/done), per the plan's ordering instruction.
- `_project_field_resolve`'s four-conditions-one-class behaviour is untouched — grepped and
  byte-diffed before/after this task; only new callers were added around it.
- Did not edit `run-unit-tests.sh`, `harness.json`, or add `test-factory-integration.py` to any
  list, per D-12.
- Two pre-existing uncommitted changes were found in the working tree at task start
  (`.claude/skills/harness/templates/harness.json` and this feature's own `plan.yaml`, marking a
  different task `status: done`) — not touched, not authored by this run; noted here only so a
  reviewer does not attribute them to T-03.

## Digest note (issue #778)

Task `change_type: api` — flagging per dispatch instruction in case the digest validator's enum
rejects it; not independently confirmed this run (no digest submission failed), reporting only
that the instruction was received and no reclassification was made.
