# Receipt — harness-dev-ops — T-18

## Task

Append `.claude/skills/harness/bin/test-context-watch-hook.py` to the pipe-separated
`test_kinds.integration.detect` string in `.harness/harness.json`. Nothing else touched.

## Edit

`.harness/harness.json` line 119, `test_kinds.integration.detect`:

```diff
-...test-run-unit-tests-kinds.py",
+...test-run-unit-tests-kinds.py|.claude/skills/harness/bin/test-context-watch-hook.py",
```

Verified via `git diff -- .harness/harness.json`: exactly one line changed, one new pipe-segment
appended at the end, every prior entry and the leading `tests/integration/**` glob preserved
byte-for-byte. `test_kinds.unit.detect`, all `cmd`, `exclude`, `budgets`, `gates`, `test_matrix`
untouched (confirmed no other hunks in the diff).

## Verify — before edit

Command (verbatim, matches plan.yaml T-18 `verify:` byte-for-byte, cross-checked against
lines 1495-1515):

```
python3 -c "
import json, re
d = json.load(open('.harness/harness.json'))
ig = [g.strip() for g in d['test_kinds']['integration']['detect'].split('|')]
assert '.claude/skills/harness/bin/test-context-watch-hook.py' in ig, ig
base = set(g.rsplit('/', 1)[-1] for g in ig)
src = open('.claude/skills/harness/bin/run-unit-tests.sh').read()
ints = re.findall(r'\"([^\"]+)\"', re.search(r'INTEGRATION_SCRIPTS=\((.*?)\)\n', src, re.S).group(1))
units = re.findall(r'\"([^\"]+)\"', re.search(r'UNIT_SCRIPTS=\((.*?)\)\n', src, re.S).group(1))
miss = [n for n in ints if n not in base]
wrong = [n for n in units if n in base]
print('integration array', len(ints), 'absent from detect', len(miss), miss)
print('unit array', len(units), 'wrongly in detect', len(wrong), wrong)
raise SystemExit(0 if not miss and not wrong else 1)
"
```

Stdout (verbatim):

```
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    assert '.claude/skills/harness/bin/test-context-watch-hook.py' in ig, ig
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ['tests/integration/**', '.claude/skills/harness/bin/test-check-state.py', '.claude/skills/harness/bin/test-factory-integration.py', '.claude/skills/harness/bin/test-gh-sync.py', '.claude/skills/harness/bin/test-check-plan-routes.py', '.claude/skills/harness/bin/test-feature-worktree.py', '.claude/skills/harness/bin/test-expertise-merge.py', '.claude/skills/harness/bin/test-validate-digest.py', '.claude/skills/harness/bin/test-check-expertise.py', '.claude/skills/harness/bin/test-gen-decisions-index.py', '.claude/skills/harness/bin/test-bash-write-guard.py', '.claude/skills/harness/bin/test-check-domain.py', '.claude/skills/harness/bin/test-harness-yaml.py', '.claude/skills/harness/bin/test-upgrade-config.py', '.claude/skills/harness/bin/test-merge-settings.py', '.claude/skills/harness/bin/test-context-watch-cli.py', '.claude/skills/harness/bin/test-run-unit-tests-kinds.py']
```

Exit status: **1** (uncaught AssertionError). Confirms nobody had already made this edit.

## Verify — after edit

Same command, re-run after the edit.

Stdout (verbatim):

```
integration array 14 absent from detect 0 []
unit array 19 wrongly in detect 0 []
```

Exit status: **0**.

Note: `miss` is `[]` because at this moment `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` array does
not yet list `test-context-watch-hook.py` — T-17 (which registers it there) had not landed in this
checkout at the time this task ran. The task's own required assertion (line 1, `assert ... in ig`)
is what flips from failing to passing; the set-balance re-check simply had nothing to unbalance yet.
This is exactly the "safe to run first" case the plan's intent block describes.

## Concurrency note

`git status --porcelain` at completion also shows `M` on
`.harness/harness/features/FEAT-31-orchestrator-context-watch/STATE.md` and
`.../plan.yaml` — both are the operator's live edits from concurrently-running tasks in this
same worktree, not touched by this task. Only `.harness/harness.json` was written here.

## Ordering hazard (not mine to encode)

Per the plan's own text: this task must land before T-12's KIND-DRIFT cross-check runs, and
ideally alongside T-17. Recording it here per the plan's instruction, since T-12's `depends_on`
edges were not to be altered this round.
