# Red demonstrations — BUG-1302 — 2026-09-05

All mutations below were temporary and absent from the final tree.

## T-01 — B-5 unreachable comparison

With the original `normalized in (".", "..")` comparison present and the new AST assertion active, `python3 tests/unit/test-suite-layout.py` exited 1 and printed:

```text
FAIL b5 structural: no unreachable dotdot comparison dotdot constants=2
```

After removing the unreachable comparison, the same check passes with one surviving `".."` constant in the earlier segment guard.

## T-02 — B-4 tautological conjunct

With the original `and not any(ch in trailing for ch in "*?[")` conjunct present and the new AST assertion active, `python3 tests/unit/test-suite-layout.py` exited 1 and printed:

```text
FAIL b4 structural: the tautological conjunct is absent any calls=2, wildcard constants=2
```

After removing the conjunct, the same check passes with one surviving `any()` call and one surviving `"*?["` constant.

## T-03 — B-6 fail-open branch

With the original `INAPPLICABLE` print branch present and the new branch-shape assertion active, `python3 tests/unit/test-suite-layout.py` exited 1 and printed:

```text
FAIL b6 message: the no-candidate failure names both remedies detail='', condition=None
```

The literal `CORPUS_BLIND_KINDS` fixture also returned no candidate, proving the branch is reachable. Replacing the print with `check(..., False, ...)` makes the structural check assert both repair phrases and the literal false condition.

## T-04 — B-14 unreadable tracked sources

With `_violations_callers` still calling unguarded `read_text()`, the fixture containing a tracked non-UTF-8 Python file caused `python3 tests/unit/test-suite-layout.py` to exit 1 and print:

```text
FAIL b14: unreadable tracked sources are reported, not raised UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

The fixture also contains a committed-then-deleted `deleted.py`. With the guard in place the function returns named entries for both `FileNotFoundError` and `UnicodeDecodeError` instead of raising.

## T-05 — B-8 narrow sentinel assertion

A temporary copy of integration case 2 inserted `python3 tests/integration/test-integration.py` immediately before the copied runner's `layout_out=` line while keeping the rogue tracked. With the widened clause, the case exited 1 and printed:

```text
FAIL git tracked rogue refused before sentinels PASS test-integration.py
```

Against the identical mutated runner, restoring only the old narrow clause made the case exit 0 and print:

```text
PASS git tracked rogue refused before sentinels
```

The pair proves the old assertion missed exactly the integration-sentinel-before-refusal failure that the generic prefix detects.
