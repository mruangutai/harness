# BRIEF — FEAT-48 Parallel-safe suite

## Problem

`test-check-domain.py:1475-1490` overwrites the live shared `feature_schema.py` in
`.claude/skills/harness/bin/` for a ~90ms window on every run, to prove that a crashing schema
checker denies a write. For that window, every other process on the machine that imports
`feature_schema` — directly or through a script it shells out to — gets a module whose
`problems_for_text` raises. That is issue #1053: `test-gh-sync.py` fails about one run in three at
8-way parallelism and never serially, because it imports that module several hundred times per run
and is therefore the likeliest victim, not the only possible one.

The hazard is proven by direct observation, not inferred from a failure rate: polling the shared
file during one run of `test-check-domain.py` saw a broken `feature_schema.py` in **5,105 of
1,032,849 polls**, first at 8.68s (`notes/research-parallel-safety.md`). The collision partner is
identified; nothing in this feature investigates or bisects to find it.

Two costs follow. The suite reports unreliably today, serial or not — a test whose verdict depends
on what a sibling is doing at that instant is not a gate. And it blocks the runner from using more
than one core: 247s serial against 47s at 8 workers, measured 2026-08-31 at `ea6f51f` on a 12-core
M3 Pro.

## Goal

Make every test in the suite independent of every other, keep it that way with an invariant that
CI runs, and then run the suite in parallel with attributable output — so that a green run means
the tests passed rather than that the scheduler happened to be kind.

## Requirements

- REQ-01: No test mutates state shared with any other process — no test writes, replaces or
  deletes a path inside the live checkout while it runs.
- REQ-02: A violation of REQ-01 reintroduced anywhere in the test tree fails a gate CI already
  runs, and the failure names the offending file and line.
- REQ-03: `run-unit-tests.sh` runs its test files concurrently, and a non-zero exit from any file
  fails the run.
- REQ-04: Output from a parallel run is attributable: every line can be traced to the test file
  that produced it.
- REQ-05: The runner picks a worker count suited to the machine it is on — including CI runners far
  smaller than the development machine — and reports the count and the wall time it took.
- REQ-06: The invocations that already exist keep their contract: `--kind unit`,
  `--kind integration`, `--kind all`, `--check-kinds`, one `PASS <file>` or `FAIL <file>` line per
  file, and exit codes 0, 1 and 2 with their present meanings.
- REQ-07: Suite correctness does not depend on the order the test files run in.
- REQ-08: The choices this feature settles are recorded in `DECISIONS.md`, including the rejection
  of change-based test selection as the speed lever.

## Success Criteria

Each criterion names what would make it fail. A fix here is proven by the **hazard being absent**,
never by the flake ceasing to reproduce: it went quiet for 6 consecutive 8-worker runs mid-
investigation while fully present and unfixed.

- SC-01: A full run of `test-check-domain.py` leaves `.claude/skills/harness/bin/feature_schema.py`
  byte-identical **and never written at all** — the schema probe asserts the live module's mtime
  and bytes are unchanged, having driven the crashing-checker case against a private copy.
  FAILS IF: the mtime moves, the bytes differ, or the crashing-checker case stops asserting exit 2
  with `CRASHED` in stderr (which would mean the case was neutered rather than isolated).
  verify: automated      evidence: integration
- SC-02: The research note's poll, re-run over a full parallel suite run after the fix, observes
  **zero** broken reads of the live `feature_schema.py`; and the same poll re-run against
  `git show ea6f51f:.claude/skills/harness/bin/test-check-domain.py` observes more than zero.
  FAILS IF: any post-fix poll sees a raising `problems_for_text`, or the pre-fix control sees none
  — a control that cannot see the hazard makes the post-fix zero inconclusive, not passing.
  verify: inspection
- SC-03: The invariant reports **zero** findings over the live tree and, in the same run, flags the
  historical violating sites: scanning the three files at `ea6f51f` yields findings that name each
  file and line, including `test-check-domain.py` at the injection site.
  FAILS IF: the live scan reports any finding, the historical scan reports none, or a finding omits
  the file or the line — a guard that cannot redden on a violating tree is the #979 defect wearing
  the remedy's clothes.
  verify: automated      evidence: unit
- SC-04: The invariant actually runs in CI: `run-unit-tests.sh --kind unit` emits
  `PASS test-suite-independence.py`.
  FAILS IF: that line is absent, which is what an unregistered test file looks like.
  verify: automated      evidence: unit
- SC-05: Ten consecutive `--kind all` runs at the worker count the runner chooses itself, on the
  12-core machine, all exit 0 with no `FAIL` line, and each run's wall time is recorded.
  Ten, and the honest bound: this flake produced 6 consecutive clean 8-worker runs while present,
  so ten clean runs alone would NOT establish that the hazard is gone. SC-01 and SC-02 are that
  proof; this criterion only catches a NEW failure the worker pool itself introduces, where ten
  runs at ~50s each is the most repetition worth its wall time.
  FAILS IF: any of the ten prints a `FAIL` line or exits non-zero, or fewer than ten were run.
  verify: inspection
- SC-06: `--kind all` on the 12-core machine prints its own worker count and wall time, and that
  wall time is at or under 120s against the 247s serial baseline observed 2026-08-31 at `ea6f51f`.
  120s, not 47s: the measured 8-worker figure was 46.9-58.5s and the floor is ~37s (no worker count
  beats the slowest single file, 36.7s), so the criterion is set where a real regression fails it
  and machine noise does not.
  FAILS IF: the printed wall time exceeds 120s, or the runner prints no worker count and no wall
  time — an unprinted number cannot be graded.
  verify: inspection
- SC-07: The existing contract holds: `--check-kinds` exits 0, prints its agreement line and runs
  no test; `--kind unit` and `--kind integration` each emit exactly one `PASS`/`FAIL` line per file
  in their set; a deliberately failing file makes the run exit 1; an unknown kind still exits 2.
  FAILS IF: any of those exit codes or line shapes changes, which would break the two CI steps and
  `harness.json`'s `test_kinds` commands.
  verify: automated      evidence: integration
- SC-08: Order is not load-bearing: the pool run over a synthetic file set produces a completion
  order different from the input order while the pass/fail verdict set is identical, and the same
  set run with one worker yields the same verdicts.
  FAILS IF: the verdict sets differ, or completion order matches input order for a set built so it
  cannot (a serialised pool).
  verify: automated      evidence: integration
- SC-09: `DECISIONS.md` at the review sha carries one entry recording private-copy isolation, the
  independence invariant, the worker-count rule, and change-based test selection as **rejected**
  with its reason; `gen-decisions-index.py --check` reports no drift.
  FAILS IF: `git show <review_sha>:.harness/harness/docs/DECISIONS.md` lacks the rejection, or the
  index check reports drift.
  verify: inspection

## Verification gaps

- No runner measures suite wall time or repeated-run stability, so SC-02, SC-05 and SC-06 rest on
  operator-recorded measurements rather than a gate. What is therefore NOT proven mechanically: the
  suite's speed and its run-to-run stability. What carries them: `notes/measurements-parallel-suite.md`,
  which `plan.yaml` T-04 requires — commands and verbatim output for all three, including the
  pre-fix control that proves the poll can see the hazard — plus SC-01 and SC-03, which are
  mechanical and are the actual hazard proof.
- `component`, `ui`, `eval` and `typecheck` have `cmd: null` in `.harness/harness.json`. None of
  them detects any surface this feature touches (bash and Python gate scripts under
  `.claude/skills/harness/bin/`, covered by `unit` and `integration`, both of which have runners),
  so no criterion here rests on a null kind.

## Constraints

**Supplies the mechanism:**

- DEC-174 — the enforcement-layer carve-out. Every file this feature touches is a hook, gate script
  or the test of one, so every task is `execution_mode: main-session-direct`. `AGENTS.md:8` names
  "hooks, validators, gate scripts, or their tests" verbatim.
- DEC-182 — the plan is `plan.yaml`, real YAML.
- The isolated-bin idiom already in the tree: `test-check-domain.py:208-216` builds an isolated copy
  of the hook under a tempdir, and `test-post-merge-sweep.py:134-140` builds a fixture bin
  directory. This feature generalises that, it does not invent it.

**Blocks or bounds:**

- FEAT-47 (`feat/FEAT-47-tests-layout`) `git mv`s every `test-*.py` out of
  `.claude/skills/harness/bin/` into `tests/unit/`, `tests/integration/` and `tests/manual/`, and
  rewrites `run-unit-tests.sh` to be directory-driven. Two consequences, both settled in
  `plan.yaml` D-09: the isolation work ships **ahead** of FEAT-47 (it is layout-independent and a
  live hazard, and an edit before a `git mv` is carried forward by the move), and the worker pool
  lands **after** FEAT-47 merges (it builds on the directory-driven runner). The invariant
  discovers its own scan set by walking the tree, so the move does not blind it.
- FEAT-47's `plan.yaml` at the time of writing still carries T-07 (the collision hunt), T-08 (the
  worker pool) and REQ-09/10/11, which are exactly this feature's scope, plus a `DEC-207` entry for
  them. That plan is not FEAT-48's to edit — see the open question below.
- CI runs two separate steps, `--kind unit` and `--kind integration`, on `ubuntu-latest`
  (`.github/workflows/tests.yml`). The worker count must therefore be derived on the machine, not
  pinned to the 12-core development box, and the two steps' attribution must survive.
- Measurements this feature is planned against, all observed 2026-08-31 at `ea6f51f` on a 12-core
  M3 Pro with each test file in its own `python3` subprocess: 247s serial across 56 files, ~47s at
  8 workers, 68.7s at 4 workers, top 5 files = 142s = 57% of the total, 28 of 56 under 1s, hard
  floor ~36.7s set by the slowest single file.

## Open question for the operator

FEAT-47 must shed T-07, T-08 and REQ-09/10/11 (and the `DEC-207` half of T-09), or this work is
planned twice by two features that will collide in `run-unit-tests.sh` and in the decisions log.
FEAT-48's decision entry therefore takes the next free `DEC-` number **at authoring time** rather
than a pinned one, so the two features cannot claim the same number.

## Approval

status: pending
approved_by:
date:
