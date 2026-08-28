# FEAT-43 final pinned QA adequacy — FAIL

**BLUF:** The immutable range cannot merge. The real grader returns exit 1 with a new grade-1 test function (`case_27`), which is a direct REQ-06 high blocker. Three signed test-adequacy obligations also remain unproven: one of 13 fixtures has no hand derivation, direction tests do not assert grade movement, and the adverse-order fixture never changes the `git diff` entry order.

## Pin, census, and commands

Reviewed committed `df63193f7ec9798d9660904e0e4e7c78d52358f5..45328d7a280d251a94b09672a7b6724d55a79f83` (both objects resolve; HEAD is the latter). Exact `git diff --name-only` census is **48 files**; no dirty metadata informed this judgement:

`.claude/agents/harness-ai-dev.md`, `.claude/agents/harness-backend-dev.md`, `.claude/agents/harness-code-reviewer.md`, `.claude/agents/harness-data-engineer.md`, `.claude/agents/harness-dev-ops.md`, `.claude/agents/harness-frontend-dev.md`, `.claude/skills/harness-code-review/SKILL.md`, `.claude/skills/harness-code-risk-grading/SKILL.md`, `.claude/skills/harness/bin/check-plan-routes.py`, `.claude/skills/harness/bin/code-grade.py`, `.claude/skills/harness/bin/code_grade.py`, `.claude/skills/harness/bin/gate_policy.py`, `.claude/skills/harness/bin/run-unit-tests.sh`, `.claude/skills/harness/bin/test-check-plan-routes.py`, `.claude/skills/harness/bin/test-code-grade-cli.py`, `.claude/skills/harness/bin/test-code-grade.py`, `.claude/skills/harness/bin/test-gate-policy.py`, `.claude/skills/harness/bin/test-validate-digest.py`, `.claude/skills/harness/bin/validate-digest.py`, `.harness/glossary.md`, `.harness/harness.json`, `.harness/harness/features/FEAT-43-code-risk-grading/answers/Q1-t09-owner-resolver.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa-rerun.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c0.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c1.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c0.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c1.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-06-c0.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c0.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c1.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-apply.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-efficiency.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-reuse.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c0.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c1.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-altitude.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-simplification.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/research-T-10-t10-product.md`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.html`, `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.md`, `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`, `.omp/agents/harness-ai-dev.md`, `.omp/agents/harness-backend-dev.md`, `.omp/agents/harness-code-reviewer.md`, `.omp/agents/harness-data-engineer.md`, `.omp/agents/harness-dev-ops.md`, `.omp/agents/harness-frontend-dev.md`.

Targeted commands, with `PATH=/opt/homebrew/bin:...` where child Python is selected:

- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --base df63193 --head 45328d7a280d251a94b09672a7b6724d55a79f83` → **exit 1**, `PASSING: 81`.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade.py` → `PASS test-code-grade`.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade-cli.py` → `PASS test-code-grade-cli`.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-check-plan-routes.py` → `ALL PASS`, including `case_27b_prior_revision_false_ok`.
- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL PASSED`, including `code-grade and review-policy gates`.

An initial plan-route probe without the Homebrew-first PATH failed only because its child selected macOS `/usr/bin/python3`, which rejects `-P`; the prescribed Homebrew-first rerun above passed. No broad suite was rerun.

## Grade result and required reasons

The one grade-1 record is `.claude/skills/harness/bin/test-check-plan-routes.py:1399` `case_27` (cyclomatic 6, cognitive 6, ABC 50.0, driver `abc`; test bar 3): high, `RESULT: FAIL`. This alone prevents merge under REQ-06.

The CLI emitted nine grade-2 demands: `check-plan-routes.py:775 main`; `code-grade.py:137 main`; `code_grade.py:322 _body_hashes.collect`; `code_grade.py:350 gated_set`; `test-code-grade-cli.py:96 test_diff_and_determinism`; `test-code-grade.py:136 check_changed_function_resolution`; `test-code-grade.py:296 main`; `test-gate-policy.py:55 check_policy_loading`; and `test-validate-digest.py:1760 run_code_grade_cases`. Their current metrics/driver are in the CLI record. The only committed reviewer note predates this pin and carries six obsolete answers; it does not answer this nine-demand set. Thus SC-15 has no independently durable written-answer evidence in the pinned range. The concurrent final code reviewer confirmed it will record all nine answers in its own final note; that later artifact is not credited here.

## F-01..F-12 resolution

| Finding | Resolution at pin | Evidence |
|---|---|---|
| F-01 grade-1 gate | **Open, high** | CLI above: `case_27` is grade 1. |
| F-02 comprehension filters | Resolved | `code_grade.py:201-209` counts each comprehension `if`; hand-derived fixture `test-code-grade.py:44-47` asserts cyclomatic 10. |
| F-03 deletion | Resolved | `code-grade.py:90-92` excludes D status; CLI test `:96-115` asserts deletion absent and never ungraded. |
| F-04 `n_a` diff basis | Resolved | `validate-digest.py:540-553,750-757` reads the reviewed Git range; named validator test passed. |
| F-05 info/none vocabulary | Resolved | `validate-digest.py:35,193` and test `:1727-1737` reject `info` as schema vocabulary rather than crashing policy evaluation. |
| F-06 true predecessor | Resolved | fixed `PRE_FEATURE_REVISION` extraction in route test `:1379-1441` and validator test `:1741-1757`; named predecessor probe passed. |
| F-07 12 derived fixtures | **Partially open, med** | 13 fixtures and `len(FIXTURES) >= 12` are present (`test-code-grade.py:19-48,306`), but `bindings-and-calls` at `:22` has no adjacent hand derivation, so SC-02 still fails. |
| F-08 adverse ordering | **Open, med** | `test-code-grade-cli.py:120-129` writes in differing order, but both commits/Git diff enumeration remain canonical and neither call supplies a reordered diff stream; an order-dependent `_diff_paths` implementation would stay green. |
| F-09 named metric movement | **Open, med** | `test-code-grade.py:316-320` asserts only the named metric changes; it never asserts `grade(after) < grade(before)` or the reverse demanded by SC-03. |
| F-10 NUL-safe paths | Resolved | `code_grade.py:302-316` and `test-code-grade.py:207-229` exercise tab/newline rename records; focused test passed. |
| F-11 approximation label | Resolved | CLI text/JSON assertions `test-code-grade-cli.py:64-78` require `Sonar-style approximation`. |
| F-12 per-record bar/outcome | Resolved | CLI assertions `:64-81` require production/test bars and individual PASS/FAIL results. |

## Requirement and success-criterion adequacy

REQ-02/03/04/05/07/08/09/10/11 have a changed, named contract test or direct targeted CLI evidence. REQ-01's guidance text exists, but its behaviour claim is intentionally pending SC-11 UAT. REQ-06 fails on the grade-1 result. SC-01 is covered by the 13 exact fixtures and band-set assertion; SC-02 is not met for the missing derivation. SC-03 is not met because the named metric assertion replaced, rather than accompanies, strict grade-direction assertions. SC-04 remains inadequately discriminating for adverse input ordering. SC-05/06/07/08/09/10/12/13/14/16/17/19/20 have named tests that passed in the targeted files. SC-11 remains UAT-only and unrun by constraint; SC-15 lacks a pinned current nine-demand written-reason record; SC-18 is directly stated in the guidance at `SKILL.md:162-165`.

## Final blockers and adequacy gaps

1. **HIGH — F-01 / REQ-06:** merging creates grade-1 `case_27`; the stated grade-1 gate forbids merge.
2. **MED — F-07 / SC-02:** a future metric regression can retain all fixture values while `bindings-and-calls` remains an undocumented self-oracle; add its checkable derivation.
3. **MED — F-08 / SC-04:** changing `_diff_paths` to preserve an adversarial external changed-file order would remain green because the fixture only varies write order, not the presented Git record order.
4. **MED — F-09 / SC-03:** swapping grade banding or otherwise preventing a grade crossing while metrics still move leaves all six direction pairs green; assert both grade inequality and the named metric movement per pair.
5. **MED — SC-15 evidence:** at assessment time no pinned artifact answers all nine current reason demands. This is a record gap; the final reviewer owns the required answers.

`severity_max: high`. Rework budget is exhausted; these are final blockers, not an internal loop.

Files touched: `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-review-final-validator.md`.
