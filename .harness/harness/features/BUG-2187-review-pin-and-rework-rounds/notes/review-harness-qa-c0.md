# QA gate — BUG-2187 T-01 @ 1b35414b (run 2026-11-21-02-validate-validator, c0)

BLUF: PASS. Matrix floor met (unit + integration both `satisfied`); SC-01/02/03 base-red reproduced by me
against production-identical `ee550318` with the pinned tests, as real assertion failures (not setup/import).
Every pinned verify/audit command exits 0. Five test-strength gaps (mutants that survive) are listed; none
reddens the gate, all go in `coverage_gaps`. Nothing authored, no source touched in the feature tree.

## Phase 1 (from BRIEF + plan only, before source)
Expected tests: (a) integration: station-only change silent, serialization-only silent, nested/other status
STALE, other content STALE, five silences kept, changed-then-restored silent, placeholder, legacy/unloadable
byte fallback; (b) unit: pin-review default HEAD, ref/short→full id, noncommit/unresolved/option-shaped refused
exit 2 + REFUSED + bytes unchanged, APPLIED output, unrelated fields preserved, writer refusals retained, both
guidance docs name the verb, seam order kept; (c) unit spend: direct-fix regate, multiple, start-equality,
earlier/non-regate excluded, replace-never-sum, legacy fallback, no validate, cycles_used unchanged.
Matrix: change_type bugfix → unit `when touches_runtime_code` (true: bin/*.py), integration carries SC-01.
Gaps vs this list: see "Coverage gaps".

## Subjects
- Pin 1b35414bfc865786baffe0418528deeeef141272; branch base 5bd9efd4. Receipt "base" subject ee550318 is an
  ancestor of the pin and a descendant of 5bd9efd4. `git diff --stat 5bd9efd4 ee550318 -- .claude tests`
  is empty (only feature docs differ): production at ee550318 == branch-base production, so the receipt's
  "ee550318 + new tests" is an authentic base-red subject, not a preproduction fork.
- Managed pins (pinned-checkout.py, persona harness-qa and harness-qa-base); both removed on return.
  Env: `env -u HARNESS_AGENT_TYPE`; no HARNESS_*/OMP project-root vars exported (env shows only CLAUDECODE, OMPCODE).

## Executions at the pin (mine, not the receipts)
| command | exit | observed |
|---|---|---|
| `python3 tests/integration/test-check-state-records.py && python3 tests/unit/test-feature-record.py` (exact verify) | 0 | integration 44 `ok -`, 0 `FAIL`, empty stderr; unit `Ran 128 tests OK` (32.7s; stderr is the tests' own expected REFUSED/broken-validator noise); total 52.6s < 60s |
| `check-plan-routes.py --canonical-reader-audit` | 0 | `0 unresolved reader site(s) across 100 Python file(s)` |
| `tests/integration/test-checker-structure-locks.py` | 0 | `ALL PASS` (incl. feat63/64/65/69 census) |
| `code-grade.py --base 5bd9efd4 --head 1b35414b` | 0 | 31 functions, 31 `RESULT: PASS` (grades 4–5, bar 3) |
| `run-unit-tests.py --kind unit` (G-04, standing kind) | 0 | 61 files discovered (`tests/unit/test-*.py`), includes test-feature-record.py, `OK` |
| `run-unit-tests.py --kind integration` | 0 | 87 files (`tests/integration/test-*.py`), includes test-check-state-records.py and test-checker-structure-locks.py, `ALL PASSED`, 116s |
Discovery check: runner globs are `tests/unit/test-*.py` / `tests/integration/test-*.py`; both bound files match
and printed PASS lines (P-14). New unit tests: 10 (PinReviewTest 4, SpendTest 6); new integration cases: 3 (inv33.e/f/g).

## Base-red reproduction (isolated pin at ee550318; tests overlaid via `git checkout 1b35414b -- <3 test files>`)
Command: same two scripts. Integration exit 1: `FAIL (inv33.e)` and `FAIL (inv33.f)`, each with the real
defect line `VIOLATION FEAT-TEST: review_sha … is STALE — plan.yaml has changed since it was pinned` (production
reports STALE for a station-only / reserialized plan); `ok (inv33.g)` (safety assertion, allowed green at base).
Unit exit 1, `Ran 128 FAILED (failures=8)`, all AssertionError (no ImportError/collection error):
- SC-02: PinReviewTest `…omitted_sha…` (`0 != 2`, argparse "invalid choice: 'pin-review'"), `…ref_or_short_sha…` (`0 != 2`),
  `…non_commit_or_unresolved…` (stderr usage not REFUSED), `…guidance_names_only_verbs…` (`'pin-review' not found in {'run-start','close-run'} : build-phase.md`).
- SC-03: `test_a_direct_fix_round_counts_its_regate_judgement` (`1 != 0`), `test_every_regate_in_the_window_is_a_round` (`2 != 0`),
  `test_the_window_opens_exactly_at_the_first_validate_start` (`1 != 0`), `test_regates_replace_the_fix_run_count_never_add_to_it` (`1 != 2`);
  fallback tests (keeps_fix_run_count, no_validate) pass at base as the BRIEF permits.
Matches receipts/red-inv33.txt and red-feature-record.txt line for line. Weakness (form): red-inv33.txt records only
ok/FAIL labels, no violation text or stderr; my reproduction supplies it.

## fail_first map
SC-01 → tests/integration/test-check-state-records.py:489 `case_inv33e_station_writes_are_silent` (and :498 inv33f), red = this note, base-red section.
SC-02 → tests/unit/test-feature-record.py PinReviewTest (:1278,1285,1291,1301), red = this note.
SC-03 → tests/unit/test-feature-record.py SpendTest :1231, :1234, :1238, :1245 (defect-exposing tests), red = this note.

## Mutation proofs (isolated pin, restored with `git checkout`, `git status --porcelain` empty after each)
Controls prove the harness bites: strip-one-level-nested-status mutant → inv33.g FAILs; `>=`→`>` in `_not_before` → boundary test FAILs.
SURVIVING (suite stays green): 
- M-C `_inv33_reviewed` returns None on load error (instead of raw bytes): all green → bytes fallback undefended.
- M-L `_inv33_reviewed` returns None for non-plan.yaml (legacy PLAN.md): all green → legacy path undefended.
- M-E strip `status` one level inside each task's dict values: all green → only `approval.status` is exercised as nested.
- M-P/M-Q pin-review also bumps `cycles_used` / wipes `judgements`+`mission`: 128 OK → "preservation of unrelated fields" not asserted.
- M-R pin-review bypasses `feature_json_write` (plain json read/write, no lock/schema): 128 OK → writer path unbound.
- M-N2 drop the naive/aware tz guard in `_not_before`: 128 OK (defensive branch untested).

## Boundary audit
- No-write refusal: test iterates tree, absent object, unknown name, `--sha=--git-dir`; exit 2, stderr starts `REFUSED:`, bytes identical. Code: `code_grade.commit_oid` runs before `_apply`; `^{commit}` + `--end-of-options`. Hypothesis holds. Not tested: nonexistent/schema-invalid `--file`, lock contention.
- Silences: unchanged gate (`feature_record.py:197`) and both-reads clause preserved; only terminal (c) and absent-pinned-path (d) have cases. No git work tree, unresolved pin, absent disk plan, placeholder: no case existed before or after (pre-existing).
- Nested status: g covers `approval.status` only. Bytes fallback and legacy PLAN.md: no case (M-C, M-L).
- Docs: diff keeps seam order (set-tasks-done → commit → pin → status review; fix-loop repin), adds `feature-record.py pin-review --file <feature.json> --sha …`; frozen/external HARNESS-REVIEW-PIN text kept. Guidance test checks the verb is named and exists, not the flags.
- Classification: `_inv33_reviewed` exempt `in_memory_validation`; audit 0 unresolved. Spend: only `_regate_rounds` path; `cycles_used` untouched in diff.

## Coverage gaps (all test-strength, task T-01)
1. substance: INV-33 unloadable/legacy byte fallback has no test (M-C, M-L) — tests/integration/test-check-state-records.py cases e–g; feature_record.py:84-89. Scenario: a regression that treats an unparseable edited plan as equal ships green and hides a real edit.
2. substance: nested-status boundary tested only on top-level `approval.status`; task-nested status (M-E) unguarded — feature_record.py:71-72.
3. substance (pre-existing, preserved not regressed): three of five silences (no git tree, unresolved pin, no disk plan) and placeholder lack cases.
4. substance: pin-review unrelated-field preservation and shared-writer use unasserted though plan intent line 57 requires them — feature-record.py:607-619; tests PinReviewTest.
5. form/advisory: naive-vs-aware timestamp guard untested (feature-record.py:673); red receipts carry labels without stderr.

## Principles applied
Fail-first is graded on my own natural-RED reproduction at an immutable production-identical SHA (O-03); mutants kept to single-site and controls included (P-09, O-06).
