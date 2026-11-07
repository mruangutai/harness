# Red-first receipt — slice S2 (corpus-reading tests, discovery and classification)

Baseline pin: `4a05030d401593003209f525fd06e00802eccd36` (origin/main).
Baseline clone: `git clone --no-local -q /Users/molchairuangutai/GitHub/harness /private/tmp/feat71-base-S2 && git -C /private/tmp/feat71-base-S2 checkout -q --detach 4a05030d` (removed after the run).
Every command ran from the clone root with `CLAUDE_PROJECT_DIR` and `HARNESS_PROJECT_DIR` set to that root.

## R1 — new assertions against the baseline IMPLEMENTATION (full corpus present)

Only the new test file (and, in the third run, the new inventory) was copied in. The failures are the dependency itself: the
exemption mechanism, and the audit's document-level default plan.

- `python3 tests/unit/test-feature-corpus-discovery.py` → exit 1
    - `FAIL: test_no_exemption_mechanism_exists (__main__.BranchClaims.test_no_exemption_mechanism_exists)`
    - `AssertionError: Lists differ: ['entries', 'exempt'] != ['entries']`
    - `FAILED (failures=1)`
- `python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test` → exit 1
    - `FAIL canonical_reader_current_plan_owns_its_source [': plan cannot be read: ownership plan must be a nonempty path']`
    - `FAIL canonical_reader_planless_rows_read_no_plan ({}, [': plan cannot be read: ownership plan must be a nonempty path'])`
    - `FAIL canonical_reader_planless_row_is_not_an_ownership_finding ['fixture.py::reader json_string remedy=json.loads: T-02 task files omit this source. PLAN AMENDMENT REQUIRED']`
    - `FAIL canonical_reader_live_inventory_names_no_plan ['<document>', '.claude/skills/harness/bin/check_state/ctx.py::Ctx._load_plan_docs::load_plan#1', '.claude/skills/harness/bin/dispatch-guard.py::_repository_identity::load_feature_json#1', '.claude/skills/harn`
    - `FAIL canonical_reader_audit_holds_without_a_feature_corpus [".harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml: plan cannot be read: failed to parse YAML in /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpw0jsml0a/.harness/harness/featur`
    - `5 FAILURE(S): ['canonical_reader_current_plan_owns_its_source', 'canonical_reader_planless_rows_read_no_plan', 'canonical_reader_planless_row_is_not_an_ownership_finding', 'canonical_reader_live_inventory_names_no_plan', 'canonical_reader_audit_holds_without_a`
- `python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test` → exit 1
    - `FAIL canonical_reader_current_plan_owns_its_source [': plan cannot be read: ownership plan must be a nonempty path']`
    - `FAIL canonical_reader_planless_rows_read_no_plan ({}, [': plan cannot be read: ownership plan must be a nonempty path'])`
    - `FAIL canonical_reader_planless_row_is_not_an_ownership_finding ['fixture.py::reader json_string remedy=json.loads: T-02 task files omit this source. PLAN AMENDMENT REQUIRED']`
    - `FAIL canonical_reader_audit_holds_without_a_feature_corpus [': plan cannot be read: ownership plan must be a nonempty path', '.claude/skills/harness/bin/bash-write-guard.py::<module> json_string remedy=artifact_accessors.read_hook_payload: T-06 task files omit`
    - `FAIL canonical_reader_live_classification_consistent [': plan cannot be read: ownership plan must be a nonempty path', '.claude/skills/harness/bin/bash-write-guard.py::<module> json_string remedy=artifact_accessors.read_hook_payload: T-06 task files omit this `
    - `FAIL canonical_reader_live_audit_is_zero {'exit_code': 2, 'unresolved': 0, 'scanned_files': ['.claude/skills/harness/bin/amendment_contract.py', '.claude/skills/harness/bin/artifact_accessors.py', '.claude/skills/harness/bin/bash-write-guard.py', '.claude/skil`

Named failing assertions:
- `test_no_exemption_mechanism_exists`: baseline `branch_collisions` takes `['entries', 'exempt']` (BRANCH_ERA_EXEMPT grandfathers FEAT-02/FEAT-03-subissue-mirror).
- `canonical_reader_planless_rows_read_no_plan` / `canonical_reader_current_plan_owns_its_source`: baseline always reads the document-level `plan` (`': plan cannot be read: ownership plan must be a nonempty path'`).
- `canonical_reader_planless_row_is_not_an_ownership_finding`: baseline checks a plan-less row against the default plan (`T-02 task files omit this source`).
- `canonical_reader_live_inventory_names_no_plan`: baseline inventory names `<document>` plus 28 rows with plan pointers.
- `canonical_reader_audit_holds_without_a_feature_corpus`: baseline audit on a tree without `.harness` reads FEAT-1928/FEAT-1559/BUG-285 plans and exits 2.

## R2 — baseline FILES, dead folders deleted and committed

The 120 non-survivor folders under `.harness/harness/features/` were removed with `git rm -rq` and committed (`3909460f`), which simulates
the post-deletion corpus. The baseline has no FEAT-71 folder, so 4 survivors remain. Each red below is the historical dependency.

- `python3 tests/unit/test-factory-cli.py` → exit 1
    - `ok    run(): unhandled KeyError exits 2, not 1`
    - `ok    run(): unhandled KeyError leaves stdout empty`
    - `ok    run(): unhandled KeyError stderr mentions FACTORY_DEBUG`
    - `FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/feat71-base-S2/.harness/harness/features/FEAT-10-software-factory/plan.yaml'`
- `python3 tests/integration/test-branch-create-gate.py` → exit 1
    - `FAIL  ALLOW: a branch naming a flow that DOES exist on disk`
- `python3 tests/unit/test-feature-json-budget.py` → exit 1
    - `FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/feat71-base-S2/.harness/harness/features/FEAT-54-handoff-done-when/feature.json'`
    - `FAILED (errors=1)`
- `python3 tests/unit/test-plan-depends-on.py` → exit 1
    - `  FAIL the live plan corpus loads cleanly (4 files found, floor 67)`
    - `1 of 12 FAILING.`
- `python3 tests/integration/test-corpus-real-owner.py` → exit 1
    - `SKIP (host prerequisite missing): /private/tmp/feat71-base-S2 is the owner itself, so there is no active-worktree caller to compare`
    - `FAIL: test_audited_names_equal_the_tracked_directories (__main__.RealOwner.test_audited_names_equal_the_tracked_directories)`
    - `AssertionError: 4 not greater than 70`
    - `FAILED (failures=1)`
- `python3 tests/integration/test-corpus-non-regression.py -v` → exit 0
    - `SKIP: live manifest validation runs only with --conversion-manifest PATH`
    - `SKIP: no conversion manifest at /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/conversion-manifest.json (T-06 has not run)`
    - `test_converted_checkouts_still_verify_clean (__main__.ConversionManifest.test_converted_checkouts_still_verify_clean) ... skipped 'no --conversion-manifest'`
    - `test_the_manifest_is_internally_consistent (__main__.ConversionManifest.test_the_manifest_is_internally_consistent) ... skipped 'no conversion manifest yet'`
    - `OK (skipped=2)`
- `python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test` → exit 1
    - `FAIL canonical_reader_live_classification_consistent [".harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1559-corpus-outside-worktree/p`
    - `FAIL canonical_reader_live_audit_is_zero {'exit_code': 2, 'unresolved': 0, 'scanned_files': ['.claude/skills/harness/bin/amendment_contract.py', '.claude/skills/harness/bin/artifact_accessors.py', '.claude/skills/harness/bin/bash-write-guard.py', '.claude/skil`
    - `FAIL canonical_reader_T-03_postcondition [".harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: [E`
    - `FAIL canonical_reader_T-04_postcondition [".harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: [E`
    - `FAIL canonical_reader_T-05_postcondition [".harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: [E`
    - `FAIL canonical_reader_T-06_postcondition [".harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: [E`
- `python3 tests/integration/test-check-plan-routes.py` → exit 0
    - `PASS case_19a3c_the_examined_line_reports_dirs_entered_and_shipped_skipped`
    - `PASS case_22c_broken_symlink_plan_is_reported_not_skipped`
    - `PASS case_24_done_is_skipped`
    - `PASS case_24_abandoned_is_skipped`
    - `PASS case_24_no_feature_yaml_is_checked_not_skipped`
    - `PASS case_24_ten_key_feature_json_with_a_done_plan_station_is_skipped_end_to_end`
- `python3 tests/unit/test-harness-yaml-corpus.py` → exit 0
- `python3 tests/integration/test-plan-team.py` → exit 0
    - `ok    (2) plan/should-not-exist outputs list is empty (its correct state — skipped, not counted)`
- `python3 tests/unit/test-feature-corpus-discovery.py` → exit 0
- `python3 tests/integration/test-gen-decisions-index.py` → exit 0
- `python3 tests/integration/test-feature-worktree.py` → exit 0
- `python3 .claude/skills/harness/bin/check-plan-routes.py` → exit 0
    - `examined 4 feature dir(s); 3 skipped as shipped`
- `python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` → exit 2
    - `CLASSIFICATION .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml: [Errno 2] No such file or direct`
    - `CLASSIFICATION .harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml: [Errno 2] No such file or dire`
    - `CLASSIFICATION .harness/harness/features/BUG-285-canonical-reader/plan.yaml: plan cannot be read: failed to parse YAML in /private/tmp/feat71-base-S2/.harness/harness/features/BUG-285-canonical-reader/plan.yaml: [Errno 2] No such file or directory: '/private/t`
    - `CLASSIFICATION .claude/skills/harness/bin/bash-write-guard.py::<module> json_string remedy=artifact_accessors.read_hook_payload: T-06 task files omit this source. PLAN AMENDMENT REQUIRED`
    - `CLASSIFICATION .claude/skills/harness/bin/bash-write-guard.py::<module> manifest_domains remedy=artifact_accessors.manifest_domains: T-07 task files omit this source. PLAN AMENDMENT REQUIRED`
    - `CLASSIFICATION .claude/skills/harness/bin/board-station.py::main json_file remedy=artifact_accessors.load_harness_json: T-03 task files omit this source. PLAN AMENDMENT REQUIRED`

Notes:
- `test-corpus-non-regression.py` exits 0 at baseline, but only by SILENTLY SKIPPING both manifest assertions (`skipped 'no conversion manifest yet'`, `skipped 'no --conversion-manifest'`). That skip is the defect. The new file has no skip path.
- No red is possible from deletion for `test-harness-yaml-corpus.py` (the comment pointer only), `test-plan-team.py` (the `FEAT` constant renders a route path and is never read from disk), `test-feature-corpus-discovery.py` (dead ids used only as in-memory data; its red is in R1), `test-gen-decisions-index.py`/`gen-decisions-index.py` (docstring pointer only) and `test-feature-worktree.py` (a fixture id inside a temp repo: `FEAT-70` → `FEAT-74`).

## G — new files, dead folders deleted (same clone, my 15 changed files overlaid)

- `python3 tests/unit/test-factory-cli.py` → exit 0 — 33/33 checks passed.
- `python3 tests/integration/test-branch-create-gate.py` → exit 0 — 15/15 cases passed.
- `python3 tests/unit/test-feature-json-budget.py` → exit 0 — OK
- `python3 tests/unit/test-plan-depends-on.py` → exit 0 — 13/13 checks passed.
- `python3 tests/integration/test-corpus-real-owner.py` → exit 0 — OK
- `python3 tests/integration/test-corpus-non-regression.py -v` → exit 0 — OK
- `python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test` → exit 0 — ALL PASS
- `python3 tests/integration/test-check-plan-routes.py` → exit 0 — ALL PASS
- `python3 tests/unit/test-harness-yaml-corpus.py` → exit 0 — 16/16 checks passed.
- `python3 tests/integration/test-plan-team.py` → exit 0 — 121/121 checks passed.
- `python3 tests/unit/test-feature-corpus-discovery.py` → exit 0 — OK
- `python3 tests/integration/test-gen-decisions-index.py` → exit 0 — ok - test_dec_233_entry_names_every_removed_enforcement_point
- `python3 tests/integration/test-feature-worktree.py` → exit 0 — PASS test-feature-worktree.py
- `python3 .claude/skills/harness/bin/check-plan-routes.py` → exit 0 — examined 4 feature dir(s); 3 skipped as shipped
- `python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` → exit 0 — 0 unresolved reader site(s) across 100 Python file(s)

`test-corpus-real-owner.py` announced `SKIP (host prerequisite missing): ... is the owner itself` only for the optional linked-caller
leg (the clone is a plain checkout). The synthetic non-vacuity case `test_the_walk_reaches_every_fixture_directory` is asserted and ran.

## W — worktree green (sparse; dead folders not materialised)

- `python3 tests/unit/test-factory-cli.py` → exit 0 — 33/33 checks passed.
- `python3 tests/integration/test-branch-create-gate.py` → exit 0 — 15/15 cases passed.
- `python3 tests/unit/test-feature-json-budget.py` → exit 0 — OK
- `python3 tests/unit/test-plan-depends-on.py` → exit 0 — 13/13 checks passed.
- `python3 tests/integration/test-corpus-real-owner.py` → exit 0 — OK
- `python3 tests/integration/test-corpus-non-regression.py -v` → exit 0 — OK
- `python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test` → exit 0 — ALL PASS
- `python3 tests/integration/test-check-plan-routes.py` → exit 0 — ALL PASS
- `python3 tests/unit/test-harness-yaml-corpus.py` → exit 0 — 16/16 checks passed.
- `python3 tests/integration/test-plan-team.py` → exit 0 — 121/121 checks passed.
- `python3 tests/unit/test-feature-corpus-discovery.py` → exit 0 — OK
- `python3 tests/integration/test-gen-decisions-index.py` → exit 0 — ok - test_dec_233_entry_names_every_removed_enforcement_point
- `python3 tests/integration/test-feature-worktree.py` → exit 0 — PASS test-feature-worktree.py
- `python3 .claude/skills/harness/bin/check-plan-routes.py` → exit 0 — examined 125 feature dir(s); 119 skipped as shipped
- `python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` → exit 0 — 0 unresolved reader site(s) across 100 Python file(s)

## Files changed (slice S2)

- `.claude/skills/harness/bin/feature_corpus.py`: deleted `BRANCH_ERA_EXEMPT` (FEAT-02/FEAT-03-subissue-mirror grandfather) and the `exempt` parameter of `branch_collisions`. The collision rule is now uniform.
- `.claude/skills/harness/bin/check-plan-routes.py`: removed the document-level default plan. Task-file ownership is checked only for a row that names its own `plan`, and `_classification_task_files` reads only those plans. Per-task units and the T-07 terminal contract select rows that name no plan.
- `tests/integration/canonical-reader-classification.json`: dropped the top-level `plan` (BUG-285) and all 28 row `plan` pointers (FEAT-1928 ×14, FEAT-1559 ×1, BUG-20261006 ×13). Those 28 rows' foreign-plan task labels became `none`. Rows owned by the inventory keep their task labels.
- `tests/integration/test-check-plan-routes.py`: `CASE17_PATH` → synthetic `FEAT-90-fixture`. The ownership/glob/route cases now name a synthetic `plan.yaml`/`current.yaml` per row. New `case_canonical_reader_reads_no_feature_plan` covers plan-less rows reading nothing, the live inventory naming no plan, and the audit passing on a tree with no feature corpus.
- `tests/unit/test-feature-corpus-discovery.py`: replaced the four era-exemption cases with a uniform-collision case on synthetic ids and an assertion that no exemption mechanism exists.
- `tests/unit/test-factory-cli.py`: the em-dash source of truth is now `unicodedata` (U+2014 "EM DASH") instead of FEAT-10's plan.yaml. Dropped the dead `feature_corpus` import and unused ROOT/BIN_DIR/HERE.
- `tests/integration/test-branch-create-gate.py`: assertion 3 allows a synthetic `FEAT-90-fixture-flow` in a fixture root and denies the same branch once that directory is absent. It no longer uses the live FEAT-18 folder.
- `tests/unit/test-feature-json-budget.py`: the FEAT-54 live read is replaced by a synthetic 300+ line heterogeneous-ledger record with a nested github block. Dropped the `feature_corpus` import.
- `tests/unit/test-plan-depends-on.py`: the floor of 67 is replaced by synthetic non-vacuity (the walk must reach exactly 3 fixture plans). The paired detector shares the plan writer. The live walk asserts integrity only.
- `tests/integration/test-corpus-real-owner.py`: removed `FLOOR = 70` and the real-corpus record-less requirement. Added `test_the_walk_reaches_every_fixture_directory` (exact fixture names, the record-less dir, owner plus linked caller) and `test_an_empty_walk_is_rejected`.
- `tests/integration/test-corpus-non-regression.py`: removed the FEAT-1559 manifest read and the `--conversion-manifest` mode. The manifest is now produced by really converting a synthetic owner's worktrees (converted, dirty-skipped, excluded). Its consistency and live-verify halves always run, and a mutant, a moved checkout and a broken layout are each caught.
- `tests/unit/test-harness-yaml-corpus.py`: the comment pointer into the FEAT-59 folder now reads "kept in git history".
- `tests/integration/test-plan-team.py`: the rendered `{{feat}}` is synthetic `FEAT-90-fixture` instead of FEAT-59-proportional-flow.
- `.claude/skills/harness/bin/gen-decisions-index.py`: the docstring pointer "See FEAT-04-decisions-index PLAN.md T-02" now reads "The contract (FEAT-04 T-02)".
- `tests/integration/test-feature-worktree.py`: the temp-repo fixture id `FEAT-70` (a dead real flow id) is now `FEAT-74`.

Classified, unchanged: `feature-worktree.py` (:124 FEAT-01-kaya-platform, :311-312 FEAT-32 are provenance comments), `test-gen-decisions-index.py:3` (provenance label), `test-feature-worktree.py:1042-1043` (provenance docstring), `tests/integration/fixtures/prior-check-plan-routes.py.fixture` (ids appear only in comments of the frozen copy; nothing is executed as data).
