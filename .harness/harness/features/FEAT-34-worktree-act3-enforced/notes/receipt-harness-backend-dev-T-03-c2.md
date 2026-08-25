# T-03 (second rework, c2) — split `root` into two resolutions

## BLUF

`root` in `post-merge-sweep.sh` used to answer two different questions with one value:
"where do the bin scripts live" (BIN_DIR-derived, correct for locating `gh-sync.py`/
`feature-worktree.py`) and "which checkout holds the landed feature dir" (wrong — that
same value can BE a linked worktree carrying its own, possibly divergent, copy of the
feature directory). Split into two named values; `feat_dir` now uses only the second.
T-03's mandated verify passes.

## What changed

- `.claude/skills/harness/bin/post-merge-sweep.sh:65-92` (new function
  `_resolve_main_checkout_root(root)`): runs `git worktree list --porcelain` with
  `cwd=root` — the BIN_DIR-derived root, **never `os.getcwd()`** — and returns porcelain
  index 0 (the main checkout). This is INV-25's own precedent
  (`check-state.sh:1138-1143`) and the same index `worktree_terminal.classify` already
  keys on (`worktree_terminal.py:194-203`) — one rule, two uses, no second rule invented.
- `main()` (`post-merge-sweep.sh:~199-212`): resolves `main_checkout_root` right after
  `root`, prints it unconditionally (`"post-merge-sweep: resolved main checkout root:
  <path>"`), and returns 0 if it is `None` (same never-abort contract as
  `_resolve_repo_root`). `classify(root)` still receives the BIN_DIR-derived `root` —
  its own contract already handles `root` being a linked worktree correctly (skips index
  0, classifies `root` itself as a genuine record when `root` is a linked worktree). Only
  `feat_dir` resolution needed splitting out.
- `_handle_record(rec, root, cwd_real)` → `_handle_record(rec, main_checkout_root,
  cwd_real)` (`post-merge-sweep.sh:~112`): the sole use of that parameter was
  `feat_dir = os.path.join(root, ...)` — now reads `main_checkout_root`.
- Comment at the old `post-merge-sweep.sh:121-123` (feat_dir derivation) rewritten to
  name `main_checkout_root` explicitly and point at the new function's docstring for the
  rationale, rather than asserting the (now false) claim that the BIN_DIR-derived `root`
  is "the MAIN checkout".

## Verify (verbatim, cross-checked against `plan.yaml:384-385`)

```
bash -n .claude/skills/harness/bin/post-merge-sweep.sh && bash .claude/skills/harness/bin/post-merge-sweep.sh --dry-run
```

Output:
```
post-merge-sweep: resolved repository root: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-34-worktree-act3-enforced
post-merge-sweep: resolved main checkout root: /Users/molchairuangutai/GitHub/harness
```
Exit 0 (checked via file redirect, not a pipe). This run — invoked from inside a linked
worktree — is itself a live demonstration of the split: the BIN_DIR-derived root is the
worktree; the main-checkout root is the actual `harness` checkout.

## Gates (all measured this run, not inherited)

| Gate | Result |
|---|---|
| `python3 .claude/skills/harness/bin/test-post-merge-sweep.py` | **47 PASS**, exit 0 (was 41; see T-04 receipt) |
| `python3 .claude/skills/harness/bin/test-hooks-install.py` | 29 PASS, exit 0 (unchanged) |
| `python3 .claude/skills/harness/bin/test-worktree-terminal.py` | 34 PASS, exit 0 (unchanged) |
| `.claude/skills/harness/bin/check-state.sh` | exit 0, zero `violation` lines (only pre-existing `note` lines, unrelated to this change) |
| `.claude/skills/harness/bin/run-unit-tests.sh` | exit 0, zero `^FAIL` lines, run twice independently for confirmation (2973-line and 2404-line full outputs) |

## `classify(root)` — which value it receives, and why

`classify(root)` still receives the **BIN_DIR-derived `root`**, not
`main_checkout_root`. `git worktree list` is repo-global (either value would enumerate
the same set of worktrees), but `classify`'s own contract (T-01 rework, restated at
`worktree_terminal.py:194-203`) depends on which checkout is passed as `root`: when
`root` IS a linked worktree, `classify` correctly turns `root` itself into a genuine
classified record rather than silently skipping it. Passing `main_checkout_root` instead
would defeat that — the running worktree would never be classified as itself, only ever
appear (if at all) as an unrelated entry in someone else's enumeration. `feat_dir` is the
only place that needed the second value.

## Open questions

- None blocking. Advisory: today's `run-unit-tests.sh` also exercises
  `test-validate-digest.py` inside the same process tree as three concurrent full runs;
  one of the three interleaved runs showed a transient 8/14 hook-case failure in that
  file, not reproduced standalone (14/14) or in either of the other two full runs
  (both `ALL PASSED`). This matches the dispatch's Q3-CLOSED ruling — flagged here only
  as an observation, not reopened.

## Files touched

- `.claude/skills/harness/bin/post-merge-sweep.sh`
