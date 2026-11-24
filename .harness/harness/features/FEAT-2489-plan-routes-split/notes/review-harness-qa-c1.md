# QA gate — FEAT-2489-plan-routes-split — validate c1 (r-20261124-8-validate-validator)

**VERDICT: PASS.** matrix_ok: true. unit and integration both ran once at the pin, every discovered file passed (68/68 and 95/95), and both receipts are clean under `evidence_defects`. SC-03, the only `verify: automated` criterion, has a named test and two red runs from before the fix, recorded as receipts and reproduced by me. The CI route and canonical gates exit 0 under the workflow's own parsing. `tests.yml` is byte-identical to base. T-04.verify exits 0, and its MAP block equals `notes/equivalence-final.txt` line for line (164 lines).

## Pin and environment

- Repository: mruangutai/harness (unbound Harness feature, so the reviewed repo is the one that holds the feature). review_sha `be0807b024f5da33adcd034859d62ab9ec59bd8f`, base `261fdf726428bd8325fbd3d4beccad23b67e83cc`. `git merge-base pin main` = base.
- QA policy blob: `git show be0807b0:.harness/harness.json` (`test_matrix`, `test_kinds`).
- Managed checkout: `pinned-checkout.py add --feature FEAT-2489-plan-routes-split --run-id r-20261124-8-validate-validator --persona harness-qa`, HEAD = pin. `worktree-state.py --verify` exits 0 ("converged") and `git status` is clean. Before the runs I ran `bun install --frozen-lockfile` and `python3 -m compileall -q .claude/skills/harness/bin`, as CI does. The pin was removed on return (rc=0).
- Interpreter: host `/opt/homebrew/bin/python3` 3.15.2, PyYAML 6.0.3, jsonschema 4.26.0. This is the host's run, not a CI run.
- Env for each run: `env -u PYTHONUNBUFFERED -u NO_COLOR -u FORCE_COLOR -u HARNESS_AGENT_TYPE -u CLAUDE_PROJECT_DIR TERM=xterm-256color HARNESS_PROJECT_DIR=<pin>`. The host's `NO_COLOR=1` and `TERM=dumb` were stripped, and that was confirmed from an `env` dump.

## Matrix (from the pinned harness.json)

| Task | change_type | Kinds required |
|---|---|---|
| T-01 | bugfix | integration (`fix_confined_to_tests_and_contract_docs`: only the test file and notes). unit's `touches_runtime_code` is false. `match_bug_class` cannot be resolved (placeholder) |
| T-02 | scaffolding | none |
| T-03 | cross_module | unit, integration (always) |
| T-04 | config | integration only if `touches_config_shape`. The JSON change is values only (two rows re-pathed, two list entries), so the predicate is false |

Required set: **unit and integration**, both `active`. `typecheck` is active but in no matrix row and no `.ts` file changed, so it is not required and was not run. functional and eval are excluded under DEC-187. component and ui are unresolved, but no matrix row this feature hits requires them.

| kind | state | cmd | files discovered (git `discover_expected`) / selected / exit 0 | runner exit |
|---|---|---|---|---|
| unit | satisfied | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <FD>/runs/r-20261124-8-validate-validator/qa/manifest-unit.json` | 68 / 68 / 68 | 0 (25.1s) |
| integration | satisfied | same, `--kind integration` → `manifest-integration.json` | 95 / 95 / 95 | 0 (156.3s pool wall) |

- Receipts: `runs/r-20261124-8-validate-validator/qa/manifest-unit.json` (sha256 7a936798…), `manifest-integration.json` (sha256 9f4a5243…). Both have `tested_commit` = pin and `runner_exit` 0. Running `check-integration-shards.py evidence_defects` against `discover_expected(pin)` gives `[]` for both.
- Every per-file header in the output reads `(exit 0, …)`. I graded from these headers and the runner exit, not from `^FAIL`. The `FAIL BUG-1290 …` lines come from test-factory-claim-mutation.py's own mutation proof, and that file exits 0.
- The suites cover this change, not just neighbouring code. unit runs `tests/unit/test-structure-audit-index.py` and `test-broad-catch-census.py`, both edited and importing `structure_audit`; each prints `PASS audit_modules_load_from_the_bin_under_test`. integration runs `test-check-plan-routes.py` (exit 0, 42.7s, 57 `PASS canonical_reader_*`, ALL PASS), `test-checker-structure-locks.py` and `test-structure-audit-single-pass.py`.
- Full runner output: `notes/qa-c1-runner-unit-output.md` (sha256 5cd93b2d…) and `notes/qa-c1-runner-integration-output.md` (sha256 b8d61dec…).

## CI checks-job gates at the pin

Each step body was extracted from the pinned `tests.yml` with `yaml.safe_load` and run under `bash -e -c` from the pin, with the env above.

- **Plan-route gate:** exit 0. Parsed summary `0 violation(s) across 2 plan(s)`; examined `39` feature dir(s), 37 skipped as shipped. The step printed `route gate entered 39 feature dir(s), checked 2 live plan(s); checker exit 0`.
- **Canonical-reader audit:** exit 0. `0 unresolved reader site(s) across 103 Python file(s)`, so scanned=103: base was 101, and the two new modules account for the rise.
- **`--consolidation-audit`:** `tests.yml` has **no such step**, at base or at the pin (grep finds only the two steps above). I ran the raw command anyway: exit 0, output `0 consolidation finding(s) under bin/`. In CI the consolidation audit is reached only through the integration file test-checker-structure-locks.py.
- `git diff --exit-code 261fdf72 be0807b0 -- .github/workflows/tests.yml` exits 0.

## T-04.verify and the MAP block (C2)

- I took the verify block exactly as written: `plan.yaml` at the pin, `tasks[T-04].verify`, sha256 61972b16…. Run from the pin root, it exits 0 and prints `PASS T-04: matched-tree CLI equivalence ALL PASS …`.
- `split-equivalence.py` at the pin exits 0 with ALL PASS, 9/9 PASS. `perturbed:canonical` has mapped=1.
- `diff` of the live `^MAP ` lines against `notes/equivalence-final.txt` exits 0 over 164 lines, so the block is equal line for line. The TREE lines match too: head bin `d542c641…`, head tests `3f8731cd…`.

## SC evidence and fail-first

The BRIEF has one `verify: automated` SC, SC-03. SC-01, SC-02, SC-04 and SC-05 are `inspection`.

- **SC-03 tests:** `tests/integration/test-check-plan-routes.py`, run by default through `*CANONICAL_READER_CASES` at :2461:
  - `_check_live_inventory_named_plans` (:1961): no document-level plan (:1968), each plan-naming row resolves (:1971), and the audit holds on bin plus the named plans (:1978).
  - `case_canonical_reader_named_plan_contract` (:1983): a missing plan and a missing task are refused (:1994, :1996).
  - Provenance at :2326.
  - No `names no plan` / `no feature plan` / `without a feature corpus` / `names_no_plan` string remains (grep count 0).
- **Fail-first, natural red, semantic.**
  - `notes/red-t01-canonical-self-test.txt`: the base self-test exits 1 with exactly the two FEAT-71 FAILs.
  - `notes/red-t03-stale-inventory.txt`: recorded at HEAD 3b6f2a42, the T-03 commit, which predates T-04's inventory commit 427d3a7e. The default run exits 1 with 9 FAILs, all `canonical_reader_*`. The audit exits 2, and its 5 CLASSIFICATION lines name only the manifest, the moved rows and canonical_reader_audit.py. The checker exits 1 on the two canonical comparisons.
  - **I reproduced all of these** on `git archive` trees of 261fdf72 and 3b6f2a42 and got identical FAIL sets and exits: `notes/qa-c1-failfirst-repro.md`.
  - The same file shows a signature-absent red for "runs by default": the base default run prints ALL PASS with **0** `canonical_reader` lines.
- **green-t01 binding (SC-03):**
  - Recorded HEAD `c794bffe…` is an ancestor of the pin.
  - `git rev-parse c794bffe:tests/integration/test-check-plan-routes.py` = `224a0a00…`, which is the recorded BLOB.
  - Neither `canonical_reader_audit.py` nor `structure_audit.py` exists at c794bffe (`cat-file -e` 128).
  - c794bffe's test file contains `_check_live_inventory_named_plans` and not `names no plan`.
  - The receipt ends `exit=0`, with ALL PASS and every named-plan contract PASS.
- **Mutation proofs** (in memory, on the pin's test module; DEC-169):
  - M1, `_copy_named_plans` replaced with a no-op: `audit_holds_on_bin_plus_named_plans` FAILs ("plan cannot be read"). The copy step is load-bearing.
  - M2, `_named_plan_problems` always returns None: `refuses_a_missing_plan` and `refuses_a_missing_task` FAIL.
  - M3, a live row's plan renamed so it cannot resolve, which exercises the skip path: both `named_plan_resolves[…]` and `audit_holds…` FAIL.

## Disclosures judged

- **T-01 `_copy_named_plans` skip is not fail-open.** An unresolvable plan is left out of the temp root, so the audit itself refuses it ("plan cannot be read") and the row's resolves-check refuses it too (M3: both red). Skipping can only remove inputs, and removing a named plan only adds findings. A `CorpusError` from `corpus_path` is skipped in the copy, but `_named_plan_problems` catches it as a problem, so the row is still red.
- **T-02 stderr compared exactly.** `compare()` maps stdout only (`split-equivalence.py:293`) and fails on any stderr difference (:276). That is fail-closed: a relocated stderr locator, such as a traceback frame, gives a false red, never a false green. The sampled states produce no stderr locator, so nothing was masked.

## Findings

- **Q-F1, form, low, T-02** (`notes/split-equivalence.py`): T-02's intent defines `mapped` as "old stdout **and stderr** lines the relocation map changes". The script counts stdout only, and its docstring says so. Failure scenario: a reader taking `mapped=0` on a run with stderr as "no stderr locator relocated" learns nothing, because stderr is never mapped. This is not fail-open: stderr is exact-compared, and C1 refused the normalizer. Advisory.
- **Q-F2, form, info, SCOPE CHANGE (no task):** the dispatch asked for "the CI `--consolidation-audit` gate". `tests.yml` has no such step, and none was in scope (DEC-183, BRIEF out of scope). I report the raw run (exit 0) for information only. Failure scenario: a later reader cites a CI consolidation step that does not exist.

## Coverage gaps (Phase 1 expectations with no test)

- A bin missing either module now fails at import (C4, accepted). Only case 19b's copy list touches this, and no test asserts the failure shape.
- SC-02's fifth item (line-numbered locators, traceback frames, location-order exception) is measured by no automated check. It rests on inspection of SC-01's diff, as the BRIEF discloses.
- The three integration audit files are never run against a copied bin (`CHECK_PLAN_ROUTES_BIN`). Only the two unit files are (green-t04-suites.txt; T-04.verify re-ran them green here).

## Test-first audit

T-01: the red at base (red-t01) was captured before the test edit (c794bffe), and the green came after. T-03/T-04: the red at 3b6f2a42 precedes the inventory delta at 427d3a7e. Order is consistent and there are no violations.

## Principles applied

- Build the Lever: I extracted the CI step bodies and T-04.verify mechanically from the pinned YAML instead of retyping them, so "verbatim" is literally true.
