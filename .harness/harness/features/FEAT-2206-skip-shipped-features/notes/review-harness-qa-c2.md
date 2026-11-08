# QA c2 — FEAT-2206 T-01 at pin 688c5ef5e3b6e0dd694afb3d6476c915934501d4

**BLUF: FAIL.** Both c0 must-fixes are closed and every required kind is green at the pin, but a new
instance of the same crash class survives: a shipped record's `factory.parent` of 4301 ASCII digits
crashes INV-24 with a traceback (SC-03 not met). Details in F-1.

Executed in disposable pinned checkouts (HEAD verified = pin; baselines b7af829c, fe49c8df; all removed on return).
Env: HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR, HARNESS_PROJECT_DIR unset. Raw outputs: /tmp/qa-c2-*.out (volatile; counts quoted below).

## Findings (kind · severity · task · scenario)

- **F-1 · defect · must-fix · T-01 · SC-03.** `board._inv24_issue_number` (`check_state/board.py:153`)
  `int(s)` is guarded only by `isascii() and isdigit()`; Python's 4300-digit int-conversion limit raises ValueError.
  Probe (own, at pin): `_inv24_issue_number('9'*4301)` raises ValueError (4300 digits → int OK). CLI fixture
  (shipped strict-invalid `done` record with `parent:"9"*4301`, `issues T-02:11`, beside active FEAT-7-building
  `issues T-01:11`, via the test module's `claim`/`commit`/`check` helpers): full audit exit 1 with Traceback
  `board.py:153 ← _inv24_shipped_claims board.py:196 ← inv_24 board.py:255`. SC-03 says malformed shipped
  fields must not be graded and must not break the comparison; the usable 11 collision is lost and the audit aborts.
  The strict loader path is safe (`_positive_issue_number` catches ValueError). No test covers it.
  (Active-record oversized number: same `int(s)` was present at baseline; I did not characterise its output.)
- **F-2 · defect · low (advisory) · T-01 · SC-03.** ASCII-only gate narrows INV-24 vs baseline for digit strings
  `int()` accepts: probe `'٣'`, `'١٢'`, `'１２'` → `_inv24_issue_number` None, but `opt_int`/`_positive_issue_number`
  (what gh-sync and the strict loader use) read 3, 12, 12. Baseline `isdigit()+int()` claimed them. Scenario: active
  record `issues T-01:"٣"` and another record `T-01:3` — baseline INV-24 collision, pin silent. Function-level only; not run e2e.
- Q-01 (c0, intent-YAML prose vs DEC-252 classifier) left open as instructed; not duplicated.

## c0 closure — independently verified

- **Must-fix 1 (status KEY count).** Probe of `ctx.lenient_station` at pin: `done`+`status: [x]`, `done`+`status:`,
  `status: 7`+`done`, `done`+`"status":`, `done`+`'status' :`, `status : done` → "" (not shipped); plain, quoted value,
  tabs, CRLF, commented-out dup → `done`. Named: unit `subjects are exactly the unshipped features…` and
  `the context records which discovered features shipped` (FEAT-10..13 fixtures, unit file lines 44-47);
  integration `test_a_duplicate_status_key_keeps_every_check` (test-check-state-shipped.py:144).
- **Must-fix 2 (INV-24 + INV-52 census).** `_inv24_issue_number('²')` None; `_positive_issue_number('²')` None;
  `opt_int('²')` still RAISES ValueError (unchanged; `git diff` shows no feature_json_write change). Integration
  `test_inv24_skips_unusable_shipped_numbers_and_keeps_usable_ones` (:210) passes: no Traceback, exactly one
  shipped/active 11 collision line, no unusable-value lines.
  Census discrimination (own mutant): fe49c8df tree + pin board.py/ctx.py/tests but `artifact_accessors.py` reverted →
  that test FAILS with Traceback (the INV-52 census crash). So the accessor edit is load-bearing and tested.
- **#2151 LABEL refusal.** `board_lifecycle._github_numbers` still `except ValueError` around `opt_int`
  (board_lifecycle.py:964-966). `test-board-lifecycle.py` (mentions 2151) is in the green integration run.
  I could NOT run an `opt_int`-made-total mutant myself (check-domain denied source edits to my disposable pin, correctly);
  the "full suite caught lost LABEL" claim is the author's, discrimination of that guard by me: unshown.

## Fail-first (natural RED, baseline source + pin tests; assertion failures, not import errors)

- Rework reds at fe49c8df (+pin tests): unit 2 FAIL (subjects, shipped set — FEAT-10..13); integration 2 FAIL
  (`test_a_duplicate_status_key_keeps_every_check`, `test_inv24_skips_unusable…`). Other 14 integration green.
- Original baseline b7af829c (+pin tests + f58_sparse_fixture.py): unit 10 FAIL assertions (strict-load finding for shipped
  plans, BRIEF/STATE opened, keep={shipped} leaves subject, population shape); integration 9 of 16 FAIL (not ERROR):
  full audit, changed audit, one-note selection, read-only boundary, INV-28/30 retired ×3, inv24 not-graded, inv24 unusable.
  Green at baseline (already-correct, not claimed red): shipped/active and shipped/shipped INV-24, INV-52, INV-29,
  missing selector, unreadable status, duplicate-key (no classifier existed).
- Real-corpus mode at baseline: ImportError (`lenient_station` absent) — signature-absent, proves no behavior.
  Real-corpus discrimination is therefore unshown (O-05), not shown useless.
  Receipts: notes/red-first.md; own captures /tmp/qa-c2-base0-*.out, /tmp/qa-c2-base1-*.out.

## Matrix (bugfix → unit if touches runtime code [yes]; integration required by contract) — config/harness.json read

- unit: `run-unit-tests.py --kind unit` exit 0, 60 files; includes `test-check-state-shipped-ctx.py` (15 PASS assertions) and `test-check-state-inv35.py`.
  (BUG-1290 FAIL-prefixed lines are that script's own mutation proof; graded on exit code.)
- integration: `--kind integration` exit 0, 86 files, 112.6s; `test-check-state-shipped.py` 16 tests OK
  (3 retired + 6 comparison + 7 subject cases).
- Literal real-corpus: `--real-corpus /Users/molchairuangutai/GitHub/harness`, exit 0, owner main @ b7af829c0207522b43f978b5275a2ebdc96b3210,
  9 landed, 7 shipped (BUG-2141, BUG-2161, BUG-2169, BUG-2180, BUG-2190, FEAT-2037, FEAT-71), 21 PASS, 0 FAIL; candidate code from the pin.
- Literal verify first command (shipped unit, integration, real-corpus bounded 55s): ran its three components, each exit 0, no FAIL-prefixed lines (total ≈20s).

## Literal verify / historical log — qualification

- The literal verify's standalone tail uses `git rev-parse HEAD`; the feature worktree HEAD is now 786bd8de (evidence commit), not the
  pin, so I did not run it literally (it would write another merge-<sha>.log). Its commands run at the pin: validate-feature-json,
  check-decision-anchors, check-plan-routes, DECISIONS-INDEX diff → exit 0. `check-state.py` at the pin → exit 1, 4 violations,
  all about this feature's own record: INV-33 STALE (pin's feature.json carries review_sha 09ac5a4e; plan.yaml last changed at 688c5ef5)
  and 3× INV-26 board mismatch (#2201, disclosed non-product). Not product defects; literal verify is NOT clean at the pin itself.
- Equivalence: `git diff --stat 602c81a3 688c5ef5` = one file, feature.json, one line (review_sha 09ac5a4e→688c5ef5) — verified.
  So 602c81a3 differs from the pin only in the metadata check-state needs; merge-602c81a3….log (146 files, verify-exit=0, review_sha=602c81a3,
  tail confirmed) is equivalent-code historical evidence, not a green execution at the pin. My own unit(60)+integration(86)=146 counts match it.
  Note that log's green does not cover F-1 (no test).

## Phase 1 (source-blind) expectations vs tests
SC-01 unit classification/ordering/strict-invalid/unreadable: covered. SC-02 CLI full/changed/one-note/read-only/real corpus: covered.
SC-03 shipped/active+shipped/shipped collisions, INV-52, INV-29, malformed-ignored: covered except oversized-integer numbers (F-1).
SC-04 retirement, no gh queries, adjacent controls: covered.

## Principles applied
None cited from craft leaves this run.
