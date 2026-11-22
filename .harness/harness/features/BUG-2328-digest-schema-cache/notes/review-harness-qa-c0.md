# QA gate — BUG-2328 T-01 — pin 1a26bc9f (base dd04e52a)

**BLUF: PASS.** The matrix is satisfied (unit, via direct Bun). The one-time verify ran green. SC-01 has natural semantic red evidence. SC-02 has none, and none was possible. Both deviations are sound. Typecheck (#2257) and generic-runner Bun discovery (#2329) remain acknowledged gaps, not green.

## Source/pin
- HEAD is 1a26bc9f. `git diff --quiet 1a26bc9f -- .omp/extensions/digest-schema.ts tests/unit/omp-hooks.test.ts` returned clean (MATCH_PIN), so executed source is the pin.
- Only `feature.json` is modified in the worktree, which is harness-managed. No git state was changed.

## Phase 1 (from BRIEF/plan only)
Expected tests:
1. The second load after a `common.json` rewrite shows the new required field.
2. Repeat, alias and alternate-path loads are equal by content.
3. All 16 persona injections are compared by content.
4. The distinct-copy check is kept.
5. BUG-2305 behavior is kept.

Every item has a test. No Phase 1 gap.

## Matrix
- `bugfix` has `always: []`.
- `when unit if touches_runtime_code` is true, because `digest-schema.ts` is hook runtime code. **unit is required.**
- `when integration if fix_confined_to_tests_and_contract_docs` is false, because a source file changed.
- `__bug_class__ if match_bug_class` is an unresolvable placeholder (repo G-08), so it never fires.
- Kind states:
  - unit: **satisfied** via the direct Bun command.
  - integration: not required.
  - typecheck: `unresolved`, cmd null. It is not in the matrix and is not claimed green (#2257).
- The unit kind's `cmd` is the generic runner `run-unit-tests.py --kind unit`. It misses Bun files (#2329), so it was not substituted. That is a standing gap, not introduced here.
- `matrix_ok: true`.

## Verify (run once, PRODUCT, authorized)
`bun test tests/unit/omp-hooks.test.ts` gave 186 pass, 0 fail, 1465 expect() calls, 1 file, exit 0 (33.04s).
Receipt `notes/receipts/sc01-sc02-green.txt` shows the same counts (186/0/1465).

## fail_first
- **SC-01 (regression-new behavior).**
  - Evidence: `notes/receipts/sc01-red.txt`.
  - The loader was unchanged from dd04e52a. The command was `bun test ... -t 'changed on disk|same contract'`. It exited 1 with a named test failure, `a schema file changed on disk is reflected by the next load`.
  - The assertion diff at test line 2771 shows the second bundle missing `persona` from `properties` and `required`. That is the stale-bundle failure mode, not a setup or import error.
  - This is a natural RED captured by the retained command. I audited the receipt and did not rerun it.
  - Tier: natural, semantic.
- **SC-02 (preserved baseline compatibility).**
  - The equality tests (`toEqual` for repeat, alias, path, and the 16 injections) were green at base too. A `toEqual` is weaker than the old `toBe`, so no pre-fix red exists or was expected.
  - Discrimination is unshown, and I do not claim it is useless.
  - Stale-cache regressions are caught by SC-01, not SC-02.
  - The `not.toBe(copy)` lines are the one SC-02 piece with discrimination value. See the BUG-2305 section below.

## Regression analysis (test lines 2764-2772)
- The fixture is a temp dir via `schemaDir`. `common.json` defines `$defs.entry` with required `["op"]`, and the persona references it by `$ref`.
- The first load is asserted by `toEqual` against the full projection.
- `common.json` is rewritten to required `["op","persona"]`, and the second load is asserted by `toEqual` against the **entire** projected bundle: the root schema plus the property and required lists.
- This is a whole before/after projection equality. It is not a substring or source-text check.
- A new temp dir per test avoids interference from the old process-lifetime map. At base the map was keyed on the root and persona, so the red is genuinely the cache.
- The fix is in the diff: BUNDLES is removed, and the load, project and `deepFreeze` run on every call. `#documents` is untouched.
- Alias and path equivalence (test line 2754) uses `toEqual` for the repeat load, the `main-session` alias and the alternate path `join(DIR,"..","digest-schemas")` with `backend-dev`.
- `DIGEST_PERSONAS` drives the 16-persona injection test. It asserts `tasks` has length 17, including the scout passthrough, and `toEqual` is applied per persona.

## Deviations
1. **Deleting `outputSchema` `toBe(bundle)` (old line 1711): sound.**
   - The line above it is `toEqual({...tasks[i], outputSchema: bundle, schemaMode:"strict"})`. That whole-item `toEqual` compares outputSchema content for each of the 16 personas.
   - The deleted line asserted only identity with a cached object, which no longer exists.
   - A replacement `toEqual` would be a duplicate.
   - Literal wording of SC-02 ("toBe→toEqual") is not met. The intent, content comparison across all 16, is met. This is an intent-satisfied / text-unmet distinction, and I rule the intent satisfied. The plan intent said "change toBe to toEqual", so the BRIEF-level SC-02 wording is satisfied and only the build intent differs.
2. **BUG-2305 `toBe(bundle)` → `not.toBe(copy)` (two sites): sound, and strictly necessary.**
   - Identity with the cached bundle can no longer hold, because each load is a fresh object. The cached-identity assertion therefore had to change.
   - `not.toBe(copy)` is the only discriminating assertion there. `toEqual` ignores key order, so a mutant that passes the caller's reordered copy straight through would still satisfy the preceding `toEqual(bundle)`.
   - The other assertions are retained: the distinct-copy `expect(copy).not.toBe(injected)` at the old 1757 location, the `toEqual` of the whole result, and `guardCalls` length 5.
   - The grilling fact list missed these two lines. That is a record gap, not a test defect.

## Coverage gaps
None against Phase 1. SC-03 is inspection-only.

## Advisories (none blocking)
- Advisory, scope SC-03, reader inspection: `digest-schema.ts` has no residual BUNDLES. The `cached` hits at lines 116-117 are the per-loader `#documents` map, which is allowed.
- Advisory, scope SC-03 comment text: it says "a few small JSON files per dispatch". That matches the simplify note's measurement of 0.616 ms per call.
- Advisory, scope #2329 (standing): the unit `cmd` misses Bun. It was not introduced here.
- Advisory, scope #2257 (standing): typecheck is null. It was not introduced here.

## Principles applied
- Verification rules (O-03 / O-04 / O-05 patterns): fail-first graded as natural-semantic RED for SC-01 only, text-unmet versus intent-met distinguished for deviation 1, and discrimination reported unshown rather than "useless" for SC-02.
