# Receipt — harness-dev-ops — T-12

## Task
FEAT-45 · T-12 · correct the team-count tripwire in
`.claude/skills/harness/bin/test-harness-yaml-corpus.py`.

## Cross-check
Re-extracted T-12's `verify:` block from `plan.yaml:1244-1245` and byte-compared it against the
block quoted in the dispatch: identical. No mismatch, proceeded.

## Changes (exactly two, both in the target file)
1. `TEAMS_EXPECTED = 2` → `TEAMS_EXPECTED = 3` (line 174 post-edit). The `check(...)` condition
   argument stays the literal `counts.get(TEAMS_ROOT) == TEAMS_EXPECTED`; its label still
   interpolates `{TEAMS_EXPECTED}`.
2. Replaced the nine stale `#` comment lines above the constant with a fresh, contiguous
   `#`-line block (no blank line before `TEAMS_EXPECTED = 3`) recording: the three expected
   filenames (`build.yaml`, `plan-panel.yaml`, `review.yaml`); that `plan-panel.yaml` was added
   by T-02 under the operator's 2026-08-30 signature (REQ-01..REQ-14), not drift; the ruling is
   **D-15** in this feature's `plan.yaml`; that FEAT-06's SC-05 is a completion snapshot,
   already and permanently met, never revisited — what was corrected is this constant; and that
   the count stays ASSERTED (not a label), and widening it **silently** is still forbidden.
3. (Permitted disambiguation, also applied) the `check()` label's trailing `(SC-05)` →
   `(FEAT-06 SC-05)`, since that reference belongs to FEAT-06 not FEAT-45.

## Verify — T-12's verify: block, run verbatim from worktree root
Command: the two-line `python3 .../test-harness-yaml-corpus.py && python3 -c "..."` block quoted
in the dispatch and independently re-extracted from `plan.yaml`.

Observed output: corpus test printed `16/16 checks passed.`, second command printed `OK`.
**Exit status: 0** (both commands succeeded; `&&` chain completed).

## RED proof
Temporarily set `TEAMS_EXPECTED = 4` (backed up file first) and reran the corpus test:

```
FAIL  .claude/skills/harness/teams holds exactly 4 team definitions (FEAT-06 SC-05)
      | found 3: ['build.yaml', 'plan-panel.yaml', 'review.yaml']
1 of 16 FAILING.
```

The count check is what failed, naming both the found count (3) and the directory listing.
Reverted from backup immediately after.

`git diff -- .claude/skills/harness/bin/test-harness-yaml-corpus.py` after revert (confirmed
clean, contains only the three intended edits above): **1 file changed, 16 insertions(+),
11 deletions(-)**.

## Full unit suite
Ran `.claude/skills/harness/bin/run-unit-tests.sh`, captured exit status and counted `^FAIL `
lines separately from the tail:

```
rc=0 fails=0
```

Grep of the full log confirms `PASS test-harness-yaml-corpus.py` (previously red, now green),
`PASS test-panel-findings.py`, and `PASS test-plan-panel.py` all present; no other script red.

## Scope
Touched only `.claude/skills/harness/bin/test-harness-yaml-corpus.py`. No team file added,
deleted or renamed. No other test, `run-unit-tests.sh`, plan, state, or approval fragment
touched. Tree left uncommitted.
