# Receipt — harness-backend-dev — T-05 (loop-back, cycle 2) — FEAT-55-issue-types-created-work

## Verdict up front

Same defect, same fix, in `tests/integration/test-gh-backlog-issue-types.py`: its
`calls()` reader used the identical un-stripped-`\x01` idiom as T-03's file. Fixed with
the exact same reader-side change (matching T-07's and T-03's choice), nothing else
touched. `PASS`.

## Repro

Same repro as the T-03 receipt — this file's `FAKE_GH_TYPES` (line 55) is byte-identical
to T-03's: `echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"`. Confirmed the
same disk artifact (`...harness\x01\n`) independently before editing.

## The fix

### Before (`tests/integration/test-gh-backlog-issue-types.py:128-131`)
```python
def calls(tmp, log="calls.log"):
    p = os.path.join(tmp, log)
    return (open(p, encoding="utf-8", errors="replace").read().splitlines()
            if os.path.exists(p) else [])
```

### After (`tests/integration/test-gh-backlog-issue-types.py:128-132`)
```python
def calls(tmp, log="calls.log"):
    p = os.path.join(tmp, log)
    return ([l.rstrip("\x01") for l in
              open(p, encoding="utf-8", errors="replace").read().splitlines()]
            if os.path.exists(p) else [])
```

Identical shape to the T-03 fix (same choice made in both files, as required). No change
to `FAKE_GH_TYPES`'s emit line, no change to `labels_of()`, no change to any assertion.

## Assertions that flipped, and why each is a compatibility-mode control

CASE C's three exact-list label checks — the compatibility-mode path
(`FAKE_TYPES="absent"`, `test-gh-backlog-issue-types.py:204`, before any typed-Issue-Type
logic runs):

- `CASE C: bug item labels are exactly harness, bug` — FAIL -> ok
- `CASE C: chore item labels are exactly harness, chore` — FAIL -> ok
- `CASE C: enhancement item labels are exactly harness` — FAIL -> ok

Each is `labels_of(create_argv) == [...]` under today's label-only path — no `IT_*` value,
no reference to `backlog-issues.json`/typed receipts anywhere in the comparison. Same
list, same order, same `==`, same fixture. Nothing else in CASE C, or in any other case,
flipped.

## Verify — run verbatim from the worktree root, cross-checked against plan.yaml T-05's
own `verify:` block (identical string)

```
$ python3 -c "import ast; ast.parse(open('tests/integration/test-gh-backlog-issue-types.py').read())" || exit 1
$ for c in A B C D E F G H; do grep -qF "CASE $c:" tests/integration/test-gh-backlog-issue-types.py || { echo MISSING; exit 1; }; done
$ for s in IT_bug IT_task IT_feature updateIssue issueTypes backlog-issues.json FAKE_TYPE_APPLY partial nobug github.issue_types; do grep -qF "$s" tests/integration/test-gh-backlog-issue-types.py || { echo MISSING; exit 1; }; done
$ python3 tests/integration/test-gh-backlog-issue-types.py && { echo "UNEXPECTED PASS"; exit 1; }
[30 FAILED — full transcript below]
$ echo "RED as required - all eight cases present"
RED as required - all eight cases present
$ echo $?
0
```

Full per-case transcript (only the three CASE C label checks changed vs. before this fix;
every other FAIL below is the unimplemented T-06 typed backlog behavior, unaffected by
this change):

```
FAIL  CASE A: bug:a defect -> Bug is typed IT_bug
FAIL  CASE A: chore:a chore -> Task is typed IT_task
FAIL  CASE A: enhancement:a wish -> Feature is typed IT_feature
ok    CASE A: three issue create argv reached the fake
FAIL  CASE B: no create argv carries --label bug
FAIL  CASE B: no create argv carries --label chore
ok    CASE B: every create argv carries --label harness
ok    CASE C: three issues created
ok    CASE C: bug item labels are exactly harness, bug
ok    CASE C: chore item labels are exactly harness, chore
ok    CASE C: enhancement item labels are exactly harness
ok    CASE C: zero updateIssue argv reached the fake
FAIL  CASE C: exactly one 'gh-sync: issue types ' line for a three-issue run
ok    CASE C: no backlog-issues.json is written in compatibility mode
FAIL  CASE D: backlog-issues.json exists after a successful run
FAIL  CASE D: 'bug:a defect' recorded with number 41 and typed true
FAIL  CASE D: 'chore:a chore' recorded with number 42 and typed true
FAIL  CASE D: 'enhancement:a wish' recorded with number 43 and typed true
FAIL  CASE D: zero issue create argv on the rerun (everything already recorded)
FAIL  CASE D: exactly one argv containing issueTypes on the zero-create rerun
ok    CASE D: zero 'gh-sync: issue types ' lines on the zero-create rerun
FAIL  CASE E: (7 of 8 checks; only "the rerun makes no issue close argv" and
      "the rerun makes no issue delete argv" ok)
ok    CASE F: the second run makes three MORE issue create argv
ok    CASE F: no backlog-issues.json exists after either run
ok    CASE F: no stdout line names a skipped recorded item
FAIL  CASE F: the second invocation still prints exactly one diagnostic line
FAIL  CASE G: (5 of 9 checks; "zero updateIssue argv reached the fake",
      "zero updateIssue argv carries a node id derived from remnant 601",
      "the seeded remnant is unchanged - number still 601",
      "the seeded remnant is unchanged - typed still exactly false",
      "no entry was recorded for the chore item",
      "no entry was recorded for the enhancement item" ok)
FAIL  CASE H: (2 of 8 checks FAIL: "the run refuses", "the refusal names both Bug
      and github.issue_types", "zero issue create argv reached the fake"; rest ok)

30 FAILED
```

CASE B/D/E/F/G/H's other FAILs (labeling behavior not yet gated by an unimplemented
Issue Types check, and every typed-receipt/refusal assertion) are pre-existing and
untouched by this fix — none of them is a `labels_of(...) ==` exact-list check gated by
the `\x01` artifact; they pin behavior T-06 has not implemented yet (backlog-mode Issue
Type detection/apply/refusal), which correctly stays red pending that task.

## Scope confirmation

```
$ git -C <worktree> status --porcelain -- tests/integration/test-gh-issue-types.py tests/integration/test-gh-backlog-issue-types.py
?? tests/integration/test-gh-backlog-issue-types.py
?? tests/integration/test-gh-issue-types.py
```
Both untracked, no other file touched, nothing staged, nothing committed.

## Open questions

None new.

## expertise_update

`[]` — not a distillation dispatch.
