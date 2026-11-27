# Operator ruling — BUG-2451 after validate c2 (2026-11-27)

Answers OQ-A from run 2026-11-26-03-validate-c2-validator.

- **MF-2R: one narrow extra fix round granted** beyond the spent 1-round ruling, in tests/unit/test-prune-run-evidence.py only. Acceptance:
  - a capitalised forbidden claim fails the check;
  - a changed DEC-257 claim fails the check;
  - no current text in the five files gives a false failure.
  - A-3 is folded in: scope the scan so that an unrelated future 'git add' elsewhere in DECISIONS.md does not fail the test.
- **A-1** is not fixed in this round. It goes to the backlog.
- **Backlog at ship:** A-1, A-2, SEC (unescaped stderr names) and SCHEMA (orchestrators forward outputSchema/schemaMode to leads). A-3 is backlogged only if the fix does not resolve it.
- **Struck:** C2-F1, C2-F2, QA-F2, OQ-2, OQ-1.
- **Housekeeping:**
  - runs -02 and -03 are accepted as recorded (DEVIATION-1 and DEVIATION-2);
  - no forced succession judgement (DEVIATION-3);
  - the red-first note's '55 PASS' is corrected to the measured 52.
