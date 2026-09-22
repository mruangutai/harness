# FEAT-63 QA scoped gate — c0

## Verdict: FAIL

Reviewed SHA: `4066581f6cec2d6eab1fc5094740c13a8d144d7f`. The working tree differed from that pin only in feature metadata; `git diff --quiet <pin> -- .claude/skills/harness tests` exited 0, so every executed product/test gate was against pinned content. All assigned scoped commands passed, including the requested live audit and grade. The release gate nevertheless fails: the plan has an unconfigured `refactor` change type, and no direct build-ledger red-first receipts exist for SC-01..SC-05.

## Scoped command receipts

| command | exit | observed non-vacuity / result |
|---|---:|---|
| `python3 tests/integration/test-check-state.py` | 0 | `3/3 T-07` cases; `ALL PASSED` |
| `python3 tests/integration/test-check-state-entry.py` | 0 | named assertion output; no failures |
| `python3 tests/integration/test-check-state-plans.py` | 0 | named assertion output; no failures |
| `python3 tests/integration/test-check-state-handoff.py` | 0 | named assertion output; no failures |
| `python3 tests/integration/test-check-state-worktrees.py` | 0 | named assertion output; no failures |
| `python3 tests/integration/test-check-state-inv26.py` | 0 | named assertion output; no failures |
| `python3 tests/integration/test-check-state-records.py` | 0 | named assertion output; no failures |
| `python3 tests/integration/test-check-state-feat59.py` | 0 | `(63.a)` CANNOT RUN and `(63.b)` no-300-fallback assertions passed |
| `python3 tests/integration/test-check-state-table.py` | 0 | `ALL PASSED` |
| `python3 tests/integration/test-check-plan-routes.py` | 0 | FEAT-63’s 8 named reparse/census mutation assertions passed; `ALL PASS` |
| `python3 tests/unit/test-harness-boundary.py` | 0 | named `RepoModuleError`, process-control, registration, by-name, and call-boundary assertions passed; `ALL PASS` |
| `python3 .claude/skills/harness/bin/check-plan-routes.py --consolidation-audit` | 0 | `0 consolidation finding(s) under bin/` |
| `python3 .claude/skills/harness/bin/code-grade.py --base 804d68b8 --head 4066581f6cec2d6eab1fc5094740c13a8d144d7f` | 0 | `PASSING: 28` |

The audit is the requested AST/syntax census: `check-plan-routes.py:2185-2219` parses each bin script with `ast.parse`, counts only `ExceptHandler(type=None)` and `ExceptHandler(Name('Exception'))`, and applies `check-state.py`’s zero default ceiling. Its live result was zero findings. The mutation suite independently exercised both check-state syntaxes and expects one ceiling-zero finding for each (`tests/integration/test-check-plan-routes.py:2766-2772`).

## Matrix

| task | declared change type | required kind result |
|---|---|---|
| T-01 | `cross_module` | unit satisfied; integration satisfied |
| T-02 | `refactor` | **invalid/unconfigured**: no `refactor` entry exists in `harness.json:test_matrix` |
| T-03 | `cross_module` | unit satisfied; integration satisfied |

`cross_module` requires `unit` and `integration` (`.harness/harness.json:174-178`); both targeted kinds ran successfully above. `refactor` cannot be mapped or silently treated as another type. Therefore `matrix_ok: false`.

## SC evidence and fail-first audit

| SC | current green evidence | fail-first evidence assessment |
|---|---|---|
| SC-01 | `tests/integration/test-check-state*.py`; especially `test-check-state-feat59.py:1027-1043` | **inadequate**. `notes/build-divergences.md:46` narrates “63.a red on T-01, green on T-02,” but supplies no captured pre-fix command/output receipt. Narrative is not a direct receipt. |
| SC-02 | eight checker suites; live AST audit | **missing**. No build-ledger red-first receipt for the spawn/cache behavior was present at the pin. |
| SC-03 | `tests/unit/test-harness-boundary.py:518-599`; audit | **missing**. Current mutation/behavior tests passed, but no receipt shows these tests failing before the T-01/T-02 production change. |
| SC-04 | `tests/integration/test-check-plan-routes.py:2766-2802`; live audit | **missing**. The current isolated mutants are direct current-run discrimination evidence, not a build-ledger pre-fix red-first receipt. |
| SC-05 | `tests/integration/test-check-plan-routes.py:2741-2752` | **missing**. Current isolated-loader mutants passed, but no build-ledger pre-fix red-first receipt exists. |

The pinned feature record has only planning and currently pending validator runs (`feature.json:8-48`), and its pinned feature tree has no build-run ledger or fail-first receipt. `build-divergences.md` is the only candidate; it contains aggregate/narrative claims rather than preserved red command output. A green suite cannot close the required fail-first gate.

## Findings

- **QA-63-01** — high — substance — harness-qa — T-02 / `plan.yaml:111`: `refactor` is absent from the configured `test_matrix`. Scenario: a later T-02 regression could be classified as an unrecognized type and receive no enforced floor if QA guessed or skipped a mapping.
- **QA-63-02** — high — substance — harness-qa — SC-01..SC-05 / feature build ledger: direct red-first receipts are absent. Scenario: a newly added assertion can pass against the finished implementation while never having constrained the pre-fix defect; the present narrative claim would still permit release.

## Coverage gaps

- Matrix floor for T-02 cannot be evaluated because `refactor` is not a configured `test_matrix` change type.
- Automated SC-01..SC-05 lack direct build-ledger fail-first receipts; SC-04 and SC-05 have current mutant discrimination only.

```yaml
VERDICT: FAIL
DIGEST:
  headline: All scoped gates passed at the review pin, but invalid T-02 matrix typing and absent direct fail-first receipts prevent release.
  suite: pass
  failures: 2
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-harness-boundary.py", named_tests: 1 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-check-state.py; python3 tests/integration/test-check-state-entry.py; python3 tests/integration/test-check-state-plans.py; python3 tests/integration/test-check-state-handoff.py; python3 tests/integration/test-check-state-worktrees.py; python3 tests/integration/test-check-state-inv26.py; python3 tests/integration/test-check-state-records.py; python3 tests/integration/test-check-state-feat59.py; python3 tests/integration/test-check-state-table.py; python3 tests/integration/test-check-plan-routes.py", named_tests: 10 }
  coverage_gaps:
    - "T-02 refactor is unconfigured in test_matrix"
    - "SC-01..SC-05 lack direct build-ledger fail-first receipts"
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-state-feat59.py:1027" }
    - { id: SC-02, test: "tests/integration/test-check-state*.py" }
    - { id: SC-03, test: "tests/unit/test-harness-boundary.py:518" }
    - { id: SC-04, test: "tests/integration/test-check-plan-routes.py:2766" }
    - { id: SC-05, test: "tests/integration/test-check-plan-routes.py:2741" }
  fail_first:
    - { sc: SC-01, evidence: "notes/build-divergences.md:46 is narrative only; no direct red receipt" }
    - { sc: SC-02, evidence: "missing: no build-ledger red-first receipt at pinned tree" }
    - { sc: SC-03, evidence: "missing: no build-ledger red-first receipt at pinned tree" }
    - { sc: SC-04, evidence: "current-run mutant proof at tests/integration/test-check-plan-routes.py:2766-2802; no pre-fix receipt" }
    - { sc: SC-05, evidence: "current-run mutant proof at tests/integration/test-check-plan-routes.py:2741-2752; no pre-fix receipt" }
  severity_max: high
  must_fix: [QA-63-01, QA-63-02]
  findings:
    - { id: QA-63-01, severity: high, kind: substance, reader: harness-qa, task: T-02, location: "plan.yaml:111", scenario: "unconfigured change type has no enforceable matrix floor" }
    - { id: QA-63-02, severity: high, kind: substance, reader: harness-qa, task: "SC-01..SC-05", location: "feature build ledger", scenario: "green tests can be newly added and never constrain the pre-fix defect" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-63-broad-exception-sweep/.harness/harness/features/FEAT-63-broad-exception-sweep/notes/review-harness-qa-c0.md
```