# Receipt — harness-backend-dev — T-05 — c2 (fix cycle: gate test red-green)

## Task
T-05: Delete branch-create-gate.sh's dormant board-flip block and its four config keys.
Cycle 2 — a genuine red-green unit test, `.claude/skills/harness/bin/test-branch-create-gate.py`,
added in addition to (not instead of) T-05's signed `verify:`.

## Step 0 — preserve and probe, before restoring

```
$ git status --porcelain -- .claude/skills/harness/bin/branch-create-gate.sh
 M .claude/skills/harness/bin/branch-create-gate.sh
```

c1's post-deletion file was already saved to the scratchpad
(`branch-create-gate.c1.sh`) before restoring.

## Step 1 — restore, then prove it worked

```
$ git checkout -- .claude/skills/harness/bin/branch-create-gate.sh
$ grep -cE 'project_number|project_id|status_field|in_progress_option|item-edit' .claude/skills/harness/bin/branch-create-gate.sh
7
```

The four keys and the `item-edit` call are present (count 7) — the restore worked, proceeding
to step 2 on a genuinely pre-deletion file.

## Step 2 — write the test, watch it fail against the restored file

Wrote `.claude/skills/harness/bin/test-branch-create-gate.py`. Minimum coverage, five
independent assertions per the dispatch: (1) absence of the four keys + `item-edit`, (2) deny
for a nonexistent flow, (3) allow for `feat/FEAT-18-board-truth` (live on disk), (4) self-gating
on `github.sync`/`github.repo` — absent github block, `sync: false`, and `sync: true` with repo
unpinned (`"-"` sentinel), each asserted to exit 0 with empty stdout, using a fresh
`CLAUDE_PROJECT_DIR` fixture (its own synthesized `harness.json`) rather than the live repo, and
(5) both branch-name forms — flow-id and issue-number, the latter with `GH_BIN` pointed at a
nonexistent path so the "`'gh' is not installed`" deny proves the issue-number extraction ran
without touching gh or the network.

Verbatim run against the RESTORED (pre-deletion) file:

```
$ python3 .claude/skills/harness/bin/test-branch-create-gate.py
FAIL  the four config keys and the item-edit call are absent from the script
      | found: ['project_number', 'project_id', 'status_field', 'in_progress_option', 'item-edit']
ok    DENY: a branch naming a flow that does not exist on disk
ok    ALLOW: a branch naming a flow that DOES exist on disk
ok    self-gate: no github block at all -> exit 0, no stdout
ok    self-gate: github.sync false -> exit 0, no stdout
ok    self-gate: github.sync true, repo unpinned ("-" sentinel) -> exit 0, no stdout
ok    form 1 (flow id) parses: deny names the exact flow id extracted
ok    form 2 (issue number) parses: 'gh' not installed deny names issue #123

7/8 cases passed.
```
(exit code 1)

**Discriminator confirmed**: only the absence assertion (1) failed red. The deny case, the allow
case, both self-gating cases and both branch-name parse cases all PASSED against the restored
file — the deleted block was dormant, not broken, exactly as the discriminator in the dispatch
requires.

An intermediate attempt at assertion 3 (using a suffixed branch name
`feat/FEAT-18-board-truth-more-work`) initially failed because the gate's flow-id regex
(`[a-z0-9-]*`, greedy) captures the whole slug after `FEAT-NN`, so a suffixed name extracts a
flow id the `ls` glob under `.harness/features/` cannot find — fixed by using the exact live
directory name `feat/FEAT-18-board-truth`, which then passed (recorded here since it happened
before the RED capture above, which is post-fix on that assertion and pre-fix on nothing else).

## Step 3 — re-apply the deletion exactly, diff, re-run green

Re-applied the edit by hand per T-05's `intent:` (not a file copy): deleted the board-flip block
and the `gh api graphql` / `gh project item-edit` calls, removed `PROJ_NUM`/`PROJ_ID`/`FIELD_ID`/
`OPT_ID` from the `read -r` line and the python heredoc's print statement, and replaced the
header bullet. First pass used my own wording for the header bullet, which differed from c1's;
per the operator's reconciliation rule the diff below drove reconciling to c1's exact wording.

```
$ diff <scratchpad>/branch-create-gate.c1.sh .claude/skills/harness/bin/branch-create-gate.sh
15,18c15,18
< #   - Station moves live in gh-sync.py (FEAT-18) — this gate deliberately never
< #     pins any board config keys again: it only ever moved one card, at branch
< #     time, with no way to move it back, and the derived parent station covers
< #     that case. It is in git history if the derivation ever misses something.
---
> #   - Station moves live in gh-sync.py (FEAT-18); this gate deliberately never pins
> #     board config keys again — it only ever moved one card, at branch time, with
> #     no way to move it back, and the derived parent station covers that case. It
> #     is in git history if needed.
diff exit: 1
```

After reconciling the header bullet to c1's exact text:

```
$ diff <scratchpad>/branch-create-gate.c1.sh .claude/skills/harness/bin/branch-create-gate.sh
diff exit: 0
```

Empty diff — the re-applied edit is byte-identical to c1's post-deletion file, which already
passed T-05's signed verify and a lead review.

Re-ran the new test suite, GREEN:

```
$ python3 .claude/skills/harness/bin/test-branch-create-gate.py
ok    the four config keys and the item-edit call are absent from the script
ok    DENY: a branch naming a flow that does not exist on disk
ok    ALLOW: a branch naming a flow that DOES exist on disk
ok    self-gate: no github block at all -> exit 0, no stdout
ok    self-gate: github.sync false -> exit 0, no stdout
ok    self-gate: github.sync true, repo unpinned ("-" sentinel) -> exit 0, no stdout
ok    form 1 (flow id) parses: deny names the exact flow id extracted
ok    form 2 (issue number) parses: 'gh' not installed deny names issue #123

8/8 cases passed.
```
(exit code 0)

## T-05's signed `verify:` — re-run after the re-applied deletion

```
$ ! grep -qE 'project_number|project_id|status_field|in_progress_option|item-edit' .claude/skills/harness/bin/branch-create-gate.sh && python3 -c "import json;print(json.dumps({'tool_input':{'command':'git check'+'out -b feat/FEAT-99-nope'}}))" | CLAUDE_PROJECT_DIR="$PWD" bash .claude/skills/harness/bin/branch-create-gate.sh | grep -q '"permissionDecision": "deny"'
$ echo "verify exit: $?"
verify exit: 0
```

`task_verify: pass`.

## Note on `run-unit-tests.sh`

Not touched — registering `test-branch-create-gate.py` there is a declared `main-session-direct`
step per the dispatch. The new test was run directly with `python3
.claude/skills/harness/bin/test-branch-create-gate.py`, not through the runner. Running
`run-unit-tests.sh` in this state would report `MISCONFIGURED: ... test-branch-create-gate.py is
not in run-unit-tests.sh's explicit script list` — expected, transient, not a finding.

## Files touched
- `.claude/skills/harness/bin/branch-create-gate.sh` (re-applied deletion, byte-identical to c1)
- `.claude/skills/harness/bin/test-branch-create-gate.py` (new)
