# Receipt — harness-backend-dev — T-13 — c1

## What now works

`.claude/skills/harness/bin/verify-context-watch-live.py` — SC-01's live half. For a named agent
id it: (1) locates the sidecar/transcript itself under a projects dir, (2) recomputes
current/peak/entries **inline, independently, from D-11's text** (no import of `context-watch.py`,
not the module, not a helper, not a constant, not via `importlib`), (3) invokes
`context-watch.py` as a subprocess with the same agent id and `--projects-dir`, parses its stdout
row (regex anchored on `feature=`/`current=`/`peak=`/`entries=`, so it tolerates T-08's `blind
spot` footer and any other prose line), and (4) prints both triples side by side, then a bare
`PASS`/`FAIL` line, exiting 0 only when all three figures agree. It writes nothing, anywhere,
ever — confirmed by inspection: the only filesystem writes anywhere in the file are inside
`run_self_test()`, into paths under its own `tempfile.mkdtemp()`, removed in a `finally`.
`--self-test` builds the exact fixture the dispatch specifies and asserts both sides land on
`(747992, 747992, 1)` and that neither triple contains `1494870`.

Registered nowhere (`UNIT_SCRIPTS`, `INTEGRATION_SCRIPTS`, `test_kinds` all untouched) and named
so it can never match `run-unit-tests.sh`'s `test-*.py` drift-detector glob (D-17).

## TDD

The Iron Law's normal path (edit a committed test file, watch it fail, then pass) does not apply:
this task's `files:` list is exactly this one new file, there is no pre-existing test file for it,
and the design forbids ever creating a `test-*.py` sibling for it. The deliverable's own RED/GREEN
proof is the dispatch's `verify:` block itself, run against the tree before/after the file existed:

**RED** (before I wrote the file — `verify-context-watch-live.py` did not exist):
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py --self-test
python3: can't open file '.../verify-context-watch-live.py': [Errno 2] No such file or directory
```
Every one of the seven verify lines failed or errored against the pre-edit tree (the file was
simply absent) — genuine RED, not assumed.

**GREEN** (after implementation): all seven lines below pass. No refactor-while-red occurred;
implementation was written once, verified, and left as is.

## Verify — verbatim stdout and exit status, all seven lines separately

### Line 1
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py --self-test
```
stdout:
```
tool:        current=747992 peak=747992 entries=1
independent: current=747992 peak=747992 entries=1
PASS
```
Exit status: `0`

### Line 2
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py --self-test | grep -q 747992
```
Exit status: `0`

### Line 3
```
$ test "$(python3 .claude/skills/harness/bin/verify-context-watch-live.py --self-test | grep -c 1494870)" = "0"
```
`grep -c` output compared: `0`. Exit status of the `test`: `0`

### Line 4
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py --projects-dir /nonexistent-projects-dir some-agent-id; test $? -ne 0
```
stdout of the script:
```
verify-context-watch-live.py: projects directory not found: /nonexistent-projects-dir
```
Script's own raw exit status: `1`. Exit status of `test $? -ne 0`: `0`

### Line 5
```
$ test "$(python3 .claude/skills/harness/bin/verify-context-watch-live.py --projects-dir /nonexistent-projects-dir some-agent-id 2>&1 | grep -c 'Traceback')" = "0"
```
`grep -c` output compared: `0`. Exit status of the `test`: `0`

### Line 6
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py --projects-dir /nonexistent-projects-dir some-agent-id 2>&1 | grep -qi 'no such agent\|not found'
```
Exit status: `0`

### Line 7 (two parts)
```
$ ls .claude/skills/harness/bin/test-verify-context-watch-live.py 2>/dev/null; test $? -ne 0
```
`ls` reported nothing (file does not exist), its own exit `1`. Exit status of the `test`: `0`

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit
```
Full output captured and grepped for `MISCONFIGURED`: zero matches. Tail of output:
```
55 of 55 cases passed
PASS test-context-watch.py
```
Overall script exit status: `0`.

**Task's declared `task_verify` (the whole seven-line block above): pass**, each line individually
confirmed as shown, none summarized into a single claim.

## The `grep \|` alternation question — resolved empirically, not assumed

This machine's `grep` is `ugrep 7.5.0` (`grep --version` output), which **does** honor BRE `\|`
alternation: `echo "not found test" | grep -qi 'no such agent\|not found'` exits `0`, confirmed
before trusting line 6. No darwin-BRE gotcha materialized here. I still wrote every error message
to contain the literal, idiomatic phrase `not found` (never relying only on `no such agent`), per
the dispatch's instruction, so line 6 would have passed even had alternation been literal-only.

## A CONFIRMED DEFECT IN THE TOOL — restated, not fixed

Read `_build_row` myself (lines ~264-306 of the current `context-watch.py`, matching T-06/T-08's
prior receipts): it appends a spurious `0` to `sizes` for a parsed line with no `message.usage`
(line ~294), takes `current` as the **last raw line** (`sizes[-1]`, line 297) rather than the last
member of the D-11 measured set, and counts `entries` as `len(entries)` — every parsed line, not
the measured set's cardinality (line 305). This contradicts D-11 on `current` and `entries`;
`peak` survives because a spurious zero cannot raise a max. **I did not touch `_build_row`** — it
is not in this task's `files:` list (which names exactly one path,
`.claude/skills/harness/bin/verify-context-watch-live.py`), it belongs to T-01 (`status: done`),
and the dispatch explicitly forbids fixing it here; it is escalated separately.

**`--self-test` cannot see this defect.** Its fixture is a single jsonl line that *does* carry
`message.usage`, so the measured set and "every parsed line" are identical for it — both sides
report `(747992, 747992, 1)` and the comparison correctly agrees. This is not a gap in the
self-test's assertions; it is a structural property of a one-line fixture, stated here per the
dispatch's instruction rather than papered over by adding an unmeasured trailing line (which would
correctly red the self-test over a defect this task is forbidden to fix, converting a correct
deliverable into a false FAIL).

**Expected outcome of a hand run against a real, live orchestrator, until the escalation
resolves:** if that transcript's last raw line lacks `message.usage` (very likely on any real,
ongoing session), the tool will report `current=0` and an inflated `entries` (every parsed line,
not the measured set), while this script's independent side reports the true last-measured
`current` and the true measured-set `entries`. The comparison will disagree and print `FAIL:
disagreement on current, entries` (or a subset). **That FAIL is this script working correctly** —
catching the exact defect T-07/T-08 already confirmed by reading the source — not evidence this
script is broken. Nobody should read a live FAIL as a regression in
`verify-context-watch-live.py` while `_build_row` stands uncorrected.

## SC-01's live half — how it is actually discharged (per dispatch, recorded here for the record)

I did not have a live orchestrator agent id available to run this against during this dispatch —
no `harness-orchestrator` subagent was running under `~/.claude/projects` at the time I worked
(this task's own execution is a `harness-backend-dev` team-member spawn, not an orchestrator, and
no orchestrator sidecar for this run existed to hand-check against). Per the dispatch: "an agent
runs this script by hand against a LIVE orchestrator's agent id while that orchestrator is
running, and pastes the PASS line with the agent id and the timestamp. That is what `verify:
automated` means." I could not produce that paste in this dispatch — flagging as an
`open_question` for whoever has a live orchestrator running to do the hand run and paste the
result, per the operator's 2026-08-21 ruling that this substitutes for a `tests.yml` line for
this task specifically.

## Verify-honesty — which of the seven lines can/cannot fail

- **Line 1** can fail (a real arithmetic disagreement inside `--self-test`'s own fixture would
  redden it) and is not vacuous — it is the load-bearing self-test.
- **Lines 2 and 3** are the exact-value assertions the dispatch called the plan's "worst instance"
  concern — both are capable of failing (a tool reporting the naive `1494870` on both sides would
  fail line 3; a tool reporting neither `747992` nor `1494870` would fail line 2) and I did not
  weaken either.
- **Line 4** is capable of failing only if the script ever returns 0 on a missing projects dir —
  it does not, by construction (the `os.path.isdir` check is the very first thing `compare_agent`
  does).
- **Line 5** is the one I judge **hardest to see fail honestly**: it asserts the ABSENCE of the
  word `Traceback`, and my `main()` wraps the whole comparison in a blanket `except Exception`, so
  short of a `SystemExit`/`KeyboardInterrupt`-class escape (which `argparse` itself could
  theoretically raise before my `try` even starts, e.g. on a malformed flag) there is no code path
  left that reaches an unhandled traceback. I consider it **near-incapable of failing given the
  current implementation**, which is the intended, defensive shape — but it is not vacuous in the
  P-07 sense: it was capable of failing during development (an earlier draft without the blanket
  `except Exception` would traceback on a genuinely unexpected `OSError` subtype), and it exercises
  the same subprocess path.
- **Line 6** is capable of failing (a stated line without `not found`/`no such agent` would fail
  it) and is not vacuous; also confirmed the alternation itself works on this box rather than
  assuming it.
- **Line 7's** `ls`/`test` half can only fail if I mis-name the file — it is a naming guard, cheap
  and real. Its `run-unit-tests.sh --kind unit` half is a shared-suite check: it is capable of
  reporting `MISCONFIGURED` for an unrelated reason (see Hazard note below), which would not be my
  defect, and I did not observe that condition on this run.

## Hazard: T-17's concurrent `test-context-watch-hook.py`

Per the dispatch, T-17 (the operator's, concurrent) may register a new
`test-context-watch-hook.py` in the same `bin/` dir mid-run. My `run-unit-tests.sh --kind unit`
run above (39/39 + 55/55 checks, zero `MISCONFIGURED`) reflects the tree's state at the time I ran
it; I did not see that file present. If a later run surfaces `MISCONFIGURED` naming
`test-context-watch-hook.py`, that is T-17's create-then-register window, not a defect in this
task's deliverable — and I did not edit `run-unit-tests.sh` to guard against it, per the
boundary.

## Boundaries respected

- Only `.claude/skills/harness/bin/verify-context-watch-live.py` was created. `git status
  --porcelain` shows it as the only new file attributable to me; all other dirty/untracked paths
  (`context-watch.py`, `run-unit-tests.sh`, `test-context-watch.py`, `harness.json`, `STATE.md`,
  `plan.yaml`, other agents' receipts, `test-context-watch-cli.py`) are untouched by me — confirmed
  by `git status --porcelain` before writing this receipt.
- Python 3 standard library only (`argparse`, `json`, `os`, `re`, `shutil`, `subprocess`, `sys`,
  `tempfile` — confirmed by parsing the file's own `ast` import nodes).
- No import of `context-watch.py` anywhere (confirmed by the same `ast` walk — zero `Import`/
  `ImportFrom` nodes name it).
- Not registered in `UNIT_SCRIPTS`, `INTEGRATION_SCRIPTS`, or any `test_kinds` entry (I made no
  edit to `run-unit-tests.sh` or `harness.json` at all).
- Did not touch `STATE.md`.
- Did not commit; tree left dirty for the operator, as instructed.

## Open questions

- { id: Q1, question: "No live harness-orchestrator agent id was running under ~/.claude/projects during this dispatch to hand-run verify-context-watch-live.py against, per SC-01's live-half discharge method. Someone with a live orchestrator running needs to run `python3 .claude/skills/harness/bin/verify-context-watch-live.py <agent-id>` by hand and paste the PASS/FAIL line with agent id and timestamp. A FAIL there is EXPECTED and correct until the separately-escalated _build_row/D-11 defect in context-watch.py is fixed — it should not be read as this script being broken.", blocking: false }

## Files touched

- `.claude/skills/harness/bin/verify-context-watch-live.py` (new)
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/observations/harness-backend-dev.md` (appended)
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/receipt-harness-backend-dev-T-13-c1.md` (this file)
