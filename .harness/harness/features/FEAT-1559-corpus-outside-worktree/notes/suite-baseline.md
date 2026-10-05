# Suite baseline — FEAT-1559 — T-01 (2026-10-04)

## Planning baseline

- **Planning baseline SHA:** `652e70d4` (immutable; the seed's planning commit). It is the
  planning baseline only. SC-11's one-time receipt resolves its own pre endpoint as
  `merge-base(review_sha, main)` when it runs, and does not use this SHA.
- **Branch base at T-01:** `e8d868f7`, the merge-base with `origin/main` after `main` was merged
  in to clear the plan-check DEVIATION.
- **BRIEF condition:** approved by mruangutai on 2026-10-04; plan station `ready`. Operator ruling 3
  supersedes the FEAT-57 receipt / T-19 prerequisite (#1655 closed as abandoned).
- **Executed** directly in the main session under DEC-174. Host: git 2.54.0 (Apple Git-157),
  macOS arm64.

## Red before implementation (bootstrap)

Both production files (`feature_corpus.py`, `worktree-state.py`) are new. Before they existed,
each T-01 test was run with the two files moved aside:

| Command | Exit | Failure |
|---|---|---|
| `python3 tests/unit/test-worktree-state-rules.py` (then `tests/unit/test-worktree-state.py`) | 1 | `ModuleNotFoundError: No module named 'feature_corpus'` |
| `python3 tests/unit/test-feature-corpus.py` | 1 | `ModuleNotFoundError: No module named 'feature_corpus'` |
| `python3 tests/integration/test-worktree-state.py` | 1 | No JSON from a missing command; every case fails, e.g. `test_mixed_a_b_c_refuses_and_mutates_nothing`, `test_real_edit_in_the_active_feature` |

As the plan states, an absent command is a bootstrap red only. It does not prove each predicate.
The predicates are instead pinned by named negative cases that go red against wrong
implementations; three of those turned up during the build:

- **Repair without an index refresh.** `git sparse-checkout reapply` leaves a present hidden file
  whose stat data is stale ("not up to date … left despite sparse patterns"). Red:
  `test_class_b_identical_materialised_file` (exit 4 after repair). Fixed with
  `git update-index -q --refresh` before `reapply`, which is safe because class C is already
  excluded.
- **`set` with an unchanged cone.** Git treats it as a no-op, so a correct-cone checkout with a
  materialised file never converged. Repair now runs `set` only when the cone differs, then
  always `reapply`.
- **A cone without `.harness`** (`set --cone src`). The scan raised instead of reporting the cone
  break. Red: `test_wrong_cone` (exit 2). Fixed: an absent `.harness` reaches no feature directory.

One expectation was corrected to match git's behaviour rather than changing code. Git 2.54 clears
the skip bit of a hidden file present on disk when it loads the index
(`sparse.expectFilesOutsideOfPatterns`), so a rewritten hidden file reports `skip-bits` (4)
ahead of `materialisation` (7).

## Green (T-01 verify)

| Command | Exit | Cases | Wall |
|---|---|---|---|
| `python3 tests/unit/test-worktree-state-rules.py` | 0 | 15 | 0.1 s |
| `python3 tests/integration/test-worktree-state.py` | 0 | 23 | ~20 s |
| `python3 tests/unit/test-feature-corpus.py` | 0 | 13 | 0.5 s |

No host worktree is touched: every subject is a worktree of the synthetic owner in
`tests/integration/f58_sparse_fixture.py`, under a private temporary directory, with system and
global git config disabled.

## Amendment during T-01

`tests/unit/test-worktree-state.py` was renamed `tests/unit/test-worktree-state-rules.py`, because
`run-unit-tests.py` refuses a test basename that appears in both `tests/unit` and
`tests/integration` (MISCONFIGURED). The rename went through `plan-merge.py amend` on T-01 `files`
and `verify`, recorded as an amendment judgement with that reason.
