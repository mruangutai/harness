# QA gate — amended T-27

## BLUF

**PASS:** the exact amended T-27 verification passed non-vacuously at review pin `daba2af5513a0316f57ed8729576acb0e582708b`; its current readable-plus-absent and 500 failure matrix is covered. The operator-struck all-unreadable case was not assessed or required.

## Scope and pin

- Reader status: QA-only read-only validation; no source, fixture, plan, UAT, state, or feature-record mutation.
- Reviewed task: `T-27`; literal verify command: `python3 tests/integration/test-work-dashboard.py --case collector && python3 tests/integration/test-metrics-dashboard.py`.
- `git diff --name-status daba2af5513a0316f57ed8729576acb0e582708b --` over T-27's two production and two focused fixture paths was empty. This run therefore assessed the pinned implementation/fixtures; HEAD is plan-only amendment `49330b4a3ccbd985ab267399c8a56dd7e1960e0f`.

## Executed evidence

- Ran the literal command once from the FEAT-53 worktree; exit 0.
- Collector script discovered and executed **10/10 collector assertions**, established by its `CASE_NAMES` length and its emitted `Executed 10 collector assertions; discovered 10 collector assertions.` line (`tests/integration/test-work-dashboard.py:13-24,462-479`).
- Endpoint script discovered and executed **9/9 endpoint tests**, established by unittest's `Ran 9 tests ... OK` result and the nine `test_*` methods on `MetricsDashboardIntegrationTest` (`tests/integration/test-metrics-dashboard.py:28-159,470-471`).
- The run emitted one non-failing `ResourceWarning` for an unclosed static-file response; it did not affect collection or execution (exit 0; 9 tests OK).

## Amended matrix

| Required current behavior | Evidence | Result |
| --- | --- | --- |
| Readable control segment plus absent clone is HTTP 200 with readable rows and exactly one `{repo,path,reason}` error | Collector assertion is exact (`test-work-dashboard.py:123-152`); endpoint `test_absent_fleet_clone_degrades_work_payload` asserts 200, `FEAT-101-harness`, and the singleton exact dict (`test-metrics-dashboard.py:119-132`). | satisfied |
| Selecting only the absent configured repository is HTTP 500 with its unavailable reason | Endpoint test checks `repo=alpha` 500 and its configured-clone reason (`test-metrics-dashboard.py:133-140`); server selects the unavailable error (`serve.py:118-127`). | satisfied |
| Invalid dashboard configuration and genuine collector failure are HTTP 500 | Invalid config fixture asserts 500 JSON unavailable response (`test-metrics-dashboard.py:301-305`); the request-level `except Exception` adapts collector/configuration exceptions to `_unavailable` 500 (`serve.py:76-86,181-183`). | satisfied |
| Collector retains readable rows and emits exactly one absent-clone error | The focused collector fixture asserts readable `FEAT-71-long-id` and equality with one exact `{repo,path,reason}` dict (`test-work-dashboard.py:123-152`); it executed in this run. | satisfied |
| Python annotation compatibility remains covered | The prior QA proof records successful `serve.py` import under Python 3.14.5 (`notes/review-harness-qa-2026-09-17-24-validator.md:13-18`). `serve.py` is byte-identical to the review pin, including `from __future__ import annotations` (`serve.py:2`). | satisfied |

The API matrix requires unit plus integration for this runtime/API change. The focused collector script supplies the named collector assertions, and the literal endpoint integration script supplies the named endpoint tests; both were run by the sole authorized task command.

## Fail-first provenance

- SC-25: `notes/receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c0.md:16-17` records the endpoint absent-clone case failing before the production edit (`AssertionError: 200 != 500`).
- SC-25: `notes/receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c1.md:17-21` records the collector fixture failing before its collector correction, then passing its ten assertions.

## Gate handoff

```yaml
VERDICT: PASS
DIGEST:
  headline: "Amended T-27 passes its exact non-vacuous QA verification and current matrix."
  reader_status: qa-only-read-only
  review_sha: daba2af5513a0316f57ed8729576acb0e582708b
  task: T-27
  verify_command: "python3 tests/integration/test-work-dashboard.py --case collector && python3 tests/integration/test-metrics-dashboard.py"
  suite: pass
  failures: 0
  discovery_execution:
    collector_assertions: { discovered: 10, executed: 10 }
    endpoint_tests: { discovered: 9, executed: 9 }
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/integration/test-work-dashboard.py --case collector", named_tests: 10 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-metrics-dashboard.py", named_tests: 9 }
  matrix_results:
    - { case: readable-plus-absent, state: satisfied, evidence: "tests/integration/test-work-dashboard.py:123-152; tests/integration/test-metrics-dashboard.py:119-132" }
    - { case: selected-absent, state: satisfied, evidence: "tests/integration/test-metrics-dashboard.py:133-140" }
    - { case: invalid-configuration-and-collector-failure, state: satisfied, evidence: "tests/integration/test-metrics-dashboard.py:301-305; .claude/skills/harness/bin/dashboard/serve.py:76-86" }
    - { case: exact-absent-error-shape, state: satisfied, evidence: "tests/integration/test-work-dashboard.py:137-152" }
    - { case: python-annotation-compatibility, state: satisfied, evidence: "notes/review-harness-qa-2026-09-17-24-validator.md:13-18" }
  must_fix: []
  coverage_gaps: []
  sc_evidence:
    - { id: SC-25, test: "tests/integration/test-metrics-dashboard.py:108-140" }
    - { id: SC-29, test: "tests/integration/test-metrics-dashboard.py:328-352" }
  fail_first:
    - { sc: SC-25, evidence: "notes/receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c0.md:16-17" }
    - { sc: SC-25, evidence: "notes/receipt-harness-backend-dev-2026-09-17-23-eng-T-27-c1.md:17-21" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-qa-2026-09-17-26-validator.md
```
