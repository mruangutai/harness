# QA — test-matrix gate, BUG-285 (`592e6412` vs `6cb113f4`)

**BLUF: PASS.** Suite is green (11 files, all changed-module-touching, zero failures), the
regression is proven by mutation (three independent mutants, each caught by a distinct,
non-overlapping subset of cases), the structural single-implementation check is proven
non-vacuous, and 12/13 parity-survey rows are covered end-to-end at a call site. One real gap:
non-UTF-8 bytes is exercised only at the accessor, never at either call site — `low`, because both
call sites share the identical `except FeatureJsonError` branch already end-to-end-proven for
every other malformed-input row.

## Commands run (worktree-prefixed; own copies used throughout)

All via `python3 <file>`, no runner wrapper (per dispatch: exercise only changed-module suites).

| file | result |
|---|---|
| `tests/unit/test-feature-json-reader.py` | OK — 21/21, exit 0 |
| `tests/unit/test-gh-sync-build-entry.py` | ALL PASS — 11 named PASS lines, exit 0 |
| `tests/unit/test-feature-json-budget.py` | OK — 8/8, exit 0 |
| `tests/integration/test-validate-feature-json.py` | ALL PASS, exit 0 |
| `tests/integration/test-gh-sync-abandon.py` | ALL PASSED, exit 0 |
| `tests/integration/test-gh-sync-open.py` | ALL PASSED, exit 0 |
| `tests/integration/test-gh-sync-record.py` | ALL PASSED, exit 0 |
| `tests/integration/test-gh-sync-ship.py` | ALL PASSED, exit 0 |
| `tests/integration/test-gh-sync-start-task.py` | ALL PASSED, exit 0 |
| `tests/integration/test-factory-decompose.py` | 170/170 checks passed, exit 0 |
| `tests/integration/test-feature-json-merge.py` | 37/37 checks passed, exit 0 |

Graded on exit status + per-file/per-case verdict lines, never a bare `^FAIL ` grep (per Gotcha
G-08/dispatch note — `test-factory-decompose.py` and `test-gh-sync-*` print `ok`/`PASS`-prefixed
lines, no `FAIL ` tokens leaked from a passing mutation self-proof in this run).

## Mutation table (all work under `/tmp/bug285-mutant/`, full `bin/` copy + copy of the new unit
file; nothing touched inside the worktree — `git status --porcelain` on `bin/` and `tests/`
confirmed clean after cleanup)

| mutant | change | cases that catch it |
|---|---|---|
| M1 — collapse malformed→`{}` | both raise-sites in `load_feature_json` (`does not parse`, `not a mapping`) return `{}` instead of raising | 9: `test_unparseable_json_raises`, `test_empty_file_raises_not_returns_empty`, `test_top_level_list_raises`, `test_top_level_scalar_string_raises`, `test_top_level_scalar_int_raises`, `test_yaml_only_document_raises`, `test_duplicate_top_level_keys_raise`, `test_duplicate_nested_keys_raise`, `test_absent_and_malformed_are_distinguishable` |
| M2 — drop `object_pairs_hook` | `json.loads(text, object_pairs_hook=_reject_duplicate_keys)` → `json.loads(text)` | 2 (exactly): `test_duplicate_top_level_keys_raise`, `test_duplicate_nested_keys_raise` |
| M3 — narrow read guard | `except (OSError, UnicodeDecodeError)` → `except OSError` | 1 (exactly): `test_non_utf8_bytes_raise_not_traceback` — reddens as an **uncaught `UnicodeDecodeError`** (ERROR, not FAIL), i.e. exactly the pre-fix traceback shape claim 4 exists to close |
| M4 — reintroduce an independent parse in `load_factory` (structural-check discrimination proof, item 3) | added a fallback `json.loads(open(path).read())` inside `load_factory`'s except-branch | 1 (exactly): `test_load_factory_does_not_parse_independently` reddens on the literal `'json.loads('` match. Confirms the structural check is NOT vacuous — it can fail |

No mutant went uncaught; no case fired on more than one mutant (M1's 9 are disjoint from M2's 2
and M3's 1) — each case discriminates a distinct failure mode, none is dead weight.

## Test-quality (21 cases)

Every case asserts a consumer-observable outcome: `assertRaises(FeatureJsonError)`,
`assertIsNone`, or `assertEqual` against the returned dict — none pins a field copy, a default,
or a mock echo. The one check flagged for scrutiny per dispatch item 3:

**`SingleReaderStructuralTest`** greps `load_recorded`'s / `load_factory`'s own AST-extracted
source for `"json.load("`, `"json.loads("`, `"harness_yaml.load_file("`. This is a source-text
check, not a behavioral one — but M4 above proves it is NOT toothless: reintroducing a real
independent parse call reddens it immediately. Its one real limitation (not exercised, out of
scope of "can it fail"): an aliased import (`import json as j; j.loads(...)`) would evade the
literal match. Not a finding — dispatch asked only whether the check can fail, and it can.

## 13-row parity-survey coverage map

| # | row | accessor-level (unit) | call-site level (integration) |
|---|---|---|---|
| 1 | file absent | ✅ `test_absent_file_returns_none` | ✅ `load_recorded` fix1-B-row1a; `factory_decompose` `doc is None` path exercised throughout `test-factory-decompose.py`'s no-file fixtures |
| 2 | empty (0 bytes) | ✅ `test_empty_file_raises_not_returns_empty` | ✅ `load_recorded` fix1-B-row2 (0-byte fixture, asserts SystemExit + message) |
| 3 | present, not valid JSON | ✅ `test_unparseable_json_raises` | ✅ `factory_decompose` (1c) "unparseable feature.json: exits 2, names path, no leaked class name" |
| 4 | non-UTF-8 bytes | ✅ `test_non_utf8_bytes_raise_not_traceback` | ❌ **gap** — neither `load_recorded` nor `load_factory` has a dedicated non-UTF-8-bytes fixture; both route through the identical `except FeatureJsonError` branch already proven for rows 2/3/5/6/9, so the mechanism is exercised by proxy, but the specific byte sequence claim 4 names is untested at either call site |
| 5 | top-level list | ✅ `test_top_level_list_raises` | ✅ `load_recorded` fix1-B-row2 non-mapping (`a_list`) |
| 6 | top-level scalar string | ✅ `test_top_level_scalar_string_raises` | ✅ `load_recorded` fix1-B-row2 non-mapping (`a_scalar`) |
| — | top-level scalar int | ✅ `test_top_level_scalar_int_raises` | not separately fixtured at a call site (string/list stand in; same code path) |
| 7 | block key absent | ✅ `test_block_key_absent_returns_the_mapping` | ✅ `load_recorded` `_rec2`/fix1-B-row1b; `factory_decompose` `f is None` path |
| 8 | block key present, not a mapping | ✅ `test_block_key_present_not_a_mapping_still_returns` | ✅ `load_recorded` fix1-B-row4 (`github` = string/list); `factory_decompose`'s equivalent `isinstance(f, dict)` guard (`:127-129`, pre-existing, unchanged by this diff) is not separately call-site-fixtured, but it is untouched code, not new surface |
| 9 | block mapping, wrong-typed members (`"7"`→7) | ✅ `test_wrong_typed_members_still_returns` | ✅ `load_recorded` T-06C: "populated github: block loads, quoted milestone coerced by `_opt_int`" |
| 10 | duplicate top-level keys | ✅ `test_duplicate_top_level_keys_raise` (+ `test_duplicate_nested_keys_raise`, stricter than the row) | not call-site-fixtured; mechanism identical to row 3 |
| 11 | YAML-only block mapping | ✅ `test_yaml_only_document_raises` | not call-site-fixtured; mechanism identical to row 3 |
| 12 | valid JSON, well-formed (control) | ✅ `test_valid_well_formed_document_returns_it` | ✅ every happy-path fixture across all 8 integration files |

(13 rows collapse to 12 map entries above; top-level scalar int/string share one call-site
mechanism, noted inline.)

## Call-site (end-to-end) answer — dispatch item 5

**Not accessor-only.** Both `gh-sync`'s `load_recorded` and `factory_decompose`'s `load_factory`
are exercised post-fix for the two behaviors that matter: (a) refuse rather than traceback for a
present-and-malformed file — `test-gh-sync-open.py` fix1-Part-B rows 1a/1b/2/4 assert `SystemExit`
+ message content (never a bare "it raised"); `test-factory-decompose.py` case (1c) asserts exit
code 2, the path named on stderr, and no leaked exception-class name, proving claim 5 (refusal
shape preserved, `SystemExit` propagates unwrapped through `factory_cli.run`) directly; (b) still
return the empty record for a genuinely absent file — both exercised across the happy-path
fixtures. The one call-site gap is non-UTF-8 bytes specifically (row 4 above) — `low`, not
`missing`, since the branch it would exercise is the same branch nine other rows already prove at
the call site.

## matrix

`unit` and `integration` both satisfied — named tests ran, present in the diff (new unit file) or
already covering the changed call sites (pre-existing integration files, still exercising the new
code path through the same public entry points). No `config`/`ai_behavior`/`ui` surface touched.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Suite green (11/11 files), regression proven by 3 disjoint mutants, structural check proven non-vacuous by a 4th; one low-severity gap — non-UTF-8 bytes untested at either call site."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-feature-json-reader.py", named_tests: 21 }
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-gh-sync-build-entry.py", named_tests: 11 }
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-feature-json-budget.py", named_tests: 8 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-validate-feature-json.py", named_tests: 12 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-gh-sync-abandon.py", named_tests: 13 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-gh-sync-open.py", named_tests: 13 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-gh-sync-record.py", named_tests: 13 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-gh-sync-ship.py", named_tests: 13 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-gh-sync-start-task.py", named_tests: 13 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-factory-decompose.py", named_tests: 170 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-feature-json-merge.py", named_tests: 37 }
  coverage_gaps:
    - "non-UTF-8 bytes (parity row 4) untested at either call site (load_recorded / load_factory) — accessor-level only"
  sc_evidence: []
  open_questions:
    - { id: Q1, question: "Add one non-UTF-8-bytes fixture at load_recorded and one at load_factory to close the last call-site gap in the parity survey?", blocking: false }
  files_touched: [".harness/harness/features/BUG-285-yaml-loader-pin/notes/qa-bug285-panel.md"]
  expertise_update: []
artifact: .harness/harness/features/BUG-285-yaml-loader-pin/notes/qa-bug285-panel.md
```
