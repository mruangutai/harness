# QA pinned coverage gate — FAIL

**Pin:** `df63193f7ec9798d9660904e0e4e7c78d52358f5..1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`. Both resolve; `HEAD` is the review pin. The pinned range has 48 changed files:

```text
.claude/agents/harness-ai-dev.md
.claude/agents/harness-backend-dev.md
.claude/agents/harness-code-reviewer.md
.claude/agents/harness-data-engineer.md
.claude/agents/harness-dev-ops.md
.claude/agents/harness-frontend-dev.md
.claude/skills/harness-code-review/SKILL.md
.claude/skills/harness-code-risk-grading/SKILL.md
.claude/skills/harness/bin/check-plan-routes.py
.claude/skills/harness/bin/code-grade.py
.claude/skills/harness/bin/code_grade.py
.claude/skills/harness/bin/gate_policy.py
.claude/skills/harness/bin/run-unit-tests.sh
.claude/skills/harness/bin/test-check-plan-routes.py
.claude/skills/harness/bin/test-code-grade-cli.py
.claude/skills/harness/bin/test-code-grade.py
.claude/skills/harness/bin/test-gate-policy.py
.claude/skills/harness/bin/test-validate-digest.py
.claude/skills/harness/bin/validate-digest.py
.harness/glossary.md
.harness/harness.json
.harness/harness/features/FEAT-43-code-risk-grading/answers/Q1-t09-owner-resolver.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa-rerun.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c0.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c1.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c0.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c1.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-06-c0.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c0.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c1.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-apply.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-efficiency.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-reuse.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c0.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c1.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-altitude.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-simplification.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/research-T-10-t10-product.md
.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.html
.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.md
.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml
.omp/agents/harness-ai-dev.md
.omp/agents/harness-backend-dev.md
.omp/agents/harness-code-reviewer.md
.omp/agents/harness-data-engineer.md
.omp/agents/harness-dev-ops.md
.omp/agents/harness-frontend-dev.md
```

## Phase 1 expectation (before implementation inspection)

The BRIEF/plan requires: hand-derived exact metric fixtures across all five grades (at least 12); both worsening and improvement pairs; cross-directory/copy/order deterministic CLI output; separately asserted report fields and parse-error accounting; seven-way responsibility set, including informational untouched grade-1; guidance/tool and all-ten-agent delivery conformance; policy loading and clean-report/must-fix behavior; code-grade digest enforcement and policy-outcome pair; owner-manifest routing with a proven-old-revision false-OK; and reason-required present/absent behavior. `logic` tasks require `unit`; T-03, T-08 (`cross_module`), and T-09 require `integration`. Config/docs require none. Component/UI/eval/typecheck are not applicable to this Python/Markdown/config range.

## Evidence and matrix

| kind | state | command actually run | result |
|---|---|---|---|
| unit | satisfied (targeted portions) | `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade.py` | PASS |
| unit | satisfied (targeted portions) | `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-gate-policy.py` | PASS |
| integration | satisfied (CLI portion) | `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade-cli.py` | PASS |
| integration | missing/fail | `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-validate-digest.py` | named assertion failure: `previous validator must accept the gated digest` |
| integration | missing/fail | `PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3 .claude/skills/harness/bin/test-check-plan-routes.py` | named assertion failure: `case_27b_prior_revision_false_ok` |
| component/ui/eval/typecheck/functional | not applicable | — | no matching required matrix obligation; functional is excluded by DEC-187 |

The `/usr/bin/python3` 3.9 run of the route test also emits `Unknown option: -P`; that is the preserved unsupported-runtime mismatch, not a source finding. The supported Python 3.14 run above isolates the real route-test failure.

## Must-fix findings

1. **high — exact fixture floor is untested and unmet.** `test-code-grade.py:21-44` defines only 11 entries in `FIXTURES`; its only completeness check at `:267` tests grade-set equality, not `len(FIXTURES) >= 12`. A grader can retain every grade while deleting one independently derived fixture, so SC-01's minimum and the exact-fixture regression bar both remain unprotected. **Owner:** harness-backend-dev; add the twelfth hand-derived fixture and an explicit count assertion.

2. **high — both required prior-revision discrimination tests select the review revision, so they do not prove the regression.** `test-check-plan-routes.py:1416-1435` and `test-validate-digest.py:1763-1775` call `git show HEAD:...`. At the immutable pin `HEAD` is `1ac1bd0`, the new implementation, not `df63193`; each test then expects the extracted program to exhibit the old false acceptance and fails. Concrete scenario: rerunning either targeted integration contract after committing the feature produces the named failures above; the claimed proof of SC-16/SC-20 cannot survive the commit it is supposed to protect. **Owners:** main-session-direct enforcement routes (T-09 and T-08 respectively); extract the explicit pinned parent/base revision (or otherwise bind an actual pre-change revision) and preserve the current implementation separately.

3. **med — determinism coverage omits required adverse directory ordering.** `test-code-grade-cli.py:102-120` only copytrees a repository and invokes path mode from two CWDs; it does not run `--base/--head` with changed-file enumeration presented in a different order. Thus an implementation depending on enumeration order can pass despite violating SC-04. **Owner:** harness-dev-ops; add a controlled reversed-order/diff enumeration probe with byte equality.

4. **med — direction-pair checks assert only grade inequality, not the named metric movement.** `test-code-grade.py:48-85,272-276` labels habits but does not assert cyclomatic/cognitive/ABC changes per pair. A future grader could lower grades for an unrelated metric and pass all six pairs, contrary to SC-03. **Owner:** harness-backend-dev; assert the intended per-pair metric movement.

## SC evidence / delta

Passing named evidence exists for SC-05/06/14 (CLI cases at `test-code-grade-cli.py:52-100`), SC-07/08/09/10 (`test-code-grade.py:179-263`), SC-12/13 (`test-gate-policy.py`), and code-grade schema branches (`test-validate-digest.py:1551-1775`). SC-01, SC-03, SC-04, SC-16, and SC-20 are not adequately evidenced for the findings above. Inspection/UAT criteria (SC-02, SC-11, SC-15, SC-18) are outside this automated gate.
