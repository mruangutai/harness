# Research — FEAT-47 tests layout — 2026-08-31

**BLUF.** Both fog items in `.harness/notes/grilling-tests-layout-2026-08-31.md` are resolved by
measurement, and three of that artifact's counts are wrong. The kind split reassigns **10 files**
(all unit to integration, none the other way). `bin/fixtures/` is **test support** and travels;
`feature-schema.json` is **production** and stays. The migration is larger than "fix ~18 depth
climbs": **all 57 files measured — the 56 tests plus the probe — resolve `bin/` implicitly or by
depth, and every one of the 56 that move needs an anchor edit** (the 57th,
`test-run-unit-tests-kinds.py`, is deleted in place). Baseline census below is the load-bearing
input to SC-01.

## Corrections to the grilling artifact (measured at `ea6f51f`, worktree clean)

| It says | Measured | How |
|---|---|---|
| 55 python tests, 28 unit / 27 integration | **56**, **29** unit / 27 integration, no duplicates, no overlap | parse both arrays out of `run-unit-tests.sh` at `ea6f51f`, compare to `glob('bin/test-*.py')` |
| 40 non-test `.py` helpers stay | **42** | `glob('*.py')` minus `test-*` and `probe-*` |
| 3 live references to `bin/test-` paths | **6** | see the table under *Live references* |

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

**The 10 reassignments (unit → integration), with the child each one drives:**

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

No file moves integration → unit. Final split: **19 unit, 37 integration** (36 moved plus the new
guard test), against today's 29/27. `test-hooks-install.py` stays integration on the first sub-rule's
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

## Baseline census — measured at `ea6f51f`, all 56 files `rc=0`

Invocation, from the repo root, per file, exactly as the runner invokes it
(`python3 <path>`), counting output lines whose first token is `ok`, `not ok`, `PASS` or `FAIL`:

```text
test-bash-write-guard.py	101
test-board-lifecycle.py	160
test-board-station.py	12
test-branch-create-gate.py	8
test-check-decision-anchors.py	8
test-check-domain.py	203
test-check-expertise.py	32
test-check-omp-port.py	17
test-check-plan-routes.py	92
test-check-state.py	145
test-code-grade-cli.py	1
test-code-grade.py	1
test-dispatch-guard.py	42
test-expertise-merge.py	39
test-factory-claim.py	120
test-factory-cli.py	33
test-factory-config.py	90
test-factory-decompose.py	162
test-factory-gh.py	244
test-factory-integration.py	131
test-factory-land.py	64
test-factory-workspace.py	30
test-feature-json-merge.py	38
test-feature-worktree.py	112
test-gate-policy.py	27
test-gen-decisions-index.py	11
test-gh-board.py	26
test-gh-close-gate.py	48
test-gh-cost-log.py	39
test-gh-sync.py	273
test-harness-boundary.py	11
test-harness-merge.py	19
test-harness-yaml-corpus.py	16
test-harness-yaml.py	21
test-hooks-install.py	29
test-inflight-registry.py	112
test-inject-expertise.py	17
test-layout-migration.py	41
test-lead-stop-and-wake.py	19
test-merge-gitignore.py	7
test-merge-settings.py	22
test-no-distribution.py	35
test-observations-merge.py	33
test-omp-hooks.py	0
test-orchestrator-playbook.py	11
test-plan-merge.py	110
test-post-merge-sweep.py	52
test-render-brief.py	15
test-run-unit-tests-kinds.py	23
test-sync-agent-adapters.py	19
test-team-catalog.py	10
test-upgrade-config.py	10
test-validate-digest.py	114
test-validate-feature-json.py	61
test-wayfind.py	2
test-worktree-terminal.py	34
```

Total 3152 over 56 files. `test-run-unit-tests-kinds.py` (23) is deleted by this feature, so the
55 migrated files must still total **3129**, each file individually equal to its row above. Three
rows are low because those suites print their own summary format (`test-omp-hooks.py` delegates to
`bun`); a row equal to its baseline is still the assertion, whatever the row's absolute meaning.

**Runtime, same sha:** `--kind unit` 20s / rc 0, `--kind integration` 152s / rc 0. The CI comment
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
