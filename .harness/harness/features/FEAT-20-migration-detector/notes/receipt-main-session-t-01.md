# Receipt — T-01, main-session-direct — 2026-08-14

DEC-174 carve-out by content: built by hand in the main session, never dispatched.

## Red-first record

Tests written and registered BEFORE the module existed. Observed red run, verbatim:

```
$ python3 .claude/skills/harness/bin/test-layout-migration.py
FAIL - layout_migration.py does not exist yet (red-first run)
exit: 1
```

Module then written; same suite green — 22 assertions across cases 1-17 (case 5 has two
halves; cases 1 and 14 carry multiple assertions). Case 17 is appended, never renumbered:
plan-phase Q3's bidirectional enum/table check (`validate_table` raises `LayoutTableError`
on a row keyed to a non-member surface).

## Verify clause, run as plan.yaml spells it

```
run-unit-tests.sh --kind unit  -> exit 0
output contains the exact line: PASS test-layout-migration.py
```

## Case 1 on the real tree at this commit

exit 0, non-zero feature-dir and reader-file counts, X+Y+Z == 2 — both surfaces judged
CLEAN on today's all-legacy tree, so the reader-table patterns hold against the real
files, not only against stubs.

## Q3 gap closed while implementing

The intent specified enum→table only. `validate_table` closes table→enum: a row keyed to
a surface outside the enum is a loud `LayoutTableError`, and case 17 proves it reddens.
