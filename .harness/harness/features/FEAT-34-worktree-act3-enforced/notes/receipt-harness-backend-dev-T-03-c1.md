# Receipt — harness-backend-dev — T-03 (rework, combined with T-04)

## BLUF

`_resolve_repo_root()` in `post-merge-sweep.sh` no longer derives the repository root from
`git worktree list --porcelain` run with `cwd=os.getcwd()`. It now derives root purely from the
sweep script's OWN on-disk location — `BIN_DIR` walked up the same four path segments
(`.claude/skills/harness/bin`) the T-11 shim already walks from its own location. The caller's cwd
— inside the repo, inside a linked worktree, or entirely outside any git repository — can no
longer change what root resolves to. This closes the defect the operator measured: run from cwd
`/`, outside the repository, the sweep used to print "could not resolve the repository root via
`git worktree list` — nothing to sweep" and do nothing, defeating T-11's own `$0`-based resolution.

## What changed

`.claude/skills/harness/bin/post-merge-sweep.sh`:
- `_resolve_repo_root()` rewritten: no `subprocess`/`git worktree list` call at all. `root =
  os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BIN_DIR))))`, returning `None`
  only if that path is not a directory (a broken installation, never a cwd property).
- `main()` now prints `post-merge-sweep: resolved repository root: {root}` unconditionally once
  root resolves, ahead of `classify(root)` — this is the line T-04's new safety-belt assertions
  read back out of every fixture case (see the T-04 receipt).
- The "could not resolve" message's wording updated to match the new failure mode ("...from this
  script's own on-disk location...", not "...via `git worktree list`...").

No second resolution rule was introduced, no env-var override was added — one rule, derived from
the script's own location, per the operator's ruling. `classify(root)`'s own consumers (`feat_dir`
at the old `:128`, `classify(root)` at the old `:184`) are unaffected — they take whatever `root`
they're handed, and `classify` skips porcelain index 0 rather than keying on `root`'s identity
(confirmed at `worktree_terminal.py:203-205` — `classify` never compares any record's path against
`root` to decide the main-checkout skip; it only special-cases the first porcelain record).

## Verify — verbatim

Command:
```
bash -n .claude/skills/harness/bin/post-merge-sweep.sh && bash .claude/skills/harness/bin/post-merge-sweep.sh --dry-run
```

Output:
```
post-merge-sweep: resolved repository root: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-34-worktree-act3-enforced
```
Exit code: 0

Cross-checked verbatim against `plan.yaml` T-03's `verify:` block — identical string, no mismatch.

## Order of work (Iron Law honored across the combined T-03/T-04 dispatch)

1. T-04's new RED case (`case_cwd_outside_repo`, case (h)) and the full fixture-safety rework
   (see the T-04 receipt) were written FIRST, against this file UNCHANGED (the pre-existing
   cwd-based `_resolve_repo_root`).
2. The full suite was run against that unfixed script — case (h)'s "MEASURED DEFECT PROOF"
   assertion failed with the exact symptom the operator described (`post-merge-sweep: could not
   resolve the repository root via \`git worktree list\` — nothing to sweep`, worktree left
   standing, no milestone-close call reached `gh`). Verbatim RED output is in the T-04 receipt.
3. Only then was this file's `_resolve_repo_root()` rewritten.
4. Full suite re-run: all cases, including (h), GREEN. See T-04 receipt.

## Files touched

- `.claude/skills/harness/bin/post-merge-sweep.sh`

## Scope discipline

Only this file and `.claude/skills/harness/bin/test-post-merge-sweep.py` were touched
(`git diff --stat` confirms — exactly these two paths). No edit to `plan.yaml`, `feature.json`,
`STATE.md`, `check-state.sh`, or `test-check-state.py`. No commit made.
