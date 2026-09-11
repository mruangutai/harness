# GitHub mirror ids — FEAT-58-corpus-outside-worktree — recorded by hand, 2026-09-10

**DO NOT RE-RUN `gh-sync.py open` FOR THIS FEATURE.** It would create fourteen DUPLICATE
sub-issues. Its skip check reads the same empty map described below, so nothing would be skipped.

## Why this file exists

`gh-sync.py open` ran successfully at build entry and created everything on GitHub. It then lost
the id map locally. The cause is a defect in the receipt LOADER, not in the create path:

- `gh-sync.py:1159` writes `rec["issues"][task["id"]] = num` after every create, and saves.
- `gh-sync.py:609-614` reads that map back through `re.fullmatch(r"T-\d+", key)` — a HARDCODED
  task-id shape.
- This plan's task ids are `N-01 … N-14`, so **every key is silently dropped on the next load**,
  and `save_recorded` (`:929`) then writes the filtered — empty — map back to disk.

The proof that this is a defect rather than a contract is inside the same receipt: `attached`
(`:604-608`) carries the identical ids with NO id-shape filter and survived intact, while `issues`
did not. One record, two lists, one arbitrary regex.

**Consequences, all live:** `status ready` moves nothing (`:1594-1597`); `start-task` refuses every
task with "has no recorded issue — was `open` run?" (`:1482-1483`); `status review` moves nothing
(`:1629`); `ship` lands no card (`:2085`). The mirror is inert for this feature until the loader is
fixed. It is never a gate, so nothing is blocked from proceeding — but nothing on the board will
move either, and a card at `Ready` is therefore NOT available as proof of the signature.

**The fix is one regex, in `bin/gh-sync.py`, and it is main-session-direct work outside FEAT-58.**
Writing these ids into `feature.json` `github.issues` before that fix is pointless: the loader drops
them again on the next read.

## The mapping, from `open`'s own stdout at build entry

- milestone: **#66**
- parent: **#1641**
- source issue: **#1559**

| task | issue |
|---|---|
| N-01 | #1642 |
| N-02 | #1643 |
| N-03 | #1644 |
| N-04 | #1645 |
| N-05 | #1646 |
| N-06 | #1647 |
| N-07 | #1648 |
| N-08 | #1649 |
| N-09 | #1650 |
| N-10 | #1651 |
| N-12 | #1652 |
| N-13 | #1653 |
| N-14 | #1654 |

All thirteen were created AND attached to parent #1641; `feature.json` `github.attached` still
carries all thirteen ids, which is the surviving half of the receipt. `github.build_entry` reads
`opened`, so the Build-entry precondition is satisfied and `start-task`'s preflight will pass — it
is the per-task id lookup immediately after it that fails.

N-11 and SC-15 are deliberate id gaps (N-11 retired into N-10 at cycle 5; SC-15 struck at cycle 5).
