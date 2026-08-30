# FEAT-43 backend grading validation fix

**BLUF:** The backend-owned grader now counts every comprehension filter in cyclomatic complexity and consumes rename-aware NUL-delimited Git status records, including tab/newline-bearing Python paths. The grade-1 gate-policy test entry point is split into focused checks; no owned function is grade 1.

## Files touched

- `.claude/skills/harness/bin/code_grade.py`
- `.claude/skills/harness/bin/test-code-grade.py`
- `.claude/skills/harness/bin/test-gate-policy.py`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-eng.md`

## Test-first evidence and focused proof

- **RED:** `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade.py` exited 1 before the production edit: the one-filter fixture expected cyclomatic 3 but got 2; the eight-filter fixture expected 10 but got 2; the odd tab/newline rename expected one changed Python path but got `[]`.
- **GREEN:** `/opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade.py && /opt/homebrew/bin/python3 .claude/skills/harness/bin/test-gate-policy.py` exited 0. The first script printed `PASS test-code-grade`; the second printed all 27 named `ok` checks.
- **CLI grade proof:** `/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --json .claude/skills/harness/bin/code_grade.py .claude/skills/harness/bin/test-code-grade.py .claude/skills/harness/bin/test-gate-policy.py | jq '[.records[] | select(.grade == 1)]'` exited 0 and printed `[]`.
- The grading fixture suite has 12 explicitly hand-derived fixtures spanning grades 1–5, a minimum-count assertion, named-metric direction assertions, and a rename fixture that asserts the special path reaches an actual grading record.

## Remaining grade-2 functions and reasons

- `code_grade.py:_body_hashes.collect` (cyclomatic 9, cognitive 18, ABC 17.3; cognitive): its recursive AST walk must keep qualification, docstring exclusion, body hashing, and nested traversal coupled to the pre-image identity calculation.
- `code_grade.py:gated_set` (cyclomatic 8, cognitive 25, ABC 22.6; cognitive): it is the single ordered no-ratchet transaction resolving same-name, same-body, and rename pre-images into gated versus informational records.
- `test-code-grade.py:check_changed_function_resolution` (cyclomatic 5, cognitive 0, ABC 33.3; ABC): the integrated fixture keeps the seven required source-change cases and their exact gated/informational assertions visible together.
- `test-code-grade.py:main` (cyclomatic 8, cognitive 11, ABC 35.7; ABC): it intentionally orchestrates fixture-band, nested-name, direction-pair, NUL-path, resolution, worked-example, and delivery contracts in one test script.
- `test-gate-policy.py:check_policy_loading` (cyclomatic 1, cognitive 0, ABC 36.1; ABC): it retains all policy-load success and malformed/missing configuration cases in one temporary-directory lifecycle, preserving shared fixture setup and error-value assertions.

No broad unit command, formatter, linter, project-wide suite, UAT, or gate-policy vocabulary change was run or made.
