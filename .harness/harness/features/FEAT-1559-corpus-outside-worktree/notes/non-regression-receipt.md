# Non-regression receipt — FEAT-1559 (2026-10-05)

T-05's receipt half (SC-06, SC-11, SC-12; D-13): a one-time proof, executed once and recorded
here. It is not a collected test. Executed in the main session under DEC-174.

## Endpoints, frozen at execution

| Name | SHA | How resolved |
|---|---|---|
| code-final (`C`) | `69e3d81987b8a9d7676dbaf0f18674b8bf039579` | this branch's tip after SIMPLIFY and the T-06 ruling |
| resolved main | `e8d868f78a6ec43880598af5c5873f5daa8ba985` | `git rev-parse origin/main` after `git fetch origin main` |
| `pre_change_sha` | `e8d868f78a6ec43880598af5c5873f5daa8ba985` | `git merge-base C origin/main` |
| planning baseline | `652e70d4` | the baseline only (SC-11), not used as an endpoint |

**Why `C` and not `review_sha`** (operator ruling, 2026-10-05). `review_sha` can be pinned only
after every task is `done`, and a later `plan.yaml` write makes the pin stale (INV-33). So this
receipt runs at the code-final commit, and the seam commit pinned as `review_sha` follows it.

- Between `3dd9e02b` (SIMPLIFY) and `C`, the only path outside this feature's directory that
  changed is `.harness/README.md`'s conversion paragraph.
- Between `C` and `review_sha`, nothing outside this feature's directory changes. That is
  checked again when the pin is made, and recorded in STATE.md.

Every claim below therefore holds for `review_sha` too.

## Whole-feature diff, `pre_change_sha..C` (SC-11)

```
$ git diff --name-only e8d868f7 69e3d819 | grep -E '^\.harness/[^/]+/features/' | awk -F/ '{print $2"/"$4}' | sort | uniq -c
     23 harness/FEAT-1559-corpus-outside-worktree
$ ... | grep -v '^.harness/harness/features/FEAT-1559-corpus-outside-worktree/' | wc -l
0
```

The diff changes **no path under any other feature directory in any segment**.

## Main-corpus manifest bytes (SC-11)

The manifest is `git ls-tree -r <sha> -- .harness` restricted to feature directories other than
this one: mode, blob id and path for every file.

| Endpoint | Entries | sha256 (first 16) |
|---|---|---|
| `pre_change_sha` | 4635 | `aa1dcc2134e8e9db` |
| `C` | 4635 | `aa1dcc2134e8e9db` |

The owner's working tree, at HEAD `e8d868f7`, matches `pre_change_sha` for every other feature:
`git diff --stat e8d868f7 -- '.harness/*/features/' ':!<this feature>'` prints nothing.

## Full suites in a disposable full clone at `C` (SC-06)

| Field | Value |
|---|---|
| clone path / cwd / root | `/tmp/f1559-receipt-clone-TBn9/clone` |
| made by | `git clone --no-local /Users/molchairuangutai/GitHub/harness clone; git checkout --detach C` |
| HEAD | `69e3d81987b8a9d7676dbaf0f18674b8bf039579` |
| shallow / linked | `false` / no (`.git` is a directory) |
| `core.hooksPath` | unset: local config is not cloned, as the docs say |
| checkout class | `worktree-state.py --verify --json` → `plain-clone`, findings `[]`, no-op reason "not a linked worktree; a plain clone keeps the full corpus" |
| feature directories present | 116, the full corpus |

| Command | Exit | Files passed / failed | Wall |
|---|---|---|---|
| `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | 54 / 0 | 16 s |
| `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | 86 / 0 | 79 s |

CI workflow, checkout depth and runner selection are unchanged; the diff touches no
`.github/` path. No historical failure appeared, so no baseline exception is carried. The clone
was removed after this receipt was written.

## Real-owner checks, non-skipped (SC-12)

| Field | Value |
|---|---|
| command | `python3 tests/integration/test-corpus-real-owner.py -v`, from this worktree |
| worktree HEAD | `69e3d81987b8a9d7676dbaf0f18674b8bf039579` |
| owner root / HEAD | `/Users/molchairuangutai/GitHub/harness` / `e8d868f78a6ec43880598af5c5873f5daa8ba985` |
| owner corpus | 116 landed feature directories (floor > 70), 11 record-less, segment `harness` |
| callers | the owner root, and this linked worktree |
| probe pin | `.claude/worktrees/.pins/BUG-1016-worktree-relative-paths--f1559-61151--probe` at `e8d868f7`, made by `pinned-checkout.py add` and removed at teardown (0 `f1559` pins left) |

Raw output:

```
test_dirty_is_reported_and_a_structural_break_refuses (__main__.DisposablePin...) ... probe pin /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/BUG-1016-worktree-relative-paths--f1559-61151--probe at e8d868f78a6ec43880598af5c5873f5daa8ba985 (owner /Users/molchairuangutai/GitHub/harness)
ok
test_audited_names_equal_the_tracked_directories (__main__.RealOwner...) ... ok
test_check_state_passes_the_corpus_choke_point (__main__.RealOwner...) ... ok
test_a_correct_fixture_passes (__main__.TheEqualityRejectsMutants...) ... ok
test_a_staged_missing_directory_is_rejected (__main__.TheEqualityRejectsMutants...) ... ok
test_a_wrong_root_override_is_rejected (__main__.TheEqualityRejectsMutants...) ... ok
----------------------------------------------------------------------
Ran 6 tests in 10.185s
OK
```

No owner file and no live worktree was written. The only tree created was the probe pin, and it
was removed.

## What this receipt does not cover

SC-10's conversion manifest belongs to #2101, after merge (operator ruling, 2026-10-05).
`test-corpus-non-regression.py --conversion-manifest` validates that manifest when it exists.
