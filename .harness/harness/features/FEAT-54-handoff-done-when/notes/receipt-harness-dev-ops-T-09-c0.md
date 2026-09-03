# Receipt — harness-dev-ops — T-09 c0

T-09 passes its approved scoped verify. The probe is executable, stdlib-only, dry-run safe under the supplied audit hook, and registered only as `locally_run`.

## Test-first record

Before implementation, the exact scoped verify exited 2 at its first command because `tests/manual/probe-handoff-comprehension.py` did not exist:

```text
/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/tests/manual/probe-handoff-comprehension.py': [Errno 2] No such file or directory
```

## Approved verify

The task id (`T-09`) and command below were cross-checked against `plan.yaml:622-655`; the dispatch copy is verbatim.

```sh
cd "$CLAUDE_PROJECT_DIR" && python3 tests/manual/probe-handoff-comprehension.py --dry-run && python3 -c "
import runpy, sys
P='tests/manual/probe-handoff-comprehension.py'
BLOCKED=('socket.connect','socket.getaddrinfo','subprocess.Popen','os.system','urllib.Request')
def hook(event, args):
    if event in BLOCKED: raise SystemExit('probe made a %s call during --dry-run' % event)
sys.addaudithook(hook)
sys.argv=[P,'--dry-run']
try:
    runpy.run_path(P, run_name='__main__')
except SystemExit as e:
    if e.code not in (0, None): raise
print('ok: dry run made no model call')" && python3 -c "
import json
d=json.load(open('.harness/harness.json'))
k=d['test_kinds']['handoff_comprehension']
p='tests/manual/probe-handoff-comprehension.py'
assert k['status']=='locally_run' and k['detect']==p and k['cmd']==p, k
assert k['exclude']=='.claude/worktrees/**', k
assert 'handoff_comprehension' not in json.dumps(d.get('test_matrix')), 'kind leaked into test_matrix'
print('ok')" && bash .claude/skills/harness/bin/run-unit-tests.sh --check-layout
```

Exit: `0`

Exact output:

```text
handoff comprehension probe: DRY RUN
model: anthropic/claude-sonnet-5
arms: as-written, done-when-stripped
questions:
- What is the one immediate next action?
- What exact scope must be completed?
- Which authorities define when that action is complete?
- What evidence would show that every authority is satisfied?
notes:
- /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md
planned model calls: 2 (not executed)
handoff comprehension probe: DRY RUN
model: anthropic/claude-sonnet-5
arms: as-written, done-when-stripped
questions:
- What is the one immediate next action?
- What exact scope must be completed?
- Which authorities define when that action is complete?
- What evidence would show that every authority is satisfied?
notes:
- /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md
planned model calls: 2 (not executed)
ok: dry run made no model call
ok
```

`run-unit-tests.sh --check-layout` emitted no text; its successful exit completed the command chain.

## Baseline preservation

Before and after T-09, the byte slice from the `_handoff_done_when_baseline_note` key through the byte immediately before `_test_matrix_note` was identical:

```text
bytes 13095
sha256 180ac0daad21acb197f14191f3f204f8c5672f7e57a0ea5f2247f5281d82f0df
```

This slice includes `_handoff_done_when_baseline_note`, `handoff_done_when_baseline`, their values, key order, whitespace, and trailing delimiter.

## Files touched by this task

- `tests/manual/probe-handoff-comprehension.py`
- `.harness/harness.json`
- `.harness/harness/features/FEAT-54-handoff-done-when/notes/receipt-harness-dev-ops-T-09-c0.md`

The worktree also showed `plan.yaml` modified by orchestration; T-09 did not edit it.
