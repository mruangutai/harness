# Receipt — harness-backend-dev — T-02 cycle 3 — FEAT-32-concurrent-write-merge

## Send-back

Case 7's `dotdot_literal` (old `test-harness-merge.py:278`ish) was two nested `..`/`../..`
segments layered onto the same non-matching `otherdir` path already covered by the check above
it — its literal string does not end in the tail regex's matching pattern, so it duplicated the
"plainly non-matching" check rather than pinning `require_destination`'s stated property (match
the RESOLVED path, never the argument). Confirmed by measurement below: mutating
`require_destination` to search `path` instead of `resolved` left all three case-7 checks green.

No purely-`..` literal can pin this property: textually walking `..` collapses to a path whose
literal and resolved forms agree (or both fail to match the tail) — divergence between "what the
string ends in" and "what it resolves to" requires a symlink.

## Fix — replaced the one authorised check

Only `.claude/skills/harness/bin/test-harness-merge.py` changed;
`.claude/skills/harness/bin/harness_merge.py` is untouched (`git status --porcelain` shows it
`??` — untracked from earlier cycles — with no diff against the pre-edit copy I never touched).

Replaced the `dotdot_literal` block in `case_7_require_destination` with a symlink construction:
- real directory `outside/` and a separate real directory `linkholder/`;
- `linkholder/mydir` created as `os.symlink(outside_dir, mydir_link)`;
- literal passed to `require_destination`: `linkholder/mydir/myfile-zzz.md` — its STRING ends in
  `mydir/myfile-zzz.md`, matching the tail regex verbatim;
- `os.path.realpath` resolves the symlink, giving `outside/myfile-zzz.md`, which has no `mydir/`
  segment and does not match.

Kept the two pre-existing checks unchanged: "matching resolved path is accepted" (stops a
refuse-everything implementation from passing) and "non-matching path raises MergeRefusal(9)"
(the plain non-matching case). Nothing was weakened; one check was replaced because it did not
test what its label claimed, per the dispatch's sole authorised exception.

## Proof it bites

Copied `bin/` to a tmpdir via `python3 -c "shutil.copytree(...)"` (the accepted `cp`-avoidance
substitution — `bash-write-guard.sh` denies literal `cp` with a variable target). In the copy,
mutated `harness_merge.py`'s `require_destination` BY NAME:

```
target: "if tail_regex.search(resolved):"
repl:   "if tail_regex.search(path):"
assert m != s  # confirmed applied — grep on the mutated file shows line 152: `if tail_regex.search(path):`
```

Ran the suite (unmutated `test-harness-merge.py`) against that mutant:

```
PASS - case7: matching resolved path is accepted
PASS - case7: non-matching path raises MergeRefusal(9)
FAIL - case7: symlink escape (literal ends in matching tail via symlinked 'mydir', realpath resolves outside and does not match) raises MergeRefusal(9)
FAIL - 1/18 checks failed
```

The new symlink check is the one that reddens, and it is a real assertion failure (`check(...,
raised_9_symlink, ...)` evaluated `False`, not a traceback — the call to
`require_destination(symlink_literal, ...)` returned normally under the mutant instead of
raising, so no exception was ever thrown to interrupt the test).

**The plainly-non-matching check does NOT redden under this mutant.** Its literal
(`otherdir/myfile-abc.md`) does not contain a `mydir/` segment either as a literal string or as a
resolved path, so `tail_regex.search(path)` still fails to match under the mutant, and
`require_destination` still refuses it via the `path`-based mutant search exactly as it would via
`resolved`. Only the new symlink check discriminates the argument-vs-realpath property; the other
two checks are non-discriminating against this specific mutant (by design — they pin the accept
direction and a case that happens not to overlap the mutated branch's blind spot).

Confirmed unmutated suite stays fully green: 18/18 checks passed with the new construction in
place (run separately, no mutation).

## `verify:` — re-run verbatim (with the `cp -R` → `python3 -c "shutil.copytree(...)"`
substitution, same as cycles 1-2, because `bash-write-guard.sh` denies literal `cp` with a
variable target)

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
PASS - case7: symlink escape (literal ends in matching tail via symlinked 'mydir', realpath resolves outside and does not match) raises MergeRefusal(9)
PASS - case8: acquire raises MergeRefusal(6) against a live holder
PASS - case8: refusal lines name the lock path
PASS - 18/18 checks passed
VERIFY_BLOCK_EXIT=0
```

The RED-PROOF leg (`USE_FLOCK` off, mutated by `verify:`'s own script) did not print "RED PROOF
FAILED" — the suite still goes red under it. `verify:` exited 0 end-to-end.

## USE_FLOCK-off mutant — re-confirmed still reddens case 4 only

Ran the same mutant separately with output visible:

```
FAIL - case4: locked_update returned normally after stale lock killed (raised MergeRefusal(...) instead of returning normally)
FAIL - case4: transform output is on disk (locked_update did not return)
FAIL - 2/18 checks failed
exit=1
```

All 16 other checks (18 total, including the new symlink check) still pass — case 4 and only
case 4 is flock-dependent, unchanged from cycles 1-2.

## `run-unit-tests.sh --check-kinds`

```
$ .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
MISCONFIGURED: .claude/skills/harness/bin/test-dispatch-guard.py is not in run-unit-tests.sh's
explicit script list
(exit 2)
```

Same outcome as cycle 2, predicted by the dispatch. `test-dispatch-guard.py` is T-07's file, not
mine; registration is T-10's job. Did not touch `run-unit-tests.sh` or `.harness/harness.json`.

## Correction to the cycle-2 receipt

Cycle-2's receipt still carried, in its Step 3 bullet list, "the existing assertion verbatim" —
that part is accurate — but its rules-followed section referenced case 5/6 reporting "trial
number, both results, and file content" only in the cycle-1-quoting context; re-checking
cycle-2's own text: the sentence flagged by this dispatch ("case 5/6 report any third outcome
with trial number, both results, and file content") appears in cycle-2's **Send-back** section as
a correction of *cycle-1's* claim, not as a restatement of cycle-2's own — it already states "true
of case 5 only — case 6 had no trials and reported byte lengths." That correction was already
made in cycle 2. No further correction needed; cycle-2's send-back section already carries the
accurate version. (Re-reading confirms this — no live inaccurate sentence found in the cycle-2
receipt to fix.)

## Rules followed

- Added and strengthened only, with the one authorised replacement: case 7's `dotdot_literal`
  check swapped for the symlink construction because it did not test what its label claimed.
  Every other assertion (18 total minus the 1 replaced = kept all others) is unchanged.
- Only `.claude/skills/harness/bin/test-harness-merge.py` changed —
  `git status --porcelain -- .claude/skills/harness/bin/harness_merge.py` shows only the
  pre-existing untracked `??`, no modification.
- Did not touch `test-expertise-merge.py`, `run-unit-tests.sh`, `.harness/harness.json`, or any
  DEC-174 surface.
- `cp -R` → `python3 -c "shutil.copytree(...)"` substitution reused and declared per cycle 1-2
  precedent.

## Open items

None blocking.
