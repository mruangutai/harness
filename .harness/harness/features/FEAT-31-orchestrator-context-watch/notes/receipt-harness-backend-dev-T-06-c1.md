# Receipt — harness-backend-dev — T-06 — c1

## What now works

`context-watch.py` accepts `--config PATH` (default: `.harness/harness.json`
resolved from the script's own on-disk location via `_repo_root_from_script()`
walking up four dirs from `.claude/skills/harness/bin/`). It reads
`budgets.orchestrator_context_warn_tokens`; on a missing/unreadable file,
invalid JSON, or an absent/non-numeric key it falls back to
`DEFAULT_CONTEXT_WARN_TOKENS = 200000` and prints one line stating the
default was used and why (`resolve_threshold()`), never raising.

Every measured row now carries a `headroom=` (non-negative) or `overage=`
(negative) figure — threshold minus current — so the operator never
subtracts by hand. A row whose current or peak is at or above threshold
emits a `WARNING` line naming the agent id, current size, threshold, and
the instruction to find the nearest seam; the wording avoids "blocked",
"stopped", "refused", "prevented" (verified by grep in-session). Exit
status is 1 when any row is unmeasured or any row warned, 0 otherwise.

## TDD

RED first: appended CASE D–G to `test-context-watch.py`, ran it against
the pre-change tree — it failed on `argparse: error: unrecognized
arguments: --config` (an unhandled `SystemExit`), confirming the new flag
and behavior did not exist yet. Then implemented in `context-watch.py`.

One implementation note from the RED→GREEN pass: the plan's phrase "delete
the line performing the threshold comparison" (CASE F) is naturally an
`if` header; deleting an `if` header alone breaks Python syntax rather
than producing a clean fail-open mutant. I refactored the comparison into
its own assignment line (`at_or_above_threshold = row["current"] >=
threshold or row["peak"] >= threshold`), preceded by an initializing
`at_or_above_threshold = False`, so CASE F's mutation (deleting exactly
that assignment line) is syntactically valid and fails open to "0
warnings" as the plan requires — the mutant's and real script's warning
COUNTS differ (0 vs 1), never an exit-status-only proof (D-08). Test's
`comparison_line_f` string was updated to match this exact line.

## Verify — three lines, verbatim stdout and exit status, run separately

### Line 1: `python3 .claude/skills/harness/bin/test-context-watch.py`

```
ok    A1: one row discovered
ok    A2: peak equals the corrected per-iteration MAX 747992 exactly
ok    A3: peak does not equal the naive top-level sum 1494870
ok    A-RED anchor: the iterations branch text is present in context-watch.py
ok    A-RED: mutation actually changed the source text
ok    A-RED: with the branch deleted the mutant reports the naive sum 1494870
ok    B1: exactly one row survives the agentType filter
ok    B2: the surviving row is the orchestrator's
ok    C1: row count equals the number of sidecar files found by globbing
ok    C2: exactly 2 rows are unmeasured
ok    C3: the invalid-JSON sidecar's unmeasured row names its own absolute path
ok    C4: the missing-.jsonl sidecar's unmeasured row names its own absolute path
ok    C5: the exit path is non-zero when any row is unmeasured
ok    C-RED: mutation actually changed the source text
ok    C-RED: with unmeasured rows dropped, the mutant's row count is 2, not 4
ok    D1: below-threshold config produces exactly 1 warning line
ok    D2: below-threshold config exits non-zero
ok    D3: above-threshold config produces exactly 0 warning lines
ok    D4: above-threshold config exits zero
ok    E1: a config with the key deleted never raises
ok    E2: the default-used line is present in stdout
ok    E3: the effective threshold applied is the DEFAULT 200000
ok    E4: resolve_threshold names a reason when the key is absent
ok    F-anchor: the threshold-comparison line is present in context-watch.py
ok    F-RED: the mutant copy's text differs from the original
ok    F1: the mutant, run against the below-threshold fixture, warns 0 times
ok    F2: the real script, run against the SAME fixture, warns 1 time
ok    F3: the mutant and real warning counts actually differ (mutation applied)
ok    G1: current=150000 against threshold=200000 carries the figure 50000
29 of 29 cases passed
```
Exit status: `0`

### Line 2: floor check `-ge 19`

```
(no stdout — bare `test` command)
```
Exit status: `0` (29 of 29 cases satisfies `-ge 19`)

### Line 3: `bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit`

Full output is long (60.7KB, many unrelated unit scripts); the line that
matters:

```
PASS test-context-watch.py
```
Exit status of the whole invocation: `0`

## Honesty note on the verify block

None of the three lines is incapable of going red: line 1 is the bare
suite (would print `FAIL` lines and exit 1 on any regression); line 2 is a
numeric floor comparison that reds on any count below 19 (measured
starting floor was 15 before this task; this run adds 14 new `check()`
calls for D–G, landing at 29); line 3 is the full unit-kind runner and
reds if `run-unit-tests.sh` reports anything other than `PASS
test-context-watch.py` for this script. I did not find any of the three
assertions to be structurally incapable of failing.

## Files touched

- `.claude/skills/harness/bin/context-watch.py`
- `.claude/skills/harness/bin/test-context-watch.py`

No other file was written. `.harness/harness.json`, `STATE.md`, and
`plan.yaml` show as modified in `git status` but were not touched by this
task — they are the operator's concurrent tasks in this same worktree.
