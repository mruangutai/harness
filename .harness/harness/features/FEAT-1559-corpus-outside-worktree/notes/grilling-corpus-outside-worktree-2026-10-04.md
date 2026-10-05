# Grilling — the feature corpus outside the worktree (#1559) — 2026-10-04

Seed: `.harness/notes/seed-corpus-outside-worktree-2026-10-04.md`. Predecessor: FEAT-58, abandoned
2026-10-04; its record is archived on `origin/feat/FEAT-58-corpus-outside-worktree`.

## Destination
No checkout that holds harness records contains any feature directory except its own active
feature's. That covers a harness feature worktree, a fleet planning worktree and a validator pin
checkout. Every landed feature's records stay readable from the main corpus, and no check passes
silently because it sees fewer features than exist.

## Mission
mission: plan
reason: adds new enforcement (a post-checkout hook, a worktree-state.py --verify preflight in
check_state/, and a sparse layout on every checkout) across many files; only "cause known" holds.
confirmed-by: operator

## Settled
- Validator pin checkouts (`.claude/worktrees/.pins/`) are in scope → yes.
- Read path → **B**. Other features' records are read from the main corpus only: the owner root
  that tools resolve, `HARNESS_CONTROL_PLANE_ROOT` for agents. No symlink, and no reads through
  git. This replaces FEAT-58 D-09.
- In-progress features in other worktrees → **not readable**. Only landed records in the main
  corpus are. The merge gate's branch-uniqueness check therefore sees landed features only;
  accepted, because `feature-worktree.py create` already refuses an existing branch.
- Pins get the same sparse layout → yes. The active feature comes from the pin name
  `<feature>--<run-id>--<persona>`.
- Layout enforced by a git `post-checkout` hook running `worktree-state.py --repair`, whoever
  creates the checkout; gates call `--verify` → yes (FEAT-58 D-03 and D-10). There are four
  structural error exits, not six: the two symlink exits go.
- Existing worktrees → converted by one explicit `--repair` pass over each clean worktree. A dirty
  one is reported and skipped, never converted by force.
- FEAT-58 decisions carried over: D-05, D-06, D-11, D-13, D-14, D-15, D-16, D-17 as written; D-01,
  D-02, D-03, D-07, D-10, D-12 with updated file references. D-04 is dropped (moot under B). D-08
  is re-decided: derive the sparse list over every `.harness/*/features`, not one segment, and
  re-add the active feature from whichever segment holds it. D-09 is replaced by B.

## Not yet specified
- How the derived sparse list finds the active feature's segment in a fleet planning worktree,
  where the worktree sits under the `harness` segment but its record sits under the fleet
  segment.
- Whether BUG-1016's hook path rooting needs any change once reads go to the owner root, or only
  proof that it doesn't interfere.

## Out of scope
- Clone-on-write copies: the operator's 2026-09-09 ruling is "never materialised".
- Hardlink aliasing: #1638 (FEAT-58 D-14).
- The `gh-sync` loader dropping non-`T-NN` task ids: #2060.
- Reading records through git: rejected in favour of B, and forbidden in hooks by DEC-193.
- Removing stale worktrees: a separate manual cleanup. This feature converts worktrees; it does
  not prune them.
- Reading in-progress features from sibling worktrees: ruled out above.

## Facts I verified (so pm does not re-derive them)
All at `652e70d4`.
- `merge-gate.py:197` `feature_for` searches `ROOT/.harness/*/features/*/feature.json`, where
  `ROOT` is the script's own checkout. Read.
- `harness_boundary.linked_worktrees(owner_root)` lists `<owner_root>/.git/worktrees` and returns
  `[]` when given a worktree. `check-domain.py:2693` and `validate-digest.py:752` pass a root
  that can be a worktree. Read, and callers found by grep.
- `.claude/skills/harness/hooks/` holds only `post-merge`; `core.hooksPath` points there.
  Checked with `ls` and `git config`.
- Pin directory name: `pinned-checkout.py:58` `_pin_name` = `<feature>--<run-id>--<persona>`.
  Read.
- The only branch collision among records is still FEAT-02 / FEAT-03-subissue-mirror on
  `feat/harness-native-foundation`. Scanned every `feature.json`.
- `branch-create-gate.py` and `merge-gate.py` deny by printing a `permissionDecision` payload;
  `merge-gate` exits through `hook_guard(..., fail="closed")`. Read.
- `HARNESS_CONTROL_PLANE_ROOT` is injected by `inject-expertise.py:125` `_control_plane_block`.
  Read.
- Standing worktrees: 7 under `.claude/worktrees/`, each 48–61 MB, of which `.harness/` is
  41–51 MB. Measured with `du`.
