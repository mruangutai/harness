# Observations — harness-qa — FEAT-2489-plan-routes-split

- 2026-11-24: tests.yml has no --consolidation-audit step; the consolidation audit reaches CI only via test-checker-structure-locks.py (integration). Dispatches that name a "CI consolidation gate" are mistaken; run it raw and say so.
- 2026-11-24: cp into notes/ under bash-write-guard succeeds only with a literal absolute target; a $VAR target is blocked (confirms G-13 for cp, not only redirects).
