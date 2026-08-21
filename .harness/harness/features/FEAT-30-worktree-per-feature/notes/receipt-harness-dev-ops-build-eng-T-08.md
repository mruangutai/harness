# Receipt — harness-dev-ops — T-08 — build-eng

## Verdict: FAIL

Both registrations were made correctly and are independently verified as correct. The plan's
`verify:` block, run byte-verbatim, exits 1 — not because either registration is wrong, but
because it also exercises `test-harness-yaml.py`, an already-registered integration script that
fails on a pre-existing, out-of-scope defect: `feature-worktree.py` (T-01/T-02) carries an `except
ImportError` guard not covered by that test's hardcoded allowed set. This was invisible before
T-08 because D-06 forbade any earlier task from routing through `run-unit-tests.sh`.

## The two edits

1. `.claude/skills/harness/bin/run-unit-tests.sh` line 18 — appended `"test-feature-worktree.py"
   "test-expertise-merge.py"` to `INTEGRATION_SCRIPTS` (was 12 entries, now 14). Nothing else in
   the file touched.
2. `.harness/harness.json` line 119 — appended
   `.claude/skills/harness/bin/test-feature-worktree.py` and
   `.claude/skills/harness/bin/test-expertise-merge.py` as two more pipe-separated entries to
   `test_kinds.integration.detect` (was 5 entries, now 7), preserving order. No other key touched.

Idempotence precondition checked first: neither filename was present in `INTEGRATION_SCRIPTS` nor
in `detect` before this run.

## Verify — run exactly as quoted in T-08's `verify:` block

Ran via a script file at `/private/tmp/.../scratchpad/t08-verify.sh` rather than typed inline as a
heredoc directly into a Bash call, per the hazard note (heredoc content read as literal text by
the guard). No line of the verify itself was altered.

```
set -u
out=$(.claude/skills/harness/bin/run-unit-tests.sh --kind integration 2>&1) || { echo "$out"; exit 1; }
echo "$out" | grep -q '^PASS test-feature-worktree.py$' || { echo "$out"; exit 1; }
echo "$out" | grep -q '^PASS test-expertise-merge.py$' || { echo "$out"; exit 1; }
echo "$out" | grep -q '^FAIL ' && { echo "$out"; exit 1; }
python3 - <<'PY' || exit 1
import json
d = json.load(open(".harness/harness.json"))["test_kinds"]["integration"]["detect"]
for f in ("test-feature-worktree.py", "test-expertise-merge.py"):
    assert ".claude/skills/harness/bin/" + f in d, f + " missing from integration detect"
PY
exit 0
```

Actual output (relevant lines; full run log kept at
`/private/tmp/.../scratchpad/t08-run.log`):

```
PASS test-feature-worktree.py
PASS test-expertise-merge.py
FAIL test_exactly_one_guarded_import_in_the_tree: unexpected guarded-import file(s) outside the allowed set: {'feature-worktree.py'}
FAIL test-harness-yaml.py
```

VERIFY_EXIT=1 — the second `grep -q '^FAIL '` found a match (exit 0), so its `&&` right side fired
and the script exited 1 via `{ echo "$out"; exit 1; }`, exactly as the trap note describes for the
"FAIL exists" branch (the note only covers the no-match branch; a real match still aborts, and it
should).

Confirmed the two new files themselves are unconditionally green and this is not caused by my
edits: ran `python3 .claude/skills/harness/bin/test-harness-yaml.py` standalone before making the
edits (via `git stash`, untracked new-test files unaffected by stash) and after — same FAIL either
time, same message, naming `feature-worktree.py`, which is not in T-08's file list and which I did
not touch.

## The four numbers (operator's own baseline was 179 / 0 unit, 90 / 0 integration at 49c528a)

- `--kind unit`: `rc_unit=$?` after `out_unit=$(... 2>&1)` → **exit 0**; `printf '%s\n' "$out_unit" | grep -c '^PASS '` → **179**; `grep -c '^FAIL '` → **0**. Unchanged from baseline, as expected (no unit-kind file touched).
- `--kind integration`: `rc_int=$?` → **exit 1**; `printf '%s\n' "$out_int" | grep -c '^PASS '` → **198** (grew from 90, as required); `grep -c '^FAIL '` → **2** (both from `test-harness-yaml.py`, one summary line + one assertion line).

## Idempotence / drift-window check

Before this change, `run-unit-tests.sh --kind integration` (and `--kind unit`) exited 2
MISCONFIGURED per D-06's expected window — confirmed via `git stash` (which does not touch
untracked files, so `feature-worktree.py`/`test-feature-worktree.py`/`expertise-merge.py`/
`test-expertise-merge.py` remained present but unregistered): `rc=2`, 0 PASS, 0 FAIL. That window
is now closed for both kinds; the runner discovers and runs both new files with 0 registration
gap.

## Not fixed, and not mine to fix

`test-harness-yaml.py`'s `allowed` set for guarded imports
(`{harness_yaml.py, feature_schema.py, check-domain.sh}`) does not include `feature-worktree.py`,
which guards an import at line 50. Fixing this means editing either `feature-worktree.py` (not in
my file list, and explicitly listed as finished/not-mine in the dispatch) or
`test-harness-yaml.py` (not in my file list either). Raised as an open question rather than
touched.
