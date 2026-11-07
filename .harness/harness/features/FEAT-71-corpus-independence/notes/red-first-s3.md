# Red-first receipt — slice S3 (guard, boundary and digest fixtures)

Baseline pin: `4a05030d` (origin/main). Throwaway clone: `/private/tmp/feat71-base-s3`
(`git clone --no-local` + `checkout --detach 4a05030d`), removed after the runs.
Every run below had `CLAUDE_PROJECT_DIR` and `HARNESS_PROJECT_DIR` set to the tree it ran in.

## Simulated deletion

In the baseline clone every `.harness/harness/features/*` folder was deleted except the five
survivors that exist at the pin. FEAT-71-corpus-independence does not exist at `4a05030d`.
The survivors were BUG-20261006-fleet-planning-recovery, BUG-2141-dec174-main-orchestrator,
BUG-2161-abandon-source-tickets and FEAT-2037-product-document-guidance.

## A. Baseline test files, dead folders absent: no live-read dependency

| file | exit |
|---|---|
| tests/integration/test-dispatch-guard.py | 0 |
| tests/unit/test-harness-boundary.py | 0 |
| tests/integration/test-validate-digest.py | 0 |
| tests/integration/test-bash-write-guard.py | 0 |
| tests/integration/test-check-domain-claims.py | 0 |
| tests/integration/test-check-domain-grant.py | 0 |
| tests/integration/test-check-instruction-paths.py | 0 |
| tests/integration/test-gh-sync-start-task.py | 0 |
| tests/integration/test-plan-merge.py | 0 |
| tests/unit/test-factory-claim-mutation.py | 0 |
| `bun test tests/unit/omp-hooks.test.ts` | 137 pass, 0 fail |

**Why there is no red for the renames.** None of these files read a dead feature folder at
run time. Every dead id they used was a literal inside a temp-dir fixture, an in-memory
payload, or a digest text. They pass identically whether the folders exist or not. Renaming
those literals to synthetic ids (FEAT-8x/9x, BUG-9x) therefore cannot turn anything red. It
only removes the reuse of real ids as data.

`REVIEW_SHA` in test-validate-digest.py held FEAT-43's recorded `review_sha`. It was copied
by hand from FEAT-43's feature.json, so it was not a live read, and it is a git commit, so
deleting the folder does not remove it. Every case that resolves it already runs inside
`_hermetic_review_sha_repo`, which re-points it at a commit built in a fixture repo. The
constant is now the synthetic `"5eed" * 10`. Run B and the worktree run are green with it,
which proves no case resolved the ambient commit. No red is possible.

## B. New (worktree) test files copied into the baseline clone, dead folders absent

All 10 Python files exit 0. `bun test tests/unit/omp-hooks.test.ts`: 137 pass, 0 fail.

## C. The one behaviour change: era-exempt cases depended on dead-id data

These cases are in tests/integration/test-gh-sync-start-task.py:
- "T-04 era-exempt continues"
- "T-12 era-exempt trailing slash continues"

Both staged `BUG-1030-stale-anchor-write-hazard` and passed only because that dead id is
listed in `feature_schema.BUILD_ENTRY_ERA_EXEMPT`. Slice S1a deletes that mechanism, as Main
confirmed. To simulate the deletion, the baseline clone got `BUILD_ENTRY_ERA_EXEMPT = set()`
appended to `.claude/skills/harness/bin/feature_schema.py`.

The baseline test file (copied as `test-gh-sync-start-task-old.py`):

```
$ python3 tests/integration/test-gh-sync-start-task-old.py
exit=1
FAIL  T-04 era-exempt continues
FAIL  T-12 era-exempt trailing slash continues
```

The new test file, same patched baseline:

```
$ python3 tests/integration/test-gh-sync-start-task.py
exit=0
ok    T-04 absent receipt refuses
ok    T-04 BUG-named absent receipt refuses
ok    T-12 absent receipt with a trailing slash refuses the same way
ok    T-04 station discriminator
ok    T-04 recovery-required recover-terminal horn names the derived command
ALL PASSED
```

The era cases are deleted. The new T-12 case keeps the trailing-slash path discrimination
under the uniform rule: a no-receipt feature named with a trailing slash is refused exactly
like the bare path (exit 2, points at `gh-sync.py open`).

## D. Worktree runs (green)

| command | exit | summary |
|---|---|---|
| python3 tests/integration/test-dispatch-guard.py | 0 | 135 of 135 cases passed |
| python3 tests/unit/test-harness-boundary.py | 0 | ALL PASS |
| python3 tests/integration/test-validate-digest.py | 0 | ALL PASSED. |
| python3 tests/integration/test-bash-write-guard.py | 0 | all PASS |
| python3 tests/integration/test-check-domain-claims.py | 0 | all PASS |
| python3 tests/integration/test-check-domain-grant.py | 0 | all ok |
| python3 tests/integration/test-check-instruction-paths.py | 0 | all PASS |
| python3 tests/integration/test-gh-sync-start-task.py | 0 | ALL PASSED |
| python3 tests/integration/test-plan-merge.py | 0 | PASS test-plan-merge.py |
| python3 tests/unit/test-factory-claim-mutation.py | 0 | KEY-COLLAPSE PROOF printed |
| bun test tests/unit/omp-hooks.test.ts | 0 | 137 pass, 0 fail |

## Files changed

- `.claude/skills/harness/bin/dispatch-guard.py`:
  - The comment no longer points at the dead FEAT-31 notes path.
  - The refusal's example line `FEAT-42-one-root-resolver` became the format `FEAT-NN-slug`.
- `.claude/skills/harness/bin/harness_boundary.py`: the docstring no longer spells the dead
  folder name `FEAT-32-concurrent-write-merge`.
- `.claude/skills/harness/bin/gh_cost_log.py`: the docstring path into the FEAT-29 notes
  became the bare-id provenance "FEAT-29's before-measurement".
- `.claude/skills/harness/bin/plan_merge/check.py` and `plan_merge/panel.py`: the comment's
  slugged `BUG-285-canonical-reader` became the bare id `BUG-285`.
- `tests/integration/test-dispatch-guard.py`:
  - Fixture ids FEAT-42/BUG-124/FEAT-495/FEAT-43/FEAT-44/FEAT-31 became FEAT-90..97 and
    BUG-92.
  - Two docstring pointers to the dead FEAT-32 notes were removed.
  - The BUG-124 comment was updated.
- `tests/unit/test-harness-boundary.py`: worktree and claim fixture ids FEAT-31/32/40/50 and
  BUG-1305 became FEAT-90..93 and BUG-94.
- `tests/integration/test-validate-digest.py`:
  - FEAT-01/02/09/63/64 and BUG-285/BUG-1898 fixture ids became FEAT-89..96, BUG-92 and
    BUG-97.
  - `REVIEW_SHA` became synthetic, and its comment block and the send-back-1 comment were
    rewritten.
  - The distill-path docstring now uses `<FEAT>`.
- `tests/integration/test-bash-write-guard.py`: FEAT-17 branch, BUG-1304 worktree and
  FEAT-495 fixtures became FEAT-94, BUG-91 and FEAT-93.
- `tests/integration/test-check-domain-claims.py`: BUG-1304, FEAT-01 and FEAT-495 fixtures
  became BUG-91, FEAT-92 and FEAT-93.
- `tests/integration/test-check-domain-grant.py`: the `features/FEAT-01/runs` path became
  `features/FEAT-90-fixture/runs`.
- `tests/integration/test-check-instruction-paths.py`: the landed-feature path into dead
  FEAT-23 became `FEAT-90-fixture-landed`.
- `tests/integration/test-gh-sync-start-task.py`:
  - The era-exempt cases were deleted.
  - A T-12 trailing-slash refusal was added.
  - "non-era" ids and labels were renamed.
  - FEAT-09/FEAT-24 fixtures became FEAT-89/FEAT-88.
- `tests/integration/test-plan-merge.py`:
  - The `notes_ref` fixture `research-BUG-285.md` became `research-BUG-9-x.md`.
  - The docstring's slug became the bare id.
- `tests/unit/test-factory-claim-mutation.py`: the docstring path into the dead BUG-1290
  notes became bare-id provenance.
- `tests/unit/omp-hooks.test.ts`:
  - The FEAT-43-long-run, FEAT-44-omp-context-advisory, FEAT-61 and FEAT-10 fixtures became
    FEAT-90..93.
  - The comment's slug became the bare id.
