# T-01 backend-dev receipt

## Result

PASS — `gh_board.project` is the sole feature-phase projection. Active `plan`, `ready`, `building`, and `review` project every unique recorded source issue, parent, and non-abandoned task to the active station. Terminal and absent-phase behavior remains task/terminal-specific. `status` records locally before outbound writes; a missing board or disabled sync is local-only; each outbound `BoardError` is reported and later cards continue. INV-26 consumes the same projection. `start-task` retains its task-start write rather than becoming another feature-phase projection.

## Fail-first proof

Before production changes, I ran:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py
```

It exited 1 in the record runner (so the `&&` chain did not reach INV-26). The new unit cases failed for all four active phases: the old projection returned mixed task-local stations such as `{11: 'building', 12: 'building', 13: 'ready', 91: 'building'}` instead of the requested feature station. The record runner reported 10 failures, including no plan/building projection writes, omitted source/parent cards, sync-off skipping local recording, and no later-card continuation after a failed write.

## Signed verification

Executed exactly:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py
```

Result: exit 0, wall time 60.64s. Every runner printed its passing terminal marker (`all pass` for the unit runner; `ALL PASSED` for each integration runner). No runner emitted a discovery or assertion count. Relevant observed assertions included exact de-duplicated active projections, local-only no-board/sync-off status, per-card failure continuation, source-card INV-26 violations, terminal/abandonment behavior, and start-task's independent Building write.

## Files changed for T-01

- `.claude/skills/harness/bin/gh_board.py`
- `.claude/skills/harness/bin/gh-sync.py`
- `.claude/skills/harness/bin/check-state.py`
- `tests/unit/test-gh-board.py`
- `tests/integration/test-gh-sync-record.py`
- `tests/integration/test-check-state-inv26.py`
- `tests/integration/test-gh-sync-start-task.py` — updated the affected status assertion to require the parent in the complete active projection.
- This receipt.

No T-02 through T-05 implementation, plan, or BRIEF content was changed by this task. No HOW amendment was necessary.
