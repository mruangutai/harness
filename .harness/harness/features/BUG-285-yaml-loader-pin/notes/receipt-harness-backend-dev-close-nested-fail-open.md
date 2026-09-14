# BUG-285 nested loader close — backend receipt

## BLUF
`load_factory` now refuses a present non-mapping `factory` block while preserving both legitimate absent paths, and it delegates parent and issue-number coercion to `feature_json_write.opt_int`.

## Evidence
- TDD RED: before the source edit, `python3 tests/integration/test-factory-decompose.py` ended `2 of 177 FAILING`; the new direct `load_factory` cases for `factory: "x"` and `parent: "7"` failed exactly as predicted. The bool, integer, absent-key, absent-file, and non-UTF-8 controls already passed.
- GREEN: the same suite ended `177/177 checks passed` after the source edit.
- Mutation proof (copy only, never the live source): replacing the non-mapping refusal in a temporary copy returned the empty record; replacing `opt_int` with the former strict-int parent read returned `parent: None`. Both probes printed `RED`.
- 13-row `load_factory` probe: all rows printed `ok`; absent and absent-factory returned empty, malformed/present-unusable shapes refused, and quoted/well-formed parents read as 7.
- Shared-coercion check: `factory_decompose.load_factory` contains two `feature_json_write.opt_int` call sites and no `isdigit`; `feature_json_write.py` contains the sole `def opt_int` in `bin/`.

## Required suites
- `python3 tests/unit/test-feature-json-reader.py` — `Ran 21 tests ... OK`
- `python3 tests/integration/test-factory-decompose.py` — `177/177 checks passed.`
- `python3 tests/integration/test-factory-integration.py` — `131/131 checks passed.`
- `python3 tests/integration/test-factory-issue-types.py` — `ALL PASSED`
- `python3 tests/integration/test-gh-sync-open.py` — `ALL PASSED`
- `python3 tests/integration/test-gh-sync-ship.py` — `ALL PASSED`

## Scope notes
The dispatch's stated `:126-127` and `:131-133` anchors were accurate in the assigned worktree before the edit. The other same-policy numeric field was each value in `factory.issues`; it now shares `opt_int`, so legacy quoted issue numbers are retained and booleans remain absent. No other nested field has an integer coercion contract. The `load_recorded` non-UTF-8 call-site gap is now covered directly in `test-gh-sync-open.py`.
