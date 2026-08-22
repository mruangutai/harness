# Receipt — harness-backend-dev — T-02 (run c1)

## Verify — plan cross-check

Dispatch's quoted `verify:` matched the plan's own T-02 `verify:` block byte-for-byte
(`.harness/harness/features/FEAT-31-orchestrator-context-watch/plan.yaml`, loaded via
`harness_yaml.load_file` and grepped for `T-02`, not read whole). No mismatch, so no BLOCKED.

## Verify — command-by-command result, each reported individually

```
$ python3 .claude/skills/harness/bin/test-context-watch.py
... 15 "ok" lines ...
15 of 15 cases passed
LINE1_EXIT=0
```
Final line names the count as the plan's comment requires: "15 of 15 cases passed".

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
LINE2_EXIT=1
```
The raw exit of line 2 is **1**, not 0 — but that is `test-harness-yaml-corpus.py` failing on a
**pre-existing, unrelated** fixture: `.harness/harness/features/FEAT-31-orchestrator-context-watch
/notes/recovered-draft-14task-does-not-parse.yaml`, committed at `ae89da4` (title says it does not
parse) — nothing under my `files:` (confirmed via `git log -1` on that path, and `git diff
--stat HEAD` shows the only files I created are `context-watch.py`'s test and `run-unit-tests.sh`'s
one-line append; `context-watch.py` itself is T-01's, untouched by me). The plan's own comments for
line 2 name two conditions, not "exit 0" — matching how T-01's receipt separated a pipe's exit from
the script's own exit for the same reason. Both are independently asserted below, not inferred from
the raw exit:

```
$ test "$(bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit 2>&1 | grep -c MISCONFIGURED)" = "0"
TRAP1_EXIT=0   # NO line containing MISCONFIGURED — satisfied
$ test "$(bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit 2>&1 | grep -cx 'PASS test-context-watch.py')" = "1"
TRAP2_EXIT=0   # the line "PASS test-context-watch.py" appears exactly once — satisfied
```

`echo "$CLAUDE_PROJECT_DIR"` printed empty. `run-unit-tests.sh:3`'s `cd
"${CLAUDE_PROJECT_DIR:-$(pwd)}"` therefore fell back to `$(pwd)`, which was this worktree
(`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-31`) — confirmed, not assumed, by
Trap 2's result: `grep -cx` found the PASS line exactly once, which is only possible if the suite
ran against the worktree copy where `test-context-watch.py` exists. The suite did NOT silently run
against the main checkout.

**`task_verify: pass`** — both of the plan's named expectations for line 2 hold; the unrelated
`test-harness-yaml-corpus.py` failure predates this task and is outside T-02's `files:`.

## Open question — not mine to fix, flagging for the orchestrator/dev-ops

`test-harness-yaml-corpus.py` fails the WHOLE `--kind unit` (and therefore `--kind all`) run because
it scans `.harness` for every `*.yaml`/`*.yml` and finds
`notes/recovered-draft-14task-does-not-parse.yaml`, a deliberately-invalid file committed as
recovery evidence at `ae89da4`. This means `run-unit-tests.sh --kind unit`'s current overall exit is
`1` for reasons that have nothing to do with T-02, T-01, T-03, or T-11 — any CI step gating on that
exit alone will report red today, feature-wide, independent of this task. Not touching it: it is
outside my two `files:` and outside my domain to judge whether the corpus scanner should exclude
`notes/`, or whether the recovered draft should move/be renamed out of the `.yaml` glob.

## What was built

- `.claude/skills/harness/bin/test-context-watch.py` (create) — loads `context-watch.py` via
  `importlib.util.spec_from_file_location` (D-01), honouring `CONTEXT_WATCH_BIN` for the path under
  test. Three case groups, all fixtures literal under `tempfile.mkdtemp()`, cleaned in `finally`:
  - **Group A** (D-11, the corrected arithmetic): one entry whose top-level sum (1494870) and
    per-iteration MAX (747992) are deliberately made to differ. Asserts the reported peak is
    747992 exactly and is not 1494870. RED PROOF: a mutant with the exact three-statement
    `iterations`-resolution branch removed (located by verbatim text, not line number, per the
    dispatch's warning that T-06 moves these lines) — asserted to differ from the original, then
    asserted to report the naive 1494870 when loaded and run against the same fixture.
  - **Group B** (the agentType filter): three sidecars (`harness-orchestrator`, `harness-qa`,
    `general-purpose`), asserts row count 1 and that the surviving row is the orchestrator's.
  - **Group C** (the unmeasured branch, REQ-07): four sidecars — complete, no-toolUseId (still
    measured), invalid-JSON meta, missing `.jsonl`. Asserts the row count equals a **glob computed
    in the test** (never hard-coded), exactly 2 unmeasured, each unmeasured row naming the absolute
    offending path, and a non-zero exit path via `cw.main(["--projects-dir", ...])`. RED PROOF: a
    regex mutation (`return _unmeasured_row(...)` → `return None`, located by symbol name) that
    fail-opens by dropping both unmeasured rows instead of surfacing them — asserted to differ from
    the original, then asserted to shrink the row **count** from 4 to 2 (a count, not an exit
    status, per D-08).
- `.claude/skills/harness/bin/run-unit-tests.sh` (append) — added `"test-context-watch.py"` to
  `UNIT_SCRIPTS` (one element; `context-watch.py` and its test never fork a subprocess, so unit is
  correct per the file header's own split rule and DEC-197).

`tests_added: 15`, `suite: pass` (all 15 assertions in my own file are green; the only red result
anywhere in the run is the pre-existing, unrelated `test-harness-yaml-corpus.py` finding above).

## Files touched

- `.claude/skills/harness/bin/test-context-watch.py` (created)
- `.claude/skills/harness/bin/run-unit-tests.sh` (one-element array append)
