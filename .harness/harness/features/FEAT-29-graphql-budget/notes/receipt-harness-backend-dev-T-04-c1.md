# Receipt — harness-backend-dev — FEAT-29 T-04 (c1)

## Result

`run_gh` (`factory_gh.py`) now detects a rate-limited gh failure by MESSAGE TEXT (never exit
code alone), queries `gh api rate_limit` once, and raises `GhError` whose message reads exactly:

```
GraphQL budget exhausted: <used> of <limit> points used, resets at <UTC ISO 8601 reset>
```

with a remedy naming both facts an operator needs (this is the GraphQL budget, not REST; REST's
own `<core.used> of <core.limit>`), and the original gh stderr preserved as `GhError.stderr`
(never swallowed). If the `rate_limit` query itself fails, the raised `GhError`'s message is
`"gh reported a rate limit and the budget could not be read"`, with the original rate-limit
stderr still preserved as detail.

## Files touched

- `.claude/skills/harness/bin/factory_gh.py` — new `_RATE_LIMIT_MARKERS`,
  `_looks_like_rate_limit`, `_is_rate_limit_query` (recursion guard), `_iso_utc`,
  `_rate_limit_budget_error`; `run_gh`'s non-zero-exit branch checks
  `_looks_like_rate_limit(r.stdout, r.stderr)` before its existing generic-error path.
- `.claude/skills/harness/bin/test-factory-gh.py` — three new sections after the existing
  `delete_ref` test: (1) budget-exhausted happy path, asserting GraphQL, the used/limit numbers,
  the reset UTC ISO 8601 timestamp, the REST-usage remedy fact, the preserved original stderr, and
  the exact two-call sequence (failing call, then `api rate_limit`); (2) the discriminator — an
  exit 1 carrying `"could not resolve to a Repository"` does NOT raise the budget message; (3) a
  rate-limit failure whose own `rate_limit` read also fails, asserting the "could not be read"
  message and that the original rate-limit stderr survives as detail.

## Recursion guard (item 3 in the dispatch)

`_is_rate_limit_query(argv)` returns True only for the internal `["api", "rate_limit"]` call.
`run_gh`'s detection check skips the budget path entirely when the FAILING call is itself that
query — so if `gh api rate_limit` itself fails with rate-limit-shaped text, it falls through to
the ordinary `GhError` path, which `_rate_limit_budget_error`'s own `except GhError:` then catches
and turns into the "could not be read" message. No second level of recursion is possible: the
inner `run_gh(["api", "rate_limit"], ...)` call short-circuits the guard on its own account.

## RED confirmed before implementation

Wrote the three new test sections first, ran the suite against the untouched module:

```
FAIL  run_gh: budget message names GraphQL
FAIL  run_gh: budget message carries used and limit points
FAIL  run_gh: budget message carries the reset UTC ISO 8601 timestamp
FAIL  run_gh: budget remedy names REST's own usage
FAIL  run_gh: queried rate_limit exactly once, after the failing call
FAIL  run_gh: budget-read failure names its own message, not the original rate-limit text
6 of 198 FAILING.
```

The "unrelated exit-1" checks were already green on the untouched module (expected — the current
code always preserves the original gh text and never mentions "GraphQL budget exhausted").

## GREEN after implementation

```
198/198 checks passed.
```

## `task_verify` — run exactly, verbatim from plan.yaml T-04

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Captured exit status into a variable (not read from `tail`), and counted `^FAIL ` lines across
the full output, per the dispatch's warning about `run-unit-tests.sh`'s own trailing
`N/N checks passed` line masking a red suite:

```
EXIT=0
FAIL count: 0
```

Tail of output: `19/19 cases passed.` / `PASS test-inject-expertise.py` (the runner's final two
lines). `task_verify: pass`.

## Mutation proofs (both pairs)

**Mutation 1 — detection on exit code alone (drop `_looks_like_rate_limit` from the guard).**

Applied: `if not _is_rate_limit_query(list(args)):` (text check removed).

Running the full `test-factory-gh.py` under this mutation does **not** cleanly redden only the
target check — it crashes the whole file with an uncaught `AssertionError` originating at an
EARLIER, pre-existing test (`run_gh: raises GhError on non-zero exit`, line 217), which queues
exactly one `Result` and was never designed to survive a second subprocess call now attempted for
every failing call. This is inherent blast radius from mutating a function every other test in the
file calls through — not a leaked-state fixture-isolation bug of my two new tests (no shared
mutable state between them and the earlier tests; `restore()` runs after each). Recorded honestly
rather than reported as a clean single-check redness.

To get the discriminating signal the task asks for, isolated the two target checks into a scoped
standalone probe (own `Result`/`recorder`, imports `factory_gh` directly, no dependency on the
other 190+ pre-existing tests):
`/private/tmp/claude-501/.../scratchpad/mutation-probe-t04.py`

```
ok    budget-message test: GhError raised with GraphQL budget headline
FAIL  unrelated-failure test: GhError raised WITHOUT the GraphQL budget headline
1 FAILING
```

Exactly the unrelated-failure check reddens; the budget-message check stays green (a real budget
failure still triggers the budget path — dropping the text check doesn't touch it, since the guard
was `and`-combined, not the sole gate).

**Reverted.** `sha256sum factory_gh.py` before mutation: `ff1cf1f57fd455b6dd996cb3c4eda8ac6235a038d0562c3cbfcb40f2d76825e8`. After revert: same hash. `git status --porcelain factory_gh.py` immediately after revert-and-hash-check showed no diff for that intermediate state (only the intended net T-04 changes remain staged as working-tree modifications afterward, confirmed at the end of the run).

**Mutation 2 — remove the budget message entirely, fall through to the raw generic error.**

Applied: deleted the `if not _is_rate_limit_query(...) and _looks_like_rate_limit(...): raise
_rate_limit_budget_error(...)` block from `run_gh`'s non-zero-exit branch.

Ran the same scoped probe:

```
FAIL  budget-message test: GhError raised with GraphQL budget headline
ok    unrelated-failure test: GhError raised WITHOUT the GraphQL budget headline
1 FAILING
```

Exactly the budget-message check reddens; the unrelated-failure check stays green (removing the
budget path only removes the budget behavior — the generic-error path it falls back to already
never mentions "GraphQL budget exhausted", so the unrelated case behaves as before).

**Reverted.** `sha256sum factory_gh.py` after revert: `ff1cf1f57fd455b6dd996cb3c4eda8ac6235a038d0562c3cbfcb40f2d76825e8` — matches the pre-mutation baseline exactly. Full suite re-run clean afterward: `198/198 checks passed.` `git status --porcelain` on `factory_gh.py`/`test-factory-gh.py` shows only the intended net T-04 diff (both files modified, no stray mutation artifact).

## No live `gh` call

Every test drives `factory_gh.subprocess.run` (or the recorder helper wrapping it) — no `gh`
binary invoked, no `check-state.sh` run, per the hard constraints. `gh_cost_log.py` /
`test-gh-cost-log.py` were not created (T-03 remains untouched, as instructed).
