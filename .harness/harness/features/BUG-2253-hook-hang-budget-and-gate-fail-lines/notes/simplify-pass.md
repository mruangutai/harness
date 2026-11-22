# Simplify pass — BUG-2253 T-01

Four read-only reviewer angles (reuse, simplification, correctness, altitude) over `git diff 3769919f 7f62b2d3 -- .claude tests`.

## Applied

| Finding | Angle(s) | Change |
|---|---|---|
| The `FAIL `/`MUTATED ` prefix match also listed per-case `FAIL <label>` lines echoed from a failing file's output | simplification, correctness | The gate matches only run_pool's one-token `(?:FAIL\|MUTATED) \S+` line. The buried case now carries a `FAIL  [x] some case: detail` line that must stay unlisted |
| The block probe's `ready` and whole-run `elapsed < 1.5` checks would flake under the host load this patch addresses | simplification, correctness | Only the real budgeted call is timed (`spent`), so setup and pre-call load no longer count. `ready` is the watchdog's pid channel, not a pass condition: `TimeoutExpired` already proves the child was alive at the budget. The signed budget + 0.5s bound stands |
| The hand-rolled globals rebinder silently added a misspelled name | reuse, simplification | `mock.patch.multiple` (raises on an unknown name). The budget alone is rebound with `create=True`, so a tree without the constant fails per site instead of crashing the group |
| The duplicated "other call" double | reuse, simplification | One `_bug2253_doubles(target, budgeted)` |
| Duplicated write+chmod, and unclosed `open().write()` | reuse | `_bug2253_executable` over `_write_verification_brief` |
| Docstrings: the drivers' return shape, the watchdog's role, the "passing control" claim, and an exception class used as a sentinel | altitude | Corrected. The sentinel is gone with the rebinder |

## Declined

- Dropping the second rebound value (0.10): kept, because the signed intent names both 0.05 and 0.10.
