# Receipt — harness-dev-ops — build-eng — T-02 cycle 2 (SC-07 red-proof gap)

## Result

PASS, no code change. Cycle 1's DIGEST count ("6 of the new cases redden") does not match its own
11-line paste, and the challenge's premise — that neither SC-07 case appears among the reddened
set — is refuted by direct re-measurement. **Both `case_remove_dirty_untracked` and
`case_remove_dirty_tracked` genuinely redden under T-02's verify mutation.** Cycle 1's paste was an
incomplete capture of a real run, not a fabricated one: every line it pasted is present in mine;
three lines are missing from its paste (the two SC-07 `WOULD DISCARD` assertions, plus one SC-04
`refuse: the tree still exists on disk` line), and the true unsuppressed FAIL count is 14 assertion
lines, not 6 or 11.

## The measurement (item 1: complete verdict list for both SC-07 cases, mutated build)

Re-ran the exact mutation from T-02's `verify:` (both `REFUSE_ON_DIRTY` and `REQUIRE_LANDED` forced
`False` in a tempdir copy) and captured the **full, unsuppressed** run — not the `>/dev/null 2>&1`
gated form. Every `check()` line for the two SC-07 cases:

```
PASS  SC-07 refuse (untracked): remove exits 4
FAIL  SC-07 refuse (untracked): stdout names WOULD DISCARD untracked.txt
      | (empty stdout)
PASS  SC-07 refuse (untracked): the tree and the untracked file still exist on disk
PASS  SC-07 refuse (tracked): remove exits 4 on an otherwise fully landed tree
FAIL  SC-07 refuse (tracked): stdout names WOULD DISCARD .harness/team-config.yaml
      | (empty stdout)
```

Both cases have exactly one FAIL each. The suite as a whole reddens 14 assertions total (not 6):
the two above, plus 3 in `SC-04 refuse`, 3 in `SC-04 allow`, 3 in `SC-04 differs`, 3 in
`no artifact directory at all` (full list in the DIGEST). Total check() count across the suite is
74 (60 PASS + 14 FAIL under mutation), all 74 PASS unmutated — not "76" as cycle 1's receipt
states; that number does not reconcile with either run and is flagged as an open question, not
corrected here (out of this cycle's scope).

## Mechanism (item 2: which half survives, and why)

**Exit-code half survives for both SC-07 cases, but not for the reason GATE 2 exists.** With
`REFUSE_ON_DIRTY = False`, the module's own dirty-check print is skipped entirely — control falls
through to GATE 3 (also disabled) and then to the removal step, which calls `git worktree remove`
directly against a tree that is genuinely dirty (an untracked file present, or a tracked file
modified). Git itself refuses to remove a worktree with uncommitted changes without `--force`,
exits non-zero, and `cmd_remove`'s existing "pass git stderr through, exit 4 on non-zero git exit"
path (the same path that handles a real git failure at removal time) maps that refusal to exit 4 —
coincidentally identical to GATE 2's own exit code. This is an unrelated mechanism producing the
same number; **it does not exercise the code this test exists to protect.**

**Stdout half is the one that actually discriminates.** `WOULD DISCARD <path>` is printed only
inside the `if REFUSE_ON_DIRTY:` block (feature-worktree.py:216-227). With the constant `False`,
that block never executes, so `r2.stdout` is empty for both cases, and both `"WOULD DISCARD ..." in
r2.stdout` assertions correctly FAIL. This is exactly why the intent's closing line ("every one of
these six asserts BOTH the exit code and the named path — an exit-code-only assertion passes
against a guard that refuses for the wrong reason") is satisfied as written: the exit-code
assertion alone would have been blind here, and the paired stdout assertion is what makes the case
capable of red.

## Diagnostic-only run (item: isolate `REFUSE_ON_DIRTY` alone, never touching the plan's verify)

Per the dispatch, mutated `REFUSE_ON_DIRTY` alone (in a separate scratch tempdir copy,
`REQUIRE_LANDED` left `True`) purely to understand the interaction — this run is not part of, and
did not replace, the plan's own verify:

```
FAIL  SC-07 refuse (untracked): remove exits 4          (rc=5, GATE 3 fires: no artifact dir yet)
FAIL  SC-07 refuse (untracked): stdout names WOULD DISCARD untracked.txt
PASS  SC-07 refuse (untracked): tree/file still exist
PASS  SC-07 refuse (tracked): remove exits 4             (GATE 3 passes — already landed; git's own
                                                            dirty refusal still yields exit 4)
FAIL  SC-07 refuse (tracked): stdout names WOULD DISCARD .harness/team-config.yaml
```

This confirms the exit-code survival in the real (both-gates-off) mutation is contingent on GATE 3
also being disabled for the untracked case — with only GATE 2 off, GATE 3 fires first for FEAT-94
(no artifact ever landed) and produces a *different*, also-wrong exit code (5, not 4), which is a
second, independent way that case can redden. Either way the stdout assertion is what is actually
load-bearing.

## Conclusion (item 4)

Both halves' behavior differs (exit code survives via an unrelated git-level mechanism; stdout
reddens for the real reason), but **the case as a whole reddens in both instances** — RESULTS
contains a FAIL for each. There is no gap to close: item 3's conditional ("if `WOULD DISCARD` does
not redden, that is yours to close") does not apply, because it does redden, measured directly.
**No production or test code was changed.** Cycle 1's count was simply an incomplete paste of a
real run, not a false claim about which cases reddened — but the record should have said "14, all
pasted" or named the omission, not "6" against an 11-line excerpt. That mismatch is the actual
defect in cycle 1's receipt: a record that undercounts by more than half without flagging that the
paste was partial.

## Unmutated suite (final state)

`python3 .claude/skills/harness/bin/test-feature-worktree.py` (real, unmutated
`feature-worktree.py`): 74/74 check() calls PASS, `PASS test-feature-worktree.py`, exit 0. The
literal T-02 `verify:` block (byte-checked against plan.yaml lines 460-473 before running, unchanged
from cycle 1's copy) also exits 0 end to end.

## git status, before and after

Identical apart from two untracked files that appeared mid-run and were never touched by me —
`.claude/skills/harness/bin/expertise-merge.py` and `test-expertise-merge.py`, `harness-backend-dev`'s
concurrent work per the dispatch's own note. No file under my write scope changed.

## Not done here

No change to `feature-worktree.py` or `test-feature-worktree.py`. `run-unit-tests.sh` not invoked
(D-06). Nothing staged or committed. `harness_boundary.py`, `check-domain.sh`,
`bash-write-guard.sh`, and their test files untouched.
