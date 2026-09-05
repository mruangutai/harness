# Receipt — harness-data-engineer — SIMPLIFY EFFICIENCY angle — build cycle 1

## BLUF

One measured finding: `tests/unit/test-suite-layout.py` calls `suite_layout.violations(ROOT)`
against the real repository root **5 times** (lines 54, 55, 321, 326, 327) where **3** calls
suffice; 2 are pure duplicates paid only because `check(name, cond, detail)` evaluates both
positional arguments unconditionally. Each call now costs ~32ms (measured), almost all of it
newly attributable to this feature's `tracked_paths()` git shell-outs (~22ms of the ~32ms) —
before this feature, `violations()` was pure-glob and the same duplicate pattern cost
microseconds. Net: ~64ms of genuinely wasted work per unit-suite run, real but not on the
suite's wall-clock critical path (see suite measurement below — `test-suite-layout.py` is the
*third*-slowest file at 1.24s; `test-code-grade.py` at 2.14s sets the pool's wall time, so
shaving 64ms off `test-suite-layout.py` would not move total wall time today).

No other efficiency finding survived measurement. In particular: no import-time I/O was added
(module-level is tuple literals only), `violations()` itself invokes `tracked_paths()` exactly
once per call (no internal duplication), and the redundant `sorted(tracked)` re-sort inside the
new tracked-paths block costs ~24 **microseconds** on this repo's 2722 tracked paths — measured
and dropped as below the "hot-path milliseconds" bar. The five `git_tree()`/`base_git_fixture()`
fixture builds in the integration and unit test files (~79ms each, measured) are not waste: each
case mutates the tree differently (clean / one rogue / three rogues / broken `.git` / untracked
control) and the ordering assertions ("refused before any sentinel runs") require a fresh,
isolated checkout per case — one shared fixture cannot serve five divergent mutations without
cross-contamination.

## Required suite measurements

1. `env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.sh --kind unit`
   - exit: **0** (own `$?`, captured directly)
   - `^PASS ` count: **341**
   - `^FAIL ` count: **0**
   - wall clock: **2.28s** (`date +%s.%N` around the invocation)
   - matches expected baseline (exit 0, 341 PASS, 0 FAIL) exactly.
   - Runner's own pool summary line: `pool: 8 workers, 27 files, 2.14s wall` (27 files, matching
     expected baseline file count) and `slowest: test-code-grade.py 2.14s,
     test-suite-independence.py 1.33s, test-suite-layout.py 1.24s`.

2. `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-run-unit-tests-layout.py`
   - exit: **0** (own `$?`)
   - `^PASS ` count: **14**
   - `^FAIL ` count: **0**
   - wall clock: **3.07s**
   - matches expected baseline (exit 0, 14 PASS, 0 FAIL) exactly.

Both are deliberate full-suite/full-integration runs at a boundary step (this pass, immediately
before `review_sha` pins) — that is the evidence the boundary exists, not waste, per the skill's
own guidance.

## Finding 1 (the only finding)

- **File**: `tests/unit/test-suite-layout.py`
- **Line**: 54–55 and 326–327 (two separate sites, same mechanism; 321 and one of 54/55 and one
  of 326/327 are the 3 legitimately distinct calls — cleared-registry state, first assertion,
  restored-registry assertion)
- **Summary**: `check(name, suite_layout.violations(ROOT) == [], repr(suite_layout.violations(ROOT)))`
  calls `violations(ROOT)` twice per site because Python evaluates both positional arguments
  before entering `check()`; the second call is redundant with the first and only used to render
  the failure detail.
- **Concrete cost (measured)**: single `violations(ROOT)` call against this repo's real
  root = **~32-34ms** (measured: single call 34.4ms; mean of 5 calls 31.7ms). Of that,
  `tracked_paths(ROOT)` — this feature's new git-shelling addition (`git ls-files -z` +
  `git rev-parse --show-toplevel`) — alone costs **~22.4ms** (mean of 5 calls), i.e. most of the
  per-call cost is new work this feature introduced. Two sites × one redundant call each = **one
  call's worth of pure waste each, ~64ms total** per run of this file. Confirmed via direct grep:
  `violations(ROOT)`/`tracked_paths(ROOT)` appear against the real ROOT 5 times in this file
  (lines 54, 55, 321, 327, and 511's `tracked_paths` call), where the check logic only requires 3
  distinct `violations(ROOT)` evaluations plus the one `tracked_paths(ROOT)` at 511 for case 11.
  This 64ms is real CPU work paid on every unit-suite invocation across the fleet, but — per the
  pool summary above — does not sit on this suite's wall-clock critical path today
  (`test-code-grade.py` at 2.14s dominates the 2.14s wall time; `test-suite-layout.py` at 1.24s
  has headroom).
- **Alternative**: bind the result once and reuse it for both the condition and the detail
  message, e.g. `got = suite_layout.violations(ROOT); check(name, got == [], repr(got))` — the
  same shape case 7 already uses correctly at line 321 for its *first* assertion. No behavioural
  change, no assertion removed or weakened.

## Candidates considered and dropped (measured, not flagged)

- **Redundant re-sort in the new tracked-paths block** — `violations()`'s new code (D-01/D-03
  addition) does `for rel in sorted(tracked):` where `tracked` is already
  `tracked_paths()`'s `tuple(sorted(...))`. Measured: sorting a 2722-entry list costs **~24
  microseconds** per call. Below the "hot-path milliseconds" bar named in the dispatch; not a
  finding.
- **Import-time cost in `suite_layout.py`** — checked the full module top (lines 1-41): no
  subprocess, no filesystem I/O, no compiled-regex construction at import time; only tuple
  literals (`RESTRICTED_NAME_PATTERNS`, `AGNOSTIC_NAME_PATTERNS`, `SOURCE_EXTENSIONS`,
  `DOCUMENTED_EXCEPTIONS`). Since this file is on the runner's path (imported by
  `run-unit-tests.sh` on every invocation), this was checked deliberately. Zero added startup
  cost. No finding.
- **`violations()` internal duplication** — confirmed exactly one `tracked_paths(root)` call per
  `violations()` invocation (line 132 of `suite_layout.py`); no per-call repetition inside
  production code. No finding.
- **Pre-existing glob/rglob loops in `violations()`** (the `unit_tests`/`integration_tests`
  globs, the `shaped_tests` triple-`rglob`, the `bin_dir` triple-`glob`) — confirmed via
  `git show 139f6afe:.claude/skills/harness/bin/suite_layout.py` that all of these predate this
  feature entirely (the whole pre-feature file was 34 lines); this feature added only the
  `DOCUMENTED_EXCEPTIONS`-adjacent block starting at what is now line 129. Out of scope for "work
  the change would actually do."
- **Five `git_tree()`/`base_git_fixture()` builds per test file** (~79ms measured per build) —
  each of the 5 integration cases and each of ~9 unit-file git-fixture cases exercises a
  genuinely distinct tree mutation (clean / 1 rogue / 3 rogues / broken `.git` / untracked
  control, etc.) and several assert output *ordering relative to other sentinels*
  ("refused BEFORE any sentinel runs" — line 69-71 comment). A single shared fixture reused
  across mutations would either serialize the cases (defeating the ordering assertions) or
  contaminate later cases with earlier mutations. Not waste; necessary isolation.
- **`tracked_paths()`'s two subprocess calls** (`git ls-files -z` + `git rev-parse
  --show-toplevel`) — both are load-bearing per D-03 (self-ownership precondition must run
  before/alongside enumeration, fail-closed). Settled; not reopened for a speed argument.

## Hard boundary respected

No settled item reopened. The three vocabularies (D-01/D-04) are untouched and not proposed for
merging. No assertion is proposed for deletion anywhere in this receipt — Finding 1's fix
collapses a redundant *call*, not a redundant *assertion*; the same two `check()` calls, same two
messages, same two truth values remain.

## Files touched

None. This receipt only.
