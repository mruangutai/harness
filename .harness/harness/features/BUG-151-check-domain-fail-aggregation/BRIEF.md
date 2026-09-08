# BRIEF — BUG-151 check-domain suite fail aggregation

## Problem

`tests/integration/test-check-domain.py` is the suite that proves the write-domain hook still
refuses what it must refuse, and its own failure reporting is unprotected. `main()` (line 5190)
aggregates its 23 test blocks through 21 hand-written sites — 20 `fails += run_x()` statements
(5211-5230) plus `return fails + run_bug1305_cases()` (5231). Each block prints its own
`ok    NAME` / `FAIL  NAME` verdict lines independently of whether its return value ever
reaches that sum, so dropping seven characters from any one line leaves the block running and
printing `FAIL` on screen while `sys.exit(1 if main() else 0)` (5235) still exits 0 — and the outer
runner, which keys off exit code, reports the suite green. The mirror-image defect is a block that
is defined and never called at all: nothing anywhere notices. The comment at 5207-5210 claims the
aggregate "is asserted non-negative so the shape of this line stays deliberate"; no such assertion
exists anywhere in `main()`, so the file currently documents a safeguard it does not have. Nobody
has been bitten yet only because the suite is green today (398 `ok` lines, 0 `FAIL` lines, exit 0,
38s wall — measured on this worktree at 6d969ed3); the cost lands the first time a domain regression
is silently absorbed.

## Goal

Make this suite incapable of reporting success while it is failing, and incapable of quietly
skipping a test block someone wrote. Whoever adds a test block to the file should get it run, and
whoever breaks the hook should get a red suite — neither outcome depending on remembering to edit a
second place. The file should also stop asserting a safeguard it does not have.

## Requirements

- REQ-01: When any test block in `tests/integration/test-check-domain.py` prints a `FAIL` verdict
  line, the suite exits non-zero.
- REQ-02: A test block defined in that file is executed on every run, without being registered
  anywhere a second time.
- REQ-03: The suite's behaviour on a healthy tree is unchanged: it prints the same set of case
  verdicts and still exits 0, and the new safeguard raises no alarm.
- REQ-04: No comment in the file asserts a safeguard the file does not contain.

## Constraints

- **Scope is one function in one file.** Only `tests/integration/test-check-domain.py`, and within
  it `main()` plus the block-level helpers the fix dissolves. Issue #151 names this suite.
- **Out of scope, deliberately, not by oversight.** `tests/integration/test-validate-digest.py` and
  `tests/integration/test-bash-write-guard.py` carry the identical `fails += run_*()` shape and the
  identical exposure — measured on this worktree at 6d969ed3, `grep -c '^    fails += run_'` returns
  13 sites in `test-validate-digest.py` (lines 4280-4292) and 8 in `test-bash-write-guard.py`
  (lines 1316-1323), so issue #151's guess that other `bin/` suites use a different shape is
  falsified and any follow-up starts from measurement. This ticket excludes them; whether to
  propagate the mechanism to them is a separate ticket, not a silent widening of this one.
- **The outer layer SUPPLIES the exit-code contract and does not change.**
  `.agents/skills/harness/bin/run-unit-tests.sh` execs `run_pool.py`, which runs each test script as
  a subprocess and keys off its exit code. That layer is already sound; nothing in it is touched.
- **The print convention is load-bearing and must be preserved.** Every per-case verdict line starts
  at column 0 with `ok    ` or `FAIL  `; every detail or continuation line is indented. Counting
  `^ok` / `^FAIL` lines out of captured stdout is precise only while this holds.
- **The naming convention is load-bearing and must be preserved.** Module-level test blocks are
  `run_*`; private helpers are `_*`. Two non-underscore helpers exist
  (`bug1304_pre_change_hook`, `bug1304_assert_pre_change_allows`) and neither starts with `run_`.
- **DEC-179 SUPPLIES the routing:** the lane for this path is resolved at plan time.
  `check-domain.sh --resolve tests/integration/test-check-domain.py` returns harness-backend-dev,
  harness-dev-ops, harness-qa (exit 0), so the work is a `team` lane, not a main-session carve-out.
- **DEC-182 SUPPLIES the plan format:** `plan.yaml`, written only through `plan-merge.py`.
- **The suite costs ~38s wall.** A 60s verify budget affords exactly one full run and nothing more.

## Success Criteria

- SC-01: A printed `FAIL` verdict cannot coexist with a successful exit. Two executable
  observations, both required: (a) permanent, in this suite — the safeguard, driven on synthetic
  printed-output-and-total pairs, reports a failure exactly when a `FAIL` line was printed while the
  returned total says zero, and passes on the agreeing pairs; these cases must be shown to fail
  before the safeguard exists. (b) one-off, recorded with the change — with a defect injected into a
  real test block on a throwaway copy of the file, the suite exits 1, and it does so even when that
  block's contribution to the total is also deleted.
  verify: automated        evidence: integration
- SC-02: The set of blocks the suite runs is derived from the file's own contents at run time — no
  hand-written enumeration of block names survives in `main()`, and the composite wrapper
  `run_bug1305_cases` is gone with its three sub-blocks discovered directly — so a defined-but-never-
  called block is impossible to write. This direction is closed structurally, by construction, and
  is therefore graded by reading the code: a test asserting it could only restate the discovery
  implementation back to itself.
  verify: inspection
- SC-03: No regression in what the suite proves, established as an equality between two
  measurements of this same file rather than against a hardcoded target: the SET of case names
  printed on `^ok` lines by the pre-change file — recovered from the pinned commit `6d969ed3` and
  run as a sibling copy inside `tests/integration/`, not read out of the working tree — equals the
  set printed by the post-change file once the new safeguard block's own names are excluded, with
  `^FAIL` count 0 and exit 0 in both. Both halves are taken together, in one task, so no
  measurement is transcribed between tasks. A raw count equality would read red for a correct
  change, because the new block adds `ok` lines of its own; a hardcoded 398 would read red the next
  time anyone adds a test.
  verify: automated        evidence: integration
- SC-04: The safeguard raises no false alarm on a healthy tree: a full green run prints no
  safeguard diagnostic line and exits 0.
  verify: automated        evidence: integration
- SC-05: The false comment is gone — no comment in the file claims an assertion on the aggregate
  that the code does not perform, and any comment describing the new safeguard describes what it
  actually does.
  verify: inspection

## Approval

status: approved
approved-by: operator
date: 2026-09-07
