# REUSE assessment — BLOCKED

A warranted reuse edit remains before review: Git commit-resolution logic has three independent implementations.

## Assessed paths

- `.claude/skills/harness/bin/code-grade.py`
- `.claude/skills/harness/bin/code_grade.py`
- `.claude/skills/harness/bin/validate-digest.py`
- `.claude/skills/harness/bin/test-code-grade-cli.py`
- `.claude/skills/harness/bin/test-code-grade.py`
- `.claude/skills/harness/bin/test-check-plan-routes.py`
- `.claude/skills/harness/bin/test-validate-digest.py`

Source/test edits: none.

## Finding R-01

- **File / line / symbol:** `.claude/skills/harness/bin/code-grade.py:26`, `_commit_oid`; `.claude/skills/harness/bin/validate-digest.py:540`, `resolve_reviewed_commit`.
- **Existing thing:** `.claude/skills/harness/bin/code_grade.py:281`, `_commit_oid(repo_root, revision)`.
- **Summary:** The CLI and digest validator restate the existing commit-only Git revision resolver instead of reusing it.
- **Concrete cost:** The three variants must be hardened in lockstep for revision validation and Git invocation; a future correction can reach only one caller, leaving another stale and silently changing the security/fail-closed boundary.
- **Required alternative:** Use `code_grade._commit_oid` as the single resolver: have `code-grade.py` call it directly, and have `validate-digest.py` call it and translate its `ValueError` to the existing `None` result. Preserve each caller's present reporting contract.
