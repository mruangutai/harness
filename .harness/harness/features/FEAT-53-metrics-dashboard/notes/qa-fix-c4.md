# QA gate — FEAT-53 backend c4

**BLUF:** Scoped c4 repair evidence is green, but the QA gate is **FAIL** because its required full test runner exits 1 on the explicitly excluded F-QA-01 retained asset assertions (`/assets/index-hkwR5g06.js` → 404). This records the excluded failure without reopening it as a c4 regression.

## Phase 1 expectations (before code)

- V-04: hostile Host cannot reach `/`, `/api/work`, or `/api/kpis`; loopback variants remain usable.
- V-07 / SC-03: fixture and repository KPI payloads bind every returned KPI to their own roots.
- V-08 / SC-09: a baseline plus two separately-worktree-appended records survive two merges.
- V-19 / SC-07: every absent trend field is unavailable/null, never zero.
- F-QA-02 / SC-16: three full-repository KPI requests remain below 8.0 seconds with meaningful headroom.
- V-12, V-13, V-14, V-15: the four named changed functions meet their grade bars without weakening their exercised contracts.

All six in-scope expectations have a direct scoped proof; no c4 regression was found. The full gate remains red solely on excluded F-QA-01.

## Commands and exact results

Plan clauses, retained verbatim:

```text
T-06 verify: |
  python3 tests/unit/test-metrics-kpi.py
T-10 verify: |
  python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-trend.py
T-12 verify: |
  python3 tests/integration/test-metrics-dashboard.py
T-26 verify: >-
  python3 tests/integration/test-work-dashboard.py --case worktrees
T-27 verify: >-
  python3 tests/integration/test-metrics-dashboard.py
T-31 verify: >-
  python3 tests/integration/test-work-dashboard.py --case metrics && python3 tests/integration/test-work-dashboard.py --case worktrees
```

- T-06: 21 tests passed.
- T-10: layout check passed; 16 trend tests passed.
- T-12/T-27: 8 dashboard tests discovered; 6 passed. The two failures are both the excluded retained asset assertion at `test-metrics-dashboard.py:339` (`200 != 404` for `/assets/index-hkwR5g06.js`). Targeted c4 tests passed 3/3.
- T-26: 4 worktree assertions discovered/executed, all passed.
- T-31: 7 metrics assertions and 4 worktree assertions discovered/executed, all passed.
- Canonical grade: `code-grade.py --base ffd9fb0204701cdae968ef0febc86943fb4829bd --head 3b78eb833f12e82e711c6e1b82bf712821ab0a1b` passed 38 records. `kpi.compute` grade 4/bar 4; `work._tokens` grade 4/bar 4; `test_work_api_filters_live_disk_payload_and_preserves_static_routes` grade 4/bar 3; `worktree_case` grade 4/bar 3.

## Discrimination and timing

- V-04: receipt lines 16 records the pre-fix attacker Host `/` response of 200; the scoped host test now verifies 400 JSON for all three protected routes and 200 for all six allowed loopback variants (`test-metrics-dashboard.py:118-126`).
- V-07: live mutant recorded at receipt line 18 changed the repository client to the fixture client; `test_kpi_route_isolated_from_fixture_for_all_output` failed with equal roots, then passed restored (`test-metrics-dashboard.py:128-144`).
- V-08: receipt line 17 records `_records → {}` failing the new three-record/two-merge assertion; the green test binds all three identities (`test-metrics-trend.py:68-86`).
- V-19: live mutant recorded at receipt line 19 changed missing `runs` to zero; the every-field assertion failed, then passed restored (`test-metrics-trend.py:151-162`).
- F-QA-02 / SC-16: independently re-ran the full-root three-sample scenario. Samples were 5.104s, 5.027s, 5.028s; slowest 5.104s, leaving 2.896s below 8.0s (and above the test's >1.0s headroom floor). The repeated targeted invocation produced 5.085s, 5.058s, 5.055s, confirming the result is not a one-sample artifact (`test-metrics-dashboard.py:146-153`).

## Matrix

The changed runtime and integration-test paths require unit and integration coverage for this backend repair. Both in-scope portions are satisfied by the named direct proofs; the independent unit-kind rerun passed 42 files in 9.73s. The complete runner executed 119 files but exited 1 only because `test-metrics-dashboard.py` retains the two excluded F-QA-01 asset assertions. No frontend, UI, formatter, or linter was run. The retained static 404 is recorded as excluded and is not re-raised as a c4 regression.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Scoped c4 proofs pass, but the required complete runner fails only on the explicitly excluded F-QA-01 retained asset 404.
  suite: fail
  failures: 2
  matrix_ok: false
  kinds:
    - kind: unit
      state: satisfied
      cmd: env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit
      named_tests: 42
    - kind: integration
      state: satisfied
      cmd: Scoped T-10/T-12/T-26/T-27/T-31 commands
      named_tests: 35
    - kind: integration
      state: missing
      cmd: env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/run-unit-tests.py
      named_tests: 119
  coverage_gaps: []
  sc_evidence:
    - id: SC-03
      test: tests/integration/test-metrics-dashboard.py:128-144
    - id: SC-07
      test: tests/integration/test-metrics-trend.py:151-162
    - id: SC-09
      test: tests/integration/test-metrics-trend.py:68-86
    - id: SC-16
      test: tests/integration/test-metrics-dashboard.py:146-153
  fail_first:
    - sc: SC-03
      evidence: notes/receipt-harness-backend-dev-fix-c4.md:18
    - sc: SC-07
      evidence: notes/receipt-harness-backend-dev-fix-c4.md:19
    - sc: SC-09
      evidence: notes/receipt-harness-backend-dev-fix-c4.md:17
    - sc: SC-16
      evidence: runs/2026-09-17-17-validator/digest.md:20
  open_questions:
    - id: Q1
      question: The required complete runner exits 1 only on excluded F-QA-01 retained asset assertions; should the gate accept scoped evidence or must the excluded bundle be repaired?
      blocking: true
  files_touched:
    - .harness/harness/features/FEAT-53-metrics-dashboard/notes/qa-fix-c4.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/qa-fix-c4.md
```
