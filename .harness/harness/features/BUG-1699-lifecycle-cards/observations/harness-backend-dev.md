# Observations — harness-backend-dev — BUG-1699-lifecycle-cards

- 2026-09-16: Feature-phase status projection must use gh_board.project; task-start remains a direct task Building write so active phase projection does not override the task-start receipt.
- 2026-09-16: INV-26 eligibility must require recorded github.issues before both its batched board lookup and comparison loop; otherwise active no-mirror records are falsely treated as board drift.
- 2026-09-16: Direct code-grade path mode measures named functions after a refactor; the mandated diff mode may omit a changed enclosing function when only its helper extraction registers.
- 2026-09-16: When a QA fail-first audit needs a preservation criterion whose historical runner is green, a narrow restored source mutant plus the named direct runner supplies criterion-specific red evidence; record the exact mutant, assertion, exit, and restoration hash.
