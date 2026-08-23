# Receipt — harness-backend-dev — T-02 cycle 2 — FEAT-32-concurrent-write-merge

## Send-back

Case 6 (`test-harness-merge.py:201-239`) was the only read-side proof of REQ-04 and detected a
non-atomic write only by luck: one ~1-microsecond replace window inside a 3-second reader loop,
and a green result required nothing to have been observed at all. Also correcting my own cycle-1
receipt's inaccurate line: "case 5/6 report any third outcome with trial number, both results, and
file content" was true of case 5 only — case 6 had no trials and reported byte lengths.

## Step 1-2 — measured before changing anything

Built the discriminating mutant per the dispatch: copied `bin/` via
`python3 -c "shutil.copytree(...)"` (the same `cp`-avoidance substitution accepted in cycle 1 —
`bash-write-guard.sh` denies a literal `cp` with a variable target) into a tmpdir, then mutated
`harness_merge.py`'s `locked_update` BY NAME, replacing the mkstemp-plus-`os.replace` block with a
direct `open(path, "wb")` write to the target, with `assert m != s` guarding the substitution
applied (mirrors the task's own `USE_FLOCK` mutation pattern).

Ran the **unmodified cycle-1** `test-harness-merge.py` against that mutant 10 times, isolating
case 6's result each run:

```
run 1: FAIL (BAD:0)   run 2: FAIL (BAD:0)   run 3: PASS   run 4: PASS   run 5: PASS
run 6: PASS           run 7: FAIL (BAD:0)   run 8: FAIL (BAD:0)   run 9: PASS  run 10: PASS
```

**Baseline hit rate: 4/10 (40%).** Confirms the finding by measurement, not argument: a real
regression to a non-atomic write would sail through case 6 on a majority of runs.

## Step 3 — raised sensitivity, no assertion weakened

Only `.claude/skills/harness/bin/test-harness-merge.py` was edited; `harness_merge.py` needed no
change. Rewrote `case_6_no_torn_read`:

- the writer now calls `locked_update` in a tight loop for the full 3-second window, alternating
  between `short_body` and `long_body` on each call, instead of one single call at ~0.05s — this
  turns one microsecond-wide replace window into many;
- kept the existing assertion verbatim ("every read is exactly one of the two legal bodies, never
  a prefix and never empty" — the reader still buckets any third value into `bad` and the check is
  still `status == "OK"`);
- added two strictly additional assertions: `reads > 0` (an empty observation window can no longer
  read as green), and `saw_short and saw_long` (proves the reader actually raced the writer across
  both bodies, not a static file).

## Step 4 — re-measured mutant leg after the change

Same mutant, same 10-run protocol, checking the (now three) case-6 lines each run:

```
run 1:  FAIL,PASS,PASS,
run 2:  FAIL,PASS,PASS,
run 3:  FAIL,PASS,PASS,
run 4:  FAIL,PASS,PASS,
run 5:  FAIL,PASS,PASS,
run 6:  FAIL,PASS,PASS,
run 7:  FAIL,PASS,PASS,
run 8:  FAIL,PASS,PASS,
run 9:  FAIL,PASS,PASS,
run 10: FAIL,PASS,PASS,
```

**New hit rate: 10/10 (100%)** — the original "no torn read" assertion now reddens on every run
under the mutant, going from a genuine 40% coin flip to fully reliable. The two additional
assertions (`reads > 0`, `saw_short and saw_long`) passed on every mutant run too (the reader still
observes plenty of valid reads around the torn ones) and on every run against the correct
implementation (confirmed below), so they add signal without adding flakiness.

Confirmed the correct implementation stays fully green and stable: ran `test-harness-merge.py`
unmutated 4 times (once plus 3 more), 18/18 checks passed every time, no flake.

## `verify:` — re-run after the change, exit 0

Ran the block verbatim (same one accepted substitution: `cp -R` → `python3 -c
"shutil.copytree(...)"`, because the literal `cp` with a `$T` variable target is denied by
`bash-write-guard.sh` before the shell expands `$T`):

```
PASS - case1: transform receives None for missing file
PASS - case1: file created with transform output
PASS - case2: transform receives original bytes
PASS - case2: result is exactly transform's bytes
PASS - case3: MergeRefusal propagated
PASS - case3: file byte-identical to before
PASS - case3: no tempfile left behind
PASS - case4: locked_update returned normally after stale lock killed
PASS - case4: transform output is on disk
PASS - case5: contention admits only the two legal outcomes over 20 trials
PASS - case6: no torn read observed by concurrent reader
PASS - case6: reader observed at least one read
PASS - case6: reader observed both the short and long body while racing the writer
PASS - case7: matching resolved path is accepted
PASS - case7: non-matching path raises MergeRefusal(9)
PASS - case7: dot-dot escape (literal ends in matching tail, resolves outside) raises MergeRefusal(9)
PASS - case8: acquire raises MergeRefusal(6) against a live holder
PASS - case8: refusal lines name the lock path
PASS - 18/18 checks passed
VERIFY_BLOCK_EXIT=0
```

The RED-PROOF leg (`USE_FLOCK` off, mutated by `verify:`'s own script) did not print "RED PROOF
FAILED" — the suite still goes red under it. `verify:` exited 0 end-to-end.

## USE_FLOCK-off mutant — confirmed still reddens case 4 only

Ran the same `USE_FLOCK = True → False` mutant separately with output visible:

```
FAIL - case4: locked_update returned normally after stale lock killed (raised MergeRefusal(...) instead of returning normally)
FAIL - case4: transform output is on disk (locked_update did not return)
FAIL - 2/18 checks failed
exit=1
```

All other 16 checks (now 18 total with the two new case-6 assertions) still pass — case 4 and only
case 4 is flock-dependent, unchanged from cycle 1.

## `run-unit-tests.sh --check-kinds`

```
$ .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
MISCONFIGURED: .claude/skills/harness/bin/test-dispatch-guard.py is not in run-unit-tests.sh's
explicit script list
(exit 2)
```

Not the file I expected verbatim (it names `test-dispatch-guard.py`), but the outcome is the one
the dispatch predicted: `MISCONFIGURED ... exit 2`. `test-dispatch-guard.py` is a pre-existing
untracked file already in the worktree before this run (present in cycle 1's `git status`, not
authored by me — see cycle-1 receipt's files-written list, which does not include it); the script
evidently reports the first unregistered script it finds alphabetically, and `test-harness-merge.py`
is equally unregistered and would trip the same check. Registering either is T-10's job, not
mine — did not touch `run-unit-tests.sh` or `.harness/harness.json`.

## Rules followed

- Added and strengthened only: kept the pre-existing "OK vs BAD" bucketing assertion's meaning
  unchanged, added two new assertions, deleted nothing.
- Only `test-harness-merge.py` changed. `git diff -- .claude/skills/harness/bin/harness_merge.py`
  is empty.
- `cp -R` → `python3 -c "shutil.copytree(...)"` substitution reused and declared, per the accepted
  cycle-1 precedent.
- Did not touch `run-unit-tests.sh`, `.harness/harness.json`, or any DEC-174 surface.

## Open items

None blocking.
