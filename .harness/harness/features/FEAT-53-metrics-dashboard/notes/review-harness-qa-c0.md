# FEAT-53 pinned QA gate

```yaml
review_sha: 9b34c65246136666bc69f220824bb262965e75c0
merge_base: a18d6a9f1f832084df84be22097a409d73bf4f61
reader: harness-qa
verdict: FAIL
cycles_used: 0
suite: pass
matrix_ok: false
severity_max: high
files_touched:
  - .harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-qa-c0.md
change_types:
  - {task: T-01, type: config}
  - {task: T-02, type: config}
  - {task: T-03, type: config}
  - {task: T-04, type: scaffolding}
  - {task: T-05, type: scaffolding}
  - {task: T-06..T-09, type: logic}
  - {task: T-10, type: api}
  - {task: T-11, type: feature}
  - {task: T-12, type: api}
  - {task: T-13..T-15, type: frontend}
  - {task: T-16..T-18, type: scaffolding|docs}
  - {task: T-19, type: cross_module}
  - {task: T-20, type: docs}
  - {task: T-21, type: frontend}
  - {task: T-22, type: scaffolding}
  - {task: T-23..T-25, type: cross_module}
  - {task: T-26, type: logic}
  - {task: T-27, type: api}
  - {task: T-28, type: frontend}
  - {task: T-29, type: scaffolding}
  - {task: T-30, type: cross_module}
  - {task: T-31, type: logic}
required_kinds:
  - {kind: unit, basis: logic|api|feature|cross_module|frontend, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", outcome: "pass; 42 files"}
  - {kind: integration, basis: cross_module|feature plus api external/runtime and config-shape surfaces, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", outcome: "pass; 77 files"}
  - {kind: component, basis: frontend always, state: satisfied, cmd: "npm --prefix .claude/skills/harness/bin/dashboard/client run test", outcome: "pass; 5 files, 20 tests"}
  - {kind: ui, basis: frontend/feature interaction flow, state: not_applicable, cmd: null, outcome: "no browser-driver runner; BRIEF.md:201-204 assigns rendered-surface proof to UAT/inspection"}
  - {kind: typecheck, basis: added TypeScript/TSX, state: unresolved, cmd: null, outcome: "not matrix-required; BRIEF.md:205-215 records this known unproven surface"}
  - {kind: eval, basis: no ai_behavior task, state: excluded, cmd: null, outcome: "DEC-187 exclusion"}
sc_coverage:
  - {id: SC-01, test: "tests/integration/test-metrics-dashboard.py:50,99", fail_first: "receipt-harness-backend-dev-2026-09-17-07-eng-T-12-c0.md:9"}
  - {id: SC-03, test: "tests/integration/test-metrics-dashboard.py:99-106", fail_first: "receipt-harness-backend-dev-2026-09-17-07-eng-T-12-c0.md:9"}
  - {id: SC-04, test: "tests/unit/test-metrics-kpi.py:42-80,83-97,342-390", fail_first: missing}
  - {id: SC-05, test: "tests/unit/test-metrics-kpi.py:137-141", fail_first: missing}
  - {id: SC-06, test: "tests/unit/test-metrics-kpi.py:83-97,143-155", fail_first: "receipt-harness-backend-dev-T-07-c0.md:11"}
  - {id: SC-07, test: "tests/integration/test-metrics-trend.py:121-129", fail_first: "receipt-harness-backend-dev-T-10-c0.md:25-27"}
  - {id: SC-09, test: "tests/integration/test-metrics-trend.py:56-66,208-230", fail_first: "receipt-harness-backend-dev-T-19-c0.md:5-18"}
  - {id: SC-10, test: "tests/integration/test-metrics-trend.py:153-159", fail_first: "receipt-harness-backend-dev-T-11-c0.md:5-16"}
  - {id: SC-12, test: "tests/integration/test-metrics-dashboard.py:99-106,169-179", fail_first: "receipt-harness-backend-dev-2026-09-17-07-eng-T-12-c0.md:9"}
  - {id: SC-13, test: "tests/unit/test-metrics-kpi.py:297-331", fail_first: missing}
  - {id: SC-14, test: "tests/unit/test-metrics-kpi.py:342-390", fail_first: "receipt-harness-backend-dev-T-09-c0.md:6-8"}
  - {id: SC-16, test: "tests/integration/test-metrics-dashboard.py:169-179", fail_first: "receipt-harness-backend-dev-2026-09-17-07-eng-T-12-c0.md:9"}
  - {id: SC-17, test: "tests/integration/test-metrics-trend.py:131-151,179-196", fail_first: "receipt-harness-backend-dev-T-11-c0.md:5-16"}
  - {id: SC-18, test: "tests/integration/test-metrics-client-render.py:65-76", fail_first: "receipt-harness-frontend-dev-2026-09-17-09-eng-T-21-c0.md:5-10"}
  - {id: SC-19, test: "tests/integration/test-metrics-trend.py:83-103", fail_first: "receipt-harness-backend-dev-T-10-c0.md:25-27"}
  - {id: SC-21, test: "tests/integration/test-work-dashboard.py:123-133,195-246", fail_first: "receipt-harness-backend-dev-T-23-c0.md:5-23"}
  - {id: SC-22, test: "tests/integration/test-work-dashboard.py:284-331", fail_first: missing}
  - {id: SC-23, test: "tests/integration/test-grilling-status.py:33-52,74-102", fail_first: missing}
  - {id: SC-25, test: "tests/integration/test-metrics-dashboard.py:108-167", fail_first: "receipt-harness-backend-dev-2026-09-17-08-eng-T-27-c0.md:9"}
  - {id: SC-29, test: "tests/unit/omp-hooks.test.ts; tests/integration/test-work-dashboard.py:149-193", fail_first: missing}
fail_first:
  complete: false
  missing: [SC-04, SC-05, SC-13, SC-22, SC-23, SC-29]
coverage_gaps:
  - "SC-04, SC-05, SC-13, SC-22, SC-23, and SC-29 have no durable criterion-binding pre-fix failure evidence"
findings:
  - id: F-01
    kind: substance
    task: T-06; T-07; T-08; T-24; T-25; T-30
    reader: harness-qa
    severity: high
    scenario: "A wrong KPI, attention threshold, grilling lifecycle transition, or run-token result can pass its current green test without evidence that the criterion's assertion ever failed against its pre-implementation state; the required fail-first gate therefore cannot establish that the asserted contract discriminates the claimed regression. T-25 is recorded only as an evidence gap, not relitigated."
known_deferred:
  - "T-17/METRICS.md is operator-sequenced deferred completion work; not a finding."
  - "T-25 is operator-ratified; not relitigated."
```
