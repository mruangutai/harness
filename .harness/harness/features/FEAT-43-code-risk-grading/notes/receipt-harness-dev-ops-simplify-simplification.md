# SIMPLIFICATION — FEAT-43

**Verdict: findings recorded.** The complete scoped diff from `7ccfae8dd7644bc3aaea612dabf4317c0d804f99` through the working tree, including untracked files, was assessed only for added unnecessary complexity. Settled decisions, including the test-kind split, DEC-187 exclusion, canonical boundary resolver, reviewer-grade policy, and deliberate boundary evidence, were not flagged.

## Findings

1. **File:** `.claude/skills/harness/bin/code-grade.py`
   **Line:** 42
   **Summary:** `_is_test` reloads and reparses `harness.json` for every graded function instead of classifying each path once.
   **Concrete cost:** A file containing N functions performs N identical config reads, JSON parses, and glob setup; the policy that determines a record's bar is also split between per-record construction and report traversal.
   **Alternative:** Load active test-kind patterns once per report invocation, classify each source path once, and pass its bar into record construction.

2. **File:** `.claude/skills/harness/bin/code-grade.py`
   **Line:** 89
   **Summary:** `_diff_report` reconstructs function-to-path locations by fetching and grading every changed head file after `gated_set` already fetched and graded those same files.
   **Concrete cost:** Every changed Python file incurs an extra `git show` and AST parse; the second traversal exists only because `FunctionGrade` drops the path supplied to `grade_source`.
   **Alternative:** Retain the source path on each grade record (or return path-record pairs from `gated_set`) and feed that directly to `_record`, removing the `locations` reconstruction loop while preserving rename and pre-image semantics.

No assertion deletion or weakening is recommended.
