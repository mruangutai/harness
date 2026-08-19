# Receipt — harness-backend-dev — FEAT-29-graphql-budget T-03 c3 — FIX CYCLE (qa-matrix-gate FAIL)

## Verdict: gap closed. Test-only change — production code was already correct.

The gate's finding was exact: `with gh_cost_log.measured(args)` at BOTH wrap sites
(`factory_gh.py:151`, `gh-sync.py:115`) was asserted by nothing that drove the real wrapper.
Every existing case in `test-gh-cost-log.py` called `gh_cost_log.record()`/`measured()`
directly, bypassing the interface; `test-factory-gh.py` runs with `HARNESS_GH_COST_LOG=0` at
module scope, so its `run_gh` calls never exercise the recorder at all.

## Fix — 8 new checks in `test-gh-cost-log.py`, no production code touched

Added a `_counting_fake()` double standing in for the `gh` binary (patches
`gh_cost_log.subprocess.run`, which is the SAME module object `factory_gh.subprocess` and the
freshly `importlib`-loaded gh-sync module's `subprocess` resolve to, so one patch covers all
three call sites) and a `_load_gh_sync()` helper using the exact mechanism at
`test-gh-sync.py:890-891` (read-only, not edited).

Four cases, each driving the REAL wrapper function directly and asserting both the write and
the subprocess call count:

- `factory_gh.run_gh(...)`, `HARNESS_GH_COST_LOG=1` — 1 line written, 3 subprocess calls
  (counter, real, counter).
- `factory_gh.run_gh(...)`, variable genuinely unset (`os.environ.pop(...)`) — 0 lines, exactly
  1 subprocess call.
- `_ghs.gh(...)` (gh-sync.py, loaded via importlib), `HARNESS_GH_COST_LOG=1` — 1 line, 3 calls.
- `_ghs.gh(...)`, unset — 0 lines, exactly 1 call.

`test-factory-gh.py`'s module-scope `HARNESS_GH_COST_LOG=0` at line 25 is untouched.
`run-unit-tests.sh` already lists `test-gh-cost-log.py` under `UNIT_SCRIPTS` (prior cycle) —
no change needed there this cycle.

## RED/GREEN

Production code (`gh_cost_log.py`, `factory_gh.py`, `gh-sync.py`) is unmodified by this cycle —
the dispatch is explicit that this is a coverage hole, not a code defect, and `git diff` on
those three files is empty both before and after. The new checks are GREEN against the
already-correct code on first run (24 baseline + 8 new = 32/32). "RED" here is proven by the
three mutations below, which is the applicable proof shape for a test-only fix (P-07).

## Mutation proof — three mutations, each on a named check, none an abort

Hashes recorded before any mutation:
- `gh_cost_log.py`: `b5d24cea70dcdf0eeadc097ae51faaea19f478fc8c82ad78f7f50e62ff198f5e`
- `factory_gh.py`: `110d07c7053e3ff627c818504174a7ce4c271b0cf37eae9355101f5cfb46c252`
- `gh-sync.py`: `10c0fe13cded6ae63fe2504db28c1fc021b1ea2a74dd5bd42e7198dc280dbd6e`

**Mutation 1 — deleted the `with` block at `factory_gh.py:151`** (replaced with `if True:` and
dropped the now-orphaned `_cost.returncode = r.returncode` line, so the mutation aborts nothing
and stays a clean redden). Predicted: factory_gh ON check fails. Result: **reddened, exactly as
predicted**, exit 1, suite ran to completion (32 tallied):
```
FAIL  factory_gh.run_gh wrap site, ON: one line written for the wrapped invocation — lines=[]
FAIL  factory_gh.run_gh wrap site, ON: three subprocess calls (counter, real, counter) — calls=[['gh', 'issue', 'view', '1']]
2 of 32 FAILING.
```
Reverted. `sha256sum factory_gh.py` = `110d07c7...` (matches). `git diff --stat factory_gh.py`
empty.

**Mutation 2 — deleted the `with` block at `gh-sync.py:115`.** Predicted: gh-sync ON check
fails. Result: **reddened, exactly as predicted**, exit 1, suite ran to completion:
```
FAIL  gh-sync.py gh() wrap site, ON: one line written for the wrapped invocation — lines=[]
FAIL  gh-sync.py gh() wrap site, ON: three subprocess calls (counter, real, counter) — calls=[['gh', 'issue', 'view', '1']]
2 of 32 FAILING.
```
Reverted. `sha256sum gh-sync.py` = `10c0fe13...` (matches). `git diff --stat gh-sync.py` empty.

**Mutation 3 — deleted `not _enabled() or` from `gh_cost_log.py:157`** (leaving
`if is_counter_call(argv):`). Predicted: an OFF call-count check fails (the guard is now bypassed
for a non-counter argv even when disabled — `measured()` reads the counter twice and calls
`record()`, which still suppresses the WRITE via its own separate guard at `:112`, but the
subprocess call count rises from 1 to 3). Result: **reddened, exactly as predicted, both sites**
(the guard is shared code), exit 1, suite ran to completion:
```
FAIL  factory_gh.run_gh wrap site, OFF: exactly one subprocess call (the real call only) — calls=[['gh', 'api', 'rate_limit', '--jq', '.resources.graphql.used'], ['gh', 'issue', 'view', '1'], ['gh', 'api', 'rate_limit', '--jq', '.resources.graphql.used']]
FAIL  gh-sync.py gh() wrap site, OFF: exactly one subprocess call (the real call only) — calls=[same shape]
2 of 32 FAILING.
```
This is the exact vacuity the dispatch named: the write stayed absent (record()'s own `:112`
guard still fires), so an OFF assertion scoped to the write alone would have stayed green.
Only the call-count assertion catches it. Reverted. `sha256sum gh_cost_log.py` = `b5d24cea...`
(matches). `git diff --stat gh_cost_log.py` empty.

All three mutations produced a trailing "N of 32 FAILING." line — the suite ran to completion
each time, never an abort (B-1's property does not apply to this file).

## `.harness/logs/gh-cost-2026-08-19.jsonl` — untouched throughout

Before any work this cycle: 39504 bytes, 168 lines, sha256
`7f8ae55288af9d5da39e2ebd5355c341b45668bd6e863ebe5a2743c5a6d5a563`. After all mutation cycles
and both final suite runs: identical byte count, line count, and hash. Every new case redirects
`factory_config.harness_root` to a `tempfile.TemporaryDirectory()` and asserts the redirect took
effect before trusting it (`redirect()`, matching every existing case in this file). Did not run
`check-state.sh`. Made no live `gh` call.

## task_verify

`task: T-03`. Verify string cross-checked against `plan.yaml` T-03 (lines 265–266) — matches the
dispatch's quoted string exactly: `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`.

Expected PASS count computed BEFORE running: prior baseline 164 (per `qa-matrix-gate.md`'s
measured run) + 8 new checks = **172**.

- `--kind unit`: exit 0, **172 PASS / 0 FAIL** (18 scripts) — matches the predicted count exactly.
  `task_verify: pass`.
- `--kind integration` (test_matrix gate requirement for `change_type: feature`, not the plan's
  `verify:` string): exit 0, **90 PASS / 0 FAIL** (12 scripts) — unchanged from baseline, as
  expected (no integration-kind file was touched: `test-gh-sync.py` is on the LEAVE LIST and was
  not edited).

## Anomaly during this cycle — transient, resolved, re-verified

After the mutation-3 revert, my tooling twice reported `gh_cost_log.py` "changed on disk since
last read" showing the guard back in its mutated (defect) form — once matching mutation 3
exactly, once again after a fresh check. Each time, an immediate independent `sha256sum` +
`git diff` check showed the file WAS actually correct on disk (hash `b5d24cea...`, empty diff);
one `Edit` attempt hit a stale-read guard and was retried after a fresh read. Final state, checked
last and reported above, is unambiguous: all three production files hash-match their pre-cycle
baselines, `git status --porcelain` shows none of them modified, and both suites are green. Not
acting further on this beyond the final verification already run below — flagging only so a
reviewer knows this was checked twice, not assumed once.

## Scope discipline

Only `test-gh-cost-log.py` (one of T-03's six declared files) was changed —
`git status --porcelain .claude/skills/harness/bin/` shows exactly that one file, modified.
`gh_cost_log.py`, `factory_gh.py`, `gh-sync.py`, `run-unit-tests.sh`, `test-factory-gh.py` are
byte-identical to their pre-cycle state (all three mutated files' hashes verified above; the
other two were never touched). `test-gh-sync.py` was read (the importlib mechanism at
890–891) but not edited, per instruction. No LEAVE LIST file touched, no live `gh` call, no
`check-state.sh` run.

## Not done / explicitly out of scope

B-1 (abort shape), B-2 (`or {}` guard), B-3 (T-04 fixtures), the `hasNextPage`/null `endCursor`
finding — none acted on, per dispatch instruction.
