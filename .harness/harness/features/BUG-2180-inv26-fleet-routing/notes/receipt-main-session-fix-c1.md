# BUG-2180 fix c1 — main-session-direct receipt (2026-11-07)

These are the must-fix items from validate run `2026-11-07-02-validate-validator` at `556a23ff` (`runs/2026-11-07-02-validate-validator/digest.md`). The owning dev is T-01's `execution_agent: main-session-direct` (DEC-174).

## Must-fix 1: case_x complexity (grade 1, CC48)

`tests/integration/test-check-state-inv26.py` now splits `case_x` into one function per scenario (`_x1_…` to `_x6_…`), built on three shared helpers: `_x_run`, `_x_has` and `_x_asked`. Every assertion was kept with the same meaning. The one exception is x.1's two-part check, "asked == {org/prod}" plus "numbers == [14,16,17]", which is now the single equivalent check `asked == {"org/prod": {14, 16, 17}}`.

Grading command: `code-grade.py --json <both test files>`. Every new function passes at grade 4 or 5 against a bar of 3, and `case_x` itself is now grade 4. The only failing record is `case_v` at grade 1. That function predates this change, is untouched by it, and is outside the diff.

The integration run (`python3 tests/integration/test-check-state-inv26.py`) exits 0 with 37 ok and 0 FAIL.

## Must-fix 2: DEC-217 unit floor

A T-01 `files` amendment, recorded through `plan-merge.py record-amendments` with digest `notes/amendment-T-01-unit-floor-2026-11-07.md`, added `tests/unit/test-check-state-inv26-routing.py` to the task. Advisor ruling Inv26RoutingAdvisor authorized it: production scope and task count are unchanged, and the signed BRIEF already named the floor.

The new unit test runs in-process. It uses the real `gh_board` projection, a recording `board_stations_for`, and a table-driven resolver. Every case calls the public `inv_26(ctx)`, so it grades behaviour and not helper names.

**Fail-first.** The test was run against a scratch bin whose `check_state/board.py` was taken from base `4a05030d`, with the same test file. It exited 1 with 7 behavioural FAILs:
- u.1 ×2: the owner read `[16, 17, 40, 41]`;
- u.2: owner sync off meant nothing was read;
- u.3: CANNOT VERIFY "not on the board" instead of the GitHub answer;
- u.4 ×2: the unresolved feature's numbers went to the owner;
- u.6: gh was probed with nothing in flight.

The controls u.3-healthy and u.5-offline passed at base, as intended. At the fixed tree it exits 0 with 9 PASS. Output is saved in this run's evidence.

The full unit suite (`run-unit-tests.py --kind unit`) passes: 58 files, OK, 19.8 s.

## Production code

`check_state/board.py` is unchanged since `554f219e`.
