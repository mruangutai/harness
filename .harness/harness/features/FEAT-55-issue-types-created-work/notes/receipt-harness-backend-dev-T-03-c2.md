# Receipt — harness-backend-dev — T-03 (loop-back, cycle 2) — FEAT-55-issue-types-created-work

## Verdict up front

Confirmed the diagnosed defect independently, then fixed it the way T-07 already did in
`tests/integration/test-factory-issue-types.py`: strip the trailing `\x01` in the reader
(`calls()`), not the fake's emit line. Only that one function changed. `PASS`.

## Repro (confirmed the defect before editing)

```
$ bash -c 'echo "$*" | tr "\n" "\001" >> /tmp/repro.log; echo >> /tmp/repro.log' -- --label harness
$ python3 -c "print(open('/tmp/repro.log','rb').read())"
b'--label harness\x01\n'
```
Matches the diagnosis exactly: `echo "$*"`'s own trailing newline is converted to `\x01`
by `tr` before the second bare `echo` supplies the real line terminator, so every logged
line ends with a `\x01` glued to its last token. `labels_of()`'s
`re.findall(r"--label (\S+)", line)` therefore returns `"harness\x01"`, not `"harness"`,
for the last `--label` on any line — unfixable under any implementation until the
artifact itself is removed.

## The fix

Read `tests/integration/test-factory-issue-types.py`'s `read_log()` (T-07's own fix for
the identical fixture): it keeps the fake's emit untouched and instead strips the
artifact in the reader, one line: `[l.rstrip("\x01") for l in ... .splitlines()]`. Applied
the identical pattern to this file's `calls()` (the equivalent reader) so all three files
that share this fake-gh idiom now agree on one place to fix it.

### Before (`tests/integration/test-gh-issue-types.py:201-204`)
```python
def calls(tmp, log="calls.log"):
    p = os.path.join(tmp, log)
    return (open(p, encoding="utf-8", errors="replace").read().splitlines()
            if os.path.exists(p) else [])
```

### After (`tests/integration/test-gh-issue-types.py:201-205`)
```python
def calls(tmp, log="calls.log"):
    p = os.path.join(tmp, log)
    return ([l.rstrip("\x01") for l in
              open(p, encoding="utf-8", errors="replace").read().splitlines()]
            if os.path.exists(p) else [])
```

No other line in the file touched. `FAKE_GH_TYPES`'s emit (`echo "$*" | tr ...`) is
byte-identical to before — the artifact is produced exactly as it was, only stripped on
read, matching T-07's choice of "smaller and clearer change" (a one-line reader fix vs.
rewriting the bash emit and re-verifying its interaction with three `case` blocks).

## Assertions that flipped, and why each is a compatibility-mode control

All five are CASE C's exact-list label checks — the compatibility-mode path (today's
`--label` behavior, `FAKE_TYPES=absent`), not the unimplemented typed behavior:

- `CASE C: parent labels are exactly harness` — FAIL -> ok
- `CASE C: bugfix labels are exactly harness, bug` — FAIL -> ok
- `CASE C: config labels are exactly harness, chore` — FAIL -> ok
- `CASE C: logic labels are exactly harness` — FAIL -> ok
- `CASE C: feature labels are exactly harness` — FAIL -> ok

Each compares `labels_of(create_argv) == [...]` under `FAKE_TYPES=absent`
(`test-gh-issue-types.py:262-268`, `run(..., {"FAKE_TYPES": "absent"}, ...)`), i.e. the
label set gh-sync emits *today*, before any Issue Type detection/creation logic runs —
none of the five names an `IT_*` typed value or any T-04-only behavior. They were
guaranteed to fail under every implementation before the fix (the `\x01` artifact sits on
every logged line regardless of what gh-sync does), and nothing about what they assert
changed: same list, same order, same comparison operator (`==`), same fixture inputs.

## Verify — run verbatim from the worktree root, cross-checked against plan.yaml T-03's
own `verify:` block (identical string; the dispatched block quoted above matches)

```
$ python3 -c "import ast; ast.parse(open('tests/integration/test-gh-issue-types.py').read())" || exit 1
$ for c in A B C D E F G H H2 I J K; do grep -qF "CASE $c:" tests/integration/test-gh-issue-types.py || { echo MISSING; exit 1; }; done
$ for s in IT_feature IT_bug IT_task IT_defect IT_epic IT_maintenance updateIssue issueTypes 4242 adopted created partial nobug github.issue_types; do grep -qF "$s" tests/integration/test-gh-issue-types.py || { echo MISSING; exit 1; }; done
$ python3 tests/integration/test-gh-issue-types.py && { echo "UNEXPECTED PASS"; exit 1; }
[19 FAILED — full transcript below]
$ echo "RED as required - all twelve cases present"
RED as required - all twelve cases present
$ echo $?
0
```

Full per-case transcript (all previously-Blocker-1 FAILs unchanged, all five Blocker-2
CASE C label checks now `ok`; case counts: 43 ok/24 FAIL before this fix per the T-04
receipt -> 48 ok/19 FAIL now — exactly +5 ok / -5 FAIL, matching the five flipped
assertions and nothing else):

```
FAIL  CASE A: parent is typed IT_feature
FAIL  CASE A: T-01 bugfix is typed IT_bug
FAIL  CASE A: T-02 config is typed IT_task
FAIL  CASE A: T-03 logic is typed IT_task
FAIL  CASE A: T-04 feature is typed IT_task
ok    CASE B: no create argv carries --label bug
ok    CASE B: no create argv carries --label chore
ok    CASE B: every create argv carries --label harness
FAIL  CASE B: the four sub-issue creates still carry --milestone FEAT-77-types
ok    CASE C: five issues created
ok    CASE C: parent labels are exactly harness
ok    CASE C: bugfix labels are exactly harness, bug
ok    CASE C: config labels are exactly harness, chore
ok    CASE C: logic labels are exactly harness
ok    CASE C: feature labels are exactly harness
ok    CASE C: zero updateIssue argv reached the fake
ok    CASE C: exactly one 'gh-sync: issue types ' line for a five-issue run
ok    CASE D: zero issue create argv on the rerun (everything already recorded)
ok    CASE D: still exactly one 'gh-sync: issue types ' line on the rerun
FAIL  CASE E: parent -> Epic / T-01 -> Defect / T-02..T-04 -> Maintenance (x5)
ok    CASE F: (all 7 checks)
FAIL  CASE G: T-01's typed value is 'created' after a failed type-apply
ok    CASE G: T-01's typed value is not True after a failed type-apply
ok    CASE G: the rerun creates no issue for the already-recorded T-01
ok    CASE G: the rerun contains no issue delete argv anywhere
ok    CASE G: the rerun contains no issue close argv anywhere
FAIL  CASE G: the rerun's log carries an updateIssue call for T-01's node id
FAIL  CASE G: T-01's typed value is promoted to True after the backfill
ok    CASE H: no updateIssue argv carries a node id derived from adopted parent 4242
ok    CASE H: no updateIssue argv carries a node id derived from source_issues #100
ok    CASE H: no updateIssue argv carries a node id derived from source_issues #200
FAIL  CASE H: the parent's typed provenance is recorded as 'adopted'
ok    CASE H2: the rerun without --parent still emits zero updateIssue for 4242
FAIL  CASE H2: the parent's typed provenance stays exactly 'adopted' across the rerun
ok    CASE I: (all 5 checks)
ok    CASE J: (8 of 12 checks; 4 FAIL — all Blocker 1, schema refusal)
ok    CASE K: (all 7 checks)

19 FAILED
```

Still RED as required — the remaining 19 FAILs are Blocker 1 (the `feature-schema.json`
`typed`-key refusal, out of this task's scope) and unimplemented T-04 typed-value
assertions; none is a CASE C label check.

## Scope confirmation

```
$ git -C <worktree> status --porcelain -- tests/integration/test-gh-issue-types.py tests/integration/test-gh-backlog-issue-types.py
?? tests/integration/test-gh-backlog-issue-types.py
?? tests/integration/test-gh-issue-types.py
```
Both untracked (as at T-03/T-05 handoff) — no other file touched, nothing staged,
nothing committed.

## Open questions

None new. Blocker 1 (`feature-schema.json`'s `typed` key) from the T-04 receipt remains
open and is out of scope for this dispatch (target list explicitly excludes it).

## expertise_update

`[]` — not a distillation dispatch.
