# Receipt — BUG-1016 tests-efficiency (harness-dev-ops)

**BLUF: findings [].** No wasted work in `tests/unit/omp-hooks.test.ts` diff 8d79d63d..89b7d960 (+281/-4).

Read: `angle-efficiency.md`, `delete-first.md`, the actual diff, fixture (lines 179-387) and new block (1280-1550).

## Why empty
- The injected `runner` is an in-memory stub: `fixture()` builds a Map, an array and closures. There is no process spawn, file or network I/O. One `rootedHooks()` costs microseconds.
- The only repeated construction is `rootedHooks()` per test (14 calls) plus 6 in the "unusable or refused resolver answer" loop and 2 in "sibling runs". Each needs a fresh fixture on purpose: the validated-success cache and the `calls` ledger are per-run and asserted. Sharing would void the cache-isolation, call-count and sibling cases. Cost of a share would be correctness, savings sub-millisecond.
- `calls.slice(at)` / `.filter` ledger scans run over tens of entries. `structuredClone` runs 6 times on tiny inputs.
- The `fixture()` change adds one `cwd` field per call and one `if` per runner call. This is negligible and needed by the `cwd` assertion at the feature-root lookup.
- Full-suite runs at boundary steps are evidence, not waste. The T-01 verify (`python3 tests/unit/test-omp-hooks.py`) was not run, per contract.

Named BUG-1016 behavior changes: none.
