# T-01 backend-dev receipt — cycle 1

## Result

PASS — INV-26 now requires recorded `feature.json` `github.issues` before it queries or compares cards. Active features without mirrored issues are generically ineligible; eligible mirrored features still delegate their complete active card set to `gh_board.project`.

## Hypothesis and fail-first

Hypothesis: the prior T-01 change left the mirror-never-ran branch in INV-26, treating any active record without `github.issues` as board drift even though there is no recorded card projection to compare. Falsifier: an active no-mirror fixture would be silent before the production change.

After changing only `v.4` in `tests/integration/test-check-state-inv26.py`, I ran:

```sh
python3 tests/integration/test-check-state-inv26.py
```

It exited 1. The sole failing assertion was `(v.4) tasks in flight with an EMPTY issues map are ineligible for INV-26`; the checker emitted `VIOLATION INV-26 FEAT-X: tasks are in flight or finished (plan derives building) but feature.json records no mirrored issues...`.

## Focused regression

After the eligibility fix, the same runner exited 0. It passed v.4 and the paired factory/no-mirror cases v.11 and v.12, while preserving the active shared-projection cases v.6, v.6b, v.10, and v.T04-{ready,building,plan}.

## Signed verification

Executed exactly:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py
```

Exit 0. `test-gh-board.py` ended `all pass`; each six integration runners ended `ALL PASSED`. The canonical project state checker was not run because the orchestrator owns it.

## Files touched

- `.claude/skills/harness/bin/check-state.py`
- `.agents/skills/harness/bin/check-state.py` (hardlinked mirror of the T-01 checker)
- `tests/integration/test-check-state-inv26.py`
- `.harness/harness/features/BUG-1699-lifecycle-cards/observations/harness-backend-dev.md`
- `.harness/harness/features/BUG-1699-lifecycle-cards/notes/receipt-harness-backend-dev-T-01-c1.md`
