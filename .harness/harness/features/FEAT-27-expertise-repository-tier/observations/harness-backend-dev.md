# Observations — harness-backend-dev — FEAT-27

- 2026-08-19: REUSE-angle read of `b4659cd..252fa72`. `test-check-expertise.py` has two
  fixture builders for the identical Expertise-file skeleton in one file: `valid()` (line
  22, pre-existing) and `body_with_entry()` (line 94, added for T-03's tier/advisory
  cases) — the latter is `valid()` generalized over the Patterns-entry text. Worth
  checking for this shape (a later cycle adding a parametrized twin of an existing fixture
  builder instead of generalizing the original in place) in future `test-*.py` diffs in
  this bin/ directory — the split happens across two PLAN tasks (T-01 vs T-03) authored at
  different times, which is exactly when nobody notices the earlier builder already does
  the job.
