# Fix c3 — FEAT-1559 (outside panel on PR #2103) — main-session-direct (DEC-174)

**Source.** After validate c3 passed, three outside reviewers looked at PR #2103:

- `reviewer` (correctness) returned six findings, each reproduced in a disposable fixture;
- `security-reviewer` returned two lows and one informational finding;
- `fable-advisor` (design) returned one medium plus a plan correction for #2101.

The operator approved one more round, recorded in `notes/answers-operator-2026-10-05-rework-raise.md` (3 rounds, 180 min).

Each fix below was red before it was applied: every new test failed against the code at `6c11ab62` and passes now.

| # | Finding | Fix | Regression test (red before) |
|---|---|---|---|
| 1 | high: `factory_claim` read other features' `plan.yaml` and `feature.json` in the local checkout, so from a sparse worktree it reported `no_plan` and found no issue map | `_record_path` resolves both through `feature_corpus.corpus_path` (the only `features_root()` caller) | `test-feature-corpus.py` `FactoryClaim` (red: `('no_plan', …)`, issue `None`) |
| 2 | high: a lossy clean filter made different bytes hash equal, so repair deleted bytes the index did not hold | `present_blobs` hashes RAW bytes (`hash-object --no-filters`); a type mismatch against the index is C | `test-worktree-state.py` `test_bytes_a_clean_filter_hides_are_class_c` (red: exit 3, bytes removed) |
| 3 | medium: an unchanged tracked symlink was hashed through its target, so it was falsely C | index entries carry the mode; mode-120000 entries are hashed from their `readlink` text | `test_an_unchanged_tracked_symlink_is_class_b` (red: exit 8); positive control `test_a_retargeted_tracked_symlink_is_class_c` |
| 4 | medium: `sparse-checkout list` C-quotes non-ASCII names, so the cone never verified | `unquote` decodes git's C quoting (octal escapes and `\"`, `\\`, `\t`, …) | `test_a_non_ascii_top_level_directory_converges_and_verifies` (red: exit 3) |
| 5 | medium: a branch-named worktree became a no-op `probe` once a rebase or bisect detached HEAD | `current_branch` falls back to `rebase-merge/head-name`, `rebase-apply/head-name` or `BISECT_START` | `test_a_branch_named_worktree_keeps_its_feature_mid_rebase` (red: `('probe', None)`) |
| 6 | medium: a deleted active directory was answered from the landed owner copy | `corpus_path` keeps the checkout's own feature local by identity (`checkout_feature`). `select` now shares `worktree_slot` with it | `test_a_missing_active_directory_is_missing_not_a_landed_copy` (directory-named and branch-named; red: owner path) |
| 7 | medium: the hooks printed "commit or stash" on every operation in a converged worktree with ordinary uncommitted work | `worktree-state.py --quiet-dirty` prints nothing when the only finding is dirty (the exit code is unchanged, per SC-07); all three hooks pass it and print only when there is output | `test-worktree-state-hooks.py` `test_ordinary_work_in_a_converged_worktree_draws_no_instruction` (red: the full report) |

**Test change.** `tests/unit/test-worktree-state-hooks-rules.py` `test_repair_runs_on_gits_checkout_not_the_install_root` used to pin the exact argv. It now asserts what it was written for: `--repair`, and the checkout passed to `--checkout`.

## Filed, not fixed (lows)

- #2107: `branch-create-gate` fails open on a `feature.json` that raises outside `FeatureJsonError`.
- #2108: repair walks through an untracked symlink planted in a feature-directory slot.

## Plan correction

#2101 is amended (issue comment): convert only checkouts whose HEAD tracks `feature_corpus.py`. Pre-1559 worktrees and pins are excluded and named in the manifest.

## Verification

Full suites, the canonical-reader audit, code-grade and check-state results at the fix tip are in STATE.md and in the commit that records this receipt.
