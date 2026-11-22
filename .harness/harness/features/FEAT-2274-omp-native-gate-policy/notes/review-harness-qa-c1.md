# QA gate, cycle 1 — FEAT-2274 (run r-20261122-4-validate-validator)

Pin `649612d8bc0add67014613f208180a3344a6ac02`, baseline `1e0b014917125bc9aae1f30a2f6fd53ed239f3bc`. Gate run in a managed pinned checkout (`pinned-checkout.py`, persona `harness-qa`, HEAD verified = pin, clean); baseline reproduction in a second managed checkout (persona `harness-qa-base`, baseline source plus pin tests via `git checkout 649612d8 -- tests`). Both removed on return. `HARNESS_AGENT_TYPE` unset for runners (G-07).

## VERDICT: FAIL — the new SC tests are green, but the standing unit and integration kinds are red on 3 regression findings

Two unit-kind tests and one integration-kind test that PASS at baseline FAIL at the pin. None is in T-01/T-02/T-03's task-local verify, which is why the task gates were green. They are not the known baseline failures (canonical-reader self-test), which I did not rerun.

## Findings (all `regression`, owner T-01, assertion failures, not load errors)

1. **F-1, severity high — `tests/unit/test-lead-start-preflight.py` case `[control] BUG-2141/lead-eng` (line ~381).** It asserts "lead -> harness-eng-lead keeps its existing spawns allowlist refusal" (`refused_before_claim` and `"spawns: list"` in stderr). Scenario: product-lead dispatches eng-lead with otherwise valid inputs. dispatch-guard now passes it through, by SC-06's own design (exit=0, claim=yes, receipt=yes, stderr=''). A stale pre-cutover assertion was not migrated. Standing `run-unit-tests.py --kind unit` exits 1 (60 of 61). Passes at baseline (own reproduction, exit 0).
2. **F-2, severity med — `tests/unit/test-code-grade.py` self-grading gate.** The new `run_feat65_guard_cases` and `run_feat2274_unavailable_cases` in `tests/integration/test-validate-digest.py` (lines 5340 and 5436) grade below the bar of 3 for self-graded test files: `FAIL ...run_feat65_guard_cases grade >= 3` and `...run_feat2274_unavailable_cases grade >= 3`. Scenario: any CI run of the unit kind. The test passes at baseline with baseline tests (exit 0). Fix is to split the functions or record a CR-01 allowlist entry, which is Main's call.
3. **F-3, severity med — `tests/integration/test-gen-decisions-index.py::test_committed_index_is_complete_and_within_budget`.** 5 rows of DECISIONS-INDEX.md exceed the 30-word ruling cap: DEC-204 (38), DEC-234 (37), DEC-118 (33), DEC-208 (33), DEC-100 (31). The T-03 amendment tails were not shortened, and T-03's verify never ran this test. Standing `--kind integration` exits 1. Passes at baseline (exit 0). The index still matches a fresh regeneration (T-03 `diff` clean).

## Final gate results at the pin

| Command | Result |
|---|---|
| T-01 `test-omp-native-gate-runtime.py` | exit 0, 445 passed, 0 failed |
| T-01 `test-omp-hooks.py` (runs `omp-hooks.test.ts`) | exit 0, 179 pass, 0 fail |
| T-01 `test-harness-boundary.py` | exit 0, ALL PASS |
| T-02 `test-harness-constraints.py` | exit 0, 14 passed |
| T-03 `gen-decisions-index.py --stdout \| diff` | clean |
| `run-unit-tests.py --kind unit` (cmd from harness.json) | exit 1: 63 files, 2 failing files (F-1, F-2) |
| `run-unit-tests.py --kind integration` | exit 1: 91 files, 1 failing file (F-3) |

The `FAIL BUG-1290 ...` lines in the unit log are test-factory-claim-mutation's deliberate mutation-proof output (G-09), not counted; the runner exit decides.

## Matrix and kinds

Matrix from the control-plane `.harness/harness.json`. T-01 is `cross_module`, which requires unit and integration. T-02 is `config`, with integration only `when: touches_config_shape`; integration is required by T-01 regardless. T-03 is `docs`, with no kinds. `matrix_ok: false`: standing cmds are red.

- unit: active; named tests for this change ran nonzero (179 TS tests, boundary cases, runtime, dispatch cases). It is red on the standing cmd (F-1, F-2).
- integration: active; named tests ran nonzero (445 runtime cases, 14 constraints, extended gate suites). It is red on the standing cmd (F-3).
- functional and eval: `excluded`, signed DEC-187 (`not_applicable`; no SC rests on them).
- component and ui: `unresolved`, cmd null. The matrix names them only for `frontend` or `feature` types, which this feature does not have, so they are not required here.
- typecheck: `unresolved`, cmd null. Not in the matrix; known gap #2257, no compiler claim made.
- `locally_run` kinds: the diff touches none of their detect surfaces.

No misconfiguration: every failure is a named assertion, not an import or collection error.

## Fail-first per automated SC (pre-fix red proven by my own reproduction at the immutable baseline `1e0b0149` with pin tests, in addition to Main's captured receipts)

Own baseline reproduction (all exit 1, assertion failures; logs `/tmp/qa2274/base/*.log`, not durable): runtime suite `3 passed, 442 failed`; `omp-hooks` 20 fail of 179; boundary 7 failures; constraints `3 passed, 11 failed`; check-domain 4; bash-write-guard 4; dispatch-guard 8 (160 of 168); validate-digest 7; gh-close-gate 49; branch-create-gate 36 (44 of 80); plan-sign-gate 67. Receipts by Main under `notes/`: `t01-red-runtime.md`, `t01-red-ts.md`, `t01-red-py-broad.md`, `t01-red-py-narrow.md`, `t02-red-green.md`.

| SC | Test at pin | Pre-fix red |
|---|---|---|
| SC-01 | `tests/integration/test-omp-native-gate-runtime.py` (broad guarded crash, startup, missing, interpreter, spawn, SIGKILL per gate); `tests/unit/test-harness-boundary.py` feat2274_*; `test-dispatch-guard.py:513 case_f2274_unavailable_outcome` | baseline repro red; `notes/t01-red-runtime.md`, `t01-red-py-broad.md` |
| SC-02 | `test-omp-native-gate-runtime.py` narrow-gate cases; `test-gh-close-gate.py`, `test-branch-create-gate.py` (incl. `run_issue_2107:382`), `test-plan-sign-gate.py` corpora; `omp-hooks.test.ts` narrowGateApplies, classifyPolicyRun | baseline repro: 49/36/67 fail; `notes/t01-red-py-narrow.md`, `t01-red-ts.md` |
| SC-03 | `tests/unit/omp-hooks.test.ts:2305` before_subagent_spawn refuses a harness target outside task, for Main and governed parents alike | baseline repro: in the 20 TS fails; `notes/t01-red-ts.md` |
| SC-05 | `tests/integration/test-harness-constraints.py` lines 57–99 (exact agents, alwaysApply, five groups, two exclusions, three lead guidance cases) | baseline repro 11 fail; `notes/t02-red-green.md`. Note: the 3 passes are the vacuous exclusions plus the RULES.md control. |
| SC-06 | `test-dispatch-guard.py:1198, 1218, 1228` (27a, 27c, 27e: formerly refused, now passes the guard) | baseline repro: the 27a/27c/27e FAILs plus the f2274 cases; `notes/t01-red-py-broad.md` |
| SC-07 | `omp-hooks.test.ts:2172, 2184, 2196, 2221, 2229, 2246, 2259, 2287` | baseline repro in the 20 TS fails; `notes/t01-red-ts.md` |
| SC-09 | runtime suite controls and `validate-digest` unknown schema; digest refusal controls; `test-validate-digest.py:run_feat2274_unavailable_cases`; omp-hooks deny and pass cases | unavailable assertions red at baseline (7 validate-digest fails); controls (normal pass, explicit deny, absent/null/empty digest_object stay refusals, merge-gate fail-closed at `omp-hooks.test.ts:2111`) green at baseline in `t01-red-runtime.md` section B, as intended |

Limit: the SC-06 sub-claim that the other dispatch-guard checks are retained rests on the unchanged green dispatch-guard suite (168 cases at the pin). I ran no per-check mutation proof; discrimination of the retained checks is unshown, not disproven.

## Coverage gaps (Phase 1 vs tests)

- SC-04 and SC-08 are inspection (no test required).
- No Phase 1 expectation lacks a test. The SC-05 native delivery claim is deliberately unbound to a live OMP session (approved gap); no rule-selection or compiler claim is made.
- Stale-caller gap: `test-lead-start-preflight.py` was not swept in the clean cutover (F-1).

## Scope exceptions

- No TypeScript typecheck (#2257), approved.
- External omp 19.1.0 evidence is not in the pin, approved.
- The two known baseline canonical-reader failures were not rerun and are not part of the runner's failing set.
