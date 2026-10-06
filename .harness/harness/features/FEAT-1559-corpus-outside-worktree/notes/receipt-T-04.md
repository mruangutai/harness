# Receipt — FEAT-1559 T-04 (2026-10-05)

Executed directly in the main session under DEC-174.

## What changed

- **`hooks/post-checkout` (new)** and **`hooks/post-rewrite` (new)**: tracked, mode 100755.
  Each one runs `worktree-state.py --repair --checkout <git's top level>`, with these rules:
  - **Two roots.** The implementation is found four directories above the hook (`pwd -P`). The
    checkout repaired is git's own, from `git rev-parse --show-toplevel`. With an absolute
    `core.hooksPath` these are different checkouts, and the integration fixture uses exactly
    that configuration.
  - **Exit 0, always.** Every other outcome is reported on stderr:
    - not inside a working tree;
    - a missing or non-executable implementation;
    - a nonzero repair, with its output and "NOT converged";
    - a dirty-tree skip (exit 8: "layout repair SKIPPED … nothing was changed").
  - **A successful repair prints nothing**, because it runs after every checkout.
  - **Repair's stdin is `/dev/null`**, so it never consumes what git hands the hook.
- **`hooks/post-merge`**: repair first, on the same terms, then `post-merge-sweep.py "$@"` as
  before.
  - `exec` became a call, so a nonzero sweep is attributed ("post-merge-sweep.py exited N") and
    the hook still exits 0.
  - The sweep runs whatever repair did: on failure, when the implementation is missing, and
    outside a working tree.
  - The missing-sweep message is unchanged, on stdout.
- **Unchanged, as the intent requires:** `core.hooksPath` configuration, `feature-worktree.py`
  and `pinned-checkout.py`. No helper-specific hook was added.

## What git does on its own (measured on git 2.54, before the tests were written)

| Operation on a converged sparse worktree | Layout after |
|---|---|
| ordinary merge, `--squash`, `-s resolve/octopus/recursive/ours/subtree` | intact |
| rebase, `reset --hard`, cherry-pick, checkout, editing a hidden feature | intact |
| merge or rebase bringing in a NEW top-level directory | cone 3 + skip-bits 4: the directory stays hidden |
| `git read-tree HEAD` (an index rewrite) | skip-bits 4: hidden paths show as unstaged deletions (class A) |
| a merge after that index rewrite | intact: the merge re-applies the skip bits itself |
| `git sparse-checkout disable` | cone 3 + skip-bits 4 + materialisation 7 |

`git sparse-checkout set` and `reapply` fire no hook, so repair cannot recurse into itself.
Git exports no `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` to these three hooks (checked
for checkout, worktree add, merge and amend).

## Deviation from the plan text, with reason

The intent asks to "reproduce a merge touching a hidden feature that previously clears
skip-bits and leaves unstaged absent outside-cone paths (class A)". On git 2.54 a merge does
not do that: merges keep cone-mode skip bits, and they even restore bits an earlier index
rewrite cleared (table above). The cases that do break the layout are tested instead:

- **class A:** produced by `git read-tree HEAD` (seven ` D` entries). It is repaired by the
  first hook-firing operation that does not repair it itself, `commit --amend` (post-rewrite).
- **merge:** a merge bringing in a new top-level directory, which leaves the cone stale (3 + 4)
  without the hook.
- **rebase:** the same shape through post-rewrite.

The host-scale figures in the plan (3,337 paths deleted, 3,807 skip bits cleared) came from
FEAT-58's earlier layout and remain a one-shot measurement, not a fixture assertion.

## Red before implementation

Both test files ran against the tree before any shim was added or changed: `post-checkout` and
`post-rewrite` absent, `post-merge` sweep-only.

- **`tests/unit/test-worktree-state-hooks-rules.py`** (then `test-worktree-state-hooks.py`):
  exit 1, 11 failures and 13 errors.
  - Every `post-checkout` / `post-rewrite` case errors, because the shim does not exist.
  - Every `post-merge` repair case fails, because no repair runs.
  - The two not-tracked-executable cases fail.
  - The control passed: the sweep still runs when repair is missing (the old shim always
    swept).
- **`tests/integration/test-worktree-state-hooks.py`**: exit 1, 7 failures and 1 error, each red
  for its own hook. Operation cases converge their worktree explicitly first, so creation cannot
  mask them.

  | Case | Pre-change result |
  |---|---|
  | bare `git worktree add`, `feature-worktree.py create`, fleet planning create, `pinned-checkout.py add` | cone 3, "sparse-checkout is not enabled" |
  | merge with a new top-level directory | cone 3 (missing `newtop`) + skip-bits 4 |
  | rebase with a new top-level directory | cone 3 (missing `newtop`) + skip-bits 4 |
  | amend after an index rewrite | skip-bits 4 (7 entries) |
  | class C | `post-checkout` not found |

## Green

| Command | Exit | Cases |
|---|---|---|
| `python3 tests/unit/test-worktree-state-hooks-rules.py` | 0 | 12 (~3 s) |
| `python3 tests/integration/test-worktree-state-hooks.py` | 0 | 8 (~9 s) |

What the integration cases show:

- **Creation.** All four creators converge, recordless:
  - the cone holds `.harness/{harness,kaya}/features/<id>`, and no feature directory is on disk;
  - after the record is written in its already included path and committed, the checkout
    converges to that exact segment;
  - the fleet planning worktree sits in the `harness` worktree segment while its
    `artifact_segment` is `kaya`;
  - the pin keeps `_pin_name` naming (`FEAT-2-beta--r1--qa`) and holds only `harness/FEAT-2-beta`.
- **Merge.** It leaves a clean status and `--verify` 0 with `newtop/` present, and its output
  carries the sweep's "resolved repository root: <fixture owner>".
- **Class C.** An untracked file in a hidden feature directory makes `post-checkout` report
  "layout repair SKIPPED" and leave a byte-identical snapshot (work tree, index,
  `config.worktree`, sparse-checkout file, common config).

Existing tests over the same surface also pass: `test-hooks-install.py`,
`test-post-merge-sweep.py`, `test-check-state-worktrees.py` (INV-31),
`test-check-state-records.py`, `test-check-state-table.py` and
`test-checker-structure-locks.py`.

## Amendment

The plan named `test-worktree-state-hooks.py` in both `tests/unit` and `tests/integration`, a
basename `run-unit-tests.py` refuses (MISCONFIGURED). The unit file was renamed
`test-worktree-state-hooks-rules.py` through `plan-merge.py amend` on T-04 `files` and `verify`,
the same remedy as T-01 and T-02. No basename now appears in both kinds, in the plan or on disk.
