# Receipt — T-02, main-session-direct — 2026-08-14

DEC-174 carve-out named in CLAUDE.md: check-state.sh edited by hand, tests co-changed in
the same diff, both suites run explicitly.

## What landed

- INV-27 in check-state.sh, composed from layout_migration's STRUCTURED result (import of
  the two exposed functions; no subprocess, no CLI re-parsing). Failed import and a raising
  scan are both CANNOT RUN violations, INV-25's precedent. Every finding ends with the
  remedy clause. NOT APPLICABLE and clean append nothing.
- test-check-state.py case_x, five cases: x.1 mixed (tag + remedy asserted at THIS call
  site), x.2 cannot-verify, x.3 applicable-clean asserting ABSENCE of INV-27 specifically,
  x.4 no-marker, x.5 unimportable module -> CANNOT RUN (run via a copied check-state.sh in
  a bin dir holding only harness_yaml, because the script prepends its own dir to
  PYTHONPATH and a shadow dir cannot outrank the real module).
- test-layout-migration.py case 18: exit-code contract 0/1/2 and scan() prints nothing.

## Found on the way, fixed in scope

test-check-plan-routes.py case_20 joins physical lines until paren depth balances,
counting parens inside string literals. Four reader-table regex rows carried unmatched
parens in their pattern strings, merging the table into one logical line that swallowed
the module's real marker probe — case_20 FAILED. Fixed with per-row `# balance:` comments
in layout_migration.py, documented as load-bearing at the table.

## Verify, run as plan.yaml spells it

run-unit-tests.sh --kind unit -> 0 with 'PASS test-layout-migration.py';
--kind integration -> 0 with 'PASS test-check-state.py'. Live gate at this commit:
exit 0, zero INV-27 lines.
