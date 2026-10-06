# FEAT-1559 T-06 — conversion of standing worktrees (#2101)

This is a post-merge, main-session-direct run under DEC-174. It ran on 2026-10-05, after #2103 merged as `6866c3ee`.

## Endpoints

| Field | Value |
|---|---|
| owner | `/Users/molchairuangutai/GitHub/harness` |
| owner_head | `6866c3ee6f05b6f314d3bdf09a530600783ef088` (main after #2103) |
| review_sha | `f8a67546bcb42b6a5fd4327398615a4cfc07ae4d` |
| pre_change_sha | `e8d868f78a6ec43880598af5c5873f5daa8ba985`, which is `merge-base(review_sha, main)`, the same endpoint as T-05. It is not the planning baseline `652e70d4`. |

**Validation:** `python3 tests/integration/test-corpus-non-regression.py --conversion-manifest .harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/conversion-manifest.json` returns OK. It runs 6 tests, including the live re-verify of every converted checkout.

## Method

- **Inventory:** `git worktree list --porcelain` from the owner. There were 10 linked worktrees and no pins under `.claude/worktrees/.pins`. Fleet product repositories carry no feature records, and kaya's records live in this repo's `FEAT-01-kaya-platform` worktree.
- **HEAD-era precondition** (the #2101 amendment): a checkout is converted only if its HEAD tracks `.claude/skills/harness/bin/feature_corpus.py`. All other checkouts are `excluded` and named.
- **Each eligible checkout** went through these steps, with nothing removed, pruned, forced or stashed:
  1. snapshot;
  2. `worktree-state.py --repair` (main's copy);
  3. snapshot;
  4. if not refused, `--verify` and a second `--repair`, then a final snapshot.
- **What a snapshot records:** a digest over every working-tree file (raw bytes, symlinks as link text, `.git` excluded), plus digests of the worktree's index, its sparse-checkout file and its `config --worktree`. It also records the materialised feature-directory names and file counts.
- **Measurement is in file counts**, as signed. No `du` figure below is a claim of disk savings.

## Inventory and outcome

Directory and file counts are the materialised `.harness/*/features/*` entries on disk at the time of the run.

| Worktree | Branch | HEAD | Class | Outcome | Feature dirs | Feature files |
|---|---|---|---|---|---|---|
| `BUG-2037-readiness-contracts` | feat/BUG-2037-readiness-contracts | `2880a6148559` | planning-worktree | excluded | 117 | 4636 |
| `BUG-2102-panel-reader-slots` | feat/BUG-2102-panel-reader-slots | `6866c3ee6f05` | planning-worktree | skipped-dirty | 0 | 0 |
| `BUG-2104-guard-repo-binding` | feat/BUG-2104-guard-repo-binding | `c4d2be6e83c0` | planning-worktree | excluded | 116 | 4634 |
| `BUG-brief-approval-wording` | feat/BUG-brief-approval-wording | `9f06d31f5ec5` | probe | excluded | 91 | 3430 |
| `FEAT-01-kaya-platform` | feat/FEAT-01-kaya-platform | `47cc48693e4c` | planning-worktree | excluded | 117 | 4885 |
| `FEAT-1559-corpus-outside-worktree` | feat/FEAT-1559-corpus-outside-worktree | `8a0d83442f7f` | planning-worktree | converted | 1 | 67 |
| `FEAT-1774-observations-hindsight` | feat/FEAT-1774-observations-hindsight | `502dd5457f66` | planning-worktree | excluded | 100 | 3709 |
| `FEAT-2037-product-document-guidance` | feat/FEAT-2037-product-document-guidance | `df22ac7d1930` | planning-worktree | excluded | 117 | 4683 |
| `FEAT-2081-ci-shard-structure-audit` | feat/FEAT-2081-ci-shard-structure-audit | `ccb1732d4c7d` | planning-worktree | excluded | 117 | 4677 |
| `FEAT-46-decision-standard` | feat/FEAT-46-decision-standard | `ba21f0322118` | planning-worktree | excluded | 54 | 2535 |

**Per class:**
- **converted (1):**
  - `FEAT-1559-corpus-outside-worktree` was already converged by its own hooks.
  - Repair, verify and the second repair all exit 0, and the snapshots are byte-identical.
  - Its directory set is exactly its active feature, `harness/FEAT-1559-corpus-outside-worktree` (67 files before and after).
- **skipped-dirty (1):**
  - `BUG-2102-panel-reader-slots` has a post-1559 HEAD, with uncommitted work in `panel_findings.py` and others. Repair exited 8, and the before and after snapshots of each run are identical.
  - Its layout is already converged: dirty work is its only finding, which does not gate.
  - Another session is live in it: it gained one file between two runs of this pass, and that file was not written by this pass.
- **excluded, pre-1559 HEAD (7):** BUG-2037, BUG-2104, FEAT-01-kaya-platform, FEAT-1774, FEAT-2037, FEAT-2081 and FEAT-46.
  - Their branches have not merged main since FEAT-1559 landed, so tools at their HEAD still glob the checkout. Converting them now would recreate the fail-open #1559 removed.
  - `--verify` from main reports structural findings 3/4/7 on every one, and dirty work (8) on three: BUG-2037, FEAT-1774 and FEAT-2037.
- **excluded, probe (1):** `BUG-brief-approval-wording` names no feature, so it is a code-only probe and not record-bearing. It is never counted as converted.

**Feature-file totals:** before, 33,256 materialised feature files across the 10 worktrees. After, the same 33,256: the one converted checkout was already at its target, and every other checkout was left untouched by design. The reduction arrives as each excluded branch merges main and its `post-merge` hook converges it.

**Main corpus:** the owner's `.harness/` digest (`64e8165a…`, 5575 feature files) is identical immediately before and after a full rerun of this pass. The pass invokes repair only on linked worktrees.

**Which run is committed:** the manifest is from the first validated run. The rerun used for the owner bracket saw BUG-2102's bytes change between its snapshots while repair exited 8, which refuses before it mutates anything. The changed files were that session's own work: `panel_findings.py`, `plan_merge/panel.py`, `test-plan-merge.py`, fresh `__pycache__` and its in-flight claims file. A live session's edits are not evidence about repair.

## Consequence and recovery for each skipped or excluded checkout

A skipped or excluded checkout stays on its old, fully materialised layout. Its consequence depends on the case:
- **Excluded pre-1559:** nothing changes until the branch merges or rebases onto main. From then on, `worktree-state.py --verify` reports structural findings 3/4/7, which refuse check-state and the corpus gates. Dirty work alone (8) does not gate.
- **The merge itself converges it** through the tracked `post-merge`/`post-rewrite` hook, provided the tree is clean.
- **Dirty at that moment** (most standing worktrees are): the hook says so and changes nothing.

**Recovery, for any of these:**
1. Preserve the work by committing it, or by `git stash -u` so untracked files are included.
2. Run `worktree-state.py --repair --checkout <path>`.
3. Run `worktree-state.py --verify --checkout <path>`; it must exit 0.
4. Rerun the refused audit or gate.
5. Restore the stash, then recheck with `--verify`. If structural debt returns, repeat from step 1.

Never force a repair, prune a worktree or erase user work. `BUG-2104-guard-repo-binding` and `FEAT-1559-corpus-outside-worktree` have merged; removing their worktrees is the owner's call, and out of scope here.

## Not done here, by scope

There was no forced dirty repair, no stale-worktree removal, no rewrite of the corpus history, no symlink provider and no scaffold cleanup. The 48–61 MB logical sizes of the standing worktrees motivated the feature but are not conversion evidence.
