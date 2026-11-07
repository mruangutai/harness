# QA c1 — BUG-2180 T-01 @ 556a23ffea8dafcf5110e80fe25a42ee2542ff2b — matrix-presence reconciliation

**Verdict: FAIL (matrix only).** Code/SC behavior is correct and unchanged from c0; the unit floor is `missing`, so `matrix_ok: false`. This supersedes c0's "unit satisfied" (c0 file preserved unedited). No reruns, no source/test edits (evidence assessment).

## Separation
- **Behavior/SC (unchanged, PASS-grade):** c0 stands — unit 57 files green, integration 84 files green, literal `python3 tests/integration/test-check-state-inv26.py` 37 ok / 0 FAIL / 5.97 s; fail-first x.1–x.6 red at base bin (31 ok, 6 FAIL, semantic); code SHA equality `554f219e`==`556a23ff` for board.py + test.
- **Matrix presence (corrected):** T-01 `change_type: bugfix`; `harness.json` `bugfix.when: unit if touches_runtime_code`. `git diff --stat 4a05030d 556a23ff` (non-.harness): `check_state/board.py` (runtime) + `tests/integration/test-check-state-inv26.py` -> predicate TRUE -> unit required.

## Reconciliation of texts
- DEC-217 (DECISIONS.md:7044-7068): `touches_runtime_code` "is true for ordinary code fixes, so they retain the unit floor." The ceremonial-unit/copy prohibition ("Over") is scoped to unchanged runtime code and test-and-contract-only fixes. It grants no exemption to a code fix, and no rule treats "unit kind runs green" as the floor.
- harness-verification-rules: presence is not satisfied by an unrelated existing test; required with nothing covering this change -> `missing` -> FAIL. Applies directly; DEC-217 is consistent with it (it names the unit floor as retained), not overriding it. No specific reference found that exempts this diff. c0 misread DEC-217 as making unrelated unit-green sufficient.

## Is there a named unit-kind test exercising this diff? No.
grep over `tests/unit` for check-state/board.py/gh_board/INV-26: hits are unrelated — `test-check-state-inv35.py` (INV-35 only), `test-gh-board.py` (gh_board.py functions; gh_board unchanged by this diff), `test-config-shape-matrix.py` (prose mention), plus incidental mentions (accessors, broad-catch census, harness-boundary fake checker, etc.). None executes `check_state/board.py` `_inv26_*` routing or the changed GhError/BoardError/FleetError handling. The only exercising test is in `tests/integration/` (kind `integration`, which T-01 is not required to cite as satisfying unit).

Resolved kind states: unit = `missing` (the 57-file unit run is green but unrelated — `named_tests: 0` for this change); integration = `satisfied` (voluntary add, the real exercising test: 37 cases).

## Actionable gap (T-01, owner: dev, severity: blocking for matrix)
Add a unit-bucket test (under `tests/unit/`) that exercises changed `check_state/board.py` INV-26 logic directly — e.g. the repository/board-scoped grouping and the error-boundary conversion (BoardError/GhError -> CANNOT VERIFY, FleetError -> no owner fallback). It should be discriminating (red against base board.py), not a copy of the integration cases solely for a directory label (DEC-217 "Over"). Source/test edits are dev's, not mine.

## BoardError branch assessment
Decision: **nonblocking assurance qualification, no required action** (not a finding). Why: `board.py:698` handles `(_gb.BoardError, _gb.factory_gh.GhError)` in a single `except` tuple with one shared handler body (699-701); x.5 drives that same handler through GhError, so the CANNOT VERIFY emission is exercised. The untested element is only the second exception-class member of the tuple. SC-03 expressly requires GhError; not widening acceptance. If the dev adds the unit test above, covering BoardError there is optional.

## Principles applied
Not citing craft leaves (none read this run).
