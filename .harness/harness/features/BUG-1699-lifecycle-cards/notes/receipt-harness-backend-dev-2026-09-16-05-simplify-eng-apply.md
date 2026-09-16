# T-01 simplify apply receipt

Apply remained: the dead `_derived`/`_statuses` branch formerly at `check-state.py:2305-2329` was removed. Control now proceeds from the terminal-station exemption directly to the recorded-card eligibility check. No assertions changed.

## Manual restoration block

```python
            _derived = _gb.derive_station(_pdoc)

            # A None derivation silences the PARENT claim ONLY. It used to `continue` here
            # and skip the whole feature, which took the per-task comparison with it — and
            # that comparison never needed the parent derivation, since project places each
            # task's card from that task's own status. The cost was exact: a plan with one task
            # `done` and
            # the rest `pending` derives None, so the mis-columned `done` card SC-05 names
            # went unreported. That is the ordinary window between two tasks, not a corner,
            # and every INV-26 fixture was single-task so the suite could not see it.
            # An absent status reads as the NOT-STARTED STATION (FEAT-41 T-04). The PLAN.md
            # corpus predates the field, so absence still has to mean something, and what it
            # means is `ready`.
            _statuses = [(_t.get("status") or "ready")
                         for _t in (_pdoc.get("tasks") or [])
                         if isinstance(_t, dict) and _t.get("id")]
            # THIS GUARD INVERTS UNDER THE RENAME IF IT IS COPIED LITERALLY (FEAT-41 T-04).
            # It read `not any(_s != "pending")` — true only when every task is unstarted. The
            # migration rewrote every such task to `ready`, so a literal rename would leave the
            # test comparing against a word no file carries: `_s != "pending"` is true for
            # EVERY task, `not any(...)` is false for every feature, and the skip would stop
            # firing everywhere at once. Written against the not-started station instead.
            if _derived is None and all(_s == "ready" for _s in _statuses):
                # Active feature phases now project cards even before task-local work begins.
                pass
```

## Signed T-01 verification

Command:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py
```

Result: exit 0 in 57.27 seconds.

| Script | Evidence |
| --- | --- |
| `tests/unit/test-gh-board.py` | `all pass` |
| `tests/integration/test-gh-sync-record.py` | `ALL PASSED` |
| `tests/integration/test-check-state-inv26.py` | `ALL PASSED` (including v.8/v.9 and active-phase cases) |
| `tests/integration/test-gh-sync-open.py` | `ALL PASSED` |
| `tests/integration/test-gh-sync-start-task.py` | `ALL PASSED` |
| `tests/integration/test-gh-sync-ship.py` | `ALL PASSED` |
| `tests/integration/test-gh-sync-abandon.py` | `ALL PASSED` |

Source touched: `.claude/skills/harness/bin/check-state.py`.

## Verbatim output
