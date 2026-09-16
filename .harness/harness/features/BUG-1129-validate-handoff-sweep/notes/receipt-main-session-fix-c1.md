# Fix c1 — BUG-1129 (validate c0 FAIL: Q1, Q2, Q3) — by Main, main-session-direct (DEC-174)

- **Q1 (SC-01 assertions).** The refusal case now asserts `validation incomplete` + the note's name, byte-identical plan.yaml with the station equal to its pre-call value, and an EMPTY write set across the whole gh boundary (every logged call except `auth status`) with a `--body-file` supplied so the comment path is inside the boundary.
- **Q2 (SC-03 fail-closed coverage).** New `tests/unit/test-handoff-policy.py`: the one exempt shape plus absent / unparsable / non-mapping / empty tasks / non-list tasks / non-mapping task / missing mode / team / mixed / unreadable (mode 000) → no exemption, with the detail named where the plan could not be evaluated. Through the verb: an unparsable plan with no note → exit 1, names the note and `does not parse`, no write. Red under the fail-open mutant (receipt arm 5).
- **Q3 (SC-04 fixture contract).** The default `stage_ship` is asserted to write the note with every handoff section; red against origin/main's support module (receipt arm 4).
- Matrix at HEAD: unit OK, integration OK; code-grade 0 FAIL.
