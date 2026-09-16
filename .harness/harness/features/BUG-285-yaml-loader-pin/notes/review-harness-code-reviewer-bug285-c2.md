# Code re-review — BUG-285 nested guards — `6cb113f4..ab0c9987`

## BLUF

**PASS. Cycle-1 F1 is CLOSED, not sustained.** At pinned `ab0c9987`, a present non-mapping `factory` value refuses before any remote write, while the legacy quoted parent `"7"` reaches the caller as integer `7` through the one shared `feature_json_write.opt_int` coercion. I re-measured all 13 survey rows from fresh binary files with real `load_recorded` and `load_factory` calls: all now have the settled outcome. No regression or new fail-open was found.

## Stage 1 — acceptance compliance

The acceptance authority is the 13-row parity survey plus the settled opposite-policy ruling, not the frozen BRIEF/plan.

- **Non-mapping nested factory REFUSES.** `factory_decompose.py:128-133` calls `factory_cli.refuse` with the `feature.json` path rather than returning the empty record. Live row-9 invocation raised `SystemExit(2)`, named the exact path, and contained no `unexpected failure` text.
- **The CLI does not rewrap the refusal.** A live `factory_cli.run(fd.TOOL, lambda: fd.load_factory(dir))` probe returned the same `SystemExit(2)` and canonical refusal line. This matches `factory_cli.py:72-82`, whose `except SystemExit: raise` precedes the generic `BaseException` trap.
- **Quoted member coercion is shared.** `factory_decompose.py:137-143` calls `feature_json_write.opt_int` for parent and each issue number. Live row 10 returned parent integer `7`; `feature_json_write.py:167-181` excludes bool before the Python `int` check, so live `true` returned `None`, not `1`.
- **Legitimate absence stays empty.** Live absent-file and missing-`factory` cases returned `_empty_factory()` (`factory_decompose.py:125-126`).
- **No partial mutation.** The sole production caller is `_main` at `factory_decompose.py:519`. The load occurs before `ensure_labels`, explicitly marked the first remote write at `:538-545`; earlier preflight, board resolution, station option lookup, and validation are reads. Thus the newly escaping row-9 `SystemExit` cannot leave a partial remote mutation.
- **Legitimate writer output cannot trigger the new refusal.** `_factory_block` always constructs a mapping (`factory_decompose.py:188-201`), and `write_factory` assigns that mapping to `doc["factory"]` at `:245`; the internal calls all pass the same normalized in-memory factory record. Existing integer parents remain integers; quoted/whitespace digit strings are newly tolerated; bool, junk strings, floats, and missing values remain absent. No prior-valid input regressed.

### Live 13-row outcome table

Method: for every row, identical bytes were written in binary mode to a new `TemporaryDirectory`; both actual functions were imported from the pinned worktree and invoked. `REFUSE` means `SystemExit`; path naming is recorded separately. Empty/populated is classified against each reader's own default record.

|#|input|`load_recorded` caller gets|`load_factory` caller gets|acceptance|
|---:|---|---|---|---|
|1|file absent|RETURN empty|RETURN empty|met|
|2|empty, 0 bytes|REFUSE, path in exception text|REFUSE 2, path on stderr|met|
|3|invalid JSON|REFUSE, path in exception text|REFUSE 2, path on stderr|met|
|4|non-UTF-8 bytes|REFUSE, path in exception text|REFUSE 2, path on stderr|met|
|5|top-level list|REFUSE|REFUSE 2|met|
|6|top-level string|REFUSE|REFUSE 2|met|
|7|top-level integer|REFUSE|REFUSE 2|met|
|8|record key absent|RETURN empty|RETURN empty|met|
|9|record key present, non-mapping|REFUSE|**REFUSE 2, exact path, no rewrap**|**met; F1 closed**|
|10|mapping with parent `"7"`, issues `"nope"`|RETURN populated, parent `7`|**RETURN populated, parent integer `7`**|**met; F1 closed**|
|11|duplicate record keys|REFUSE|REFUSE 2|met|
|12|YAML-only mapping|REFUSE|REFUSE 2|met|
|13|valid JSON control|RETURN populated, parent `7`|RETURN populated, parent `7`|met|

## Cycle-1 adjudication

**F1: CLOSED.** Its two concrete reproductions changed exactly as required: row 9 changed from `RETURN empty` at `592e6412` to a path-naming `SystemExit(2)` at `ab0c9987`; row 10 changed from `RETURN empty` to populated parent `7`. The first blocks before the mutation boundary, and the second prevents duplicate parent creation by making `need_parent_create` false at `factory_decompose.py:526`.

## Stage 2 — code quality

No findings. The remedy reuses the existing refusal seam and the existing shared coercion rather than adding another parser or conversion rule. Changed-Python grading over the repository-derived `merge-base(origin/main, ab0c9987)..ab0c9987` range passed all 27 reported functions (`code_grade: pass`). No `[harness:human]` commits occur in `6cb113f4..ab0c9987`.

## Scoped verification

- `python3 tests/integration/test-factory-decompose.py`: **177/177 checks passed**, including nested refusal/coercion, non-UTF-8, idempotence, and zero-mutation refusal cases.
- `python3 -m unittest tests/unit/test-feature-json-reader.py`: **21 tests passed**.
- Independent 13-row live probe: **13/13 settled outcomes met**.
- Independent `factory_cli.run` row-9 probe: exit 2, exact path named, `unexpected failure` absent.
- `code-grade.py --base "$(git merge-base origin/main ab0c9987)" --head ab0c9987`: **PASSING: 27**.

## Findings

None. `severity_max: none`; `must_fix: []`; `spec_violations: []`.
