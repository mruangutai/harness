# QA combined-tip gate — BUG-1699 lifecycle cards, c1

**Verdict: FAIL.** I verified immutable head `15fd356ff76e31c7b7ca4978c25819834c0ffe54` in a detached worktree. Both configured matrix kinds, the signed T-01 command, and focused T-03 checks pass. QA-03 remains open: the receipts do not contain criterion-specific *pre-fix* failures for SC-08, SC-12, SC-13, or SC-14. A generic red result is not proof that those criteria failed.

## Phase 1: requirements-derived matrix

Before reading implementation, I derived the following floor from `BRIEF.md`, `plan.yaml`, and the configured matrix. T-01 through T-04 are `cross_module`; therefore both active kinds are required:

| Kind | Required command | Required criteria |
|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | SC-11 |
| integration | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | SC-01–10, SC-12–14 |

SC-15 and SC-16 are inspection criteria. No AI, UI, local, browser, or host-gated test kind is implicated. The signed T-01 command is:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py
```

## Execution at the verified head

| Scope | Result | Evidence |
|---|---|---|
| configured unit matrix | pass | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` discovered and passed 40 files (14.63 s); includes `test-gh-board.py` and `test-omp-hooks.py` (`75 pass`, `0 fail`). |
| configured integration matrix | pass | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` discovered and passed 72 files (127.13 s). |
| signed T-01 | pass | Exact command above exited 0 (99.66 s); each of the seven named runners reported its terminal pass marker. |
| focused T-03 | pass | `python3 tests/integration/test-station-argument-spelling.py && python3 tests/integration/test-sync-command-adapters.py && python3 .claude/skills/harness/bin/sync-command-adapters.py --check` exited 0. The station test exercised its eight negative ordering/spelling controls; adapter test passed 15/15. |
| mechanical complexity recheck | pass for the two requested findings | `code-grade.py --base "$(git merge-base origin/main HEAD)" --head HEAD` reported project lifecycle helper grade 5 and the decomposed INV-26 helpers grades 4–5. Complexity adjudication otherwise remains the code reviewer's remit. |

No command had a load, import, collection, or discovery failure.

## Original finding dispositions

| Finding | Disposition | Evidence |
|---|---|---|
| QA-01 | resolved | The target unit matrix passed `test-omp-hooks.py` at `75 pass/0 fail`; Main's receipt records the relevant pre-repair OMP result as `73 pass/2 fail` and the focused fixture repair. |
| QA-02 | resolved | The target integration matrix passed. Main's receipt records factory integration at `131/131` after correcting terminal factory case L to use an active Review station rather than the active-only policy's backlog placement. |
| QA-03 | **open** | The fail-first audit below finds four automated SCs without criterion-specific actual pre-fix evidence. |
| QA-04 | resolved | Current `test-plan-merge.py` exercises the no-network negative control (it reddens when `gh` is invoked) and the normal local mutation path passes; Main's receipt records the same controlled guard. |
| CR-01 | resolved mechanically | The c1 code-grade run reports the extracted project lifecycle helper at grade 5, exceeding required grade 4. |
| CR-02 | resolved mechanically | The c1 code-grade run reports the decomposed INV-26 helpers at grades 4–5, exceeding required grade 3. |

No new unowned finding was observed. QA-03 is an original finding, not a new scope change.

## Criterion evidence and fail-first audit

Current-test citations show that the fixed behavior is exercised. The second column separately audits the required historical failure. “Missing” means it cannot be promoted to a satisfied automated SC even though the current test passes.

| SC | Current fixed-tip evidence | Criterion-specific fail-first evidence |
|---|---|---|
| SC-01 | `tests/integration/test-station-argument-spelling.py:288` (focused pass) | Main T-03 receipt, line 14: pre-repair dynamic-resume violation. |
| SC-02 | `tests/integration/test-station-argument-spelling.py:288` (focused pass) | Main T-03 receipt, line 14: pre-repair status-before-open violation. |
| SC-03 | `tests/integration/test-station-argument-spelling.py:288` (focused pass) | Main T-03 receipt, line 14: reset receipt was ignored before repair. |
| SC-04 | `tests/integration/test-station-argument-spelling.py:288` (focused pass) | Main T-03 receipt, line 14: Build occurred after dispatch before repair. |
| SC-05 | `tests/integration/test-station-argument-spelling.py:288` (focused pass) | Main T-03 receipt, line 14: validation/must-fix ordering boundary violations before repair. |
| SC-06 | `tests/integration/test-plan-merge.py:3340` | Main T-02 receipt, line 13: pre-repair plan reset/resume failures. |
| SC-07 | `tests/integration/test-plan-merge.py:3360` | Main T-02 receipt, line 13: pre-repair plan reset/resume failures. |
| SC-08 | `tests/integration/test-gh-sync-ship.py:33-65` | **Missing.** The dev c1 receipt cites the c0 generic T-01 gate, but c0 receipt lines 9–15 show its `&&` chain stopped in `test-gh-sync-record.py`; `test-gh-sync-ship.py` never ran. No actual pre-fix assertion covers all source/parent cards reaching Done. |
| SC-09 | `tests/integration/test-gh-board-lifecycle.py:1148` | Main T-04 receipt, line 15: pre-repair all-card reconciliation failures. |
| SC-10 | `tests/integration/test-plan-merge.py:3438` and `tests/integration/test-gh-sync-record.py` no-network path | Main T-02/T-03 receipts, lines 13–16: controlled fake-`gh` invocation reddened before the local-only repair. |
| SC-11 | `tests/unit/test-gh-board.py:430` | c0 T-01 receipt, line 15: the unit runner actually failed active-phase source-parent assertions before repair. |
| SC-12 | `tests/integration/test-gh-sync-record.py:243` | **Missing.** c0 did run the record runner, but its generic “incomplete active projection” failure neither names nor asserts exclusion of an abandoned card. The receipt does not prove this criterion failed. |
| SC-13 | `tests/integration/test-gh-sync-ship.py:47-51` | **Missing.** The cited c0 `&&` gate never reached the ship runner, so it cannot prove the no-direct-close assertion failed. |
| SC-14 | `tests/integration/test-gh-sync-ship.py:87-156` | **Missing.** The cited c0 `&&` gate never reached the ship runner, so it cannot prove the open-child hold/refresh assertion failed. |

## Ranked must-fix

1. **High / form — QA-03:** obtain and record actual, criterion-specific pre-fix failures for SC-08, SC-12, SC-13, and SC-14. Run the named ship checks against the appropriate pre-T-01 source without an `&&` predecessor that can suppress them, and record failing assertions for all-card Done, no direct close, and the open-child hold/refresh. Run the abandoned-exclusion record assertion against its pre-fix source and record that specific failure. Then re-run the fixed-tip named tests and update the T-01 evidence receipt. Generic failures and a command that did not reach the named test are not acceptable substitutes.

The configured test matrix itself is satisfied, but the feature gate is not: the required fail-first evidence is incomplete. A fresh canonical three-perspective goalcheck must wait for this evidence repair and a subsequent gate.
