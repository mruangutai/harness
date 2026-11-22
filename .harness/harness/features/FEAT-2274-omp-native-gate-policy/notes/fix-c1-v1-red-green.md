# Fix c1 — V1 (high, SC-02): a failed config read is not "sync off"

## RED (tests written first, gates unchanged)

`cd W && python3 tests/integration/test-gh-close-gate.py` → exit 1

```
FAIL  duplicate harness.json keys refuse a matching close at exit 2 rather than choosing one
      rc=0 decision=None
FAIL  no harness.json at all: a matching close is refused at exit 2
      rc=0 decision=None
FAIL  config fault (no harness.json): a matching close is refused at exit 2, named
      rc=0 stderr=''
FAIL  config fault (not JSON): a matching close is refused at exit 2, named
      rc=0 stderr=''
FAIL  config fault (a document that is not a mapping): a matching close is refused at exit 2, named
      rc=0 stderr=''
FAIL  config fault (a github block that is a list): a matching close is refused at exit 2, named
      rc=2 stderr='-close-gate.py", line 244, in <module>\n    if not g.get("sync"):\n           ^^^^^\nAttributeError: \'list\' object has no attribute \'get\'\ngh-close-gate: BLOCKED — the gate could not run (AttributeError: \'list\' object has no attribute \'get\'); the command it guards is refused rather than left unchecked.\n'
FAIL  config fault (a github block that is an empty list): a matching close is refused at exit 2, named
      rc=0 stderr=''
FAIL  config fault (a github block that is null): a matching close is refused at exit 2, named
      rc=0 stderr=''
8 FAILED
```

`cd W && python3 tests/integration/test-branch-create-gate.py` → exit 1

```
FAIL  config fault (no harness.json): a matching branch creation is refused at exit 2, named
      | rc=0 stderr=''
FAIL  config fault (not JSON): a matching branch creation is refused at exit 2, named
      | rc=0 stderr=''
FAIL  config fault (a top-level document that is not an object): a matching branch creation is refused at exit 2, named
      | rc=0 stderr=''
FAIL  config fault (duplicate keys): a matching branch creation is refused at exit 2, named
      | rc=0 stderr=''
FAIL  config fault (a github block that is a list): a matching branch creation is refused at exit 2, named
      | rc=0 stderr='Traceback (most recent call last):\n  File "<stdin>", line 6, in <module>\nAttributeError: \'list\' object has no attribute \'get\'\n'
FAIL  config fault (a github block that is an empty list): a matching branch creation is refused at exit 2, named
      | rc=0 stderr=''
FAIL  config fault (a github block that is null): a matching branch creation is refused at exit 2, named
      | rc=0 stderr=''
86/93 cases passed.
```

## GREEN (after the gate change)

```
$ python3 tests/integration/test-gh-close-gate.py   → exit 0
ALL PASSED
(156 ok lines, 0 FAIL)
ok    duplicate harness.json keys refuse a matching close at exit 2 rather than choosing one
ok    no harness.json at all: a matching close is refused at exit 2
ok    config fault (no harness.json): a matching close is refused at exit 2, named
ok    config fault (no harness.json): an unrelated command exits 0 untouched
ok    config fault (not JSON): a matching close is refused at exit 2, named
ok    config fault (not JSON): an unrelated command exits 0 untouched
ok    config fault (a document that is not a mapping): a matching close is refused at exit 2, named
ok    config fault (a document that is not a mapping): an unrelated command exits 0 untouched
ok    config fault (a github block that is a list): a matching close is refused at exit 2, named
ok    config fault (a github block that is a list): an unrelated command exits 0 untouched
ok    config fault (a github block that is an empty list): a matching close is refused at exit 2, named
ok    config fault (a github block that is an empty list): an unrelated command exits 0 untouched
ok    config fault (a github block that is null): a matching close is refused at exit 2, named
ok    config fault (a github block that is null): an unrelated command exits 0 untouched
ok    readable config, github.sync false: a matching close exits 0 untouched
ok    readable config, no github block: a matching close exits 0 untouched

$ python3 tests/integration/test-branch-create-gate.py   → exit 0
93/93 cases passed.
ok    config fault (no harness.json): a matching branch creation is refused at exit 2, named
ok    config fault (no harness.json): an unrelated command exits 0 untouched
ok    config fault (not JSON): a matching branch creation is refused at exit 2, named
ok    config fault (not JSON): an unrelated command exits 0 untouched
ok    config fault (a top-level document that is not an object): a matching branch creation is refused at exit 2, named
ok    config fault (a top-level document that is not an object): an unrelated command exits 0 untouched
ok    config fault (duplicate keys): a matching branch creation is refused at exit 2, named
ok    config fault (duplicate keys): an unrelated command exits 0 untouched
ok    config fault (a github block that is a list): a matching branch creation is refused at exit 2, named
ok    config fault (a github block that is a list): an unrelated command exits 0 untouched
ok    config fault (a github block that is an empty list): a matching branch creation is refused at exit 2, named
ok    config fault (a github block that is an empty list): an unrelated command exits 0 untouched
ok    config fault (a github block that is null): a matching branch creation is refused at exit 2, named
ok    config fault (a github block that is null): an unrelated command exits 0 untouched
ok    readable config, github.sync false: a matching branch creation exits 0 untouched
ok    readable config, github.sync true, repo unpinned: a matching branch creation exits 0 untouched
ok    readable config, no github block: a matching branch creation exits 0 untouched
ok    the gate's config read carries no broad catch

$ python3 tests/integration/test-omp-native-gate-runtime.py   → exit 0
445 passed, 0 failed in 14.0s
```

## The change

Both narrow gates now read `.harness/harness.json` in one step, after applicability has matched
and the root has resolved:

- If the read fails (`ArtifactAccessError`: no file, not JSON or not UTF-8, a top-level document
  that is not a mapping, or duplicate keys), the command is refused through
  `_unrunnable("harness.json could not be read: <accessor error, which names the path>")` at
  exit 2.
- If `github` is present but is not a mapping, the command is refused through
  `_unrunnable("harness.json github block is not a mapping: <type> in <path>")` at exit 2. This
  covers a falsy block like `[]` or `null`, which the old `or {}` turned into sync off.
- Legitimate exemptions are unchanged. A readable config with no `github` key, `sync`
  false/absent, or (branch-create) no `repo` still exits 0 untouched.
- Unrelated commands still exit 0 before any config read; the applicability-first path is
  untouched.

## Migrated assertions (they encoded the contract V1 names as wrong)

- `test-gh-close-gate.py`, the duplicate-keys case. It used to assert only "no deny", and a gate
  that let the close through also met that. A strict reader refusing duplicate keys is a config
  read failure, so the case now asserts `rc == 2` with no structured decision. The intent "do
  not choose one copy" still holds.
- `test-gh-close-gate.py`, "no harness.json at all: the gate exits 0" became "a matching close is
  refused at exit 2". The finding names a missing harness.json at a resolved root as a read
  failure.
- `test-branch-create-gate.py`, `run_feat65_config_reader` (FEAT-65 c1, CR-01) was replaced by
  `run_config_faults`. That case pulled the `_CONFIG_READER` program out of the gate source and
  held it to two things: printing `false -` (sync off) for no file, not JSON, and a non-object
  document; and exiting 1 with an `AttributeError` traceback for a non-mapping github block
  while the gate passed. Both were the silent pass V1 condemns. Each shape is now asserted end
  to end through the live gate: a matching command gets the named refusal at exit 2, and an
  unrelated command exits 0 untouched. The case's "no broad catch" assertion was kept and now
  runs over the gate's AST.
- `_CONFIG_READER` and its `subprocess` re-run were removed. They existed only to show that
  traceback beside a pass, and that has no job once a non-mapping block refuses. The traceback
  was not kept: the type check means no exception is raised, and the named refusal carries the
  diagnosis (block type and path) along with the verdict. Throwing an exception only to print a
  traceback would add noise, not information.
- Inventory consequence, checked: `_CONFIG_READER` was a string, never an inventoried reader.
  `audit_canonical_readers` over a copy of the edited bin reports no finding for either gate.
  The four findings it does report name other files (feature plan paths, `board_lifecycle.py`,
  `check_state/board.py`). `_broad_catch_count` is 0 for both gates.
  `canonical-reader-classification.json` needs no edit. `gh-close-gate`'s `load_harness_json`
  stays at module level and `branch-create-gate`'s stays in `_github_config`, so the inventoried
  ids are unchanged.
