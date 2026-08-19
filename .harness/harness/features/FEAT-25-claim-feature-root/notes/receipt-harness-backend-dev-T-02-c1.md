# Receipt — harness-backend-dev — T-02 — c1

## Task
FEAT-25-claim-feature-root, T-02: give an unreadable plan its own blocker reason naming the path
that was tried.

## Red-first evidence

Command used (before any source edit landed — factory_claim.py was still at T-01's state):

```
cd .claude/skills/harness/bin && python3 test-factory-claim.py 2>&1 | grep -A1 "^FAIL  (B5-ter)"
```

Verbatim output:

```
FAIL  (B5-ter) absent features root: the reason names the absolute path that was tried
        factory: claim: skip #731 — issue #731 carries a feature: label that resolves, but its title yields no matching plan task (edge (i), lost task identity)
FAIL  (B5-ter) absent features root: the reason does not use the edge (i) text
        factory: claim: skip #731 — issue #731 carries a feature: label that resolves, but its title yields no matching plan task (edge (i), lost task identity)
```

Both fired the edge (i) text, carrying no path — exactly the pre-change defect the task exists to
fix. Cases 3 and 4 ("nothing claimed, zero mutating calls, stdout empty" and "plan present, task
id absent: still the edge (i) text") passed pre-change by design: no probe edit was needed, and
none was used, so there is no restore to byte-verify beyond the normal working-tree diff (see
below).

One wrinkle discovered while building the RED fixture: `run_main()` unconditionally overwrites
`claim.FEATURES_ROOT` from the test module's OWN `FEATURES_ROOT` global (its body reads
`claim.FEATURES_ROOT = FEATURES_ROOT`, the module-scope fixture root), so patching
`claim.FEATURES_ROOT` directly before calling `run_main` is silently clobbered. The absent-root
cases patch the test module's own `FEATURES_ROOT` global instead, save/restore around the call.

## New ok-line texts added (verbatim, all four from the plan's enumeration — no extras)

```
(B5-ter) absent features root: the reason names the absolute path that was tried
(B5-ter) absent features root: the reason does not use the edge (i) text
(B5-ter) absent features root: nothing claimed, zero mutating calls, stdout empty
(B5-ter) plan present, task id absent: still the edge (i) text
```

One rename, the only one this feature authorises:

- old: `(X) sc13b fixture: exactly seven skip lines fired (fixture didn't silently short-circuit)`
- new: `(X) sc13b fixture: exactly eight skip lines fired (fixture didn't silently short-circuit)`

## Observed ok-line count

`test-factory-claim.py`: **120** (verify requires `>= 120`).

## `_plan()` is the sole file-reading path

```python
def task(self, feature, task_id):
    """The plan task dict for (feature, task_id), or None when the feature's plan.yaml
    cannot be read, or contains no task with that id."""
    plan = self._plan(feature)
    if plan is None or task_id is None:
        return None
    for t in plan["tasks"]:
        if str(t["id"]) == task_id:
            return t
    return None

def plan_loaded(self, feature):
    """True when feature's plan.yaml was read successfully."""
    return self._plan(feature) is not None
```

Neither calls `harness_yaml.load_plan` nor joins a path directly — both call `self._plan(feature)`,
which alone holds the memo check, `plan_path(feature)`, the `harness_yaml.load_plan` call, and the
single `try/except harness_yaml.YamlParseError`. Verified by the plan's own verify-block probe:
patching `harness_yaml.load_plan` to a call-counting wrapper and calling `task()` then
`plan_loaded()` then `task()` again for the same feature produced exactly one call, in both call
orders (task-first and plan_loaded-first).

## sc13b handling

- Widened the 901..907 set-equality assertion to `range(901, 909)` (exact set equality, not
  weakened to subset/length) to cover the new eighth issue (#908, `feature:FEAT-99-missing`,
  `T-01` title — a `no_plan` case, since the fixture root has no such directory).
- Left the case's name byte-identical: `(X) sc13b fixture: the seven skip lines are for exactly
  issues 901..907` — still says "seven" and "901..907" even though it now covers eight/901..908.
  This is a stale label, raised below as `open_question` per the dispatch's explicit instruction,
  not fixed unilaterally.
- Did NOT rename that case. Only the authorised rename (above) was applied.
- The pairwise-distinctness assertion (`len(set(normalized)) == len(reasons)`) is unchanged and
  count-agnostic — it now runs over 8 reasons instead of 7 with no code change, and still passed
  (`ok    (X) SC-13(b): all seven skip reasons are pairwise distinct after normalising every
  embedded issue number, not just a leading one`). Its own case name also still says "seven" and
  was left alone, per "every other assertion... keeps its text."

## Neighbour-suite regression check (advisor-prompted)

`_blocker_gate`'s first branch changed (plan_loaded decides before task()), and
`test-factory-integration.py` also exercises `factory_claim.py` end-to-end but is outside T-02's
`files:` list, so it cannot be edited here — only checked. Ran it explicitly:

```
CLAUDE_PROJECT_DIR=/Users/molchairuangutai/GitHub/harness python3 test-factory-integration.py
```
```
106/106 checks passed.
```

Count matches T-01's own baseline (106) exactly — no regression, nothing silently absorbed.

## Verify block result

```
T-02 GREEN
```
Exit status: 0.

## Forbidden-set confirmation

- `.claude/skills/harness/bin/factory_config.py` — unedited (`git diff --quiet` clean).
- `.harness/factory/fleet.yaml` — unedited.
- `.harness/harness.json` — unedited.
- `.claude/skills/harness/bin/gh_board.py` — unedited.
- `.claude/skills/harness/bin/check-domain.sh` — unedited.
- `load_board` appears in no line I added (checked via `git diff | grep '^+' | grep -i load_board`
  → no hits).

## Files touched

- `/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/factory_claim.py`
- `/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/test-factory-claim.py`
- `/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-25-claim-feature-root/notes/receipt-harness-backend-dev-T-02-c1.md`

No `git add`, no `git commit`, no branch operations performed. Both source edits remain in the
working tree only.
