# T-01 fix receipt — c2

## Result

GC-01 is closed in code commit `968b791b6c8862750efba253ee9486da8f904078`: `tests/unit/test-gh-board.py` now emits its single `FAILURES` decision only after every assertion, including the active/terminal projection checks. The focused runner and signed T-01 gate pass. The configured integration matrix is currently blocked by an unrelated control-plane/worktree manifest divergence; it is recorded below without suppression.

## GC-01 fail-first evidence

Pre-fix negative-control command (with an intentionally false `check(...)` inserted after the former exit block):

```sh
python3 tests/unit/test-gh-board.py; printf 'EXIT:%s\n' $?
```

Verbatim relevant output:

```text
all pass
...
FAIL  c2 negative control: a late false assertion fails the runner — intentional false assertion
EXIT:0
```

This proves the false late assertion printed `FAIL` while the pre-fix runner exited 0.

Post-fix command, with the same deliberately false late assertion:

```sh
python3 tests/unit/test-gh-board.py; printf 'EXIT:%s\n' $?
```

Verbatim relevant output:

```text
...
FAIL  c2 negative control: a late false assertion fails the runner — intentional false assertion

1 FAIL
EXIT:1
```

The temporary negative control was fully removed before the green runs. Restored runner:

```sh
python3 tests/unit/test-gh-board.py
```

Result: exit 0; all named checks passed and the final line was `all pass`.

## T-01 verification

Executed exactly:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py
```

Result: exit 0; the unit runner ended `all pass` and each integration runner ended `ALL PASSED`.

## Configured matrix verification

```sh
.agents/skills/harness/bin/run-unit-tests.py --kind unit
```

Result: exit 0; pool reported 40 files and `9.61s wall`.

```sh
.agents/skills/harness/bin/run-unit-tests.py --kind integration
```

Result: exit 1; `test-check-plan-routes.py` failed six cases because the worktree `.harness/team-config.yaml` differs from the control-plane manifest at `/Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml` (an extra frontend dashboard-client domain grant). This path is outside T-01 ownership and was not changed.

## Changed paths

- `tests/unit/test-gh-board.py`
- `.harness/harness/features/BUG-1699-lifecycle-cards/notes/receipt-harness-backend-dev-fix-c2.md`
