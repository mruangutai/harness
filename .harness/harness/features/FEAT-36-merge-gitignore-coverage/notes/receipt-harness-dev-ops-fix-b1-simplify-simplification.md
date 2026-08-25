# Simplification review — B-1 exact diagnostic assertion

**BLUF:** No simplification findings. The assertion at `.agents/skills/harness/bin/test-merge-gitignore.py:71-81` has no unnecessary complexity that can be removed while retaining exact `  - ` bullet anchoring, equality against every required rule, and a diagnostic that distinguishes missing from unexpected rules.

## Findings

Empty (`[]`).

- Lines 71-73 deliberately extract only anchored diagnostic bullets and preserve their rule text.
- Lines 74-81 keep the expected and actual sets available for a two-sided, actionable mismatch diagnostic; inlining or reducing this structure would not improve clarity without weakening diagnostics.
- No source or test files were edited. No tests, formatters, linters, builds, or suites were run, per the read-only simplify assignment.

## Evidence consulted

- `.agents/skills/harness/bin/test-merge-gitignore.py:62-83`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-qa-validator/digest.md:1-35`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-fix-b1.md:23-40`
