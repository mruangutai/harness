# FEAT-63 QA pinned matrix gate — c1

**FAIL — review SHA `77fa741041dfcee96b545c74df699d8f802bb088`.** All assigned commands are green, the AST lock is live and discriminating, and the c0 receipt failure is closed. The amended `cross_module` typing cures c0's unconfigured-type defect, but its unit floor is still not met for T-02 or T-03: their change-specific coverage is integration-only.

## Phase 1 coverage expectation

From BRIEF and plan before source access: eight receipt suites (SC-01); direct cache/silent-path integration behavior (SC-02); typed boundary/process-control unit behavior plus checker integration behavior (SC-03); AST census and syntax/per-file mutants (SC-04); both JSON-loader reparse mutants (SC-05); and byte inspection (SC-06). `cross_module` requires both `unit` and `integration` for each T-01–T-03 (`.harness/harness.json:174-178`).

## Command receipts

| command | exit | observed result |
|---|---:|---|
| `python3 tests/integration/test-check-state.py` | 0 | `3/3 ... passed`; `ALL PASSED` |
| `python3 tests/integration/test-check-state-entry.py` | 0 | FEAT-63 probe assertion: `probes: 1`; no failure |
| `python3 tests/integration/test-check-state-plans.py` | 0 | named assertions passed |
| `python3 tests/integration/test-check-state-handoff.py` | 0 | named assertions passed |
| `python3 tests/integration/test-check-state-worktrees.py` | 0 | named assertions passed |
| `python3 tests/integration/test-check-state-inv26.py` | 0 | named assertions passed |
| `python3 tests/integration/test-check-state-records.py` | 0 | named assertions passed |
| `python3 tests/integration/test-check-state-feat59.py` | 0 | `(63.a)` and `(63.b)` passed |
| `python3 tests/integration/test-check-state-table.py` | 0 | `ALL PASSED` |
| `python3 tests/integration/test-check-plan-routes.py` | 0 | all nine FEAT-63 reparse/census cases passed; `ALL PASS` |
| `python3 tests/unit/test-harness-boundary.py` | 0 | typed error, cause, restoration, and process-control cases passed; `ALL PASS` |
| `python3 .claude/skills/harness/bin/check-plan-routes.py --consolidation-audit` | 0 | `0 consolidation finding(s) under bin/` |
| `python3 .claude/skills/harness/bin/code-grade.py --base 804d68b8 --head 77fa741041dfcee96b545c74df699d8f802bb088` | 0 | `PASSING: 29` |

`git diff --quiet 77fa741... -- .claude/skills/harness tests` exited 0; later HEAD differs only in feature metadata, so the executed product/test content is the review pin.

## Matrix and coverage

| task | required kinds | direct coverage assessment |
|---|---|---|
| T-01 | unit, integration | satisfied: `test-harness-boundary.py` exercises the typed loader boundary; checker integration suites exercise `Ctx` behavior. |
| T-02 | unit, integration | integration satisfied: the eight checker suites, including `test-check-state-entry.py:683-710` and `test-check-state-feat59.py:1027-1043`. **unit missing**: `test-harness-boundary.py:572-599` exercises T-01's loader boundary, not narrowed `check-state.py` handlers/INV-23 behavior. |
| T-03 | unit, integration | integration satisfied: `test-check-plan-routes.py:2741-2802`. **unit missing**: no unit test exercises the audit/census behavior. |

The task type is now configured, so **QA-63-01's original unconfigured-type finding is closed**. The required unit coverage gap remains independently gate-failing (QA-C1-01 below).

## Audit, receipts, and c0 closure

The live audit parses every `bin/*.py` through `ast.parse`, counts only bare and exactly-`Exception` handlers, and applies per-file ceilings (`check-plan-routes.py:2144-2221`). Live output is zero findings; source search has no checker broad handler. It is non-vacuous: the mutation suite adds each checker syntax and demands exactly one ceiling-zero finding, and it adds a catch to real `check-domain.py`, proving the observed `25` against its real `24` ceiling (`tests/integration/test-check-plan-routes.py:2766-2793`).

Receipt ledger reconciliation accepts only D-2's added entry assertion and D-1's two feat59 assertions (`notes/build-divergences.md:58-63`); all eight current suites ran to exit 0 with no skipped or missing row observed and no unruled receipt change recorded.

QA-63-02 is **closed**: `notes/red-first-receipts.md:10-27` retains verbatim RED lines against `804d68b8`, with GREEN lines at :33-41. Present-state discrimination is also direct: SC-01 `test-check-state-feat59.py:1027-1043`; SC-02 `test-check-state-entry.py:683-710`; SC-03 `test-harness-boundary.py:518-599`; SC-04 and SC-05 `test-check-plan-routes.py:2741-2802`.

PM-63-01/CR-01 is **closed**: baseline rationale bytes at `950b2f04:check-state.py:671-674,2412-2415` are present beside the narrowed review-pin paths at `check-state.py:703-705,2460-2461`; separate FEAT-63 prose does not rewrite them.

## Finding

- **QA-C1-01 — high — substance — harness-qa — T-02,T-03 / plan.yaml:108-155**: both tasks declare `cross_module`, whose configured floor is unit plus integration, but their change-specific evidence is integration-only. **Failure scenario:** a regression in T-02's narrowed checker boundary or T-03's census/audit can pass every named integration suite while no unit-kind test exercises that task's behavior, leaving the declared matrix floor unenforced.

```yaml
VERDICT: FAIL
DIGEST:
  headline: All pinned scoped gates pass and c0 fail-first/type defects are closed, but T-02 and T-03 still lack their required unit-kind coverage.
  suite: pass
  failures: 1
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-harness-boundary.py", named_tests: 1 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-check-state.py; python3 tests/integration/test-check-state-entry.py; python3 tests/integration/test-check-state-plans.py; python3 tests/integration/test-check-state-handoff.py; python3 tests/integration/test-check-state-worktrees.py; python3 tests/integration/test-check-state-inv26.py; python3 tests/integration/test-check-state-records.py; python3 tests/integration/test-check-state-feat59.py; python3 tests/integration/test-check-state-table.py; python3 tests/integration/test-check-plan-routes.py", named_tests: 10 }
  coverage_gaps: ["T-02 cross_module lacks a change-specific unit-kind test", "T-03 cross_module lacks a change-specific unit-kind test"]
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-state-feat59.py:1027-1043" }
    - { id: SC-02, test: "tests/integration/test-check-state-entry.py:683-710" }
    - { id: SC-03, test: "tests/unit/test-harness-boundary.py:518-599" }
    - { id: SC-04, test: "tests/integration/test-check-plan-routes.py:2766-2802" }
    - { id: SC-05, test: "tests/integration/test-check-plan-routes.py:2741-2752" }
  fail_first:
    - { sc: SC-01, evidence: "notes/red-first-receipts.md:13-15; present-state discriminator tests/integration/test-check-state-feat59.py:1027-1043" }
    - { sc: SC-02, evidence: "notes/red-first-receipts.md:10-11; present-state discriminator tests/integration/test-check-state-entry.py:683-710" }
    - { sc: SC-03, evidence: "notes/red-first-receipts.md:17-18; present-state discriminator tests/unit/test-harness-boundary.py:518-599" }
    - { sc: SC-04, evidence: "notes/red-first-receipts.md:20-27; present-state discriminator tests/integration/test-check-plan-routes.py:2766-2802" }
    - { sc: SC-05, evidence: "notes/red-first-receipts.md:20-22; present-state discriminator tests/integration/test-check-plan-routes.py:2741-2752" }
  must_fix: [QA-C1-01]
  findings:
    - { id: QA-C1-01, severity: high, kind: substance, reader: harness-qa, task: "T-02,T-03", location: "plan.yaml:108-155", scenario: "cross_module requires unit and integration, but only integration directly exercises T-02/T-03 behavior" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-63-broad-exception-sweep/.harness/harness/features/FEAT-63-broad-exception-sweep/notes/review-harness-qa-c1.md
```
