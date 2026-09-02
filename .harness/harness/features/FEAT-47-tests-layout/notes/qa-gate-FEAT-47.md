# QA Gate — FEAT-47 tests-layout

Graded against the staged/uncommitted migration diff in
`.claude/worktrees/harness/FEAT-47-tests-layout` (HEAD == origin/main `b7956fc4`; the route-authority
prerequisite from PR #1244 is already on `origin/main`, per dispatch). 87 staged paths (moves,
edits, two new files, one deletion). No source edited by this gate.

## BLUF

**FAIL.** Two of the plan's own success criteria are red as staged (SC-01/SC-02, SC-05), and a third
(SC-09) is graded by an instrument that does not do what the approved plan specifies and produces
false negatives across most of `tests/integration/`. A fourth item — the moved locally-run probe's
registration in `harness.json` — was left pointing at a path that no longer exists. Coverage of the
core migration mechanics (directory-is-kind, layout refusals, anchor repairs, runner selection,
`bin/` residue) is otherwise solid and independently verified.

## Phase 1 — expected coverage, from BRIEF/plan alone

Before reading the delivered test bodies: a migration like this needs (a) a unit-level test driving
the layout predicate directly against synthetic legal/illegal trees, (b) an integration-level test
driving the real runner end-to-end against violation fixtures with message assertions (not just exit
codes), (c) a migration-completeness census tying the pre-move file set to the post-move set, (d) a
residue sweep proving the deleted bash-array mechanism is gone from every live file, (e) a route-grant
test proving the new seats can write `tests/**` and the denied seats still can't, and (f) some proof
that each moved file's kind (unit vs. integration) tracks the child-process property the brief itself
names (issue #160), not just where it used to sit. All six are named as explicit success criteria in
the signed BRIEF (SC-01/02, SC-04, SC-10, SC-07, SC-03, SC-09) — this is not qa inventing scope.

## Phase 2 — what the diff delivers, and what's missing

### Migration mechanics — verified, PASS

- `suite_layout.py` (new, in `bin/`): one function, four violation classes, matches D-03/SC-05's
  shape.
- `tests/unit/test-suite-layout.py` (54 lines, new): real-repo-is-clean check, four synthetic-tree
  violation cases each asserting the message names the right path, `detect` == template for both
  kinds, `.claude/` absent from both, `tests/manual` absent from every active `detect`, runner
  delegates to `suite_layout` exactly once. Ran directly: **11/11 PASS**.
- `tests/integration/test-run-unit-tests-layout.py` (47 lines, new): drives the real
  `run-unit-tests.sh` against a fixture root — clean layout, `--kind unit`/`--kind integration` on a
  clean tree, `--bogus`/`--kind nonsense` refused, and all four violations reproduced through
  `--check-layout` with per-violation message assertions. Ran directly: **9/9 PASS**.
- `run-unit-tests.sh --check-layout` and `--bogus` against the real tree: exit 0 / exit 2 as
  specified.
- SC-03 (route grants): `tests/integration/test-check-domain.py:1857-1878` carries the eleven named
  assertions the plan specifies (3 grants × 2 kinds, 3 denials, 1 bin-denial, 1 worktree-parity);
  ran clean as part of the full integration run below.
- SC-10 (migration conservation law):
  `suite-census.py migration --floor 58 --base origin/main --deleted test-run-unit-tests-kinds.py`
  → `base test count: 63`, **exit 0**.
- SC-07 (residue, working-tree read since no commit exists yet): `suite-census.py residue` →
  3/3 declared exemptions covered, zero uncovered `LIVE` lines, **exit 0**.
- Full suite, run twice independently (once via the plan's `--strict` verdict-lines pass, once via
  direct `--kind unit`/`--kind integration`): **no genuine test failures**. (One apparent failure,
  `test-plan-merge.py` exit 1 / 12 FAILs, was this gate's own artifact — `HARNESS_AGENT_TYPE=harness-qa`
  leaking into the subprocess environment tripped the plan-sign-approval refusal; re-run with the
  variable unset, it is clean. Recorded so it isn't mistaken for a regression.)

### SC-05 — FAIL. The sole-implementation sweep is not implemented

T-05's own intent (step 2b) specifies, inside `tests/unit/test-suite-layout.py`: a local helper that
scans every tracked `*.py` file for text naming both kind directories beside a listing call, a
four-entry declared exemption list, a positive control, a ≥90-file discovery floor, and a red proof
against three reimplementation shapes (slash literal, `os.path.join` components,
`Path(r,...).glob`). This is what SC-05 is graded on — "against a SECOND implementation the
criterion is bounded."

The delivered file is 54 lines total (confirmed by direct read and `wc -l`) and contains only the
four synthetic-tree cases plus the three ancillary assertions (detect/`.claude`/`tests/manual`).
No exemption list, no positive control, no floor, no scan, no red proof exists anywhere in the diff —
grepped across `tests/**` and `.claude/skills/harness/bin/**` for `os.listdir|os.scandir|os.walk|
glob.glob|iterdir|rglob` combined with the kind-directory fragments; nothing matches this shape.
SC-05 as approved is unmet.

### SC-01 / SC-02 — FAIL as staged. T-05's own verify instrument is red

T-05's `verify:` block runs `suite-census.py verdict-lines --baseline
notes/research-tests-layout.md --deleted test-run-unit-tests-kinds.py --strict` and requires exit 0.
Run twice (once contaminated by the same env leak noted above, once clean): **exit 1** both times.
~20 of 64 files show a count mismatch against the baseline — e.g. `test-check-domain.py` 203→285,
`test-gh-sync.py` 273→301, `test-check-state.py` 147→197, `test-harness-boundary.py` 11→27,
`test-orchestrator-playbook.py` 11→17, `test-factory-config.py` 90→112. None of these files are
touched substantively by this migration beyond anchor repair, and `--kind unit`/`--kind integration`
both exit 0 with **zero** `FAIL` lines — so this is baseline staleness (D-18's acknowledged
one-review shelf life: `notes/research-tests-layout.md` is untouched by this diff, still pinned at
`56a30a0`, and unrelated commits landed on `main` since), not a real regression. But D-18's own
mitigation for staleness is `--strict` being passed only "at the one moment the baseline is
current" — that moment is supposed to be *this* review, and it is not current. SC-01/SC-02, and
T-05's own verify block, fail exactly as staged. The baseline needs a re-derive pass before this
lands, or `--strict` needs to be dropped from T-05's verify until it does.

### SC-09 — FAIL / not honestly gradable. `children` mode is not what the plan specifies

T-05 item 9 specifies `children` as **dynamic instrumentation**: wrap `subprocess.Popen.__init__`,
`os.system`, `os.fork` and `os.posix_spawn`, run each file, and report what actually forked. The
delivered `children()` in `tests/manual/suite-census.py` is a **static regex scan of the source
text** (`subprocess\.(?:run|Popen|call|check_call|check_output)\(\s*\[?['"]…`) — it never executes
anything, and it only matches a call whose argv opens with a *literal quoted string*.

Run directly: 29 of the ~40 files under `tests/integration/` report `children=-` (zero), including
`test-board-lifecycle.py`, `test-branch-create-gate.py` and `test-factory-decompose.py` — three of
the twelve files T-06's own decision text names as reclassified *because* they fork a real
subprocess. Direct inspection of `test-board-lifecycle.py:412-417` shows exactly that fork:
`subprocess.run([sys.executable, SCRIPT] + args, ...)` — argv[0] is `sys.executable`, a name, not a
literal, which is the dominant convention across this suite and is exactly the shape the regex
cannot see. SC-09 ("every file in `tests/integration/` spawns at least one child process ... The
probe output ... is the grading set") cannot be honestly graded against this instrument as written:
it currently says the opposite of what's true for most of the kind it's meant to police.

### Locally-run obligation — the moved probe's registration is broken (open question, not resolved by this diff)

Per dispatch: does the moved probe create a locally-run obligation, or is it excluded? Answer: it's
already registered (`test_kinds.omp_session_accessor`, `status: locally_run`, pre-existing from
issue #1187/DEC-201), so no *new* obligation is created — but the registration itself is now
**broken**. T-04 moved the file `git mv .../bin/probe-omp-session-accessor.py
tests/manual/probe-omp-session-accessor.py` (confirmed: old path `ls` fails, new path exists,
executable). `harness.json`'s `omp_session_accessor.detect` and `.cmd` still read
`.claude/skills/harness/bin/probe-omp-session-accessor.py` — unchanged by this diff, confirmed by
direct read. No task in the plan (T-04's files list, T-05's files list) touches this kind's entry.
The diff clearly touches this kind's `detect` surface (it moved the file the glob names) without
updating the registration, so per the locally-run rule this is not a soft skip — it needs either a
harness.json fix pointing the kind at the new path, or a stated reason it's intentionally left for a
later feature. No recorded locally-run execution exists under this feature's `notes/` either way.

## Verdict detail

```yaml
VERDICT: FAIL
DIGEST:
  headline: >
    SC-05's sole-implementation sweep is unimplemented, SC-01/SC-02's own --strict instrument is
    red on stale baseline drift, and SC-09's children instrument is a static scan that misreports
    most of tests/integration/ as spawning nothing — migration mechanics themselves are solid.
  suite: fail
  failures: 1
  matrix_ok: false
  kinds:
    - kind: unit
      state: satisfied
      cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit"
      named_tests: 20
    - kind: integration
      state: satisfied
      cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration"
      named_tests: 40
  coverage_gaps:
    - "SC-05 sole-implementation sweep (T-05 intent step 2b: exemption list, positive control, >=90 floor, 3-shape red proof) is absent from tests/unit/test-suite-layout.py"
    - "suite-census.py children is a static text regex over source, not the dynamic subprocess/os.system/os.fork/os.posix_spawn instrumentation T-05 item 9 specifies; false-negatives 29 of ~40 tests/integration/ files including test-board-lifecycle.py, which demonstrably forks via subprocess.run([sys.executable, SCRIPT], ...)"
    - "notes/research-tests-layout.md baseline is stale against the current tree (~20 files drifted since 56a30a0, unrelated to this migration's own edits), so verdict-lines --strict fails as staged"
    - "harness.json test_kinds.omp_session_accessor.detect/.cmd still name the pre-move bin/ path; the probe now lives at tests/manual/probe-omp-session-accessor.py and the old path does not exist"
  sc_evidence:
    - { id: SC-01, test: "tests/manual/suite-census.py verdict-lines --strict (T-05 verify) — FAIL, exit 1, ~20 baseline mismatches" }
    - { id: SC-02, test: "same instrument/run as SC-01 — FAIL" }
    - { id: SC-03, test: "tests/integration/test-check-domain.py:1857-1878 (11 named route-grant assertions) — PASS" }
    - { id: SC-04, test: "tests/integration/test-run-unit-tests-layout.py (4 violation cases, message-asserted) — PASS, 9/9" }
    - { id: SC-05, test: "tests/unit/test-suite-layout.py — sole-implementation sweep absent — FAIL" }
    - { id: SC-06, test: "tests/unit/test-suite-layout.py 'detect matches template' / 'excludes .claude' — PASS" }
    - { id: SC-07, test: "tests/manual/suite-census.py residue (working-tree; --ref <review_sha> not yet gradable, no commit exists) — PASS, 3/3 exemptions covered" }
    - { id: SC-08, test: "tests/unit/test-suite-layout.py 'manual tests are not actively detected' — PASS" }
    - { id: SC-09, test: "tests/manual/suite-census.py children — instrument does not match its own spec, false negatives across most of tests/integration/ — FAIL / not gradable as delivered" }
    - { id: SC-10, test: "tests/manual/suite-census.py migration --floor 58 --base origin/main --deleted test-run-unit-tests-kinds.py — PASS, exit 0" }
  open_questions:
    - { id: Q1, question: "harness.json's omp_session_accessor (locally_run) kind still points detect/cmd at the pre-move bin/ path T-04 deleted; no task updates it and no locally-run run is recorded under notes/. Fix in this feature, or defer explicitly?", blocking: true }
    - { id: Q2, question: "Should T-05's verify keep --strict on verdict-lines given D-18's own admission that the baseline has a one-review shelf life, or should the baseline be re-derived immediately before this merges?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-47-tests-layout/notes/qa-gate-FEAT-47.md
```
