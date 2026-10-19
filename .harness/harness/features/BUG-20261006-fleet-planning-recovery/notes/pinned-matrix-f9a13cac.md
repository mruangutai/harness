# Authorized additional matrix — f9a13cac

Authorization: `operator-corrected-matrix-ruling-2026-10-19.md`. Pin: `f9a13cacb4c554605dc5fa339f12d609d15818e1`. The signed plan matches that commit, and all 280 tracked tooling/test/config blobs checked against its Git blob hashes match. Commands were launched once each in parallel from this worktree; no third full matrix is authorized.

## Unit result

`python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` exited 1: 55 files, 28.84s pool wall / 29.01s command wall. Full session output: artifact 356. Only `test-omp-hooks.py` failed: its Bun suite reported 126 passing and 12 failing tests. The remaining 54 unit files passed. This result remains FAILED.

The concrete root error is `DigestSchemaBundleError: .../DIGEST/anyOf/1/properties/cycles_used: unsupported keyword(s) beside $ref: minimum`. OMP's existing projection deliberately refuses non-annotation reference siblings. Its guard must not be relaxed.

## Diagnosis before further edits

1. Replace the counted field's reference-plus-minimum with the explicit equivalent `{type: integer, minimum: 0}`. Canonical Python validation must still reject negative, boolean and fractional counts; the actual OMP projection must load all personas and the main-session alias without fallback. The projection deliberately drops semantic bounds while canonical validation enforces them. Falsifier: actual bundle loading or canonical count boundaries still fail.
2. Source inspection also found the Bun case “takes every field and required set from the persona's JSON file” directly calling `Object.keys` on `DIGEST.properties`; a composed DIGEST has no such direct property. That source-copy assertion is incidental and must be deleted rather than repinned. Retain structural-whitelist, closed-schema, role injection and real lifecycle behavior coverage. This second failure is a prediction at this point, not an observed passing/failing result.

No production source will change until the integration half settles, so the authorized matrix observes one source pin throughout. No historical receipt, count or remote object is rewritten.

## Integration result

`python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` exited 0:
all 83 files passed, 100.65s pool wall / 100.81s command wall. Full session output:
artifact 357. Both halves settled before the schema correction began.
The authorized additional matrix is nevertheless FAILED because its unit half
failed. No third full matrix has run or been authorized.

## Focused correction results

The equivalent explicit integer schema removed the projection refusal without
changing OMP. The next targeted OMP run observed the predicted source-copy
TypeError: 137 passed, one failed, 5.63s. That entire incidental copy test was
deleted rather than rewritten to mirror the new implementation.

`python3 tests/unit/test-omp-hooks.py && python3 tests/unit/test-digest-schemas.py && python3 tests/integration/test-validate-digest.py`
then passed in 16.78s (artifact 361): 137 OMP tests, 33 canonical schema tests,
all validator integration cases, including 37 undeclared-key and 81 exact-release
checks. Structural whitelist, alias caching, strict closure and lifecycle coverage
remain; no guard or behavioral rejection was weakened.

A throwaway real Bun invocation loaded the actual main-session bundle, confirmed
its backend alias, and observed two closed fully-required variants with omitted
versus required typed count. Actual canonical CLI invocations accepted omission,
0 and 4 and refused -1, true and 0.5. No model call, installed runtime change or
remote mutation was needed for these smoke checks.

These focused results do not change the failed full matrix result above.
