# Receipt — harness-dev-ops — T-16 — c1

## BLUF

`cmd_open`'s task-issue title now carries the feature id, matching the parent title's
convention. GREEN. `run-unit-tests.sh --kind all` exits 0 with `test-gh-sync.py` passing
(185 ok / 0 fail).

## The change

`gh-sync.py:764` (title builder inside `cmd_open`'s per-task loop, located by its f-string
per the task's ORDERING note — line numbers had drifted from T-07/T-08/T-13):

```
- "--title", f"{task['id']} — {task['title']}", "--body", body,
+ "--title", f"{brief['feat']} — {task['id']} — {task['title']}", "--body", body,
```

Written title format: `f"{brief['feat']} — {task['id']} — {task['title']}"` — same em dash
separator (`—`, U+2014) the parent title already uses at `:746`, full feature id (no short
`FEAT-NN` form), no colon/brackets, no truncation logic.

## Argv assertion (test-gh-sync.py, added under the existing `--- the real open` block)

```python
t01_argv = [l for l in task_create_lines if "T-01" in l]
check("T-01 issue create carries the exact title "
      "\"FEAT-05-export-fix — T-01 — streaming export rebuild\" (T-16)",
      len(t01_argv) == 1
      and "--title FEAT-05-export-fix — T-01 — streaming export rebuild" in t01_argv[0],
      str(t01_argv))
```
This asserts the exact argv substring sent to `gh issue create`, not a count or exit code.
The pre-existing "parent title carries the H1 phrase" check (unchanged, still asserting
`"FEAT-05-export-fix — reliable csv export"`) proves the parent-title site at `:746` is
untouched.

## Idempotence

`cmd_open`'s existing `if task["id"] in rec["issues"]:` skip (unchanged) means a re-run over
an already-recorded task issues no `gh issue create` call at all — no title is written,
rewritten, or touched. The suite's existing "re-run open creates nothing" check (asserts no
new `issue create` call appears in the second run's log) already covers this — I did not add
a duplicate assertion since it would test the identical code path with no new discriminator.
**This matches the plan's own IDEMPOTENCE section verbatim**: "`open` is re-run safe and
skips a task whose issue id is already recorded ... this change never re-titles an existing
issue." The plan and the code agree — no wrong-recommendation flag here.

## RED proof

Reverted `gh-sync.py` to the pre-T-16 baseline (`7d3c539`, the tip of `T-01..T-13,T-21`) via
`git show 7d3c539:.claude/skills/harness/bin/gh-sync.py > gh-sync.py` (no stash), leaving the
new test assertion in `test-gh-sync.py` in place. Ran the full `test-gh-sync.py`:

```
184 ok, 1 FAIL:
FAIL  T-01 issue create carries the exact title "FEAT-05-export-fix — T-01 — streaming export rebuild" (T-16)
      ['issue create --repo implentio/fake --title T-01 — streaming export rebuild --body ... --milestone FEAT-05-export-fix --label harness']
```
Exactly the one new assertion reddened, naming the actual (undecorated) title sent — the
defect the task describes. Restored `gh-sync.py` from a `cp` taken before the revert;
`diff -q` against the pre-revert copy reported no difference (byte-identical). Re-ran green:
185 ok, 0 FAIL, `ALL PASSED`.

## Verify — `.claude/skills/harness/bin/run-unit-tests.sh --kind all`

Ran to completion, exit code 0. `test-gh-sync.py` line in the aggregate log: `PASS
test-gh-sync.py`. No `FAIL` lines anywhere in the 2748-line output except literal test-name
strings containing the word "FAIL" as their subject (e.g. `ok    FAIL over an escalating
member is rejected`) — none are actual suite failures.

## Files touched (scope-respected)

- `.claude/skills/harness/bin/gh-sync.py` (1-line change at the title f-string, `:764`)
- `.claude/skills/harness/bin/test-gh-sync.py` (9-line addition, one new check)

Siblings' files (`board_lifecycle.py`, `test-board-lifecycle.py`, `test-factory-integration.py`,
`SKILL.md`, `harness-plan.md`, `plan.yaml`) show unrelated concurrent modifications from T-15
and the main session — untouched by this task, per `git status --porcelain` at the end of the
run.

## Issue #778 — digest enum rejection

`plan.yaml` T-16 is `change_type: logic`. `validate-digest.py:158` restricts dev-ops's
`change_type` enum to `{config, scaffolding, infra, ci}` — `logic` is rejected. This is the
same #778 class already flagged five times on this feature (six-for-six now). Substituting
`ci` in the DIGEST below as the closest available value — the work is a build-script/CI-tool
change, not config or scaffolding, and infra is a worse fit than ci. Flagging rather than
silently picking.
