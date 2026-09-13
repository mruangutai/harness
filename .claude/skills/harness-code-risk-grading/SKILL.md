---
name: harness-code-risk-grading
description: Keep Python functions readable by grading cyclomatic, cognitive, and ABC complexity. Apply before review whenever changing Python.
user-invocable: false
---

# Code-risk grading

Write Python functions that stay easy to read, change and review. **The bar: grade 4 or better in
production code, grade 3 or better in test code.** The bar is a design target, not a licence for
unrelated cleanup or for splitting coherent logic into meaningless helpers; code already below the
bar is a separate cleanup, never a touch-it-fix-it ratchet.

## The rules

- **Blocking.** A gated function below its bar and not grade 2 — grade 1 anywhere, or grade 3 in
  production — is a **high** finding and fails review.
- **Reason required.** A grade-2 function passes only with a written reason naming the function,
  one per `REASON REQUIRED` line the tool prints.
- **The tool is evidence, not the last word.** Improve a function whose shape is hard to follow
  even when its numbers pass; a clean grade decides nothing on its own.

## Self-check before review

```sh
python3 <HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main HEAD)" --head HEAD
```

The output is the contract: per function it prints the three metrics, `GRADE`, `DRIVER` (the worst
metric — a grade is the worst band, never an average), `BAR`, `RESULT` and, when a response is
owed, `SEVERITY: high` or `REASON REQUIRED`. Thresholds live in `code_grade.py`; the reviewer's
use of the same run is `harness-code-review § Grade changed Python`.

When a grade surprises you — a function you read as simple grades 3, or you cannot see how to lift
one — read `<HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/references/code-risk-examples.md`: the threshold table, five
before/after shapes (return early, one loop per function, name a compound condition, error case
first, one reason to change) and graded worked examples.
