# QA gate — BUG-1699-lifecycle-cards

**Verdict: FAIL.** Review target: immutable `ed64ea9cc4ef92e3e54adfa0849a0147230b480b`; derived range `8ef4731e816f08dbc562206134c100b0c034a812..ed64ea9cc4ef92e3e54adfa0849a0147230b480b`.

Phase 1 was performed from `BRIEF.md` and approved `plan.yaml` before source/test inspection. It required tests for each lifecycle boundary: initial resume/open/Ready, Build/Building, validation/Review, fix handoff and return, atomic reapproval reset, reclassification, ship/Done, reconciliation, best-effort writes, all six board projections, abandonment, no direct lifecycle close, and child holds.

## Matrix

| kind | state | command | evidence |
|---|---|---|---|
| unit | failed | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | `tests/unit/omp-hooks.test.ts:1261` expected `tokensOf(featureJson)` to be `null`, received `undefined`. This is a test assertion failure, not collection/load misconfiguration. |
| integration | failed | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | `test-factory-integration.py` failed 2/131: its board-lifecycle STATUS fixture expected exit 1 and a finding for a station mismatch, but received exit 0 and `board_lifecycle: 0 finding(s)`. This is a test assertion failure, not collection/load misconfiguration. |

Configured cross-module matrix requires both kinds; therefore `matrix_ok: false`.

Focused plan proofs all passed:

- T-01: `test-gh-board.py`, `test-gh-sync-record.py`, `test-check-state-inv26.py`, `test-gh-sync-open.py`, `test-gh-sync-start-task.py`, `test-gh-sync-ship.py`, and `test-gh-sync-abandon.py` (107.13 s).
- T-02: `test-plan-merge.py` (62.46 s).
- T-03: `test-station-argument-spelling.py`, `test-sync-command-adapters.py`, and `sync-command-adapters.py --check` (2.25 s).
- T-04: `test-board-lifecycle.py` (41.51 s).
- T-05: decision/command anchor check examined 40 anchors with 0 failures; generated index diff was empty (0.35 s).

Focused proofs do not override the configured-matrix failures.

## Requirement coverage and fail-first audit

| SC | Current focused coverage | fail-first evidence |
|---|---|---|
| SC-01 | `test-station-argument-spelling.py:288-358`; `test-gh-sync-record.py` status projection scenarios | T-01 receipt has a red shared-projection fixture, but no pre-fix failure proving the required RESUME/open ordering. |
| SC-02 | `test-station-argument-spelling.py:288-358`; `test-gh-sync-record.py` Building projection scenarios | T-01 receipt covers old missing Building projection, but no pre-fix dispatch-order failure. |
| SC-03 | `test-station-argument-spelling.py:288-358`; `test-gh-sync-record.py` Review projection scenarios | No captured pre-fix failure for validation boundary/Review-before-dispatch. |
| SC-04 | `test-station-argument-spelling.py:288-358` Fix Build ordering assertions | No captured pre-fix failure. |
| SC-05 | `test-station-argument-spelling.py:288-358` returned-fix Review ordering assertions | No captured pre-fix failure. |
| SC-06 | `test-plan-merge.py:3248-3357`; `test-station-argument-spelling.py:288-358` | No captured pre-fix failure for atomic reset/no hidden remote side effect. |
| SC-07 | `test-plan-merge.py:3340-3411`; `test-station-argument-spelling.py:288-358` | No captured pre-fix failure. |
| SC-08 | T-01 `test-gh-sync-ship.py` all-eligible-card Done scenarios | No captured pre-fix failure. |
| SC-09 | `test-board-lifecycle.py:1148-1232` reconciliation/idempotence scenarios | No captured pre-fix failure. |
| SC-10 | T-01 `test-gh-sync-record.py` local-first and later-card continuation scenarios | No captured pre-fix failure; no subject-bound execution test proves plan mutation makes no GitHub network write. |
| SC-11 | `test-gh-board.py:430-470` exact six-station projection/card-class cases | T-01 receipt has an old projection red fixture, but no captured per-SC pre-fix result. |
| SC-12 | T-01 `test-gh-sync-abandon.py`; `test-board-lifecycle.py:1148-1232` | No captured pre-fix failure. |
| SC-13 | T-01 `test-gh-sync-record.py` and `test-gh-sync-ship.py` no-close behavior | No captured pre-fix failure. |
| SC-14 | T-01 `test-gh-sync-ship.py` held-child scenarios | No captured pre-fix failure. |

The phase-1 test list is substantially represented by current tests. The additional coverage gap is SC-10's explicit no-hidden-network-write assertion. More importantly, the record has no complete, non-empty per-automated-SC fail-first evidence. Only T-01 has a general red receipt; T-02 through T-05 records show green commands, not a pre-fix failure. The QA contract requires one non-empty fail-first entry for every automated SC, so this independently prevents PASS.

## Findings

1. **QA-01** — kind: substance; reader: harness-qa; severity: high; owning task: **scope change**. The configured unit command fails at `tests/unit/omp-hooks.test.ts:1261` (`null` expected, `undefined` received). The pinned review range also contains uncontracted shipped changes to `.claude/skills/harness/bin/feature-record.py`, its schema, and related feature-record tests. No T-01..T-05 owns that product surface. This is an out-of-scope change, not attributed to a planned task.
2. **QA-02** — kind: substance; reader: harness-qa; severity: high; owning task: **scope change**. The configured integration command fails `test-factory-integration.py` case L: its mismatch fixture expects the board-lifecycle audit to fail and identify the stale station, but the subprocess exits 0 with zero findings. This unplanned regression blocks the integration matrix.
3. **QA-03** — kind: form; reader: harness-qa; severity: high; owning tasks: **T-01, T-02, T-03, T-04**. Fail-first proof is incomplete for automated SC-01 through SC-14, and entirely absent from the inspected T-02/T-03/T-04 records. The only available red receipt is general T-01 projection evidence and does not discharge all individual requirements. This fails the explicit QA evidence gate.
4. **QA-04** — kind: coverage; reader: harness-qa; severity: medium; owning tasks: **T-02, T-03**. SC-10 requires an executed proof that plan mutation performs no GitHub network write. Current tests exercise local-first projection, continuation after a card error, and plan mutation, but none supplies an execution-bound assertion that a plan mutation attempts no network operation.

SC-15 and SC-16 are inspection criteria and were not assigned automated evidence.
