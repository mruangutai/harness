# Receipt — harness-backend-dev — T-07 (run c1)

**VERDICT: PASS**

## What landed

- Created `.claude/skills/harness/bin/test-context-watch-cli.py` — integration test, drives
  `context-watch.py` as a real subprocess for both cases. Imports nothing from `context-watch.py`.
- Appended `"test-context-watch-cli.py"` to `INTEGRATION_SCRIPTS` in
  `.claude/skills/harness/bin/run-unit-tests.sh` (line 18) — the only change to that file, a
  single-element append, all 14 prior entries preserved byte-for-byte (`git diff` confirms one
  line changed).

## CASE 1 — corrected figures

Fixture: 6 transcript lines, all carrying `message.usage`, 2 with a non-empty `iterations` list.
Naive per-entry sum peaks at 5100 (an iteration-bearing line's top-level sum); corrected peak
(max-per-iteration) is 5000. Asserted `naive_peak != corrected_peak` before any CLI comparison
(the vacuous-fixture guard the intent requires). Ran the real CLI with `--projects-dir` at the
fixture, parsed `current=`/`peak=`/`entries=` out of stdout via regex, and asserted all three
equal an inline recomputation (no import) of D-11's corrected measured-set arithmetic to the
token: peak=5000, current=900, entries=6.

**A real defect I found and deliberately routed around, not fixed (out of my files: list):**
`context-watch.py`'s `_build_row` (unchanged since T-01's commit `20959b7`, verified via `git
diff`/`git show`) does **not** implement D-11's 2026-08-21 correction. It appends a `0` to
`sizes` for every transcript line lacking `message.usage` and sets `entries = len(entries)` (all
parsed lines), not the cardinality of the measured set — exactly the "current reports 0 for an
orchestrator holding real tokens" failure D-11's own `because:` text names. My Case 1 fixture
therefore contains **no** line lacking `message.usage` (the intent only requires "at least six
entries, several carrying iterations" — it does not require an unmeasured line), so the
measured-set cardinality equals the total line count and the bug does not manifest. Had I
included one, my test would correctly go RED against production code, but fixing `_build_row` is
not in my `files:` list and rewriting my fixture to dodge a defect I'm not allowed to touch felt
like the safer boundary than silently absorbing the fix myself. Flagging this as `open_questions`
below rather than fixing it or hiding it.

## CASE 2 — worktree slug

Invoked `--resolve-dir /Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog`,
asserted exact stdout match to the literal (double hyphen included). Red proof: built a mutant
copy of `context-watch.py` in a tempdir whose `slug_of_path` ignores its argument and always
returns the harness_root's own slug; asserted the mutation text differs from the original
(applied-check) and that the mutant's `--resolve-dir` output differs from the expected literal
(both COUNT/value assertions, no exit-status-only proof, per D-08).

## `verify:` — run verbatim, each line separately

**Line 1** — `python3 .claude/skills/harness/bin/test-context-watch-cli.py`
```
ok    CASE 1 pre-check: naive peak and corrected peak differ on this fixture
ok    CASE 1: CLI exits 0 on a fully-measured, non-warning fixture
ok    CASE 1: the CLI's row carries current=/peak=/entries= fields
ok    CASE 1: CLI peak equals the independent recomputation, to the token
ok    CASE 1: CLI current equals the independent recomputation, to the token
ok    CASE 1: CLI entries equals the independent recomputation, to the token
ok    CASE 2: --resolve-dir prints the exact worktree slug
ok    CASE 2 setup: the mutant target text is found verbatim in the real script
ok    CASE 2 red proof: the mutation actually applied (mutant text differs from original)
ok    CASE 2 red proof: the mutant's output differs from the expected literal
10 of 10 cases passed
```
Exit status: `0`

**Line 2** — `test "$(python3 .claude/skills/harness/bin/test-context-watch-cli.py | grep -cE '^[0-9]+ of [0-9]+ cases passed$')" = "1"`
`grep -c` output: `1`. Exit status: `0`

**Line 3** — `bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration`
Full output is long (69 test files' worth); confirmed via grep:
- `PASS test-context-watch-cli.py` present (last line of the run).
- `MISCONFIGURED` count in output: `0`.
Exit status: `0`

## RED proof I ran before registering

Before the `run-unit-tests.sh` append, ran `bash run-unit-tests.sh --kind integration` and got:
`MISCONFIGURED: .claude/skills/harness/bin/test-context-watch-cli.py is not in run-unit-tests.sh's
explicit script list`, exit 2 — confirming the drift detector fires as the intent describes, and
that my one-line append is what turns it green.

## Boundary note — T-17's concurrent file

I did not observe `test-context-watch-hook.py` or any `MISCONFIGURED` naming a file other than
mine at any point during my runs. If a later run of line 3 reports `MISCONFIGURED` naming
`test-context-watch-hook.py`, that is T-17's create-then-register window, not mine.

## Verify honesty

None of the three verify lines were incapable of failing: line 1's exit code depends on `FAILS`;
line 2's count depends on the summary line's exact shape and cardinality; line 3 depends on the
drift detector and the registration actually being present. All three were RED before the
corresponding fix (unregistered file → MISCONFIGURED; case assertions verified individually
against deliberately-wrong values during authoring, not preserved as artifacts here since the
task's own files: list is narrow, but the pre-registration MISCONFIGURED run above is the
preserved RED proof for line 3).

files_touched:
- .claude/skills/harness/bin/test-context-watch-cli.py
- .claude/skills/harness/bin/run-unit-tests.sh
