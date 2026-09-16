# Receipt — harness-backend-dev — T-05 — c1

## Task

T-05: Write the failing integration test for gh-sync backlog — receipt, typing and one
diagnostic. `change_type: scaffolding`. Only file created:
`tests/integration/test-gh-backlog-issue-types.py`.

Dispatch `verify:` cross-checked against plan.yaml's own T-05 `verify:` string — identical,
no mismatch.

## What the test does

Eight cases (A–H), one `check()` per assertion, labelled `CASE <letter>:` in a docstring or
`check()` name string so the file-global grep loop finds all eight. Fixture reuses the same
fake-`gh` shape as `tests/integration/test-gh-issue-types.py` (issueTypes capability query
keyed on `FAKE_TYPES` — absent/available/partial/nobug, `--jq .node_id`, `updateIssue`
honouring `FAKE_TYPE_APPLY`), scoped down to what `cmd_backlog` actually reads (no
BRIEF.md/plan.yaml/feature.json — `cmd_backlog` touches none of those today).

Command under test: `gh-sync.py backlog <featdir> "bug:a defect" "chore:a chore"
"enhancement:a wish"`.

- CASE A/B: `FAKE_TYPES=available` — three `issue create`, per-issue `updateIssue` with the
  right type id (IT_bug/IT_task/IT_feature), label suppression for bug/chore, `--label
  harness` on every create.
- CASE C: `FAKE_TYPES=absent` — today's labels unchanged, zero `updateIssue`, exactly one
  `^gh-sync: issue types ` line, no `backlog-issues.json` at all (compat mode has no
  net-new receipt).
- CASE D: receipt after a successful run (number + `typed: true` per item); rerun creates
  nothing, queries `issueTypes` exactly once (the lazily-called-detector trap), prints zero
  diagnostic lines.
- CASE E: `FAKE_TYPE_APPLY=fail` records `typed` **exactly** `false` per item (asserted via
  `entry is not None and entry.get("typed") is False`, so a missing entry fails this case,
  not just a falsy read); a later successful rerun backfills every recorded number with no
  create/close/delete.
- CASE F: compat mode run twice — three MORE creates each time, never any
  `backlog-issues.json`, one diagnostic line on the second run too.
- CASE G: `FAKE_TYPES=partial` (Task undeclared) with a pre-seeded remnant
  (`"bug:a defect"` → `{number: 601, typed: false}`) so the backfill set is non-empty;
  refusal must precede any create/apply, remnant left byte-identical.
- CASE H: `FAKE_TYPES=nobug` — both items this run would CREATE (chore→Task,
  enhancement→Feature) have declared types, so only the pre-seeded remnant's backfill need
  for the undeclared Bug can refuse (remnant `"bug:a defect"` → `{number: 602, typed:
  false}`). Discriminates against an implementation that narrows `missing_types` to the
  about-to-be-created set only.

`backlog-issues.json`'s schema is invented here (a dict keyed by the full item string,
`{"number": int, "typed": bool}`) since T-06 has not landed; T-06's job is to make this
schema real.

## RED evidence

Ran `python3 tests/integration/test-gh-backlog-issue-types.py` directly against today's
unchanged `gh-sync.py` (`cmd_backlog` untouched): 33 FAILED, exit 1. Every failure is the
absence of typed behaviour, not a fixture crash:

- CASE A/B: `updates=[]` — no `updateIssue` calls at all (detection never runs); labels
  still carry `--label bug`/`--label chore` (suppression never runs).
- CASE C: today's diagnostic printed instead is `gh-sync: no github.board configured —
  station writes are not attempted` (board note, unrelated) — zero `^gh-sync: issue types `
  lines, so the `len(lines) == 1` check correctly reads 0. `backlog-issues.json` absence
  check passes (ok) — today already writes nothing there, which is exactly what compat mode
  requires, so this row is legitimately green pre-T-06.
- CASE D: no receipt file exists at all (`rec is not None` fails), rerun still creates 3
  fresh issues (dedup never runs) and the `issueTypes` query count on the rerun is 0, not 1
  (detection never runs at all today).
- CASE E: receipt entries are all `{}` — `entry.get("typed")` reads `None`, correctly
  distinct from `False`, so the "not absent" case fails for the right reason (nothing is
  recorded, let alone `false`).
- CASE F: legitimately green today (`ok` for both create-count and no-receipt) since compat
  mode is meant to be byte-identical — only the diagnostic-line assertion fails, because
  today prints the board note instead of an `issue types` line.
- CASE G/H: `r.returncode == 0` (no refusal exists yet) and the refusal text is absent, so
  both fail correctly; the zero-create/zero-updateIssue/remnant-untouched assertions read
  `ok` today only because `cmd_backlog` happens to run to completion and create three fresh
  issues without ever touching the pre-seeded remnant — not because a refusal fired. Full
  per-case FAIL/ok lines are in the verify output below (identical run).

Full `ast.parse` + case-marker + required-string + RED-run verify, exact command from the
plan and the dispatch (matched, no divergence):

```
$ python3 -c "import ast; ast.parse(open('tests/integration/test-gh-backlog-issue-types.py').read())" || exit 1
for c in A B C D E F G H; do
  grep -qF "CASE $c:" tests/integration/test-gh-backlog-issue-types.py || { echo "MISSING case $c ..."; exit 1; }
done
for s in IT_bug IT_task IT_feature updateIssue issueTypes backlog-issues.json FAKE_TYPE_APPLY partial nobug github.issue_types; do
  grep -qF "$s" tests/integration/test-gh-backlog-issue-types.py || { echo "MISSING required assertion string: $s"; exit 1; }
done
python3 tests/integration/test-gh-backlog-issue-types.py && { echo "UNEXPECTED PASS: this test must be RED before T-06"; exit 1; }
echo "RED as required - all eight cases present"

FAIL  CASE A: bug:a defect -> Bug is typed IT_bug
      updates=[]
FAIL  CASE A: chore:a chore -> Task is typed IT_task
      updates=[]
FAIL  CASE A: enhancement:a wish -> Feature is typed IT_feature
      updates=[]
ok    CASE A: three issue create argv reached the fake
FAIL  CASE B: no create argv carries --label bug
FAIL  CASE B: no create argv carries --label chore
ok    CASE B: every create argv carries --label harness
ok    CASE C: three issues created
FAIL  CASE C: bug item labels are exactly harness, bug
FAIL  CASE C: chore item labels are exactly harness, chore
FAIL  CASE C: enhancement item labels are exactly harness
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
FAIL  CASE E: 'bug:a defect' has a receipt entry after a failed type-apply
FAIL  CASE E: 'bug:a defect''s typed value is exactly false (not absent)
FAIL  CASE E: 'chore:a chore' has a receipt entry after a failed type-apply
FAIL  CASE E: 'chore:a chore''s typed value is exactly false (not absent)
FAIL  CASE E: 'enhancement:a wish' has a receipt entry after a failed type-apply
FAIL  CASE E: 'enhancement:a wish''s typed value is exactly false (not absent)
FAIL  CASE E: the rerun makes no issue create argv
ok    CASE E: the rerun makes no issue close argv
ok    CASE E: the rerun makes no issue delete argv
FAIL  CASE E: the rerun updateIssue's the recorded node id for number None
FAIL  CASE E: 'bug:a defect''s typed value is promoted to True after the backfill
FAIL  CASE E: 'chore:a chore''s typed value is promoted to True after the backfill
FAIL  CASE E: 'enhancement:a wish''s typed value is promoted to True after the backfill
ok    CASE F: the second run makes three MORE issue create argv
ok    CASE F: no backlog-issues.json exists after either run
ok    CASE F: no stdout line names a skipped recorded item
FAIL  CASE F: the second invocation still prints exactly one diagnostic line
FAIL  CASE G: the run refuses (non-zero exit)
FAIL  CASE G: zero issue create argv reached the fake
ok    CASE G: zero updateIssue argv reached the fake
ok    CASE G: zero updateIssue argv carries a node id derived from remnant 601
FAIL  CASE G: the refusal names both Task and github.issue_types
ok    CASE G: the seeded remnant is unchanged - number still 601
ok    CASE G: the seeded remnant is unchanged - typed still exactly false
ok    CASE G: no entry was recorded for the chore item
ok    CASE G: no entry was recorded for the enhancement item
FAIL  CASE H: the run refuses (non-zero exit) though nothing to be CREATED needs Bug
FAIL  CASE H: the refusal names both Bug and github.issue_types
FAIL  CASE H: zero issue create argv reached the fake
ok    CASE H: zero updateIssue argv reached the fake
ok    CASE H: zero updateIssue argv carries a node id derived from remnant 602
ok    CASE H: the seeded remnant is unchanged - number still 602
ok    CASE H: the seeded remnant is unchanged - typed still exactly false
ok    CASE H: no entry was recorded for the chore item
ok    CASE H: no entry was recorded for the enhancement item

33 FAILED
RED as required - all eight cases present
```

Verify block exited 0, printed the success line.

## Scope confirmation

`git -C <worktree> status --porcelain -- .claude/skills/harness/bin/gh-sync.py
tests/integration/test-gh-sync.py tests/integration/test-gh-issue-types.py
tests/integration/test-gh-backlog-issue-types.py`:

```
?? tests/integration/test-gh-backlog-issue-types.py
?? tests/integration/test-gh-issue-types.py
```

`gh-sync.py` and `tests/integration/test-gh-sync.py` show no entry (clean, unmodified).
`test-gh-issue-types.py` is `??` (untracked) because T-03 created it and nothing has staged
it yet — it is unchanged by this task. Nothing staged, nothing committed by this task.

## Notes for T-06

- `backlog-issues.json` schema this test pins: `{"<item-string>": {"number": <int>,
  "typed": <bool>}}` at `<featdir>/backlog-issues.json`, written only when at least one type
  was detected/attempted (never in compat/absent mode — CASE C/F).
- `missing_types` must be computed over the WHOLE item set including already-recorded
  remnants, before any create or apply (CASE G/H).
- The capability query must run exactly once per invocation even when zero issues are
  created (CASE D's rerun) — no lazily-called detector.
- Diagnostic line `^gh-sync: issue types ` prints exactly once when at least one issue is
  created and something was detected/attempted; zero times on a zero-create, all-typed
  rerun (CASE D) or a zero-create refusal path is not applicable here since CASE G/H both
  refuse with a non-zero exit before any diagnostic would print (not separately asserted,
  no conflict).
