# QA gate — FEAT-2458-shape-stamp-sweep — validate cycle 1

**BLUF: PASS (matrix_ok true; unit + integration satisfied with runner receipts at
9b5b6a7a; every `verify: automated` SC except SC-09/SC-10 has fail-first evidence I
reproduced). There are two test-adequacy findings, both against T-02's test files, and the
validator-lead should weigh them as must-fix: (F-1) SC-07's named test does not run the T-07
case it cites; (F-2) SC-05's `absent` / `not absent` clauses are vacuous in
test-post-merge-sweep.py, because the fixture id itself contains `absent`.**

- Run: 2026-11-24-01-validate-validator, cycle 1. Persona harness-qa.
- Tested commit: `9b5b6a7a05c3dc8aa382699e33477d2f0397281c`, the feature.json `review_sha`. The
  managed pin `.claude/worktrees/.pins/FEAT-2458-shape-stamp-sweep--2026-11-24-01-validate-validator--harness-qa`
  had `git rev-parse HEAD` = the pin, and `worktree-state.py --verify` returned converged (rc 0).
  `bun install --frozen-lockfile` ran in the pin first. The diff is 322b12b0..9b5b6a7a.
- Policy blob: repository harness, commit 9b5b6a7a05c3dc8aa382699e33477d2f0397281c, path
  `.harness/harness.json`, read with `git show`.

## Matrix

Both tasks have `change_type: cross_module`, so `test_matrix.cross_module.always = [unit, integration]`.
There are no `when:` clauses. `component` and `ui` are unresolved but not required, because the diff
touches no `.tsx`, story or e2e file. `typecheck` is not in the cross_module floor, and the diff
touches no `.ts` file.

|kind|state|cmd (DEC-255 production runner, from the pin)|discovery|result|
|---|---|---|---|---|
|unit|satisfied|`env -u HARNESS_AGENT_TYPE python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <run>/qa/manifest-unit.json`|68 selected / 68 completed|runner_exit 0; `pool: 8 workers, 68 files, 51.84s wall`|
|integration|satisfied|`… --kind integration --shard 1/1 --manifest <run>/qa/manifest-integration.json`|95 selected / 95 completed|runner_exit 0; `ALL PASSED.` / `pool: 8 workers, 95 files, 192.10s wall`|

The receipts are the runner's own files and were not edited:
- `runs/2026-11-24-01-validate-validator/qa/manifest-unit.json` — sha256 `cae7b982…a701`, tested_commit 9b5b6a7a…
- `runs/2026-11-24-01-validate-validator/qa/manifest-integration.json` — sha256 `c84a996a…93b5`, tested_commit 9b5b6a7a…

The receipts name the feature's scripts. Integration holds test-worktree-terminal.py,
test-post-merge-sweep.py, test-check-plan-routes.py and test-checker-structure-locks.py. Unit holds
test-broad-catch-census.py and test-no-distribution.py. The runner output shows `PASS <file>` for all
six.

**Plan verify commands, verbatim, `env -u HARNESS_AGENT_TYPE sh -c '…'`, at the pin:**
- T-01 verify: rc 0. The log has 215 PASS lines and 0 FAIL lines; 11 of them are `classify_feature`
  rows, and the AST check passed.
- T-02 verify: rc 0. The log has 433 PASS lines and 0 FAIL lines; 10 of them are `stamps` rows (8
  criteria plus 2 SAFETY rows). The audit summary reads `0 unresolved reader site(s) across 101
  Python file(s)`, and all the greps passed.

## Phase 1 (from BRIEF and plan only, before reading the code)

These tests were expected:
- classify_feature: one row per klass and per reason contract (SC-01), the fleet rows (SC-02), the
  exact-id rows for harness and fleet (SC-01/02), and the undecodable row.
- The sweep: a fixture with 5 stamps, where the real run deletes only the done stamp and keeps the
  bytes of the others (SC-03), and a dry run leaves everything and names the done stamp (SC-04).
- Exact one-line counts and `absent` versus `not absent` on the kept lines; the building stamp is
  never named (SC-05).
- A routes test that reds when the hook keeps a private fleet reader (SC-07).
- The regression suites stay green (SC-09/SC-10).

Every expectation has a test except the two adequacy gaps F-1 and F-2 below.

## fail_first, per automated SC

I reproduced every red in a scratch extraction under /tmp. Each scratch tree is a `git archive` of
the pin with only the named production blob swapped for its 322b12b0 version (P-07). Nothing was
written to the repository.

|SC|Test (pin)|Red evidence|Tier|
|---|---|---|---|
|SC-01|`tests/integration/test-worktree-terminal.py:1105` case_classify_feature, rows (a)-(f), (i), (k)|With pin tests and 322b12b0 worktree_terminal.py: rc 1, 59 PASS, **11 FAIL**, all `AttributeError … no attribute 'classify_feature'`. This matches the builder's claim. Semantic mutants on the pin tree: M1 prefix-match reds (i) and (j); M2 (catch neutered) reds (k); M3 (absent wording removed) reds (d); M10 (not_terminal→terminal) reds (c) and (h).|natural RED (signature-absent) + semantic mutants|
|SC-02|same file, rows (g), (h), (j) (fleet subprocess)|322b12b0: (g)(h)(j) FAIL with an AttributeError traceback. M1 reds (j) and M10 reds (h).|signature-absent + semantic|
|SC-03|`tests/integration/test-post-merge-sweep.py:1162` case_shape_stamps, rows (4)-(8)|Pin tests with 322b12b0 post-merge-sweep.py (T-01's worktree_terminal.py) give rc 1, with **rows 2, 3, 4, 7, 8 FAIL** and rows 1, 5, 6 PASS. This matches the builder's claim. The deletion assertion (4) was red. The absence rows are discriminated by mutants: M8 (unresolved also deleted) reds (1)(7)(8); M12 (plain removed) reds (5); M4 (delete not_terminal) reds (6); M2 reds (4), which proves the 909-before-910 ordering bites.|natural semantic RED + mutants|
|SC-04|same, rows (1), (2)|Row (2) was naturally red at 322b12b0. M5 (dry-run ignored) reds (1).|natural + mutant|
|SC-05|same, rows (3), (6), (7), (8)|Rows (3)(7)(8) were naturally red at 322b12b0. M7 (kept line printed twice) reds (3)(7)(8), so the "exactly one" clause binds. M4 and M6 (live stamp named) red (6), so "no line names building" binds. **M11 (the reason is dropped from the kept line) stays fully GREEN**, so the `absent` / `not absent` clauses are unbound at the sweep layer. See F-2.|natural + mutants, one clause unbound|
|SC-07|named: `tests/integration/test-check-plan-routes.py`|**The named test is never red.** Mutant A is pin + old post-merge-sweep.py, where the private helper is kept. Mutant B is pin + old registry and inventory. In both, a plain run gives `ALL PASS` rc 0. The guard that does red is `check-plan-routes.py --canonical-reader-audit`, which is in the T-02 verify and in the tests.yml "Canonical-reader audit" step. It exits 2 in both mutants, once with `live AST row absent from migration inventory` and once with `observed state=missing`. See F-1.|red only via the audit command, not the named test|
|SC-09|pre-existing cases in the four integration files|**Regression guard: fail-first N/A.** These criteria assert no regression, and there is no defect to redden against. They are green at the pin, both in the receipts and in the verify runs.|N/A (regression guard)|
|SC-10|test-broad-catch-census.py, test-no-distribution.py|**Regression guard: fail-first N/A**, for the same reason. Both are green in the unit receipt.|N/A (regression guard)|

The mutant driver was a throwaway at `/tmp/feat2458-mutants.py` running against the scratch tree
`/tmp/feat2458-mut`. Each mutant was restored by asserting the source bytes were identical, and
before the run I diffed the scratch blob against the pin and it was clean.

**Assertion counts (non-vacuous):**
- SC-01: 8 rows. Each checks klass, a non-empty str reason and a must or must_not substring.
- SC-02: 3 rows.
- SC-03/04/05: 8 stamp rows plus 2 root-SAFETY rows.
- SC-07: 0 rows in a plain run. See F-1.

## Findings

- **F-1 · substance · low-med · T-02** (owns `tests/integration/test-check-plan-routes.py`).
  SC-07 says the routes test "passes at review_sha — its T-07 terminal-contract case compares
  the registry, the inventory and the live AST". `case_canonical_reader_t07_terminal_contract` is
  listed only in `CANONICAL_READER_CASES` (`test-check-plan-routes.py:2262-2278`). Those cases run
  only under `--canonical-reader-self-test` (`:2475`), and neither run-unit-tests.py, the T-02 verify
  nor CI invokes that flag (tests.yml:229 says so). The failure scenario: the hook keeps its private
  fleet reader, or the registry keeps the dead key, and test-check-plan-routes.py still exits 0. I
  measured this as mutants A and B above. The intent is still guarded, because the canonical-reader
  audit in CI and in the verify reds both mutants. The SC text is not met as written (O-04).
  - Separately, `--canonical-reader-self-test` is red at both 322b12b0 and the pin with 2
    pre-existing failures: `live_inventory_names_no_plan` and
    `audit_holds_without_a_feature_corpus`. This is not FEAT-2458's doing, and 322b12b0 shows the
    same two. Mutant A adds 6 FAILs to it and mutant B adds 8.
  - Repair, for the lead or operator to choose: re-point SC-07's evidence at
    `check-plan-routes.py --canonical-reader-audit`, or move the T-07 case into `CASES`.
- **F-2 · substance · medium · T-02** (owns `tests/integration/test-post-merge-sweep.py`; T-01's (i) row has the same pattern).
  The never-landed fixture id is `FEAT-912-stamp-absent`. Every line naming its stamp therefore
  contains `absent` whatever reason the sweep prints, so rows (3) and (7) check `absent` vacuously.
  Row (8)'s `"absent" not in` passes trivially when no reason is printed. Mutant M11, where the hook
  prints `kept .harness/{name} — unresolved` with no reason, stays fully green. That is exactly the
  operator-facing SC-05 contract ("carrying … absent", "not absent"). The function-layer row (d),
  `FEAT-904-never`, does bind the absent wording; M3 reds (d) but not the sweep rows. In T-01 row
  (i), `FEAT-920-prefix-absent` has the same property: only its klass discriminates, since M3 left
  (i) green.
  - Repair: rename the fixture ids so they do not contain `absent`, or assert on the reason phrase
    `is absent from`.

## Principles applied
- Build the Lever: the perturbation proof used one scripted mutant driver over a scratch tree,
  covering 12 mutants, instead of hand-run edits.

## Open questions
- Q-1 (non-blocking): should SC-07's evidence be re-pointed at `--canonical-reader-audit`, or the T-07 case moved into `CASES`? (F-1)
- Q-2 (non-blocking, harness owner): `test-check-plan-routes.py --canonical-reader-self-test` carries 2 pre-existing failures at 322b12b0 that no runner sees.

Raw logs were in /tmp and are ephemeral: `feat2458-qa-{unit,integration}.log`,
`feat2458-verify-t0{1,2}.log`, `feat2458-red-*.log` and `feat2458-selftest-base.log`. QA's grant
under `runs/` covers only `qa/manifest-*.json`, so the excerpts above are the durable record.
