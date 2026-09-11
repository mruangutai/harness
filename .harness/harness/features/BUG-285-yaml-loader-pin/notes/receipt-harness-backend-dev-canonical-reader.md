# Receipt — harness-backend-dev — BUG-285 canonical feature.json reader

## What changed

- **`.claude/skills/harness/bin/feature_json_write.py`** — added `load_feature_json(path)`,
  the one canonical reader: stdlib `json` only (never YAML), reads bytes inside its own
  `try` catching both `OSError` and `UnicodeDecodeError`, rejects a repeated mapping key at
  any nesting depth via a `json.load(object_pairs_hook=_reject_duplicate_keys)`, raises one
  typed `FeatureJsonError` (mirrors `factory_config.FleetError`'s shape) for every
  read/parse/shape failure, and returns `None` for an absent file — never conflated with a
  raise. Also added `opt_int(value)`, moved verbatim (same semantics, same docstring
  rationale) from gh-sync.py's private `_opt_int`.
- **`gh-sync.py`** — `load_recorded` now calls `feature_json_write.load_feature_json` and
  `feature_json_write.opt_int` instead of parsing for itself; `_opt_int` deleted, along with
  its dead `except (ValueError, UnicodeDecodeError)` (the `UnicodeDecodeError` clause could
  never fire on an already-decoded `str`). One stray docstring reference to `_opt_int`
  elsewhere in the file (`parse_source_issues`) updated to point at the new location.
- **`factory_decompose.py`** — `load_factory` now calls `feature_json_write.load_feature_json`;
  the `factory_cli.refuse(TOOL, "feature.json invalid", path, ...)` call shape, its exit code
  (`EXIT_REFUSED`/2), and the empty-record-on-absent behaviour are all unchanged. History
  comment above it updated to describe the new mechanism (not deleted).
- **`tests/unit/test-feature-json-reader.py`** (new) — 21 cases: one per parity-survey row
  exercising `load_feature_json` directly (absent, empty, unparseable, non-UTF-8, three
  non-mapping top-level shapes, block-key-absent, block-key-present-not-a-mapping,
  wrong-typed members, duplicate top-level key, duplicate nested key, YAML-only document,
  the valid-document control), an absent-vs-malformed cross-check, four `opt_int` cases, and
  two structural checks (via `ast`) asserting neither `load_recorded` nor `load_factory`
  contains `json.load(`/`json.loads(`/`harness_yaml.load_file(` in its own body any more.

## Absent-vs-malformed design

`load_feature_json` returns `None` for absent and raises `FeatureJsonError` for every other
failure — the same convention this module's own `parse_doc` (used by `write_feature_json`)
already established: `None` means absent, `{}` would mean "present, parsed, empty", and the
two are never interchangeable. A sentinel return over an `(exists, doc)` tuple or an
`exists=` flag because callers already had to draw this exact line (gh-sync.py's
`save_recorded` already special-cases `base is None` vs an empty dict) — reusing the
existing idiom means a caller cannot accidentally write `if doc:` and silently conflate
"nothing recorded" with "file missing", the way `and`-ing two booleans invites. Demonstrated
directly: `test_absent_and_malformed_are_distinguishable`.

## Dispatch anchors verified

- `_opt_int` was at gh-sync.py:512-524 as given — correct.
- `load_recorded` was at gh-sync.py:527-636, not 527-600 as given — the function runs 27
  lines longer than stated; read and edited the full range.
- `load_factory` was at factory_decompose.py:111-168 as given — correct.

## Frozen planning artifacts vs this dispatch

`BRIEF.md`/`plan.yaml` under this feature directory describe a DIFFERENT, since-superseded
design (D-16: `_opt_int` left untouched in gh-sync.py, `load_factory` reimplements it as a
nested helper inside itself, duplicate-key detection abandoned entirely). Per this
direct dispatch's explicit instruction, those artifacts were left untouched and NOT
followed — the dispatch's own seven numbered properties (in particular property 3, duplicate-key
rejection, and property 7, one shared `opt_int`) are what this receipt implements. Anyone
reconciling the frozen plan against this landed change should expect that divergence; it is
deliberate, per the operator's own direct-dispatch framing, not an oversight.

## Verify

- `python3 tests/unit/test-feature-json-reader.py` — 21/21 pass.
- `python3 tests/integration/test-gh-sync-open.py` — ALL PASSED (includes every fix1/T-06C
  row already pinned to `load_recorded`'s old behaviour, all still true through the new
  loader).
- `python3 tests/integration/test-factory-decompose.py` — 170/170 pass (includes case 1c,
  the unparseable-feature.json refusal shape).
- `python3 tests/integration/test-gh-sync-{abandon,record,ship,start-task}.py`,
  `tests/unit/test-gh-sync-build-entry.py`, `tests/integration/test-factory-integration.py`,
  `tests/unit/test-feature-json-budget.py` — all pass.
- Mutation probe (never on the live file — copied to `/tmp`, mutated, verified RED, deleted):
  removing `object_pairs_hook=_reject_duplicate_keys` from a scratch copy of
  `feature_json_write.py` makes the duplicate-key case silently return last-wins instead of
  raising, confirming `test_duplicate_top_level_keys_raise`/`test_duplicate_nested_keys_raise`
  have teeth.

## Found, not anticipated by the dispatch

Both `load_recorded` and `load_factory` were **already** grade-1 (code-risk-grading) before
this change — `load_recorded` was cyclomatic 22/cognitive 25/ABC 56.6, `load_factory` was
cyclomatic 26/cognitive 48/ABC 54.9 at `HEAD` (`6cb113f4`), confirmed by grading the
pre-change source directly. This change reduces both (`load_recorded` now 20/24/48.5,
`load_factory` now 25/47/52.3) because the parse/read logic it replaces is gone, but neither
crosses the grade-4 bar — the remaining complexity is each function's own field-by-field
extraction logic (`attached`, `issues`, `typed`, `source_issues`, `build_entry` for
`load_recorded`; `repo`, `parent`, `issues`, `items`, `edges`, `typed` for `load_factory`),
untouched by this dispatch and out of its declared scope (only the parse/read layer was in
scope; the ~10 other feature.json readers and any broader restructuring are non-goals here).
Flagging per the code-risk-grading skill's carve-out ("does not fix code already below the
bar") rather than unilaterally refactoring two functions well beyond this bug's boundary.

## Open questions

- **Q1 (non-blocking):** should the pre-existing grade-1 complexity of `load_recorded` and
  `load_factory` be split into smaller helpers in a follow-up? Both already failed the bar
  before BUG-285 touched them and this change improves rather than worsens them; a
  restructure was explicitly out of this dispatch's non-goals.
