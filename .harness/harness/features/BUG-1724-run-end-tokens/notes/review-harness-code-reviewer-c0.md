# Code review — BUG-1724-run-end-tokens — c0

## BLUF

T-01's six-file surface passes ordered spec compliance and scoped code-quality review at pinned SHA `77dbda525d1bede96071076e5b07cef40f3fbc06`. The overall review is nevertheless **FAIL** because the mandatory merge-base code-grade audit finds one unrelated, unbindable high-severity Python grade regression in the pinned range.

## Pinned review surface

Reviewed `82c9d0743ad6f289f1ce62d741d02daefdf8f68a..77dbda525d1bede96071076e5b07cef40f3fbc06`, pinned at `77dbda525d1bede96071076e5b07cef40f3fbc06`, for exactly:

- `.omp/extensions/harness-hooks.ts`
- `.claude/skills/harness/bin/feature-record.py`
- `.claude/skills/harness/SKILL.md`
- `tests/unit/omp-hooks.test.ts`
- `tests/unit/test-omp-hooks.py`
- `tests/unit/test-feature-record.py`

## Stage 1 — spec compliance: PASS

All five changed task files trace to SC-01–SC-04; `tests/unit/test-omp-hooks.py` is in the declared surface but unchanged. The hook accepts only non-negative integer result values, sums one task call, stamps once before spend, and does not stamp the no-value path (`.omp/extensions/harness-hooks.ts:369-389`, `.omp/extensions/harness-hooks.ts:1014-1032`). The ledger writes only the unique started/unended run, refuses no-open or ambiguous-open state before mutation, preserves a pre-stamped value on bare `run-end`, and retains the explicit override (`.claude/skills/harness/bin/feature-record.py:134-180`, `.claude/skills/harness/bin/feature-record.py:446-458`). The playbook removes normal transcription (`.claude/skills/harness/SKILL.md:78-86`). Tests bind summation, once-only and stamp-before-spend ordering, invalid-host-value rejection, null compatibility behavior, preservation, explicit override, named refusal diagnostics, and byte preservation (`tests/unit/omp-hooks.test.ts:1237-1282`, `tests/unit/test-feature-record.py:148-190`). No historical backfill, context-JSONL token read, spend-summation change, or advisory-decision change appears in the task surface. No scope creep, omission, or mismatch found.

## Stage 2 — code quality: FAIL (mechanical range gate)

The scoped six-file implementation has no substantive quality finding. Fail-open and silent-path inspection specifically covered missing/malformed `details.results`, invalid token types and ranges, zero as a measured value, stamp refusal with no or multiple open runs, ignored non-blocking stamp failures, pre-stamped preservation, ordering, and absence of historical mutation. The task verification passed: `python3 tests/unit/test-feature-record.py && python3 tests/unit/test-omp-hooks.py` (45 Python tests and 74 Bun tests).

The mandatory grader over `merge-base(origin/main, review_sha)..review_sha` reports an unrelated high record outside T-01's exact surface: `.claude/skills/harness/bin/check-state.py:242`, `_quoted_scalar_closed`, cyclomatic 8, cognitive 15, ABC 14.7, grade 3, driver cognitive, production bar 4. This is an **unbindable scope change**, not a T-01 defect; nevertheless the review protocol requires `code_grade: fail` and a high finding.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "T-01's exact surface passes both ordered review stages, but an unrelated high code-grade regression in the pinned merge-base range gates the review."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      task: unbindable_scope_change
      summary: "Outside T-01: _quoted_scalar_closed is grade 3 against the production bar 4."
      why: "At .claude/skills/harness/bin/check-state.py:242 the grader reports cyclomatic 8, cognitive 15, ABC 14.7, with cognitive as driver. If quoted-scalar handling is extended for an input combining escapes and comment-like text, this control shape makes a missed state transition realistically able to misclassify a valid plan and block it; the path is outside T-01's six-file surface and cannot be bound to T-01."
  must_fix:
    - "Resolve the unbindable high code-grade record in the pinned review range, or re-pin a range that excludes the unrelated change; T-01's six-file implementation itself needs no repair."
  spec_violations: []
  code_grade: fail
  reviewed: "82c9d0743ad6f289f1ce62d741d02daefdf8f68a..77dbda525d1bede96071076e5b07cef40f3fbc06"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-code-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1724-run-end-tokens/.harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-code-reviewer-c0.md
```
