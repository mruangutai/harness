# Observations — harness-pm — FEAT-2682-backlog-exposure

- 2026-11-28: A dispatch-prescribed change_type (enhancement) was outside both harness.json test_matrix and gh_issue_types.DEFAULT_TYPE_BY_CHANGE_TYPE; gh-sync open would raise UnknownWorkNature on it. Check change_type against both tables, not just the matrix.
- 2026-11-28: "Refused before any GitHub call" for a gh-sync verb means before load_config, which runs gh auth status; validation inside the cmd_* function is already too late.
