# Observations — harness-backend-dev — BUG-1699-lifecycle-cards

- 2026-09-16: Feature-phase status projection must use gh_board.project; task-start remains a direct task Building write so active phase projection does not override the task-start receipt.
- 2026-09-16: INV-26 eligibility must require recorded github.issues before both its batched board lookup and comparison loop; otherwise active no-mirror records are falsely treated as board drift.
