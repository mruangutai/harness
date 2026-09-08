# QA — BUG-201 depends_on referential integrity — final gate (post-SIMPLIFY)

## Verdict: PASS

Read-only gate over the final built diff (`af859ee8..HEAD`, HEAD = `4b6c3f5b` "BUG-201 SIMPLIFY: refuse() takes an optional stream, _projected_for uses it"). No source, test, or plan edits made.

## Phase 1 (BRIEF-only) expected coverage

From BRIEF SC-01..SC-09 before reading code: a unit-level rule test (dangling ids rejected, paired-allow, multi-dangling, non-list rejection, type-coercion parity), a write-route integration test (plan-merge refuses/allows), a corpus non-regression walk with a paired throwaway-dangling detector, a `grep`-checkable single-implementation inspection, and consumer-diagnosis tests at the three swallow sites (`factory_claim.py`, `gh-sync.py` x2) each with a paired legal-plan case and a poll/decline-not-gate case. All nine materialized; no gap between Phase 1 expectations and the landed suite.

## Matrix

`touches_runtime_code` requires **unit**. The BRIEF/D-0x binds **integration** through six consumer suites named in SC-07; the floor is the union. `matrix_ok: true`.

## Evidence

All named commands exited 0:

- `python3 tests/unit/test-plan-depends-on.py` — 12/12
- `python3 tests/integration/test-plan-merge.py`
- `python3 tests/unit/test-harness-yaml-corpus.py` — 16/16
- `python3 tests/integration/test-harness-yaml.py`
- `python3 tests/unit/test-factory-claim.py` — 133/133
- `python3 tests/unit/test-factory-claim-mutation.py`
- `python3 tests/integration/test-gh-sync.py`
- `python3 tests/integration/test-check-plan-routes.py`
- `python3 tests/integration/test-factory-decompose.py` — 162/162
- `python3 tests/integration/test-check-state.py`
- `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` — 33 files
- `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` — 49 files

## Success-criteria evidence

- SC-01: `test-plan-depends-on.py` case 1.
- SC-02: `test-plan-merge.py` `bug201a`/`bug201b`.
- SC-03: live corpus and paired dangling detector.
- SC-04: one validator definition and one call site in `harness_yaml.py`.
- SC-05: recorded pre-rule failure in `receipt-harness-backend-dev-T-01-c1.md`.
- SC-06–SC-09: the named factory, YAML, gh-sync, route, decompose, and state suites above.

## Simplify follow-up

The one permitted fold-in made `refuse()` accept an optional runtime stream and routed `_projected_for` through `refuse(..., stream=sys.stderr)`. Existing stdout callers and the required stderr refusal remain covered. The separate diagnostic double-path finding was not applied because the one-fix ceiling was reached; it is preserved for later triage, not treated as a BUG-201 blocker.

## Coverage gaps

None.