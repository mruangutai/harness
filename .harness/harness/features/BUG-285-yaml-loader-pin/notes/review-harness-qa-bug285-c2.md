# QA re-review — BUG-285 remedy C2 (`592e6412..ab0c9987`)

## BLUF

**PASS.** Cycle-1 finding F1 is **CLOSED**: `load_factory` now refuses a present non-mapping `factory` value and normalizes quoted numeric parents via the shared `opt_int`; its new tests redden when each reverted behavior is installed. The new non-UTF-8 fixture reaches **both** real callers, `load_recorded` and `load_factory`, and reddens under the restored uncaught-decode behavior.

## Scoped evidence

- `python3 tests/integration/test-factory-decompose.py` — pass, **177/177** checks.
- `python3 tests/integration/test-gh-sync-open.py` — pass, **ALL PASSED**.
- Remedy diff adds **8 behavioral cases**: seven at `test-factory-decompose.py:444-500` and one at `test-gh-sync-open.py:444-455`. The diff contains 11 `check(...)` invocations because the two refusal cases use separate no-return and diagnostic assertions.

### Mutation proof

Each mutation was made only in a fresh metadata-free `/tmp/bug285-qa-c2-plain` copy, then restored by recopying `ab0c9987`; no feature source or tests changed.

| reverted behavior | live mutant | red test / observed wrong outcome |
|---|---|---|
| nested `factory` non-mapping returns the empty record | replace the refusal at `factory_decompose.py:128-132` with `return factory` | `test-factory-decompose.py` `(1d) non-mapping factory value refuses`: fails because input `{"factory":"x"}` through caller `load_factory` returns instead of refusing. |
| quoted parent is handled strictly | replace `opt_int` at `factory_decompose.py:136` with real-int-only acceptance | `(1d) quoted parent is coerced through load_factory`: fails; input `{"factory":{"parent":"7"}}` yields `parent=None` at `load_factory`, rather than `7`. |
| bool is accepted as an integer | special-case `True` before shared `opt_int` at `factory_decompose.py:136` | `(1d) bool parent remains no value through load_factory`: fails; input `{"factory":{"parent":true}}` yields `parent=True`, rather than `None`. |
| non-UTF-8 is not caught by the canonical reader | change `feature_json_write.py:153` from `(OSError, UnicodeDecodeError)` to `OSError` | `test-factory-decompose.py` aborts at `(1d) non-UTF-8 feature.json refuses and names the file through load_factory`; `test-gh-sync-open.py` aborts at `fix1 B row4: non-UTF-8 feature.json refuses through load_recorded`. Both observe the restored uncaught `UnicodeDecodeError` for `b"\xff\xfe"`. |

## Parity-survey map

`tests/unit/test-feature-json-reader.py:38-152` directly covers the accessor for every row. Caller columns below mean an exact fixture exists in the scoped integration tests; `—` is not a claim that the code is wrong.

| survey row | accessor | `load_recorded` | `load_factory` |
|---|---|---|---|
| 1 absent file | unit `test_absent_file_returns_none` | `test-gh-sync-open.py:408-417` | `test-factory-decompose.py:483-485` |
| 2 empty file | unit `test_empty_file_raises_not_returns_empty` | `test-gh-sync-open.py:426-442` | — |
| 3 invalid JSON | unit `test_unparseable_json_raises` | — | publish fixture `test-factory-decompose.py:424-437` |
| 4 non-UTF-8 | unit `test_non_utf8_bytes_raise_not_traceback` | `test-gh-sync-open.py:444-455` | `test-factory-decompose.py:487-500` |
| 5 top-level list | unit `test_top_level_list_raises` | `test-gh-sync-open.py:457-471` | — |
| 6 top-level string | unit `test_top_level_scalar_string_raises` | `test-gh-sync-open.py:457-471` | — |
| 7 top-level int | unit `test_top_level_scalar_int_raises` | — | — |
| 8 block key absent | unit `test_block_key_absent_returns_the_mapping` | `test-gh-sync-open.py:386-423` | `test-factory-decompose.py:478-481` |
| 9 block key non-mapping | unit `test_block_key_present_not_a_mapping_still_returns` | `test-gh-sync-open.py:473-` | `test-factory-decompose.py:444-455` |
| 10 wrong-typed members | unit `test_wrong_typed_members_still_returns` | quoted milestone at `test-gh-sync-open.py:363-384` | quoted/bool/int parent at `test-factory-decompose.py:457-476` |
| 11 duplicate keys | unit top-level and nested duplicate tests | — | — |
| 12 YAML-only mapping | unit `test_yaml_only_document_raises` | — | — |
| 13 well-formed JSON control | unit `test_valid_well_formed_document_returns_it` | happy-path open cases | publish happy path `test-factory-decompose.py:505-521` |

The deliberately missing exact caller fixtures for rows 2/3/5/6/7/11/12 are parity-map coverage gaps, not a regression in this remedy: each raw parse outcome is accessor-tested and the change adds no per-caller branch for those rows. The remedy’s named risk rows 9/10 and its required row-4 parity now have direct caller coverage. Absent-file and absent-factory-key behavior remain directly covered unchanged.

## Result

No actionable defect found in `592e6412..ab0c9987`; severity_max is `none` and must_fix is empty.
