# Receipt — harness-dev-ops — T-25

**Task**: T-25, deregister the claims test from `.harness/harness.json`'s integration `detect`.
**File touched**: `.harness/harness.json` (line 119 only — the `integration.detect` string).

## Change

Removed the trailing segment `|.claude/skills/harness/bin/test-check-decision-claims.py`
(pipe + path) from the end of `test_kinds.integration.detect`. Nothing else in the file changed.
The field remains a single pipe-separated string, order of the surviving 29 entries preserved.

## Acceptance evidence

**1. `verify:` block, run verbatim from worktree root — exit 0**

```
$ cd "$(git rev-parse --show-toplevel)"
$ python3 - <<'PY'
... (verbatim script from plan.yaml T-25)
PY
detect entries: 29

$ bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
check-kinds: the script arrays and test_kinds.integration.detect agree.
EXIT_CODE=0
```

**2. One-line diff, before/after `detect` value**

```
$ git diff --numstat -- .harness/harness.json
1	1	.harness/harness.json
```

Before (tail of the string): `...|.claude/skills/harness/bin/test-check-decision-anchors.py|.claude/skills/harness/bin/test-check-decision-claims.py",`
After (tail of the string): `...|.claude/skills/harness/bin/test-check-decision-anchors.py",`

(Full before/after lines are each ~2500 chars — see `git diff -- .harness/harness.json`,
`artifact://1625` for the raw unified diff; only the single trailing segment differs.)

**3. Contract 2, both halves, with output**

```
$ python3 -c "
import json
d = json.load(open('.harness/harness.json'))
seg = d['test_kinds']['integration']['detect'].split('|')
print('anchors present:', '.claude/skills/harness/bin/test-check-decision-anchors.py' in seg)
print('claims present:', '.claude/skills/harness/bin/test-check-decision-claims.py' in seg)
"
anchors present: True
claims present: False
```

**4. JSON parses; no empty `detect` segment (unfiltered split, separate from verify's filtered comprehension)**

```
json.load: OK
unfiltered segment count: 29
empty segments (indices): []
```

No stray `||` was introduced — the adjacent separator was removed along with the path.

**5. No other key changed**

```
$ git diff --numstat -- .harness/harness.json
1	1	.harness/harness.json
```

One file, one line changed (1 insertion, 1 deletion — the JSON pretty-printer emits the whole
`detect` value on one physical line, so the diff tool reports it as a single line replaced).
`git diff -- .harness/harness.json` (full hunk, `@@ -116,7 +116,7 @@`) confirms only that one
line inside the `integration` block differs; `exclude`, `cmd`, `status`, and every other kind
(`component`, `ui`, `eval`, `typecheck`) and every other top-level key (`gates`, `github`,
`budgets`, `dirty_tree_whitelist`, …) are untouched.

## Ordering precondition (T-24)

T-24 landed at `8c879f5` per dispatch; `--check-kinds` above confirms `INTEGRATION_SCRIPTS` and
this `detect` string agree post-edit, which is the direct evidence the precondition held.
