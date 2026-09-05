# Receipt — harness-backend-dev — FEAT-55 T-06 (cycle 1)

## What changed

`.claude/skills/harness/bin/gh-sync.py` only:

- `cmd_backlog(feat_dir, repo, items, issue_types=None)` — new trailing `issue_types` param.
  `detect_issue_types(repo)` is the first statement, unconditional, once per invocation.
  All items are parsed/validated (`_parse_backlog_items`) before any create. When state is
  not `"available"`: behaves byte-for-byte as before (no receipt read/written, no item ever
  skipped) — creates every item via `_backlog_create`.
- When state is `"available"`: refuses before any create/apply
  (`_refuse_undeclared_backlog_types` + `_required_backlog_issue_types`, computed over the
  WHOLE item list including already-recorded remnants whose `typed` is not `True`) with the
  same `gh_issue_types.missing_types`/`refusal_text` vocabulary T-04 established. Labels are
  `["harness"]` only. Every item runs create-or-skip
  (`_backlog_create_or_skip`, reading `<featdir>/backlog-issues.json` fresh each time — an
  item already recorded by number is never re-created and GitHub is never read back), THEN
  every item runs a separate apply-if-not-typed pass (`_backlog_apply_type`) — a two-phase
  split, not interleaved per item.
- New receipt `<featdir>/backlog-issues.json`, flat `{"<nature>:<title>": {"number": int,
  "typed": bool}}` — written ONLY through `harness_merge.locked_update` directly
  (`_save_backlog_entry`), never `open(path, "w")`/`json.dump`, never a second lock/rename
  primitive. Read only through `_load_backlog_receipt` (absent/empty/non-mapping -> `{}`).
- `main()`'s `backlog` dispatch now passes `issue_types` through:
  `cmd_backlog(feat_dir, repo, argv[2:], issue_types)`.

## Why two-phase (create-all, then apply-all) rather than interleaved per item

The literal prose in T-06's `intent` section 5 reads as one per-item loop doing
create-then-apply. That is incompatible with CASE E of the red test: `FAKE_TYPE_APPLY=fail`
makes every `updateIssue` call fail, and `gh()` turns ANY non-zero `gh` exit into
`skip()` -> `sys.exit(0)` — a whole-process exit. An interleaved per-item loop would create
item 1, attempt its apply, and exit the process there, so items 2 and 3 would never be
created — but CASE E asserts all three items get a receipt entry with `typed` exactly
`False` after that one run. Only a two-phase split (mirroring `cmd_open`'s own
`_open_sync_task` loop followed by the separate `_backfill_issue_types` pass) creates every
item first and only then attempts to apply types, so a mid-apply abort still leaves every
item's create-time entry on disk. Verified directly: CASE E passes with this shape.

The receipt's shape is also a deliberate divergence from the intent prose's
`{"items": {...}}` nesting: the red test (`read_receipt`/`seed_receipt` in
`test-gh-backlog-issue-types.py`) reads and writes the item keys at the TOP LEVEL of the
JSON document, not nested under an `"items"` key, and that file is the one I was told to
make green without editing. Implemented to match the test.

## Verify — run verbatim from the worktree root

Cross-checked against `plan.yaml`'s own T-06 `verify:` string first — identical to the
dispatch's quoted string, no mismatch.

### 1. `python3 tests/integration/test-gh-backlog-issue-types.py` — exit 0

All eight named cases (A B C D E F G H) pass, one line per assertion:

```
ok    CASE A: bug:a defect -> Bug is typed IT_bug
ok    CASE A: chore:a chore -> Task is typed IT_task
ok    CASE A: enhancement:a wish -> Feature is typed IT_feature
ok    CASE A: three issue create argv reached the fake
ok    CASE B: no create argv carries --label bug
ok    CASE B: no create argv carries --label chore
ok    CASE B: every create argv carries --label harness
ok    CASE C: three issues created
ok    CASE C: bug item labels are exactly harness, bug
ok    CASE C: chore item labels are exactly harness, chore
ok    CASE C: enhancement item labels are exactly harness
ok    CASE C: zero updateIssue argv reached the fake
ok    CASE C: exactly one 'gh-sync: issue types ' line for a three-issue run
ok    CASE C: no backlog-issues.json is written in compatibility mode
ok    CASE D: backlog-issues.json exists after a successful run
ok    CASE D: 'bug:a defect' recorded with number 41 and typed true
ok    CASE D: 'chore:a chore' recorded with number 42 and typed true
ok    CASE D: 'enhancement:a wish' recorded with number 43 and typed true
ok    CASE D: zero issue create argv on the rerun (everything already recorded)
ok    CASE D: exactly one argv containing issueTypes on the zero-create rerun
ok    CASE D: zero 'gh-sync: issue types ' lines on the zero-create rerun
ok    CASE E: 'bug:a defect' has a receipt entry after a failed type-apply
ok    CASE E: 'bug:a defect''s typed value is exactly false (not absent)
ok    CASE E: 'chore:a chore' has a receipt entry after a failed type-apply
ok    CASE E: 'chore:a chore''s typed value is exactly false (not absent)
ok    CASE E: 'enhancement:a wish' has a receipt entry after a failed type-apply
ok    CASE E: 'enhancement:a wish''s typed value is exactly false (not absent)
ok    CASE E: the rerun makes no issue create argv
ok    CASE E: the rerun makes no issue close argv
ok    CASE E: the rerun makes no issue delete argv
ok    CASE E: the rerun updateIssue's the recorded node id for number 41
ok    CASE E: the rerun updateIssue's the recorded node id for number 42
ok    CASE E: the rerun updateIssue's the recorded node id for number 43
ok    CASE E: 'bug:a defect''s typed value is promoted to True after the backfill
ok    CASE E: 'chore:a chore''s typed value is promoted to True after the backfill
ok    CASE E: 'enhancement:a wish''s typed value is promoted to True after the backfill
ok    CASE F: the second run makes three MORE issue create argv
ok    CASE F: no backlog-issues.json exists after either run
ok    CASE F: no stdout line names a skipped recorded item
ok    CASE F: the second invocation still prints exactly one diagnostic line
ok    CASE G: the run refuses (non-zero exit)
ok    CASE G: zero issue create argv reached the fake
ok    CASE G: zero updateIssue argv reached the fake
ok    CASE G: zero updateIssue argv carries a node id derived from remnant 601
ok    CASE G: the refusal names both Task and github.issue_types
ok    CASE G: the seeded remnant is unchanged - number still 601
ok    CASE G: the seeded remnant is unchanged - typed still exactly false
ok    CASE G: no entry was recorded for the chore item
ok    CASE G: no entry was recorded for the enhancement item
ok    CASE H: the run refuses (non-zero exit) though nothing to be CREATED needs Bug
ok    CASE H: the refusal names both Bug and github.issue_types
ok    CASE H: zero issue create argv reached the fake
ok    CASE H: zero updateIssue argv reached the fake
ok    CASE H: zero updateIssue argv carries a node id derived from remnant 602
ok    CASE H: the seeded remnant is unchanged - number still 602
ok    CASE H: the seeded remnant is unchanged - typed still exactly false
ok    CASE H: no entry was recorded for the chore item
ok    CASE H: no entry was recorded for the enhancement item

ALL PASSED
```
Exit code: 0.

### 2. `python3 tests/integration/test-gh-issue-types.py` — FAILS UNAIDED, as forecast

19 checks FAIL, all tracing to one cause: T-04's `cmd_open` writes `github.typed` into
`feature.json`, and `feature-schema.json`'s `github` object still declares
`"additionalProperties": false` with no `typed` property (defect 1, already with the
operator; I did not touch this file, was told not to, and did not need to for T-06's own
file). Every failure is `feature_json_write.write_feature_json` raising
`harness_merge.MergeRefusal(11)`: `undeclared key 'typed' at /github`. This is cmd_open's
own path (T-04's code), not anything T-06 changed.

To prove T-06 did not regress this file's OWN eight cases (which are a strict subset —
`test-gh-issue-types.py`'s cases are lettered independently and cover cmd_open, not
cmd_backlog) and that the wiring T-06 added (`issue_types` threaded through `main()`) does
not break cmd_open, I ran the identical command with `TMPDIR` pointed at a throwaway
directory holding a schema copy that additionally declares `github.typed` — a copy made
with Python's `json` module, at `/tmp/t06-schema-override/.claude/skills/harness/bin/
feature-schema.json`, never written into this repo, removed after the run
(`schema_path_for`'s own documented checkout walk-up is what makes a `TMPDIR`-rooted
override visible to `tempfile.TemporaryDirectory()`'s nested feature.json path):

```
TMPDIR=/tmp/t06-schema-override python3 tests/integration/test-gh-issue-types.py
```

Result: **ALL PASSED, exit 0** — all cases A through K, all 66 checks, including CASE J
(the legacy-origin-key path) and CASE G/H/H2 (the parent/task backfill and adoption
paths). This confirms `main()`'s new `cmd_backlog(..., issue_types)` call-site edit did not
touch or regress `cmd_open`'s own code path.

**Which of the three verify commands passed unaided, which only under the override:**
- `test-gh-backlog-issue-types.py` — PASSED UNAIDED (no override needed).
- `test-gh-issue-types.py` — FAILED unaided (schema defect 1, pre-existing, not T-06's);
  PASSED under the throwaway schema override.
- `test-gh-sync.py` — PASSED UNAIDED (see below), no override needed.

### 3. `python3 tests/integration/test-gh-sync.py` — PASSED UNAIDED, exit 0

Full suite green, every named case, unaided (no override). Output tail:
`ALL PASSED` followed by the T-10/BUG-1114/F-01 station-commit block, also all green.
Full transcript is long (this test file is this repo's largest gh-sync suite); ran to
completion with exit code 0 and zero `FAIL` lines.

## Scoped git status (worktree root)

```
$ git status --porcelain -- .claude/skills/harness/bin/gh-sync.py \
    tests/integration/test-gh-backlog-issue-types.py \
    tests/integration/test-gh-issue-types.py tests/integration/test-gh-sync.py
 M .claude/skills/harness/bin/gh-sync.py
?? tests/integration/test-gh-backlog-issue-types.py
?? tests/integration/test-gh-issue-types.py
```

`gh-sync.py` is the only file I modified. The two `??` test files are untracked because an
earlier task (T-02/T-06 predecessors) added them to the working tree without committing —
I did not create, touch, or open them for write. `test-gh-sync.py` shows no line at all:
clean, unmodified. Nothing staged; nothing committed.

## Acceptance checklist

- [x] All 8 cases (A–H) pass in `test-gh-backlog-issue-types.py`, per-case transcript above.
- [x] `test-gh-sync.py` passes unaided (control: no regression to the rest of gh-sync.py).
- [x] `test-gh-issue-types.py` fails unaided for the pre-existing, already-reported schema
      defect (not caused by this task); passes in full under a throwaway, no-repo-file
      schema override, proving T-06's wiring change doesn't regress cmd_open.
- [x] Only `.claude/skills/harness/bin/gh-sync.py` modified.
- [x] Neither red test file, nor `test-gh-sync.py`, nor `feature-schema.json`, nor
      `gh_issue_types.py` edited.
- [x] Nothing committed, nothing staged.
