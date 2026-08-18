# Observations — harness-eng-lead — FEAT-24

- 2026-08-18 (run 7, fix cycle C1): routing for both fixes was over-determined, not a judgement
  call — `plan.yaml:300` and `:361` both carry `execution_agent: harness-backend-dev`, and
  `.claude/skills/harness/bin/**` is granted to backend-dev and dev-ops alike (G-01/G-02). One
  dispatch, not two, because the operator wants ONE full-suite red set taken after both fixes; a
  second dispatch would make the first one's red set stale.

- 2026-08-18: the assertion that hid FIX 1 for a whole feature is a shape worth remembering.
  `test-factory-gh.py:914-916` asserted `any("repos/o/r/contents/..." in a for a in argv)` AND
  `any("ref=main" in a for a in argv)`. Both clauses are satisfied by the correct query form AND by
  the broken `-f` form, because the assertion never says WHICH element carries the ref. An
  element-membership assertion over an argv list cannot see argv STRUCTURE, and the HTTP method is
  structure. The recorder harness models no method at all, so no case in the file could have caught
  it. The discriminating clauses are "the ref rides in the same element as the path" and
  "`-f` is not in argv".

- 2026-08-18: verified before relaying (P-09), against my own run-6 self-record of relaying an
  unchecked argv claim. `test-factory-integration.py:275` matches
  `^repos/([^/]+/[^/]+)/contents/(.+)$` on `rest[0]` and uses ONLY `cm.group(1)` at `:277`;
  group(2) is captured and never read. So the query form's `?ref=` is absorbed by `.+` and the fake
  gh's contents branch is unaffected — observed, not inferred from the regex's shape.

- 2026-08-18: `factory_config.py:263-267` documents a memo keyed `(repo_name, ref)` with
  `clear_product_config_memo()` as its only sanctioned reset. That is the trap in FIX 2: D-03's
  clause is ABOUT the cache, so an F-5 fixture whose repo key was already read successfully by an
  earlier case in the file never invokes the raising stub and proves nothing. Put the reset (or a
  repo name used nowhere else) in the dispatch, not in the member's discretion.

- 2026-08-18: "assert the value appears nowhere in the RESULT" is vacuous whenever the correct
  implementation raises — there is no result to inspect. A negative assertion scoped to a branch
  that cannot execute passes for free. It has to be paired with a capture on the no-raise branch
  and a check of `str(exc)`.

- 2026-08-18: full suite is 28 files (`run-unit-tests.sh:17-18`, 16 unit + 12 integration). At this
  commit exactly two are pre-cleared red — `test-no-distribution.py` (operator's, T-07 fixture) and
  `test-check-state.py` (red by design until T-05's `derive_station()` arity lands by hand). Any
  third FAIL line is a new defect, and saying so explicitly in the dispatch is what stops a member
  filing an unexpected red under "expected".
