# QA — FEAT-2206 validate c3 (QA c5) — review_sha 7b8e2e1f485db72a4a574e04738533cb0ab821ed

**BLUF: PASS.** F-1/Q-02 is closed: the new INV-52 regression is red at b7af829c and 4a351fae and green at the pin, on both the full-clone and sparse arms. Unit and integration suites are green at the pin (60 + 86 = 146 files, rc 0). Real corpus is nonzero. No source, test or fixture edit by me.

Environment: pinned checkouts via `pinned-checkout.py` (run-ids validate-c3-qa, -qa-base, -qa-c2), `CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR`/`HARNESS_AGENT_TYPE` unset for every test run. Baseline/c2 runs use the PIN's test file with `CHECK_STATE_BIN` pointing at the other tree's `check-state.py` (absolute path; a relative path broke my first c2 probe, G-01).

## Phase 1 (from BRIEF/plan only)
Expected: SC-01 unit (shipped classification, strict-invalid shipped plans, unreadable/missing/non-mapping status stay checked); SC-02 integration (full/changed audits, `--feature` one note, read-only observations, real corpus); SC-03 integration (INV-24/29/52 shipped/active, shipped/shipped, sparse+full, no grading of malformed shipped fields — now incl. INV-52 salvage of strict-refused records per Q-02); SC-04 integration (INV-28/30 retired, `--list`, `--only`). Every one has a named test (below). No Phase 1 gap.

## Matrix
T-01 `change_type: bugfix`: `always: []`; `when` unit if touches_runtime_code (full feature diff touches `.claude/skills/harness/bin/**`: true) → unit required; integration is required by BRIEF SC-02..04 evidence (the `fix_confined_to_tests_and_contract_docs` clause is false). `matrix_ok: true`.
- unit: `run-unit-tests.py --kind unit` → rc 0, **60 files**, 0 non-mutation FAIL (4 `FAIL BUG-1290 5a/5b/5c` lines are test-factory-claim-mutation's own passing proof, G-09). Named: `tests/unit/test-check-state-shipped-ctx.py` (0 failures).
- integration: `--kind integration` → rc 0, **86 files** (`tests/integration` holds 92 .py; runner discovers 86). Named: `tests/integration/test-check-state-shipped.py` (19 tests OK).
- 60 + 86 = 146 = the historical log's count.

## F-1 / Q-02 closure — new test run at three trees
Test: `test_inv52_keeps_the_branch_of_a_shipped_record_the_strict_loader_refuses` (`tests/integration/test-check-state-shipped.py:258-270`): shipped parent `"²"` (strict-refused) + active `FEAT-7-building` on `feat/dup`; asserts the exact `INV-52: branch feat/dup is claimed by 2 landed features (FEAT-5-shipped, FEAT-7-building)` line on a full clone AND the sparse worktree, and no `SHIPPED … does not parse` line.

|Tree|Whole file|New test, full arm|New test, sparse arm (isolated probe)|
|---|---|---|---|
|b7af829c|11 of 19 fail|FAIL (assert line 267)|FAIL — traceback, not an INV-52 omission (pre-round-1 INV-24 `ValueError`)|
|4a351fae|1 of 19 fail|FAIL (assert line 267, semantic: line absent)|FAIL (semantic: line absent)|
|7b8e2e1f|19 of 19 OK|PASS|PASS|

Sparse-arm isolation: python `-c` subclass that routes both `clone()` and `sparse()` to one sparse worktree (no file written). The in-test loop stops at the first failing arm, so the c2 sparse red needed this probe.
Fail-first tier: natural RED (retained command/outcome above plus `red-first.md` § Rework round 3). The b7af829c red is crash-class and proves less about INV-52 than the 4a351fae red, which is the semantic one.
Absence arm ("does not parse"): the assertion matches the feature.json wording `ctx.py:507`; the plan wording is "does not load". Which output the strict loader's `not a recorded issue number` refusal yields for a graded shipped record was not mutation-proved by me — discrimination of that one clause is unshown (O-05), not shown useless. The presence assertion carries the red.

Source seam (`git diff 4a351fae 7b8e2e1f -- .claude`, read): `corpus._branch_entry` re-reads only `document is None` + record path + `is_shipped(path)` entries via `comparison_record`; INV-52's declared reads gain `_PLAN_YAML` in `table.py`. Matches the expected seam. No unit-level test of `_branch_entry` itself (proportionality note only; integration pins it).

## Per-SC evidence (all fail_first: natural RED vs b7af829c `red-first.md`; reproduced here for SC-03 INV-52)
- SC-01: `tests/unit/test-check-state-shipped-ctx.py` (10 failures at b7af829c, `red-first.md` § Unit; I did not re-run that baseline — recorded receipt).
- SC-02: `tests/integration/test-check-state-shipped.py:test_a_full_audit_names_no_shipped_feature`, `test_a_changed_audit_names_no_shipped_feature`, `test_selecting_a_shipped_feature_prints_one_note_and_exits_clean`, `test_a_shipped_directory_is_read_only_for_status_and_comparison` (8 failures at b7af829c, `red-first.md` § Integration; I re-observed 11 failures of the 19-test file at b7af829c — 8 original + 3 later-round tests).
- SC-03: `…:test_inv52_keeps_the_branch_of_a_shipped_record_the_strict_loader_refuses` (this note, own reproduction), plus `test_inv24_does_not_grade_a_shipped_claim_itself` / `…skips_unusable…` / `…oversized…` (round-1/2 receipts).
- SC-04: `test_inv28_and_inv30_are_retired`, `test_selecting_a_retired_number_runs_nothing`, `test_no_milestone_or_pull_request_check_runs_for_a_shipped_feature`.

## Literal T-01 verify
- Python block (unit + integration + `--real-corpus` under the 55 s budget): run verbatim in the pin → exit 0, ~17 s, `0 failure(s)`, "PASS exit=0".
- Real corpus: **10 landed, 8 shipped** (BUG-2141, 2161, 2169, 2180, 2181, 2190, FEAT-2037, FEAT-71), each excluded/open-confined/one-note, 0 failures. Provenance limit: it reads the live owner checkout `/Users/molchairuangutai/GitHub/harness` (main; HEAD read right after the run = 00998ef1, dirty only with untracked `.harness/logs`, `.harness/notes`). I did not capture HEAD before the run, so the ref is not an immutable SHA (G-15). Earlier c4 count was 9 landed / 7 shipped at b7af829c.
- Standalone-clone half (`git clone` + check-state, validate-feature-json, check-decision-anchors, check-plan-routes, `run-unit-tests --kind all`, DECISIONS-INDEX diff, `tee` into `notes/merge-$pin.log`): NOT executed by me — it writes the shared merge log, which I am told not to write, and the control-plane's literal pin is the feature worktree HEAD (a4d5b2fa), not 7b8e2e1f. Substituted: unit and integration kind runs at the pin (above). check-state/validators/index diff at the pin are covered only by the historical log.

## Historical log and code equivalence
- `notes/merge-8cdbb3620037f9fd8c86621225fcaedd9555edaa.log` (8174 lines): header `review_sha=8cdbb362…`, 146 `-----` script blocks, all `exit 0`, `pool: 8 workers, 146 files, 123.95s`, final `verify-exit=0 review_sha=8cdbb362…`. Read, not re-executed.
- Equivalence established independently: `git diff --stat 8cdbb362 7b8e2e1f` = one file, `feature.json` (review_sha pointer + removed regate entry); `git diff --name-only` lists nothing else. Therefore 8cdbb362 differs from 7b8e2e1f only in feature.json metadata; no `.claude`/`tests`/docs/plan bytes differ. My own pin runs make the equivalent claim for unit+integration directly.
- Worktree HEAD is a4d5b2fa (evidence-only commit after 8cdbb362); uncommitted: feature.json, plan.yaml (disclosed #2201 status rewrite).
- Code-reviewer's "62 records passing" is not mine to confirm; not examined.

## Findings
None blocking. Advisory only:
- A1 (proportionality, low, T-01): no unit test directly pins `_branch_entry`'s three guard conditions (`document is None`, record path present, shipped); only the integration test covers them via one malformed-parent shape (`"²"`). Other strict-refusal shapes (oversized `1…`×4301 parent) are covered for INV-24 only.
- A2 (form, low, T-01): the absence clause uses `"does not parse"` while plan refusals say `"does not load"` — see above.

## Principles applied
- Build the Lever: the sparse-arm discrimination used a one-shot subclass probe (no file) instead of hand-reading, rerunnable from the command recorded here.

## Cleanup
Pinned checkouts removed on return (all three run-ids). `/private/tmp/qa-c3-{unit,integration}.out` hold the runner output.
