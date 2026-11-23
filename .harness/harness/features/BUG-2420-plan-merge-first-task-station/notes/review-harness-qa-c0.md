# BUG-2420 QA gate, validate run 2026-11-22-03-validate-validator, c0

**BLUF: PASS.** Every SC has a test that fails at the pre-fix base and passes at the pin. Both required receipts are green at `c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`. The literal T-01 verify exits 0. Two advisory test-strength observations, no blocking finding.

## Phase 1 (from BRIEF/plan only, before reading source)
Expected tests:
- E1 (SC-01): three-row table over set-task-station. A status-less task gains `status: building` at its field indent with STATION/APPLIED output. An existing status is rewritten with every other byte unchanged. An absent task exits 3 with absence wording, no write, and the present-id list.
- E2 (SC-01): a nested `status:` line in verify prose is never taken for the task's own status. The task's own status is not confused with a later task's.
- E3 (SC-02): the approval block is byte-compared before and after, including `status: approved`. Insertion success is required, so a failed no-op cannot satisfy it.
- E4 (SC-03): integration. `tasks: []`, apply T-01 with no status, assert nothing was seeded, set building, exit 0, reload shows building.
- E5: matrix floor. `bugfix` has `always: []`. `when` unit fires for touches_runtime_code (stations.py changed). `when` integration fires for fix_confined_to_tests_and_contract_docs, which is not true here. The BRIEF additionally requires integration for the drafting path, so I run both active kinds.

Gap against Phase 1 after reading the tests: none. E1 to E4 all have tests.

## Matrix and kinds
- unit: satisfied. `.claude/skills/harness/bin/run-unit-tests.py --kind unit`, 66 files, receipt `runs/2026-11-22-03-validate-validator/qa/manifest-unit.json`.
- integration: satisfied. `--kind integration`, 95 files, receipt `.../qa/manifest-integration.json`.
- typecheck: not claimed. Python-only patch; this is a TypeScript surface.
- Other kinds are excluded, unresolved or locally_run, none touched by the diff.

Production runner command, run from the managed pin (HARNESS_AGENT_TYPE and HARNESS_PROJECT_DIR unset):
`python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <unit|integration> --shard 1/1 --manifest <F>/runs/2026-11-22-03-validate-validator/qa/manifest-<kind>.json`
Pin: `.claude/worktrees/.pins/BUG-2420-plan-merge-first-task-station--2026-11-22-03-validate-validator--harness-qa`, HEAD = `c0c3f1b9d50ef7e196b8ab77805f79eb7f8169df`, clean.

Receipt content (read back, not hand-edited):
- unit: tested_commit = pin, runner_exit 0, 66 selected / 66 completed, none non-zero. It includes `tests/unit/test-plan-merge-first-station.py` (exit 0, 17 PASS rows) and `test-plan-merge-union-head.py`. Runner tail: `pool: 8 workers, 66 files, 39.23s wall`.
- integration: tested_commit = pin, runner_exit 0, 95 selected / 95 completed, none non-zero. It includes `tests/integration/test-plan-merge.py` (exit 0, including the four `2420:` rows). Runner tail: `ALL PASSED`, `pool: 8 workers, 95 files, 243.15s wall`.

### Honest record of the first (red) attempt, run under heavy concurrent load
My first receipts were written while I ran three other heavy jobs (the T-01 verify, a mutation panel, the second kind) on one host. Both runners exited 1:
- unit: `test-omp-hooks.py`, 4 BUG-1898 tests timed out at 5000 ms (210 pass / 4 fail), 172 s versus 28 s on the quiet rerun.
- integration: `test-check-plan-routes.py` hit a 60 s subprocess timeout (case_19, 82 s versus 106 s quiet pool time). `test-typescript-typecheck.py` failed with no `node_modules/.bin/tsc` in the fresh pin.
Neither touches stations.py or plan_merge. I did not grade them satisfied on that reasoning. I ran `bun install --frozen-lockfile` in the pin (git status clean after), then reran each kind alone, once each. Both returned 0 and overwrote the receipts. The green receipts above are those reruns. The red first-run outputs were `/tmp/qa2420/unit.out` and `integ.out` (ephemeral).
Caution for main: `test-omp-hooks.py` and `test-check-plan-routes.py` are load-sensitive. Do not run runner kinds in parallel on one host.

## Literal T-01 verify
Ran the verbatim block (identical to plan.yaml tasks[0].verify, diffed) with `BUG2420_TOOL_ROOT=<pin>` and `BUG2420_BASE=d5be53927009df8e7848f860f9d0b4b03b89f9ad`. Exit 0, 106 s. It printed:
- `git rev-parse HEAD` = `c0c3f1b9...`.
- Unit script: 17 PASS rows, 0 FAIL, `PASS test-plan-merge-first-station.py`.
- Integration script: 707 PASS lines in total, 0 FAIL, `PASS test-plan-merge.py`, including the four 2420 rows.
- check-plan-routes on plan.yaml: `0 violation(s) across 1 plan(s)`, preceded by the known `DEVIATION T-01 ... main-session-direct` line (owner-manifest note; exit 0, not a failure).
- Canonical reader audit: `0 unresolved reader site(s) across 101 Python file(s)`.
- Grades: `passing: 12`, `_task_station_site` grade 4 (bar 4), `_splice_station` grade 4 (bar 4), and `BUG-2420 grades PASS: production >=4, tests >=3`.

## Fail-first (my own reproduction, natural red, not mutation)
Base stations.py `d5be53927009df8e7848f860f9d0b4b03b89f9ad` has sha256 `ceef2a6b...738b9a`, matching notes/red-first-T-01.md.
- Unit: `PLAN_MERGE_STATIONS=<base stations.py> python3 tests/unit/test-plan-merge-first-station.py` exits 1 with 12 PASS and 5 FAIL:
  - Row 1 insertion `exactly the expected lines change`: the base rewrote `    status: prose` instead of inserting. SC-01.
  - `first station sits inside T-01's own mapping`. SC-01.
  - `T-01's verify prose keeps its own status: prose line`. SC-01 (nested verify-prose regression).
  - `first-station insert on a signed plan succeeds rc=3`. SC-02, the exact reported defect.
  - `signed approval block is byte-identical after the insert`. SC-02.
  Controls pass at base: row 2 (rewrite) 4/4, row 3 (absent) 4/4, and the absence-wording check.
- Integration: the pin's test file run with base stations.py, via `git checkout d5be... -- stations.py`, restored afterwards. Exit 1. `FAIL 2420: set-task-station gives the drafted task its first station (exit 0)` and `FAIL 2420: the written plan reloads with T-01 at building`. The two apply rows pass (`apply drafts T-01`, `does not seed a station`).
- Green: the same tests pass at the pin (receipts above).

## SC evidence
- SC-01: `tests/unit/test-plan-merge-first-station.py:91` (ROWS, three rows) and `:101` (`case_station_rows`).
- SC-02: `tests/unit/test-plan-merge-first-station.py:144` (`case_signed_approval_survives_the_first_station`). It requires `rc == 0` and the APPROVAL block verbatim, with `status: approved` count 1.
- SC-03: `tests/integration/test-plan-merge.py:5142` (`case_2420_drafted_task_takes_its_first_station`).

## Discrimination proofs (mutants in a separate disposable pin, restored; `git status` clean)
Each mutant is a one-site edit to stations.py at the pin. Result as (unit, integration):

| Mutant | Unit | Integration |
|---|---|---|
| M1 insert without field indent | red (4 fail) | red (non-zero exit) |
| M2 `_status_in_task` accepts a deeper `status:` (nested-prose regression) | red (3 fail) | green |
| M3 insert also flips `status: approved` to pending (approval proof) | red, `signed approval block is byte-identical` | green |
| M4 insert twice (duplicate key) | red | green |
| M5 absent task still writes | red | red |
| M6 rewrite also duplicates a line | red | red |
| M7 absent-task message says "no status line" | red (wording check) | green |
| M8 insert CRLF | green (see O-2) | green |

- Nested verify-prose regression: pinned by unit (M2), not by integration. It was also found as a real red at base.
- Approval proof discrimination: M3 kills it. The proof needs `rc == 0` as well as byte equality. At base it fails at `rc=3`, so an unchanged failed operation cannot satisfy it.
- 3-row table: M1, M5 and M6 each redden the rows. Three rows plus the 4-check-per-row loop exist as specified.
- Integration path: reddens at base via the drafting path, and M5 and M6 redden it via the existing set-task-station rows. It does not redden on M2/M3/M4/M7. Those are unit-owned by design.

## Observations (advisory, none blocking, no finding classified)
- O-1: the insertion row (SC-01 row 1) fails at base for a different reason than the filed rc=3 symptom. Its fixture T-01 carries `verify: | status: prose`, so the base rewrote the prose line and exited 0. The rc=3 symptom is reproduced by the SC-02 PLAIN fixture and by SC-03. Together the SC-01 insertion row does fail pre-fix as the BRIEF requires, but only the SC-02 and SC-03 tests carry the rc=3 symptom. Intent-satisfied.
- O-2: the unit file reads results with `read_text` (universal newlines) and diffs lines by membership. A CRLF vs LF difference in the inserted line is invisible (M8 green). The production splice appends `\n` explicitly, so no known defect. A byte-level compare would close it. Whether that is worth a follow-up is a question for main.
- Environment: runner receipts only valid from a quiet host; see the honest record above.

## Principles applied
- Build the Lever: ran the production runner and the literal verify rather than hand-assembling evidence. The one script `/tmp/qa2420/mut.py` (ephemeral) drove all mutant runs; the receipts are the runner's own files.

## Cleanup
Both managed pins (`harness-qa`, `harness-qa-mutation`) were removed with `pinned-checkout.py remove` on return. The control-plane and feature worktrees were not modified apart from the two ignored receipts and this note.
