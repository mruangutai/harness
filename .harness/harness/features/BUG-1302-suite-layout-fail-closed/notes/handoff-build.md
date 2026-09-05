# Handoff — BUG-1302 build → validate — 2026-09-05

## Next

Validate the completed main-session-direct build at the `feature.json` `review_sha`. Run the independent QA and review panel; do not review moving `HEAD`.

## Build result

- T-01 through T-05 are `done`; `plan.yaml` is at `review`.
- `tests/unit/test-suite-layout.py` removes the two dead conditions, makes case 11 fail closed, and reports unreadable tracked sources as named assertion data.
- `tests/integration/test-run-unit-tests-layout.py` case 2 now rejects either sentinel prefix before refusal.
- Red demonstrations are recorded in `notes/red-demonstrations-2026-09-05.md`.

## Verification

- `python3 tests/unit/test-suite-layout.py`: exit 0; every printed check PASS, including the four new B-4/B-5 checks, two B-6 checks, B-14, the real-layout check, sole-implementation sweep, case 11 hygiene, and cases 1 through 10.
- `python3 tests/integration/test-run-unit-tests-layout.py`: exit 0; every printed check PASS, including all eight pre-existing named integration checks and the widened case 2.
- B-8 discriminating experiment: widened assertion exited 1 when only the integration sentinel ran before refusal; the old narrow assertion exited 0 against the identical mutated runner.
- `code-grade.py` over the branch diff: PASS. Direct grades for changed functions are `_violations_callers` grade 3, `_is_inside_tests` grade 3, `_literal_key_present` grade 3.
- Four-angle simplify pass: REUSE none; EFFICIENCY none; ALTITUDE none; SIMPLIFICATION found one positional-AST extraction improvement, applied; unit suite rerun exit 0.

## Scope

Only the two approved test files and BUG-1302 lifecycle artifacts changed. No production gate script or unrelated file changed.
