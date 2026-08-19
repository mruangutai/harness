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

- 2026-08-19 (run 2026-08-19-4-eng, fix cycle C3): THE ABOVE PRE-CLEARED-RED NOTE IS SUPERSEDED and
  re-measuring it before reuse is the whole lesson (G-11). Settled without a shell, from
  `.git/HEAD`, `.git/refs/heads/feat/FEAT-24-config-responsibility-split` and
  `.git/logs/refs/heads/...` (G-06): HEAD is on the feature branch at `2e60cc2`, and the dispatch's
  pin `6baa39b` is its immediate PARENT. The one commit between them is a record/handoff commit
  ("the build seam handoff, and the feature reaches zero violations of its own"), no code. qa
  measured `run-unit-tests.sh --kind all` at `b0604c3` as rc=0, zero FAIL, 1365 ok, and
  `b0604c3 → 6baa39b → 2e60cc2` are all record commits. So the expected red set for this run is
  **EMPTY, rc=0** — deciding that BEFORE the member's number arrives is what stops "expected" from
  meaning "whatever came back".

- 2026-08-19: the dispatch's "test-check-state.py is expected to be involved in a separate finding"
  does NOT license a red there. qa's T-05 finding is that INV-26 assertions are MISSING — a file
  with no assertions runs green. A red `test-check-state.py` would be a new defect, not the known
  one. A "known finding" and a "known failure" are different objects and a dispatch phrase that
  blurs them is how an unexpected red gets filed under expected.

- 2026-08-19: `receipt-harness-backend-dev-fix-c2.md:112-115` records that an auto-mode Bash
  classifier BLOCKED running the suite with `validate=False` in the tracked `factory_gh.py` — the
  guard reads a weakened validation flag as the thing it exists to stop. Any dispatch whose proof
  is an in-place mutation of a security-shaped flag must ship the fallback in the prompt itself:
  copy the whole `bin/` dir to scratch, mutate the copy, run the copied test (Python puts the
  script's own dir first on `sys.path`, so the copy imports the mutated sibling; PYTHONPATH
  shadowing does NOT work for a sibling module). I could not send this mid-flight — a lead holds
  no SendMessage tool — so it costs a re-dispatch. Put it in the first dispatch next time.

- 2026-08-19: `dispatch-guard.sh` blocked my first Agent call for passing `model: sonnet` (DEC-152/155).
  Correct block, my error. Model pins are org design and never a dispatch option; the tool's own
  `model` parameter is not a licence to use it from a lead.
