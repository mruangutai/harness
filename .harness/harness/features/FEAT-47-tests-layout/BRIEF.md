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
under it are test-named — measured at `ea6f51f`, and a baseline rather than an invariant, since
FEAT-48 lands two more test files there before this feature runs.

## Goal

Harness's own tests live where any other project's do — `tests/unit/**` and `tests/integration/**`
at the repository root — and the directory a test sits in *is* its kind. `bin/` becomes provably
free of test-named files. Test-writing becomes a permission a seat can hold on its own, and the
kind bookkeeping is deleted rather than maintained. This is a deliberate architectural position, not
a drift repair: the two-base boundary model correctly accepts `bin/` today, and it is being widened
on purpose. Nothing changes for onboarded projects, whose `tests/**` already resolves in their own
product base.

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
- **Ordered against FEAT-48, which lands FIRST.** Parallel safety, the worker pool and suite wall
  time are FEAT-48, and it merges whole before this feature starts. The order is forced, not
  preferred: the cross-test injection hazard is live today and corrupts every parallel measurement
  including this feature's own, and the pool does not depend on this layout — FEAT-48's D-05 puts
  scheduling in `run_pool.py`, invoked once by bash which keeps kind selection, so the pool
  receives a script list and never sees how that list was discovered. Issue #1053 and the
  rejection of change-based test selection as a speed lever travel with FEAT-48. Nothing is
  written twice and no work interleaves across the two merges.
- **The census FEAT-48 hands this feature, confirmed against its plan's D-09.** FEAT-48 adds
  exactly two test files to `.claude/skills/harness/bin/` — `test-suite-independence.py`, a static
  `ast` scan with no subprocess, therefore unit; and `test-run-pool.py`, whose every case forks the
  pool, therefore integration — plus **two** non-test helpers that stay in `bin/` beside the
  runner, `isolated_bin.py` and `run_pool.py`. This feature migrates both test files with
  everything else and declares each one's kind. Nothing here names a count FEAT-48 could
  invalidate: every census is derived from the tree this feature merges into, carries a floor, and
  is bound by a conservation law rather than by an expected number (D-14).
- **Two inherited guards bind every test file this feature moves or writes, and neither is this
  feature's to weaken.** `test-suite-independence.py` statically forbids a test mutating any path
  derived from the live checkout, has no escape hatch, and discovers its scan set by walking the
  tree, so the move does not blind it — but its own root derivation is the one anchor in the
  migrated set that is not a `sys.path` insert, and T-03 repairs it by name. `run_pool.py
  --mutation-check` enforces the same property at runtime on every run, and the flag sits on the
  single invocation line in `run-unit-tests.sh` that this feature rewrites. Carrying it forward is
  a requirement of the rewrite, asserted in T-05's verify: dropping it leaves a green suite that
  has stopped checking.

## Success Criteria

Every criterion is graded at the pinned `review_sha` (`git show <review_sha>:<path>`), never against
the working tree. The per-file baselines the first two criteria compare against were measured at
`ea6f51f` and are recorded in `notes/research-tests-layout.md`.

- SC-01: From the new layout, `run-unit-tests.sh --kind unit` exits 0, and the set of basenames in
  its tally lines equals exactly the set of `test-*.py` files present in `tests/unit/` — set
  equality against the directory, never a count, so a file the runner silently skips and a name it
  reports without a file both go red. Each migrated unit file emits exactly the verdict-line count
  recorded for it in the baseline census; a file with no baseline row is reported as new and named
  in the goal-check rather than failed.
  verify: automated        evidence: unit
- SC-02: The same two clauses hold for `--kind integration` over `tests/integration/`.
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
  DEC-187 and DEC-197 no longer describe the arrays as live, and the committed
  `DECISIONS-INDEX.md` is byte-identical to `gen-decisions-index.py --stdout`. There is no
  `--check` flag: the tool refuses any argv token but `--stdout` and exits 2, so a criterion
  resting on one would fail for the wrong reason.
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
- SC-10: The migration is complete against the tree it merges into.
  `tests/manual/suite-census.py migration` derives the set of `test-*.py` basenames tracked under
  `.claude/skills/harness/bin/` at that ref — which by then contains FEAT-48's two — prints the
  size of that set, refuses a set smaller than 56 so a truncated or empty discovery cannot read as
  a clean sweep, and exits non-zero unless every name is present at the review sha under exactly
  one of `tests/unit/` or `tests/integration/`. One deletion is declared on the command line
  (`test-run-unit-tests-kinds.py`) and is the only permitted absence; a file present with no
  baseline name is printed as new, not failed. What makes it red: dropping a file, copying where a
  move was intended, or FEAT-48 adding a test this feature does not migrate. The one number in it
  is a floor measured at `ba338d8`, whose staleness can only make it weaker and never falsely
  green.
  verify: inspection

## Verification gaps

Read against `test_kinds` in `.harness/harness.json` at `ea6f51f`.

- Every `verify: automated` criterion above rests on `unit` or `integration`. Both have a live
  runner (`run-unit-tests.sh --kind <kind>`), so no criterion here is carried by a soft skip.
  SC-07, SC-09 and SC-10 are `inspection` and rest on named instruments — `git grep` with its exit
  status asserted, and the two `tests/manual/suite-census.py` modes — not on any test kind.
- `component`, `ui`, `eval` and `typecheck` have `cmd: null`, and `functional` is excluded by
  DEC-187. None of them covers a surface this feature touches: there is no UI, no model behaviour
  and no database path in it.
- **The one gap this feature does not close, stated at the signature:** the guard makes `bin/` free
  of test-**named** files, not of test **support**. `layout_fixtures.py` is imported only by two
  tests and stays in `bin/` under the settled scope, and FEAT-48's `isolated_bin.py` is a second
  module of exactly that shape. Nothing mechanical distinguishes a fixture module from production
  code. Purpose-level classification is left to #979.
- Runtime: `--kind unit` 20s and `--kind integration` 152s were measured at `ea6f51f`, serially.
  FEAT-48's pool lands first and changes both, and this feature does not re-measure them — it
  changes which files each kind discovers, not how they are scheduled. SC-02's evidence therefore
  costs whatever the pool costs, which is a stated unknown rather than a stated cost.

## Approval

status: pending
approved-by:
date:
