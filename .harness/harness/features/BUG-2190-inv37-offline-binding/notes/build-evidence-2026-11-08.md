# BUG-2190 T-01 build evidence (main session, DEC-174), 2026-11-08

## Commits

| Commit | Content |
|---|---|
| `c6bd42d2` | Signed plan. This is the baseline for production edits (full SHA `c6bd42d20fa9bf58e4c1dd3ede417caefc23a853`). |
| `4612447f` | Tests first: unit and integration regressions, committed red. |
| `0a3302f6` | Fix in `check_state/board.py` (`_inv37_local_repo`, `_inv37_repo`; `_inv37_feature` selects through them), plus the canonical-reader inventory row. |
| `655f71ae`, `df1fd837` | Unit test renamed to a unique basename. INV-37 row declares `gh:auth`. DEC-221 amendment with the index regenerated. |
| `907225c1` | Merge of origin/main (FEAT-71 corpus prune). The index was regenerated, and the layout was repaired with `worktree-state.py --repair`. |
| (this commit) | Integration controls i.10 and i.11 (SC-05). |

## Fail-first witnesses (unchanged `board.py` at `c6bd42d2`)

**Integration:** `python3 tests/integration/test-check-state-inv37-offline.py` exits 1. Output was captured with base `board.py` swapped in.

| Case | Base result | Base output |
|---|---|---|
| i.1, i.2 (SC-01) | FAIL | `invalid authoritative repository binding: product config unreadable: org/prod@main … gh api contents failed`. This is the exact #2189 CI failure, with the fake gh answering `auth status` 1 and refusing contents. |
| i.3, i.4, i.5 (SC-02) | FAIL | The same binding finding replaces the receipt/provenance findings. |
| i.9 (SC-05 mixed) | FAIL | The bound fixture is reported invalid. |
| i.10 (SC-05 legacy / sync-off) | FAIL | The bound fixture is reported invalid. |
| i.6 (SC-03), i.7 and i.8 (SC-04 online), i.11 (no-plan) | ok | Controls, unchanged. |

**Unit:** `python3 tests/unit/test-check-state-inv37-local-binding.py`, then named `-offline.py`, exits 1.

| Case | Base result | Base output |
|---|---|---|
| u.1 | FAIL | `log={'resolve': 1, 'product_config': 2}`: a remote read happened while offline. |
| u.2 ×3 | FAIL | A remote read was reached. |
| u.5 | FAIL | `resolve: 2`: the bound feature also went through the resolver. |
| u.3, u.4 | PASS | Controls. |

## SC-03 bypass mutant (throwaway, discarded)

`board._inv37_local_repo` was replaced by a mutant that returns `factory.repo` with no syntax or fleet check. Under that mutant, all four u.3 cases FAIL: `'not a repository'`, `5`, `''` and `'org/gone'` each became a receipt finding instead of an invalid binding. The real function gives 0 failures, and u.1 (the valid-bound twin) still passes.

## Green (HEAD)

- `python3 tests/unit/test-check-state-inv37-local-binding.py` exits 0 (14 PASS).
- `python3 tests/integration/test-check-state-inv37-offline.py` exits 0 (11 ok).
- The literal verify takes about 3 s wall time.
- `uvx pyflakes` on both tests is clean. Its findings for `board.py` are all pre-existing lines (unused `H/root/fpath` in untouched functions).
- `code-grade.py --base c6bd42d2 --head 0a3302f6 --json`: every changed function grades 4 or above. Production code: `_inv37_local_repo` and `_inv37_repo` at 4. Tests: 4 to 5.
- `check-plan-routes.py --canonical-reader-audit`: the only difference from base is the new row, which is now classified. The remaining output is environment-local (main-checkout plan paths).
- Related integration tests `test-check-state-records.py` (legacy INV-37 T-06) and `test-check-state-inv26.py` both exit 0.

## Live smoke

Covered by the Kaya PR #2189 rerun after merge. CI's tokenless gate is the real surface.
