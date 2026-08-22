# Receipt — harness-backend-dev — T-16 — c1

## What now works

`context-watch.py` gains a library seam, `warn_for_agent(projects_root,
session_id, agent_id, cwd, config_path=None)`, that answers "is THIS agent
over the threshold, and what should the warning say" for one agent. It
locates `<projects_root>/<slug of cwd>/<session_id>/subagents/agent-<agent_id>.jsonl`
via `slug_of_path` (T-01's function, reused unmodified), finds `current`
via a new tail-read helper `_last_measured_usage()` that reads the file
from the END in chunks and stops at the first (from-the-end) line that
parses AND carries `message.usage` — never scanning the whole file to
compute `peak`, and never treating an unmeasured line as a zero — then
runs `current` through `entry_context_size()` (T-01's arithmetic, D-11,
reused unmodified) and compares it against `resolve_threshold(config_path)`
(T-06's function, reused unmodified, same `DEFAULT_CONTEXT_WARN_TOKENS =
200000`). Returns `None` below threshold, or advisory warning text at or
above it, naming the agent's current figure, the threshold, and DEC-159's
seam rule with the concrete next artifact
(`notes/handoff-<stem>.md`, four required sections). The whole function is
wrapped in `try/except Exception: return None` — it never raises, and it
writes nothing.

`--warn-for AGENT_ID --session-id ID [--cwd PATH] [--projects-dir PATH]
[--config PATH]` exposes this as a CLI mode: prints the text and exits 2
when `warn_for_agent` returns text, prints nothing and exits 0 when it
returns `None`. It returns before any of the existing table/threshold-print
code runs, so the no-argument, one-argument, blind-spot-footer and
threshold-warning behaviours from T-01/T-06 are byte-for-byte unchanged —
verified by every pre-existing case (A through G) still passing unmodified.

Nothing in `.claude/settings.json` was touched, and this task registers
nothing (D-24): `warn_for_agent` has no knowledge of a PostToolUse payload,
stderr, or an exit code — those belong to T-17's separate hook file.

## TDD

RED first: I initially wrote the full implementation before any test
existed — caught myself, reverted `context-watch.py` to the exact T-06
baseline (confirmed via `wc -l` = 407 lines matching the pre-task state),
and restarted in the correct order. Appended cases H, I, J and the
absent-transcript/absent-config assertions (grouped as "K" for numbering
clarity) to `test-context-watch.py` FIRST, ran the suite, and watched it
crash with `AttributeError: module 'context_watch_under_test' has no
attribute 'warn_for_agent'` after all 29 pre-existing cases passed — RED,
confirmed on the actual unbuilt surface. Then implemented `warn_for_agent`,
`_last_measured_usage`, and the `--warn-for` CLI mode; reran to GREEN (55
of 55).

One implementation note on CASE J: the mutation target is a two-line
comparison pattern reused from T-06's CASE F (`at_or_above_threshold =
False` then overwritten by the real comparison on the next line), so that
deleting exactly the second line is syntactically valid Python and
produces a genuine fail-open mutant (the warning silently never fires)
rather than a `NameError` crash — the same reasoning T-06's receipt
recorded for its own CASE F.

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
ok    H1: warn_for_agent returns non-None text when current is at or above threshold
ok    H2: the text carries the agent's current figure
ok    H3: the text carries the threshold figure
ok    H4: the text contains the substring handoff
ok    H5: the text contains none of blocked/stopped/refused/prevented
ok    H6: --warn-for exits 2 when the function returns text
ok    H7: --warn-for stdout is non-empty when it exits 2
ok    H8: --warn-for stdout carries the current figure
ok    H9: --warn-for stdout carries the threshold figure
ok    H10: --warn-for stdout carries the substring handoff
ok    H11: --warn-for stdout contains none of blocked/stopped/refused/prevented
ok    I1: warn_for_agent returns None when current is below threshold
ok    I2: --warn-for exits 0 when the function returns None
ok    I3: --warn-for stdout is EMPTY when it exits 0
ok    J-anchor: the threshold-comparison line is present in context-watch.py
ok    J-RED: the mutant copy's text differs from the original
ok    J1: the mutant's text differs from the original's text on the SAME crossing fixture
ok    J2: real warning count is 1 on the crossing fixture
ok    J3: mutant warning count is 0 on the SAME crossing fixture (fail-open silenced)
ok    K1: an absent transcript returns None rather than raising
ok    K2: --warn-for on an absent transcript exits 0
ok    K3: --warn-for on an absent transcript prints nothing
ok    K4: an absent config returns text (not None) rather than raising, because the DEFAULT 200000 is still below this fixture's current
ok    K5: --warn-for on an absent config exits 2 (falls back to DEFAULT, still crosses)
ok    K6: an absent config, with current below the DEFAULT, returns None rather than raising
ok    K7: --warn-for on an absent config, below the DEFAULT, exits 0 and prints nothing
55 of 55 cases passed
```
Exit status: `0`

### Line 2: floor check `-ge 22`

```
(no stdout — bare `test` command)
```
Exit status: `0` (55 of 55 satisfies `-ge 22` — see the honesty section below
for why this line is vacuous for this task's work, exactly as flagged in
the dispatch).

### Line 3: `bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit`

Full output is long (1041 lines, many unrelated unit scripts); the lines
that matter:

```
PASS test-context-watch.py
```

No line anywhere in the output contains `MISCONFIGURED` (checked with
`grep -n MISCONFIGURED`, zero matches). The hazard the dispatch warned
about — the operator's concurrent T-17 creating
`test-context-watch-hook.py` before it is registered — did NOT manifest in
this run; I am reporting that absence rather than assuming it, since
`run-unit-tests.sh` reflects on-disk state at the moment this line ran.

Exit status of the whole invocation: `0`

## Count of cases: before, after, delta

**Predicted before writing a single line**: 29 (matching T-06's receipt,
which the dispatch also predicted). **Measured before my edit**: the RED
run (test cases H–K already appended, production code absent) printed all
29 pre-existing `ok` lines (A1 through G1) verbatim before crashing on the
missing `warn_for_agent` attribute — so the pre-existing count is directly
observed at 29, matching the prediction exactly. I did not additionally
run the suite with zero test-file edits, since the RED run's own leading
29 lines already establish this figure without a second invocation.

**After my edit**: 55.

**Delta: 26 new `ok` lines**, by name:

- H1: warn_for_agent returns non-None text when current is at or above threshold
- H2: the text carries the agent's current figure
- H3: the text carries the threshold figure
- H4: the text contains the substring handoff
- H5: the text contains none of blocked/stopped/refused/prevented
- H6: --warn-for exits 2 when the function returns text
- H7: --warn-for stdout is non-empty when it exits 2
- H8: --warn-for stdout carries the current figure
- H9: --warn-for stdout carries the threshold figure
- H10: --warn-for stdout carries the substring handoff
- H11: --warn-for stdout contains none of blocked/stopped/refused/prevented
- I1: warn_for_agent returns None when current is below threshold
- I2: --warn-for exits 0 when the function returns None
- I3: --warn-for stdout is EMPTY when it exits 0
- J-anchor: the threshold-comparison line is present in context-watch.py
- J-RED: the mutant copy's text differs from the original
- J1: the mutant's text differs from the original's text on the SAME crossing fixture
- J2: real warning count is 1 on the crossing fixture
- J3: mutant warning count is 0 on the SAME crossing fixture (fail-open silenced)
- K1: an absent transcript returns None rather than raising
- K2: --warn-for on an absent transcript exits 0
- K3: --warn-for on an absent transcript prints nothing
- K4: an absent config returns text (not None) rather than raising, because the DEFAULT 200000 is still below this fixture's current
- K5: --warn-for on an absent config exits 2 (falls back to DEFAULT, still crosses)
- K6: an absent config, with current below the DEFAULT, returns None rather than raising
- K7: --warn-for on an absent config, below the DEFAULT, exits 0 and prints nothing

## Verify honesty

**Line 2 is vacuous for this task's work**, exactly as the dispatch told me
in advance: the floor of 22 is satisfied by T-06's 29 alone, before I wrote
anything. I am not banking it as evidence of my work — the 26-line delta
above is.

Lines 1 and 3 are NOT vacuous. Line 1 is the bare suite: any regression in
either the pre-existing cases or the 26 new ones would print `FAIL` and
change the trailing count, which the grep/test in line 2 (and my own
reading of line 1's own tail) would catch. Line 3 reds if
`run-unit-tests.sh` reports anything other than `PASS test-context-watch.py`
for this script, or if it prints `MISCONFIGURED`. I did not find either of
these two capable of vacuous passage in a way that would mask a real
regression in my work.

## CASE J — D-08 compliance, stated explicitly

The proof is a COUNT (`real_count_j` vs `mutant_count_j`, both derived from
`buf.getvalue().count("WARNING")`), never an exit status. Measured: real =
1, mutant = 0 — they differ, so the mutation applied and is NOT a false
"surviving mutant." Had they come out equal, the test raises `SystemExit`
with an `INCONCLUSIVE` message and a non-zero exit, per the dispatch's
instruction; this branch did not fire in this run (counts differ).

## Files touched

- `.claude/skills/harness/bin/context-watch.py`
- `.claude/skills/harness/bin/test-context-watch.py`

No other file was written. `.harness/harness.json`, `STATE.md`, and
`plan.yaml` show as modified in `git status` but were not touched by this
task — they are the operator's concurrent tasks in this same worktree.
`.claude/settings.json` and `.claude/skills/harness/bin/run-unit-tests.sh`
show NO diff (`git diff --stat` on both is empty) — confirmed untouched,
per the dispatch's hardest boundary.

## Boundary notes

- `slug_of_path`, `entry_context_size`, and `resolve_threshold` are reused
  by direct call, not reimplemented — no second copy of D-11's arithmetic
  or T-06's config-resolution logic exists in this file.
- `warn_for_agent` and `_last_measured_usage` are both new module-level
  functions; nothing else in the pre-existing file (`discover_orchestrator_rows`,
  `_build_row`, `format_rows`, the no-argument/one-argument CLI table path)
  was modified, only the `main()` argument parser gained three new flags
  and one new early-return branch ahead of the existing logic.
- I did not touch `.claude/settings.json` or
  `.claude/skills/harness/bin/run-unit-tests.sh`. `context-watch-hook.py`
  and `test-context-watch-hook.py` are not mine and were not created by me.
