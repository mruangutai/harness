# Research — FEAT-47 tests layout — 2026-08-31, re-derived at `56a30a0` 2026-08-31

**BLUF.** Both fog items in `.harness/notes/grilling-tests-layout-2026-08-31.md` are resolved by
measurement, and three of that artifact's counts are wrong. The kind split reassigns **12 files**
(all unit to integration, none the other way). `bin/fixtures/` is **test support** and travels;
`feature-schema.json` is **production** and stays. The migration is larger than "fix ~18 depth
climbs": **all 60 files measured — the 59 tests plus the probe — resolve `bin/` implicitly or by
depth, and every one of the 59 that move needs an anchor edit** (the 60th,
`test-run-unit-tests-kinds.py`, is deleted in place). Baseline census below is the load-bearing
input to SC-01.

**Re-derivation, and why this file carries two refs.** Everything here was first measured at
`ea6f51f`. FEAT-45 then merged, adding `test-panel-findings.py`, `test-plan-panel.py` and
`panel_findings.py` to `bin/`, and this branch was rebased onto `origin/main` `75daa3b`
(worktree head `56a30a0`, whose `bin/` is identical to that ref). Every count below is now stated
at `56a30a0` with the `ea6f51f` value kept beside it, so a later reader can tell a re-derivation
from an error. Nothing but counts and two baseline rows changed: the criterion, the sub-rules and
the fixture and schema rulings all re-derived unchanged.

## Corrections to the grilling artifact (measured at `ea6f51f`, re-derived at `56a30a0`)

| It says | Measured | How |
|---|---|---|
| 55 python tests, 28 unit / 27 integration | **58**, **31** unit / 27 integration at `56a30a0` (56, 29/27 at `ea6f51f`), no duplicates, no overlap | parse both arrays out of `run-unit-tests.sh`, compare to `glob('bin/test-*.py')` |
| 40 non-test `.py` helpers stay | **43** at `56a30a0` (42 at `ea6f51f`; `panel_findings.py` is the addition) | `glob('*.py')` minus `test-*` and `probe-*` |
| 3 live references to `bin/test-` paths | **6**, unchanged — FEAT-45's three files name none | see the table under *Live references* |

Nothing else in that artifact's `## Facts I verified` failed re-derivation.

## Fog 1 — the per-file kind, by measurement not by feel

Issue #160's principle is in-process versus driving a real script. A grep for `subprocess` cannot
answer it: `test-factory-gh.py` has 93 `subprocess.` mentions and spawns **nothing** (it patches
`subprocess.run`), while `test-harness-merge.py` has zero and forks 43 times through `os.fork`.
So both probes were runtime ones, run from the repo root as the runner does — one counting
`Popen`/`os.system`/`os.fork`/`posix_spawn`, one recording the child's identity.

**Criterion, stated so a later reader can apply it to a new file:** a test is `integration` iff any
assertion depends on behaviour observed **in a process other than the test's own** — the artifact
forked as a script, the artifact's own module re-entered in a child, or a child spawned to observe
cross-process semantics (a lock, a concurrent write, a git hook firing). It is `unit` iff every
assertion is observable in-process. Three sub-rules, each with the exemplar that forced it:

- A child that only **builds a fixture** does not count. `test-code-grade.py` forks `git` 89 times
  to build repositories and imports `code_grade` in-process. Unit.
- A child that is a **stub standing in for a dependency** does not count — it is a mock that happens
  to be a process. `test-gh-board.py` forks `fake-gh`; `gh_board` itself runs in-process. Unit.
- A shim that only **re-enters a test suite in another interpreter** inherits that suite's kind.
  `test-omp-hooks.py` forks `bun test omp-hooks.test.ts`, whose cases stub `getSessionFile`. Unit.

**The 12 reassignments (unit → integration), with the child each one drives.** The first ten were
measured at `ea6f51f`; the last two arrived with FEAT-45 and were classified at `56a30a0` by the
same criterion, not by the `UNIT_SCRIPTS` entry FEAT-45 gave them:

| file | child observed |
|---|---|
| test-board-lifecycle.py | `python3 board_lifecycle.py` x54 |
| test-board-station.py | `python3 board-station.py` x13 |
| test-branch-create-gate.py | `branch-create-gate.sh` x7 |
| test-check-omp-port.py | `python3 check-omp-port.py` x8 |
| test-factory-decompose.py | `os.fork` x2, concurrent writers of one file |
| test-feature-json-merge.py | `python3 feature-json-merge.py` x5, plus `os.fork` |
| test-inject-expertise.py | `inject-expertise.sh` x17 |
| test-layout-migration.py | `check-state.sh` x6 |
| test-sync-agent-adapters.py | `python3 sync-agent-adapters.py` x4 |
| test-validate-feature-json.py | `validate-feature-json.py` x6 |
| test-panel-findings.py | `python3 panel_findings.py id --reader … --summary …` — the real CLI, asserting its exit-code contract (2 on an empty reader, 2 on a whitespace-only summary). The pure-function half is loaded in-process via `importlib`, but the CLI cases are not, so the file is integration on the whole |
| test-plan-panel.py | `check-domain.sh --resolve <path>` x3 call sites, asserting the resolver's `stdout` and returncode. Not a stub and not a fixture builder: the gate script IS the thing whose answer the assertion depends on |

No file moves integration → unit. Final classification of the 58 at `56a30a0`: **19 unit, 39
integration**, against today's arrays' 31/27. One of the 39, `test-run-unit-tests-kinds.py`, is
deleted in place rather than moved, so **19 and 38 move**, and `tests/integration/` additionally
receives FEAT-48's `test-run-pool.py` and the new guard test. At `ea6f51f` the same criterion gave
19 and 37 over 56 files; only FEAT-45's two moved the integration figure.
`test-hooks-install.py` stays integration on the first sub-rule's
mirror image: its 121 `git` children are not fixtures alone — `git merge` **executes the installed
hook**, which is the artifact.

## Fog 2 — fixtures and the schema

- **`bin/fixtures/` is test support. It travels.** Four files, two consumers, both integration:
  `test-check-plan-routes.py:24` (`FIXTURE_DIR = BIN_DIR/"fixtures"`) and
  `test-validate-digest.py:23` (`HERE/"fixtures"`). A repo-wide grep for the directory finds no
  other live reader. Destination `tests/integration/fixtures/` — one directory, because both
  consumers land in the same kind.
- **`feature-schema.json` is production. It stays in `bin/`.** `feature_schema.py:45` reads it at
  runtime as `BIN_DIR/feature-schema.json`, `feature_schema.py:68` names the same path as
  `SCHEMA_REL`, and `check-domain.sh:1170` names it in the text of a **write denial**. Tests read it
  too, but a production loader owns it.
- **Residue, stated rather than discovered later.** `layout_fixtures.py` is test support (imported
  only by `test-check-state.py` and `test-layout-migration.py`) and stays in `bin/` under the
  settled scope. The guard therefore makes `bin/` free of test-**named** files, not of test
  **support**. Left for #979.

## The anchor problem — the real bulk of the work

Every one of the 57 files measured is location-dependent: **25** import a `bin` module by bare name
(`import factory_claim`), relying on the interpreter putting the script's own directory on
`sys.path`; **51** derive a path from `__file__`; **19** do both; **0** do neither. **16** carry a
literal four-level `..` climb to the repo root. So the move breaks every file, not eighteen of them,
and the failure is an `ImportError` at line 1 rather than a subtle wrong answer — which is why a
per-file "does it still run" verify is a sufficient proof for the move tasks.

Two names change meaning and must not be renamed mechanically: where a file uses its own directory
as *the artifact's* directory it becomes `BIN_DIR`; where it uses it as *the test's own* directory
(`FIXTURE_DIR`) it becomes the tests directory.

## Live references (6, not 3)

| site | why it breaks |
|---|---|
| `.harness/harness.json` `test_kinds.{unit,integration}.detect` | names `bin/` paths and 27 literal files |
| `test-no-distribution.py:98-105` `ALLOW_LIST` | exactly two entries, both `bin/` paths; a stale entry un-exempts a moved file and case 2 goes red |
| `test-code-grade-cli.py:45-47,71-93` | its synthetic repo's `unit.detect` and fixture path model the old layout |
| `test-check-plan-routes.py:162-167` `case_13` | asserts `run-unit-tests.sh` **lists** this test — dies with the arrays |
| `test-check-domain.py:1749-1757` | docstring names `tests/**` as product code that resolves to NOBODY; false once it is control-plane |
| `.github/CODEOWNERS:22-27` | comment explains the ownership by the array mechanism |

**Not touched, deliberately:** `DECISIONS.md` carries **zero** line anchors into any file this
feature moves or edits (measured: 2 path-form mentions of moved files, both anchorless; 0 anchors
into `run-unit-tests.sh`, `harness_boundary.py`, `team-config.yaml`, `harness.json`), so the
anchor-rot check is not in play. Historical notes and receipts under `.harness/` stay as written.

## Baseline census — re-derived at `56a30a0`, all 58 files `rc=0`

Invocation, from the repo root, per file, exactly as the runner invokes it
(`python3 <path>`), counting output lines whose first whitespace-delimited token, **with any
trailing colon stripped**, is `ok`, `PASS` or `FAIL`, plus lines beginning `not ok`.

**The colon is load-bearing and was nearly lost.** `test-hooks-install.py`,
`test-post-merge-sweep.py` and `test-worktree-terminal.py` print `PASS: (e) …`, not `PASS …`. A
literal first-token reading scores all three at **0** against rows of 29, 52 and 34 — three rows
wrong by construction and a `--strict` run permanently red on a correct tree. Measured both ways
at `56a30a0` against the 56 rows first recorded at `ea6f51f`: the colon-stripping rule reproduces
**54** of them, the literal rule **51**. The plan's T-05 step 9 now pins the colon-stripping rule
in the instrument's own specification.

**What moved, and why.** Two rows changed and two were added, all four attributable to FEAT-45 and
to nothing else: `test-check-state.py` 145 → **147** and `test-validate-digest.py` 114 → **117**
(FEAT-45 added INV-32 cases to both), and `test-panel-findings.py` **10** and
`test-plan-panel.py` **28** are new files that now carry rows rather than being reported as
`new`. A migrated file with no baseline row is a file whose anchor repair `verdict-lines` cannot
see, which is the reason for adding them rather than leaving them rowless. The other 54 rows
re-derived byte-identical.

```text
test-bash-write-guard.py	109
test-board-lifecycle.py	163
test-board-station.py	16
test-branch-create-gate.py	8
test-check-decision-anchors.py	8
test-check-domain.py	285
test-check-expertise.py	32
test-check-omp-port.py	19
test-check-plan-routes.py	122
test-check-state.py	197
test-code-grade-cli.py	1
test-code-grade.py	1
test-dispatch-guard.py	42
test-expertise-merge.py	39
test-factory-claim.py	120
test-factory-cli.py	33
test-factory-config.py	112
test-factory-decompose.py	162
test-factory-gh.py	244
test-factory-integration.py	131
test-factory-land.py	64
test-factory-workspace.py	30
test-feature-json-merge.py	38
test-feature-worktree.py	112
test-gate-policy.py	27
test-gen-decisions-index.py	14
test-gh-board.py	44
test-gh-close-gate.py	48
test-gh-cost-log.py	39
test-gh-sync.py	301
test-harness-boundary.py	27
test-harness-merge.py	19
test-harness-yaml-corpus.py	16
test-harness-yaml.py	22
test-hooks-install.py	29
test-inflight-registry.py	120
test-inject-expertise.py	17
test-layout-migration.py	41
test-lead-stop-and-wake.py	17
test-merge-gitignore.py	7
test-merge-settings.py	22
test-no-distribution.py	35
test-observations-merge.py	33
test-omp-hooks.py	0
test-orchestrator-playbook.py	17
test-panel-findings.py	10
test-config-shape-matrix.py	10
test-plan-merge.py	285
test-plan-panel.py	28
test-post-merge-sweep.py	52
test-render-brief.py	15
test-run-unit-tests-kinds.py	23
test-sync-agent-adapters.py	19
test-team-catalog.py	10
test-upgrade-config.py	12
test-validate-digest.py	140
test-validate-feature-json.py	69
test-wayfind.py	2
test-worktree-terminal.py	42
```

Total 3700 over 59 files, re-derived at `06bd60c8`. `test-run-unit-tests-kinds.py` (23) is deleted
by this feature, so the 58 migrated files must still total **3677**, each file individually equal
to its row above. Three
rows are low because those suites print their own summary format (`test-omp-hooks.py` delegates to
`bun`); a row equal to its baseline is still the assertion, whatever the row's absolute meaning.

**This block is the one artifact a sibling merge invalidates without breaking anything**, and it
has now done so twice: FEAT-48 moved the enumeration in an earlier draft, FEAT-45 moved two rows
here. There is no derived form of it — a per-file assertion count cannot be computed from the
tree without running the tree — so it stays literal, carries its ref, and D-18 gives it a
one-review shelf life so its inevitable staleness reports rather than reddens.

**Runtime, measured at `ea6f51f` and NOT re-derived at `56a30a0`:** `--kind unit` 20s / rc 0,
`--kind integration` 152s / rc 0. FEAT-48's pool changes both, so re-measuring here would be
re-measuring a scheduler this feature does not touch; the figure is kept as the pre-pool serial
reference only. The CI comment
claiming "12 scripts, ~15s" for integration is stale by 15 scripts; out of scope here.

## Open

- The census tool is `tests/manual/suite-census.py`, created by T-05 (this line named a different
  filename before the plan settled on that one). Without it the per-file proof is a 25-line inline
  script pasted into two verifies.
- `run-unit-tests.sh --check-kinds` becomes `--check-layout`, keeping the millisecond mode that
  makes the guard's own cases cheap. The argument-parser regression cases in the deleted
  `test-run-unit-tests-kinds.py` (case 5) are absorbed by the new integration test, not dropped.
- **Parallel safety is a separate note.** The 247s serial baseline, the per-worker measurements and
  issue #1053 are in the BRIEF's Problem section and in D-09 to D-12; the identification of the
  colliding sibling is T-07's deliverable and lands in `notes/research-parallel-safety.md`, which
  does not exist yet.
