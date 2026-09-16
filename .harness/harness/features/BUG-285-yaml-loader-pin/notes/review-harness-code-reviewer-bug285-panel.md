# Code review — BUG-285 canonical feature.json reader — `6cb113f4..592e6412`

## BLUF

The accessor-level fix is real and correctly wired at both call sites: `load_feature_json`
distinguishes absent (`None`) from present-but-broken (`FeatureJsonError`), and neither
`load_recorded` nor `load_factory` swallows that exception back into an empty record — this
closes the top-level shape half of the FEAT-14 conflation (rows 2, 5, 6, 7, 11, 12 of the
survey), measured live post-fix. **But two of the six documented FEAT-14 incident-class rows
remain unfixed**: `load_factory` (`factory_decompose.py:127-128`) still returns the empty
record for a PRESENT file whose `factory`/nested field is wrong-shaped — identical, byte-for-
byte, to the pre-fix measurement in the parity survey. That is the same fail-open the fix is
billed to close, reachable through a path the migration did not touch. `FAIL`, one `high`
finding, must_fix.

## Per-claim verdicts

1. **CONFIRMED.** `grep` of both files for `json.loads|json.load|harness_yaml.|yaml\.` inside
   `load_recorded`/`load_factory` bodies: nothing (`feature_json_write.py` diff, `gh-sync.py`
   diff, `factory_decompose.py` diff). `_opt_int` is fully deleted from `gh-sync.py` (not
   merely unused) and relocated verbatim as `feature_json_write.opt_int`; `factory_decompose.py`
   has no coercion helper of its own (`grep opt_int|isdigit` → no matches) — one coercion site.
2. **CONFIRMED at the accessor + both call sites, for the top-level-shape defect; INCOMPLETE for the
   nested-field defect — see finding F1.** `load_recorded` (`gh-sync.py:544-551`) re-raises a
   caught `FeatureJsonError` as `SystemExit` naming the path; never returns `rec` from that
   branch. `load_factory` (`factory_decompose.py:122-125`) calls `factory_cli.refuse(...)`,
   which itself `sys.exit`s — control never reaches `if doc is None: return factory` on that
   path. Measured live: both readers now REFUSE identically on empty file, non-UTF-8 bytes,
   top-level list/string/int (rows 2, 4, 5, 6, 7 — see table below).
3. **CONFIRMED**, and the strictness is real: `test_duplicate_nested_keys_raise` and
   `test_duplicate_top_level_keys_raise` both pass (ran the suite, 21/21 green).
   `object_pairs_hook=_reject_duplicate_keys` fires on every `{...}` object `json.loads`
   parses, at any depth, by construction of the hook mechanism — confirmed with a
   two-level-nested duplicate probe. The `except ValueError` around it cannot swallow an
   unrelated `ValueError`: no other hook (`object_hook`, `parse_float`, …) is registered, so
   the two only possible sources are `json.JSONDecodeError` (parse failure, intended) and
   `_reject_duplicate_keys`'s own raise (intended). **Caveat (low, informational, no
   must_fix):** `parse_doc` (`feature_json_write.py:71-73`, unchanged by this diff) is a
   *different* function serving the write-modify-read path (`write_feature_json`'s callers:
   `save_recorded`, `_record_pr`, `write_factory`) and calls `feature_schema.json.loads(...)`
   with **no** `object_pairs_hook` — still silent last-wins on a duplicate key. No fixture or
   caller in the tree feeds a duplicate-keyed `feature.json` to that path today, so this is a
   pre-existing scope boundary, not a regression from this diff — noted, not gated.
4. **CONFIRMED**, both directions. `gh-sync.py:558-564`'s old `except OSError` alone is gone;
   the read now happens inside `load_feature_json`'s own `try` covering `(OSError,
   UnicodeDecodeError)` (`feature_json_write.py:157-159`). Measured live: non-UTF-8 bytes now
   REFUSE from both `load_recorded` and `load_factory` (row 4), where pre-fix `load_recorded`
   let `UnicodeDecodeError` escape uncaught.
5. **CONFIRMED**, read at source. `factory_cli.run()` (`factory_cli.py:72-96`): `except
   SystemExit: raise` — propagated unwrapped, ahead of the generic `except BaseException`
   that would print "unexpected failure". `load_factory`'s error branch calls
   `factory_cli.refuse(TOOL, "feature.json invalid", path, e.next_step)`, and `refuse` itself
   calls `fail()` (prints, naming `path` as `value`) then `sys.exit(EXIT_REFUSED)` —
   the file is named, the exit is `SystemExit`, and it is never re-wrapped.
6. **PARTIALLY REFUTED — 11 of 13 rows match the survey's acceptance set; 2 do not.** See table.

## 13-row post-fix disposition (measured live, `/tmp/bug285_probe2.py`, same harness pattern the
survey used — `importlib.util.spec_from_file_location`, `BIN` on `sys.path`)

| # | input class | `load_recorded` | `load_factory` | verdict | matches survey's acceptance? |
|---|---|---|---|---|---|
| 1 | file absent | RETURN empty | RETURN empty | SAME | yes (unchanged, correct) |
| 2 | file empty (0B) | REFUSE, names path | REFUSE exit 2, names path | SAME | **yes — closed** (was DIFFERENT) |
| 3 | not valid JSON | REFUSE | REFUSE exit 2 | SAME | yes (unchanged) |
| 4 | non-UTF-8 bytes | REFUSE, names path | REFUSE exit 2 | SAME | **yes — closed** (was DIFFERENT, `load_recorded` UNCAUGHT) |
| 5 | top-level list | REFUSE | REFUSE exit 2 | SAME | **yes — closed** |
| 6 | top-level scalar string | REFUSE | REFUSE exit 2 | SAME | **yes — closed** |
| 7 | top-level scalar int | REFUSE | REFUSE exit 2 | SAME | **yes — closed** |
| 8 | block key absent | RETURN empty | RETURN empty | SAME | yes (unchanged) |
| 9 | block key present, NOT a mapping | REFUSE | **RETURN empty** | DIFFERENT | **NO — see F1** |
| 10 | block mapping, wrong-typed members | RETURN populated | **RETURN empty** | DIFFERENT | **NO — see F1** |
| 11 | duplicate block keys | REFUSE (new — was populated/last-wins) | REFUSE exit 2 | SAME | yes, by design (D-11 stricter direction; no fixture triggers it) |
| 12 | YAML-only block mapping | REFUSE | REFUSE exit 2 (was RETURN populated) | SAME | yes — closed, by design (JSON-only) |
| 13 | valid JSON, well-formed (control) | RETURN populated | RETURN populated | SAME | yes |

## Findings

**F1 — HIGH, must_fix.** Two of the survey's six FEAT-14-incident-class rows are unfixed.
`factory_decompose.py:127-128` — `f = doc.get("factory"); if not isinstance(f, dict): return
factory` — is unchanged by this diff and still returns the empty record when the top-level
document parses fine (`load_feature_json` succeeds) but the nested `factory` value is not a
mapping (row 9), or when `factory.parent` is a quoted digit string like `"7"` rather than a
real int (row 10, `factory_decompose.py:132-134`'s strict `isinstance(parent, int)`, never
routed through `feature_json_write.opt_int`'s tolerance the way `gh-sync.py`'s three call
sites now are). **Concrete scenario:** a `feature.json` present with `factory: {"parent":
"7", ...}` — parent issue #7 already exists and was recorded in the legacy quoted form
`opt_int` exists specifically to tolerate — makes `load_factory` return `factory["parent"] =
None`. `factory_decompose.py:526`: `need_parent_create = factory["parent"] is None and
args.parent is None` evaluates `True`, and `_main()` proceeds to create a *new* parent issue
on GitHub, duplicating #7 — the exact incident (`gh-sync` — or here, `factory_decompose` —
re-creating an issue that already exists) the commit message cites as the reason this
migration exists. Measured live at `592e6412`: rows 9 and 10 are byte-identical to the
survey's `6cb113f4` pre-fix measurement; nothing changed. No live `feature.json` on disk
carries this shape today (per the frozen BRIEF's own disk survey), so this has not fired yet,
but it is squarely inside the survey's declared acceptance set ("Treat that table as the
acceptance set this change must satisfy") and inside this diff's own file. Whether the
correct close is aligning `load_factory`'s field guards to `opt_int`'s tolerance, or to
`gh-sync`'s REFUSE-on-non-mapping policy, is a real design call — not mine to make — but
shipping neither leaves the incident class half-closed.

**Not findings, for the record (checked, no gate):** `parse_doc`'s separate last-wins
duplicate-key path (informational, §3 above); the stale `plan.yaml` `approval.status` (issue
#1675, explicit non-goal); the ~10 other `feature.json` readers (`_record_pr`,
`save_recorded`'s/`write_factory`'s own transform re-parses) — pre-existing, unchanged,
explicitly out of scope (issue #1594).

## Tests run (scoped, no project-wide suite)

- `tests/unit/test-feature-json-reader.py` — 21/21 pass.
- `tests/integration/test-gh-sync-open.py` — all pass (28 checks).
- `tests/unit/test-gh-sync-build-entry.py` — all pass (11 checks).
- Live probe of all 13 parity-survey rows against both readers post-fix (table above).

## Stage 2 (code quality) — no additional findings

The new `FeatureJsonError`/`load_feature_json`/`opt_int` code is a clean, well-documented
deep module: absent/malformed distinguished in one place, one coercion, docstrings that state
invariants rather than narrate history. No dead code, no copy-paste divergence, no resource
leaks. Not reached because F1 already gates the review.
