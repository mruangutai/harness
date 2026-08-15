# Receipt — harness-backend-dev — T-03 cycle 2 (docstring + no-board assertions)

## Scope

Prose and assertions only, per loop-back `runs/2026-08-13-04-eng/loopback-T-03-c1.md`. No behaviour
change. Two files touched: `.claude/skills/harness/bin/gh-sync.py`,
`.claude/skills/harness/bin/test-gh-sync.py`.

## F-1 — docstring mis-filed the no-board case (`gh-sync.py:19-30`)

Moved the "no `github.board` configured" clause out of the ENVIRONMENTAL-PRECONDITION/
whole-invocation-SKIP sentence. New text states it separately: one plain line, station writes not
attempted, issue lifecycle (open/close-task's close/abandon/ship) runs unchanged, invocation never
abandoned for it.

## F-2 — docstring claimed a failing issue close continues (`gh-sync.py:23-30`)

Removed "OR an issue close" from the loud-continue clause, which now covers station writes only.
Added a sentence stating the issue close stays on `gh()`/SKIP-on-failure, and that the parent write
is ordered before it (T-03 step 4) specifically so termination there can never swallow it.

## F-3 — no-board test block could not discriminate (`test-gh-sync.py:1187-1206`)

Added three assertions to the `no board configured` block:
1. `"no github.board configured" in r.stdout and "SKIP" not in r.stdout` — pins the plain-line/
   not-a-skip requirement from step 4.
2. `t2R is not None` — `open` recorded T-02's issue despite no board, proving the lifecycle ran
   rather than the whole invocation having been abandoned.
3. `t1R is not None and any(l.startswith(f"issue close {t1R}") for l in logR)` — the fake's call log
   contains the actual `issue close` for T-01, proving `close-task`'s lifecycle ran too.

`t2R`/`t1R` are the same reads that were previously dead (`t2R` at old line 1201); they are now
consumed by assertions.

## Non-vacuity proof — failing mutant

A hash-swap RED does not work here (`HEAD`'s `gh-sync.py` already runs the lifecycle unconditionally
when no board is configured — F-3's own point). Used a failing mutant instead.

**Baseline hash** (post-F-1/F-2 fix, pre-mutation), taken before mutating:
```
1eed5977ae07881426855e106ef9962876c98a90c336faa4c219f9c4d871f4f7  .claude/skills/harness/bin/gh-sync.py
```

**Mutation** (local only, in `load_config`):
```python
    board = gh_board.load_board(root)
    if board is None:
-       print("gh-sync: no github.board configured — station writes are not attempted")
+       skip("MUTANT: no github.board configured — station writes are not attempted")
    return repo, board
```

**Why not run the full signed verify for the RED step:** mutating `load_config` globally also
reddens an unrelated, pre-existing FEAT-09 fixture around line ~390 of `test-gh-sync.py` that
configures `harness.json` with no `board` key at all and relies on the same "board is None ->
continue" branch — that fixture predates T-03's board feature and is not part of this loop-back's
scope. Running the real `test-gh-sync.py` against the mutant aborts on an uncaught `IndexError` in
that earlier, unrelated block before ever reaching the F-3 block, which would obscure rather than
demonstrate the two target assertions failing. Isolated the F-3 block instead, in a standalone
script built from the exact same helper functions and `FAKE_GH_STATIONS` fixture as
`test-gh-sync.py` (copied verbatim, not modified), at
`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/cd83b531-197f-4da6-a4a5-9bb0ec5fcaa5/scratchpad/mutant_repro.py`.
Confirmed this repro is faithful: run against the unmutated `gh-sync.py` first, all 6 checks in the
block pass (matches the real suite's result for that block).

**RED — mutant applied, isolated repro run:**
```
$ python3 mutant_repro.py
ok    no board configured: open exits 0
FAIL  no board configured: prints the plain no-board line, not a SKIP
      gh-sync: SKIP — MUTANT: no github.board configured — station writes are not attempted

FAIL  no board configured: open still recorded T-02's issue — the lifecycle ran, not skipped
      {'feature_id': 'FEAT-09-no-board', 'status': 'Building', 'github': {'milestone': 7, 'parent': 40, 'parent_origin': 'created', 'attached': [], 'issues': {}}}
ok    no board configured: close-task exits 0
ok    no board configured: no item-edit call is ever made
FAIL  no board configured: close-task actually closed T-01's issue — the lifecycle ran
      ['auth status\x01', 'auth status\x01']

3 FAILED
exit=1
```

All three of the new/repaired assertions FAIL under the mutant, and only those three (the two
pre-existing checks in the block that don't depend on lifecycle-continuing — `close-task exits 0`
and `no item-edit call` — still pass, as expected, since `skip()` also exits 0 and a skipped run
also makes no `item-edit` call; that is exactly F-3's point about the old assertion set).

**Revert:** restored `print(...)` verbatim. Verified:
```
$ sha256sum .claude/skills/harness/bin/gh-sync.py
1eed5977ae07881426855e106ef9962876c98a90c336faa4c219f9c4d871f4f7  .claude/skills/harness/bin/gh-sync.py
```
Matches the pre-mutation hash exactly — no net change from the mutation cycle.
`git status --porcelain` shows only the intended F-1/F-2/F-3 diffs against both files (checked
after the revert), nothing from the mutation itself since it was reverted to the identical text.

**GREEN — re-ran isolated repro** after revert: all 6 checks pass (`ALL PASSED`, exit 0).

## Task verify — run and reported

```
$ python3 .claude/skills/harness/bin/test-gh-sync.py
```
Full output tail:
```
ok    no board configured: open exits 0
ok    no board configured: prints the plain no-board line, not a SKIP
ok    no board configured: open still recorded T-02's issue — the lifecycle ran, not skipped
ok    no board configured: close-task exits 0
ok    no board configured: no item-edit call is ever made
ok    no board configured: close-task actually closed T-01's issue — the lifecycle ran

ALL PASSED
```
Exit status: 0.

Cross-checked against T-03's `verify:` in `.harness/features/FEAT-18-board-truth/plan.yaml` via
`harness_yaml.load_plan` — `'python3 .claude/skills/harness/bin/test-gh-sync.py\n'`. Matches the
dispatched command verbatim (trailing newline only).

## Additional runs

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind integration
106/106 checks passed.
PASS test-factory-integration.py
```
Exit status: 0.

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit
ALL PASS (test-validate-feature-json.py)
all pass (test-gh-board.py)
8/8 cases passed. PASS test-branch-create-gate.py
```
Exit status: 0.

## Must-not-regress — re-verified in source, all intact

- No station write on `gh()` — unchanged, `gh()` body untouched (`gh-sync.py:102-107`).
- Zero retry constructs anywhere in the file — no new loops/retries added; only docstring prose and
  test assertions changed.
- Parent write ordered before the close, with its comment — `cmd_close_task` body untouched
  (`gh-sync.py:581-588`); docstring now also states this ordering explicitly (F-2 fix), consistent
  with the code.
- `derive_station(plan_doc)` called with one argument — `_apply_parent_rule` untouched.
- Presupposition comment at `gh-sync.py:161-165` — untouched, verified present verbatim.

## Files touched

- `.claude/skills/harness/bin/gh-sync.py` — module docstring only (lines ~19-33); no code changed
  net of the reverted mutation.
- `.claude/skills/harness/bin/test-gh-sync.py` — three new assertions in the `no board configured`
  block (~lines 1197-1210).
