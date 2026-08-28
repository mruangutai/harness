# Simplification assessment — FEAT-43

**Conclusion: apply one simplification before review.** The CLI duplicates the internal commit-resolution guard already available from its imported implementation module.

## Assessed paths

- `.claude/skills/harness/bin/code-grade.py`
- `.claude/skills/harness/bin/code_grade.py`
- `.claude/skills/harness/bin/validate-digest.py`
- `.claude/skills/harness/bin/test-code-grade-cli.py`
- `.claude/skills/harness/bin/test-code-grade.py`
- `.claude/skills/harness/bin/test-check-plan-routes.py`
- `.claude/skills/harness/bin/test-validate-digest.py`

## Finding

- **Files/symbols:** `.claude/skills/harness/bin/code-grade.py:_commit_oid` (line 26) and `.claude/skills/harness/bin/code_grade.py:_commit_oid` (line 281).
  **Summary:** The CLI maintains a duplicate, byte-for-byte-equivalent commit revision resolver despite importing `code_grade`.
  **Concrete cost:** These security-sensitive option/commit validation implementations can drift; changes to Git invocation, validation, or error behavior require synchronized edits and leave the CLI and importable seam liable to diverge.
  **Required alternative:** Remove `code-grade.py:_commit_oid` and call `code_grade._commit_oid(root, args.base)` / `code_grade._commit_oid(root, args.head)` in `main`.

Source/test edits: none (assessment-only authorization).
