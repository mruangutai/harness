# BRIEF — FEAT-47 Harness's own tests move to `tests/**`

## Problem

In this repository every test lives in `.claude/skills/harness/bin/`, beside the hooks, validators
and gate scripts it tests. The only way to grant a seat permission to write a test here is to grant
it `.claude/skills/harness/bin/**` — the same grant that lets it rewrite `check-domain.sh`. Measured
at `ea6f51f` on the live PreToolUse route: `harness-qa` carries `tests/**` and is BLOCKED writing
anywhere it could put a test, while `harness-backend-dev` and `harness-dev-ops` write tests only
through the enforcement-script grant. So "may write a test" and "may write an enforcement script"
are one permission, and the qa half of issue #979 — a seat that can add the test a gate is missing
without being able to weaken the gate — cannot be built on that layout. Two further costs are
already visible: which kind a test belongs to is bookkeeping in two hand-maintained bash arrays
plus a literal file list in `harness.json`, and eight files once drifted between them silently
(DEC-197); and `bin/` cannot be described as production code, because 57 of the 118 files tracked
under it are test-named.

A third cost, measured 2026-08-31 at `ea6f51f` on a 12-core M3 Pro with each test invoked as its own
`python3` subprocess: the suite is **strictly serial** — `run-unit-tests.sh` has no worker pool — and
takes **247s** over 56 files, all `rc=0`. Five files carry 57% of it (`test-check-plan-routes.py`
36.7s, `test-gh-sync.py` 32.9s, `test-check-state.py` 30.1s, `test-check-domain.py` 26.8s,
`test-board-lifecycle.py` 15.1s = 142s), while 28 of the 56 finish in under a second: 8 files exceed
10s, 20 sit between 1s and 10s. Eight workers measured ~47s (5.3x) and four — CI-realistic — 68.7s,
against a hard floor of ~37s that no worker count can beat, because that floor is the single slowest
test. **And the suite is not safe to run that way today:** `test-gh-sync.py` fails about one run in
three at 8 workers and is green every time serially, while six concurrent copies of itself all pass —
so a *sibling* mutates state it reads. Filed as issue #1053 with the three failing assertion names and
a reproduction; the partner is not identified. Runs a and b at 8 workers were green and run c failed,
so a single green parallel run is evidence of nothing — the qa half of #979 stated again in a
different place.

## Goal

Harness's own tests live where any other project's do — `tests/unit/**` and `tests/integration/**`
at the repository root — and the directory a test sits in *is* its kind. `bin/` becomes provably
free of test-named files. Test-writing becomes a permission a seat can hold on its own, and the
kind bookkeeping is deleted rather than maintained. This is a deliberate architectural position, not
a drift repair: the two-base boundary model correctly accepts `bin/` today, and it is being widened
on purpose. Nothing changes for onboarded projects, whose `tests/**` already resolves in their own
product base.

And the suite that lands is one that can be run concurrently and trusted: tests that do not depend on
each other, a worker pool in the same runner rewrite rather than a later bolt-on, and a wall time
that was measured rather than assumed.

## Requirements

- REQ-01: A seat can be granted permission to write a test file in this repository without thereby
  being able to write an enforcement script, and a seat that should hold neither holds neither.
- REQ-02: Harness's own tests are discovered at `tests/unit/**` and `tests/integration/**`, and the
  directory a test file sits in determines the kind it runs as — no list, in any file, registers a
  test or its kind.
- REQ-03: Every test file's kind matches the property that actually distinguishes the two kinds
  (issue #160: does an assertion depend on behaviour in another process), rather than the kind it
  historically sat under.
- REQ-04: The suite that ran before the move runs after it, from the new location, with no check
  lost and no file left behind.
- REQ-05: A layout violation — a kind directory emptied, one test present in both kinds, a test
  planted in `bin/` — is caught by a check that fails loudly, and that check is itself provably
  able to fail.
- REQ-06: This repository's declared test kinds are the ones the template ships, with no
  repository-specific appendix, and cannot silently re-acquire one.
- REQ-07: The decision log states the mechanism that exists. No live file presents the deleted
  arrays or their cross-check as current.
- REQ-08: The probe that makes a live model call is under `tests/` and is reachable by no runner and
  no active test kind, so `bin/` being test-free costs nothing in CI and gains nothing false.
- REQ-09: No test's result depends on whether another test ran, or on the order it ran in, and a
  test that reacquires such a dependency is caught by a check that fails loudly rather than by an
  intermittent red.
- REQ-10: The suite runs concurrently, and running it concurrently does not change what it reports:
  every line of output is attributable to the file that produced it, any failing file fails the run,
  and every existing invocation keeps its behaviour.
- REQ-11: Running the whole suite costs materially less wall time than it does today, by a margin
  that is measured on the host that runs it rather than asserted.

## Constraints

Cited by number, each labelled by what it does to this feature.

- **DEC-174 — supplies the route, and bounds it.** Harness may plan its own enforcement-layer work
  and must not execute it through the enforcement path being changed (`AGENTS.md:8` names "hooks,
  validators, gate scripts, or their tests"). Every task here is therefore
  `execution_mode: main-session-direct`; no task may be dispatched to a squad.
- **DEC-182 — supplies the format.** The plan is `plan.yaml`, real YAML, no markdown in any value.
- **DEC-120 — blocks.** `## Approval` here and `approval:` in the plan are the main session's alone.
- **DEC-163 — binds.** No success criterion may rest on a test kind whose runner is null.
- **DEC-205 — binds.** The decision log states current truth; a correction rewrites the entry it
  corrects and supersession is deletion. DEC-187 and DEC-197 each contain present-tense claims about
  the arrays that this feature falsifies, so both are rewritten in the same edit that adds the new
  entry. Neither is struck: DEC-187's ruling (this repository excludes `functional`) and DEC-197's
  rule (an overlapping file resolves to the explicitly-named kind) both survive their mechanism.
- **DEC-129 — supplies the layout.** Everything for this feature lives under
  `.harness/harness/features/FEAT-47-tests-layout/`.
- **The historical record is not rewritten.** Notes, receipts and logs under `.harness/notes/`,
  `.harness/harness/features/**` and `.harness/logs/` that name `bin/test-` paths are a record of
  what was true when written. A raw grep reports 3219 such mentions; 6 of them are live references
  and only those 6 change (enumerated in `notes/research-tests-layout.md`).
- **Out of scope, settled at grilling:** issue #979 itself — the mutation gate, the host kind,
  fixture provenance and the measurement mode. This feature is the migration that unblocks it and
  #979 is re-planned afterwards. Also out: renaming `is_control_plane_target`, and a third
  "own-product" base for Harness. Both considered and declined.
- **Out of scope, decided by the operator on the measurements:** change-based test selection is
  **rejected as the primary speed lever** and is not planned here. Half the suite is already
  sub-second, so the only meaningful saving selection could buy is skipping the five slow gate tests
  — which is precisely where a mis-mapped selector produces a green run that proved nothing (#979).
- **Issue #1053 folds into this feature** rather than becoming its own: the runner it would have to
  change is being rewritten here, and switching a pool on over a suite with a known cross-test
  collision makes the gate flaky by construction.

## Success Criteria

Every criterion is graded at the pinned `review_sha` (`git show <review_sha>:<path>`), never against
the working tree. The per-file baselines the first two criteria compare against were measured at
`ea6f51f` and are recorded in `notes/research-tests-layout.md`.

- SC-01: From the new layout, `run-unit-tests.sh --kind unit` exits 0, its tally lines name exactly
  the files present in `tests/unit/`, and each of the 19 migrated unit files emits exactly the
  verdict-line count recorded for it in the baseline census.
  verify: automated        evidence: unit
- SC-02: The same three clauses hold for `--kind integration` over `tests/integration/`, for each of
  the 36 migrated integration files.
  verify: automated        evidence: integration
- SC-03: On the live PreToolUse route, `harness-qa`, `harness-backend-dev` and `harness-dev-ops` are
  each ALLOWED to write a new file under both `tests/unit/` and `tests/integration/`; `harness-qa`
  is DENIED a new `.claude/skills/harness/bin/*.sh`; and `harness-frontend-dev`,
  `harness-ai-dev` and `harness-data-engineer` are each DENIED `tests/unit/`. All eleven verdicts
  are asserted individually — a count of allowed seats is satisfied by the conformers alone.
  verify: automated        evidence: integration
- SC-04: The runner refuses each layout violation and names it, proven against a fixture tree it is
  pointed at: `tests/unit/` holding no test file; `tests/integration/` holding none; one basename
  present in both directories; a `test-*.py` planted in `bin/`. With all four repaired, the same
  invocation exits 0 and runs no test. Each violation is a separate case with its own message
  assertion; a non-zero exit alone is not the proof, because it cannot tell a detected violation
  from a crash.
  verify: automated        evidence: integration
- SC-05: The layout predicate is one function in one file, and driving it directly returns exactly
  the expected violation list for each of the four synthetic trees above and the empty list for this
  repository's real tree. A second copy of the predicate anywhere would falsify this criterion,
  because the two copies are what DEC-197 records going silently out of step.
  verify: automated        evidence: unit
- SC-06: `test_kinds.unit.detect` and `test_kinds.integration.detect` in `.harness/harness.json`
  equal the values in `.claude/skills/harness/templates/harness.json`, and a test asserts that
  neither contains a `.claude/` path — so the appendix cannot silently return.
  verify: automated        evidence: unit
- SC-07: At the review sha, no file outside `.harness/notes/`, `.harness/harness/features/` and
  `.harness/logs/` mentions `UNIT_SCRIPTS`, `INTEGRATION_SCRIPTS` or `--check-kinds`; the search's
  exit status is asserted, never a count of zero lines. `DECISIONS.md` carries the new entry,
  DEC-187 and DEC-197 no longer describe the arrays as live, and
  `gen-decisions-index.py --check` exits 0.
  verify: inspection
- SC-08: `tests/manual/` is matched by no `detect` glob of any kind whose `status` is `active`, and
  by neither directory the runner walks — asserted in a test, so a later `detect` edit that captures
  it goes red.
  verify: automated        evidence: unit
- SC-09: Re-running the recorded child-process probe over the new tree at the review sha, every file
  in `tests/integration/` spawns at least one child process, and every file in `tests/unit/` spawns
  either none or only children in the declared fixture set (`git`, `ps`, `fake-gh`, `fake-gh-fail`,
  `bun`, `python3 -c`). The probe output, not the plan's own table, is the grading set.
  verify: inspection
- SC-10: The sibling that mutates `test-gh-sync.py`'s state is identified by name, together with the
  shared surface and the write that collides, in `notes/research-parallel-safety.md` at the review
  sha; and the instrument that identified it re-runs from the repository root and reproduces that
  identification. "The flake no longer reproduces" is not this criterion: the deliverable is the
  named partner and the named mechanism, because a flake that stops reproducing is
  indistinguishable from one that got luckier.
  verify: inspection
- SC-11: The shared surface #1053 turns on cannot silently return: a test under `tests/unit/` asserts
  the invariant that forbids it, over every file under `tests/`, and the assertion is proven able to
  fail by being pointed at a synthetic tree holding one violating file, which it must report by path.
  The evidence for independence is this assertion, never a suite that passed once under load.
  verify: automated        evidence: unit
- SC-12: Ten consecutive `run-unit-tests.sh --kind all` runs at the default worker count each exit 0
  and print zero `FAIL` lines, and one further `--kind all --jobs 1 --reverse` run also exits 0 with
  zero `FAIL` lines and produces verdict lines byte-identical to the forward serial run's — so
  execution order is shown not to be load-bearing rather than asserted to be. A pass is 11 of 11;
  10 of 11 is `not_met`. The repetition count is chosen against the measured failure rate: at ~1 run
  in 3, one green run misses the defect 67% of the time and ten miss it 1.7% — runs a and b at 8
  workers were green and run c failed. The instrument's recorded per-run output over all eleven runs
  is the grading set, not a summary of it.
  verify: inspection
- SC-13: On a host with at least 8 usable cores, `--kind all` at the default worker count completes in
  at most 40% of the wall time of `--jobs 1` measured on the same host in the same session, both
  numbers recorded with that host's core count, and both runs exit 0. The comparison is relative on
  purpose: the 247s serial figure was measured at `ea6f51f` on a 12-core M3 Pro and does not transfer.
  No criterion here asks for less than 37s — the slowest single file measures 36.7s, so no worker
  count can beat that floor; 4 workers measured 68.7s, which is 28% of serial and still passes this.
  verify: inspection
- SC-14: Driven against a fixture root, the parallel runner is verdict-identical to the serial one and
  its output stays attributable: `--jobs 1`, `--jobs 4` and the default each produce the same set of
  `PASS`/`FAIL` lines, as does `--jobs 1 --reverse`; each file's own output appears as one contiguous
  block bounded by that file's header and its own verdict line, with no line of one file's output
  falling between two lines of another's; one deliberately failing file yields exit 1 and its own
  `FAIL` line while every other file still reports `PASS`; a file whose interpreter cannot be spawned
  is a `FAIL` line and exit 1, never a silently skipped file; `--kind unit`, `--kind integration` and
  `--check-layout` behave as they did before the pool; and `--jobs 0`, `--jobs -1`, `--jobs abc` and
  `--jobs` with no value each exit 2 with the usage line. Each clause is its own case with its own
  assertion — one "it works in parallel" case is satisfied by the conformers alone.
  verify: automated        evidence: integration

## Verification gaps

Read against `test_kinds` in `.harness/harness.json` at `ea6f51f`.

- Every criterion above rests on `unit` or `integration`. Both have a live runner
  (`run-unit-tests.sh --kind <kind>`), so no criterion here is carried by a soft skip.
- `component`, `ui`, `eval` and `typecheck` have `cmd: null`, and `functional` is excluded by
  DEC-187. None of them covers a surface this feature touches: there is no UI, no model behaviour
  and no database path in it.
- **The one gap this feature does not close, stated at the signature:** the guard makes `bin/` free
  of test-**named** files, not of test **support**. `layout_fixtures.py` is imported only by two
  tests and stays in `bin/` under the settled scope, so nothing mechanical distinguishes a fixture
  module from production code. Purpose-level classification is left to #979.
- Runtime, measured at `ea6f51f`: `--kind unit` 20s, `--kind integration` 152s. SC-02's evidence
  therefore takes ~2.5 minutes to produce; that is a stated cost, not a reason to weaken it.
- **SC-12 and SC-13 are graded on instruments under `tests/manual/`, which no runner runs.** So the
  stability and the speedup are established once, at review, by a human re-running a recorded
  command — not by the tests workflow. CI keeps only the single `--kind unit` and `--kind integration`
  runs, and a later regression in stability would surface there as an intermittent red rather than as
  a named failure. Putting eleven whole-suite runs (~10 minutes at 8 workers) into a required step
  was the alternative, and it is not taken. That is a stated gap, not an oversight.
- SC-14 covers the concurrency semantics that CI *can* afford: it runs against a fixture root of
  trivial tests, so it costs seconds and is a required step.

## Approval

status: pending
approved-by:
date:
