# FEAT-53 frontend apply receipt

**BLUF:** Safe client simplifications are committed without product-behavior changes.

- **Commit:** `2f5c087e`
- **Changed paths:**
  - `.claude/skills/harness/bin/dashboard/client/src/routes.tsx`
  - `.claude/skills/harness/bin/dashboard/client/src/work-view.tsx`
- **Applied findings:**
  1. Simplification finding 1: rendered non-null durations directly as `${value}s`, preserving the null branch and byte-equivalent non-null output.
  2. Efficiency finding 1: moved the unchanged KPI and work query definitions into their consuming routes. Overview creates both; KPI detail creates only KPI; work detail creates only work.
- **Skipped instructed edits:** none.
- **Tests:** intentionally deferred by the apply-cycle dispatch; no test, formatter, linter, build, or suite was run.
