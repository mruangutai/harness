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
- REQ-02: A violation of REQ-01 reintroduced in any test file the tree holds fails a gate CI
  already runs, and the failure names the offending file and line — for a write whose target is
  derived from the test's own path, or whose target is inside the shared code directory the
  runtime check watches. `plan.yaml` D-11 names the classes neither mechanism sees; this
  requirement does not claim them.
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
- SC-03: The invariant reports **zero** findings over the live tree — having first printed the root
  it resolved and a `discovered` count of at least 50, so a zero cannot come from a walk that found
  nothing — and, in the same run, flags the ten historical violating sites at `ea6f51f`:
  `test-check-domain.py:1482` and `:1489`, `test-check-state.py:2112`, `:2114`, `:2133`, `:2248`,
  `:2250`, `:2269`, `test-feature-worktree.py:584` and `:605`, each asserted individually.
  FAILS IF: the live scan reports any finding; the printed root is not
  `git rev-parse --show-toplevel`; fewer than 50 files were discovered; or the historical scan
  misses any one of the ten sites — a threshold of "at least eight" is satisfied by a scanner that
  quietly lost two, and an exit code alone is satisfied by a scanner that walked nothing.
  verify: automated      evidence: unit
- SC-04: The invariant actually runs in CI: `run-unit-tests.sh --kind unit` emits
  `PASS test-suite-independence.py`.
  FAILS IF: that line is absent, which is what an unregistered test file looks like.
  verify: automated      evidence: unit
- SC-05: Ten consecutive `--kind all` runs at the worker count the runner chooses itself, on the
  12-core machine, all exit 0 with no `FAIL` line, and each run's wall time is recorded, together
  with the tree condition the ten were taken under — what else was writing this checkout at the
  time. The condition is recorded because `--mutation-check` watches `.claude/skills/harness/bin/`
  and an edit to a file there during a run reddens it for a reason that is not the pool's, so a
  clean ten taken on a quiet tree is different evidence from a clean ten taken under load.
  Ten, and the honest bound: this flake produced 6 consecutive clean 8-worker runs while present,
  so ten clean runs alone would NOT establish that the hazard is gone. SC-01 and SC-02 are that
  proof; this criterion only catches a NEW failure the worker pool itself introduces, where ten
  runs at ~50s each is the most repetition worth its wall time.
  FAILS IF: any of the ten prints a `FAIL` line or exits non-zero, fewer than ten were run, or the
  tree condition is unrecorded — an unstated condition makes the ten ungradeable, not passing.
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
  independence invariant, the runtime mutation check, the worker-count rule, and change-based test
  selection as **rejected** with its reason; and `gen-decisions-index.py --stdout` is byte-identical
  to the committed `DECISIONS-INDEX.md`. There is no `--check` flag — the read-only mode piped into
  a comparison IS the drift check (`gen-decisions-index.py:9-10`, and `:253-259` rejects any argv
  token other than `--stdout`).
  FAILS IF: `git show <review_sha>:.harness/harness/docs/DECISIONS.md` lacks the rejection or its
  reason, the index comparison differs, or the entry names the required phrases without stating
  them — a section under 300 words is a stub scoring keyword bingo, not a record.
  verify: inspection
- SC-10: A test that mutates the shared code directory during a run fails that run.
  `run_pool.py --mutation-check DIR` prints `MUTATED <path relative to DIR>` and exits 1 in
  three cases, each of which is a real historical vector: a write to an existing watched file;
  the same write performed by a **subprocess**, which the static invariant cannot see; and a
  **new file created** under DIR, which is what `.mutant-*.sh` did and what a `git ls-files`
  watched set cannot see at all. It exits 2 rather than reporting clean when DIR is absent or
  holds no files, and it does not report a rewritten `__pycache__` entry.
  FAILS IF: the editing fixture run exits 0; the shell-mediated write is missed; the creating
  fixture run exits 0; a `MUTATED` line is absent or does not name the path relative to DIR;
  the empty-or-absent DIR case reports clean; a `__pycache__` rewrite is reported, which makes
  the check redden on the interpreter's own byte-code caching; or `run-unit-tests.sh` invokes
  the pool with any argument other than `"$BIN_DIR"` — no flag at all is the check silently
  off, and the repository root is the check reddening whenever a sibling agent writes a note,
  which is how it gets deleted.
  verify: automated      evidence: integration

## Verification gaps

- No runner measures suite wall time or repeated-run stability, so SC-02, SC-05 and SC-06 rest on
  operator-recorded measurements rather than a gate. What is therefore NOT proven mechanically: the
  suite's speed and its run-to-run stability. What carries them: `notes/measurements-parallel-suite.md`,
  which `plan.yaml` T-06 requires and whose SHAPE T-06's verify now enforces — ten `run <i> exit <rc>
  <wall>s` lines all exiting 0, a `control method: isolated bin copy` line (the SC-02 control is
  taken inside a private copy of the bin directory, never by reopening the removed hazard on the
  live shared tree), a `control broken reads <n>` greater than zero, a `post-fix broken
  reads 0`, a `pool:` line whose wall time is at or under 120s, and a non-empty `tree condition:`
  line. What that still cannot prove is
  that the numbers were measured rather than typed; the fenced verbatim command output beside them
  is what a reviewer reads for that. SC-01 and SC-03 remain the mechanical hazard proof.
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
  rewrites `run-unit-tests.sh` to be directory-driven. FEAT-48 ships **whole and first**, against
  today's array-driven runner (`plan.yaml` D-09). It supplies rather than blocks: nothing here waits
  on FEAT-47. Both new files are written so that the move **requires** no edit to their logic — the
  pool takes a list of script paths on argv and never sees how they were discovered, and the
  invariant resolves its root with `harness_boundary.root_above`, a marker walk with no depth
  arithmetic (`harness_boundary.py:84-100`). That is the whole of what FEAT-48 controls, and it is
  narrower than it first looks: `test-suite-independence.py` anchors its `harness_boundary` import
  on its own directory, so the move does require an edit to that import. Whether FEAT-47's plan
  leaves the rest of the file alone is **FEAT-47's to state, not FEAT-48's to predict** — as read
  on 2026-08-31, FEAT-47 `plan.yaml` T-03 described this file as deriving its root by a directory
  climb and instructed repointing that climb, which is false of the file this feature ships and
  would reintroduce exactly the depth arithmetic `root_above` exists to keep out. That correction
  is a FEAT-47 plan-text edit, in flight there; FEAT-48 states the dependency and asserts nothing
  about the sibling plan's instructions.
- The census contract FEAT-47 depends on, stated here because it is cross-feature: FEAT-48 adds
  exactly two new `test-*.py` under `.claude/skills/harness/bin/` — `test-suite-independence.py`
  (unit) and `test-run-pool.py` (integration) — plus two non-test helpers that stay in `bin/`,
  `isolated_bin.py` and `run_pool.py`. FEAT-47's enumerated move set and its count assertions must
  absorb both test files. Changing that list later is a change to FEAT-47's plan, not a FEAT-48
  detail.
- CI runs two separate steps, `--kind unit` and `--kind integration`, on `ubuntu-latest`
  (`.github/workflows/tests.yml`). The worker count must therefore be derived on the machine, not
  pinned to the 12-core development box, and the two steps' attribution must survive.
- **Every intermediate commit is gated.** `.github/workflows/tests.yml` declares `on: push:
  branches:[main]` plus a bare `pull_request:`, which includes `synchronize`, so CI re-runs on
  every push to an open PR. A transient state that trips `run-unit-tests.sh`'s drift detector —
  a `test-*.py` under `bin/` in neither script array — is a live red build, not a theoretical
  window. Every task that creates a test file therefore registers it in the same task
  (`plan.yaml` T-03, T-04).
- **Agents write this checkout while suites run, and that is the normal operating condition.**
  Operator measurement, 2026-08-31: 1,904 tracked files under `.harness/harness/features/**`
  modified in three hours across the live worktrees. Any guard that reddens on a concurrent
  tracked-file write is unusable here, which is what bounds the runtime mutation check's watched
  set to `.claude/skills/harness/bin/` (`plan.yaml` D-11).
- Measurements this feature is planned against, all observed 2026-08-31 at `ea6f51f` on a 12-core
  M3 Pro with each test file in its own `python3` subprocess: 247s serial across 56 files, ~47s at
  8 workers, 68.7s at 4 workers, top 5 files = 142s = 57% of the total, 28 of 56 under 1s, hard
  floor ~36.7s set by the slowest single file.

## The FEAT-47 boundary — settled, and not an operator question

FEAT-47 has already shed the scope that duplicated this feature. The carve-out is recorded on both
sides, in a diff, with the vacated ids retired rather than renumbered: FEAT-47 `plan.yaml` D-13
("FEAT-48 ships WHOLE and lands BEFORE this feature … the D-NN numbers D-09 to D-12 and the tasks
T-07 to T-09 that once held that scope are removed, not renumbered") and FEAT-47 `BRIEF.md`:87-94,
against `plan.yaml` D-09 and `## Constraints` above on this side. Nothing in it is put to the
operator; an earlier draft of this section posed it as open, which spent the signature on a
decision already taken.

Both plans are still `approval.status: pending`, so the settlement holds between two unsigned
drafts and becomes binding when both are signed. One consequence stands and needs no ruling:
FEAT-48's decision entry takes the next free `DEC-` number **at authoring time** rather than a
pinned one, so the two features cannot claim the same number (`plan.yaml` T-05).

## Approval

status: pending
approved_by:
date:
