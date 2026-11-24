# Observations — harness-qa — FEAT-2489-plan-routes-split

- 2026-11-24: tests.yml has no --consolidation-audit step; the consolidation audit reaches CI only via test-checker-structure-locks.py (integration). Dispatches that name a "CI consolidation gate" are mistaken; run it raw and say so.
- 2026-11-24: cp into notes/ under bash-write-guard succeeds only with a literal absolute target; a $VAR target is blocked (confirms G-13 for cp, not only redirects).
- 2026-11-24: validate c2: copying runner output into notes/ via cp with a $N variable target was blocked by bash-write-guard; the same cp with a literal absolute target succeeded (repo G-13 reconfirmed for cp, not just redirects).
- 2026-11-24: check-integration-shards.evidence_defects takes docs as a {path: doc} dict and discover_expected returns (paths, err); passing a list raises TypeError — validate-digest.py:2811 shows the call shape.
- 2026-11-24: CR-2 boundary probe: the pre-fix splitlines() checker also equated a bare CR with LF (x\ry\n vs x\ny\n PASSed); the byte-exact pin FAILs it.
