# FEAT-43 SIMPLIFY APPLY — retain graded source paths

**Verdict: applied.** Finding 2 is resolved: each `FunctionGrade` now retains its source path, so `code-grade.py` formats gated records directly and no longer reconstructs locations by re-fetching and re-parsing changed head files.

## Ownership and scope

- **Owner:** `harness-backend-dev` (shared backend/dev-ops grader runtime/data-flow logic).
- **Applied files:** `.claude/skills/harness/bin/code_grade.py`, `.claude/skills/harness/bin/code-grade.py`, `.claude/skills/harness/bin/test-code-grade.py`.
- **Preserved behavior:** `gated_set` still owns changed-file, rename, and pre-image resolution; the CLI retains its prior parse preflight, output fields, reviewer bar policy, and functional exclusion behavior.
- **Contract coverage:** `test-code-grade.py` now asserts gated and informational records retain `main.py` and renamed `relocated.py` paths.

## Test-first and verification

- **RED:** `python3 .claude/skills/harness/bin/test-code-grade.py` exited 1 before production edits: `AttributeError: 'FunctionGrade' object has no attribute 'path'` at the new source-path assertion.
- **GREEN:** the same focused command exited 0 and printed `PASS test-code-grade` after the edit.
- **Initial apply outcome:** green; no assertion was removed or weakened.
- **Corrective fixes:** 0.
- **Send-backs:** 1 (evidence-only receipt correction; no code change).
- **Unit:** `PATH=/opt/homebrew/bin:$PATH .agents/skills/harness/bin/run-unit-tests.sh --kind unit` exited 0 — **29/29 named scripts passed**.
- **Integration:** `PATH=/opt/homebrew/bin:$PATH .agents/skills/harness/bin/run-unit-tests.sh --kind integration` exited 0 in 255.28s — **28/28 named scripts passed**. The first invocation was externally cut off at 120 seconds; no test failure or code correction occurred before the completed reissue.
