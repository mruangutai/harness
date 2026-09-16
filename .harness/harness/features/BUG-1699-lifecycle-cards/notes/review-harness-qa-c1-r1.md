# QA final matrix gate — BUG-1699 lifecycle cards, c1-r1

**Verdict: PASS.** Final head `d7310f865e03534c233085e5f0a768eb9eca4687` passes both required matrix kinds and the exact signed T-01 command. The prior QA-03 form gap is resolved by correctly labelled, criterion-specific reconstructed mutation proofs; the receipt-only final commit leaves the fixed behavior from `0e1fdc22f6f9f139cb79bc69c66e1185650864c1` intact.
Reviewed range: `8ef4731e816f08dbc562206134c100b0c034a812..d7310f865e03534c233085e5f0a768eb9eca4687`; corrective-evidence range: `0e1fdc22f6f9f139cb79bc69c66e1185650864c1..d7310f865e03534c233085e5f0a768eb9eca4687`.


## Phase 1 requirements-derived floor

Before source review, `BRIEF.md` and `plan.yaml` required unit coverage for SC-11 and integration coverage for SC-01–10 and SC-12–14. T-01–04 are `cross_module`, so `.harness/harness.json:174-178` requires both unit and integration. SC-15/16 are inspection-only; no other configured kind is implicated.

## Final-head execution

| Scope | Exact command | Discovery/count and exit |
|---|---|---|
| unit matrix | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 40 files, 0 failures, exit 0 (9.01s) |
| integration matrix | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 72 files, 0 failures, exit 0 (98.99s) |
| signed T-01 | `python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py` | all seven named runners reached their pass marker; exit 0 (54.06s) |

No runner had a load, import, collection, discovery, or assertion failure. `matrix_ok: true`.

## Fail-first and fixed-tip evidence

| SC | Fixed-tip test evidence | Fail-first evidence |
|---|---|---|
| 01–05 | `tests/integration/test-station-argument-spelling.py:288` | `receipt-main-direct-validation-c1.md:14` (11 pre-repair ordering violations) |
| 06–07 | `tests/integration/test-plan-merge.py:3340,3360` | `receipt-main-direct-validation-c1.md:13` (24 pre-repair assertions) |
| 08 | `tests/integration/test-gh-sync-ship.py:33-46` | **Reconstructed mutation proof:** `receipt-harness-backend-dev-fix-c1-r1.md:11`; parent omitted from `sources + parents`, named #40 Done assertion reddened, exit 1. |
| 09 | `tests/integration/test-board-lifecycle.py:1148-1232` | `receipt-main-direct-validation-c1.md:15` (10 pre-repair all-card reconcile failures) |
| 10 | `tests/integration/test-gh-sync-record.py:270-276`; `tests/integration/test-plan-merge.py:3438` | `receipt-main-direct-validation-c1.md:13,16` (local-first/reset and powered no-network red) |
| 11 | `tests/unit/test-gh-board.py:430-448` | `receipt-harness-backend-dev-T-01-c0.md:9-15` (active-phase projection red) |
| 12 | `tests/integration/test-gh-sync-record.py:243-276` | **Reconstructed mutation proof:** `receipt-harness-backend-dev-fix-c1-r1.md:12`; abandoned #43 admitted by changing terminal exclusion, exact-projection assertion reddened in every active phase, exit 1. |
| 13 | `tests/integration/test-gh-sync-ship.py:47-54` | **Reconstructed mutation proof:** `receipt-harness-backend-dev-fix-c1-r1.md:13`; injected `issue close` into `cmd_ship.write_done`, named call-log assertion reddened, exit 1. |
| 14 | `tests/integration/test-gh-sync-ship.py:128-157` | **Reconstructed mutation proof:** `receipt-harness-backend-dev-fix-c1-r1.md:14`; removed `_place(..., stations=stations)`, named ordering and source-child refresh assertions reddened, exit 1. |

For SC-08/12/13/14 I confirmed the live fixed subjects and assertions: `gh-sync.py:2194-2235` has the shared refresh and source-plus-parent loop; `gh_board.py:126-159,190-213` retains active all-card projection and terminal exclusion; the cited assertions bind precisely those effects. The reconstruction receipt explicitly distinguishes these from historical failure (`:16`), records restoration (`:20`), and its recorded restored SHA-256 values equal the final-head files. This final run supplies each fixed-tip green counterpart. `d731..0e1fd` changes only that receipt.

## Original finding dispositions

| Finding | Disposition | Evidence |
|---|---|---|
| QA-01 | resolved | Unit matrix: `test-omp-hooks.py` 75 pass/0 fail; pre-repair 73/2 at `receipt-main-direct-validation-c1.md:17`. |
| QA-02 | resolved | Integration matrix passed; factory 131/131 at `receipt-main-direct-validation-c1.md:30`. |
| QA-03 | resolved | Criterion-specific SC-08/12/13/14 reconstructions above; all are honestly labelled reconstructed, not historical. |
| QA-04 | resolved | Powered no-network control at `receipt-main-direct-validation-c1.md:16`; current `test-plan-merge.py:3438`. |
| CR-01 | resolved | Corrective receipt `:20` restored `gh_board.py`; its stated final grade is 4; current unit and T-01 proof pass. |
| CR-02 | resolved | Corrective receipt `:20` restored INV-26 fixture; its stated final grade is 4; current integration and T-01 proof pass. |

No regression or new unowned finding was observed; no scope change is required.
