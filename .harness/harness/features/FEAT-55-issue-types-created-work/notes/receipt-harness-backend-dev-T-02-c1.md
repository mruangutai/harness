# Receipt — harness-backend-dev — T-02 — c1

## Task
FEAT-55-issue-types-created-work · T-02 · shared gh_issue_types module.
`verify:` cross-checked against plan.yaml T-02: `python3 tests/unit/test-issue-types.py\n` —
matches the dispatch string verbatim. No mismatch.

## What was created
`.claude/skills/harness/bin/gh_issue_types.py` — the only file created. No other file touched.

Contents, matching the T-02 intent block verbatim: `DEFAULT_TYPE_BY_CHANGE_TYPE` (all twelve
change_types, `"feature": "Task"` per D-18), `DEFAULT_TYPE_BY_NATURE`, `PARENT_KEY`/
`DEFAULT_PARENT_TYPE`, `LEGAL_OVERRIDE_KEYS`, `UnknownWorkNature`, three resolvers
(`type_for_change_type`, `type_for_nature`, `type_for_parent`), `overrides_from_config`,
`CAPABILITY_QUERY`/`capability_query_args`, `classify_capability` (three-state vocabulary:
absent / available / query_failed, errors-array checked before returncode, unparseable stdout
never reads as absent), `node_id_args` (reads `.node_id`, distinct from `gh_issues.py`'s
`.id`), `APPLY_TYPE_MUTATION`/`apply_type_args`, `missing_types`, `refusal_text` (keyed by the
canonical override name, not the change_type/nature string).

## Purity
Module imports only `json` from the stdlib. No `subprocess`, `os.system`, `urllib`, socket,
`open()`, or any other execution/filesystem/network call anywhere in the file — grep-verified
by inspection during authoring; the only top-level import statement is `import json`.

## Verify — exact command, full output

Command run from the worktree root:
```
python3 tests/unit/test-issue-types.py
```

Output (55 `check()` assertions, all `ok`, tail):
```
...
ok    missing_types(['Bug', 'Task'], {'Bug': 'IT_1'}) == ['Task']
ok    missing_types(['Bug'], {'Bug': 'IT_1'}) == []
ok    refusal_text: contains the type name 'Maintenance'
ok    refusal_text: contains 'github.issue_types.Task'
ok    refusal_text: contains the repo 'owner/name'

ALL PASSED
```
Exit code: 0. (Full 55-line output reproduced in full in the tool transcript; every line before
the tail above also read `ok`, none `FAIL`.)

## Proof tests/unit/test-issue-types.py was not modified
```
$ git status --porcelain -- tests/unit/test-issue-types.py
?? tests/unit/test-issue-types.py
```
Same status as T-01 left it (still untracked, never staged, never written by this task). This
task made zero writes to that path — the only `write`/`edit` call issued was to
`gh_issue_types.py`.

## Scope discipline
Did not touch `gh-sync.py`, `factory_gh.py`, `factory_decompose.py`, `harness.json`,
`DECISIONS.md`/`DECISIONS-INDEX.md`, or `github-mirror.md`. Did not prune `infra`/`ci` from any
`CHORE_TYPES` set — both remain mapped to `"Task"` in `DEFAULT_TYPE_BY_CHANGE_TYPE` per intent.
Nothing staged, nothing committed. No project-wide suite run — only the task's own `verify:`.

## Design note (not a decision, informational)
`missing_types` returns a `sorted(set(...))` — dedup and sort both satisfy the intent's "sorted,
de-duplicated list" wording and the two asserted cases (`['Task']` and `[]`), which are each
single-element or empty so sort/dedup ordering was not independently distinguished by the test;
implementation follows the intent prose directly.
