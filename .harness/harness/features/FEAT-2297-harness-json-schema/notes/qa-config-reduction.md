# FEAT-2297 T-10 — config contract reduction receipt

Checker: `python3 .harness/harness/features/FEAT-2297-harness-json-schema/notes/check-config-reduction.py --review-ref HEAD --receipt .harness/harness/features/FEAT-2297-harness-json-schema/notes/qa-config-reduction.md`
(signed D-06 amendment: the base is `git merge-base <review-ref> origin/main`; Gate A, the pre-existing
affected test/helper files, must be strictly negative; Gate B enumerates every new file below).
The checker rewrites only the measurement block; every other section is the disposition record.

Inventory: `notes/test-inventory-2026-11-22.md`, a verbatim copy of the scouts' read-only inventory at
main `c1724230` (sha256 `d3927f1b0fe6378b30284b3b7294bb2fd4dde814eb23e8b1bfc7024bfcf24496`, checked on every
run): 30 REMOVABLE, 12 UPDATE-BEHAVIOR and 110 UPDATE-FIXTURE rows across 67 files. A row's identity is
its `path:range` and class at that pin; one span carries two classes and stays two rows.

## Measurement

<!-- measured:begin -->
- base `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568` (`git merge-base HEAD origin/main`)
- review `8c945a8e88d791364b52f4a22fe3ca32856aa6b3`

| File | Base | Review | Delta |
|---|---|---|---|
| `.harness/harness/features/FEAT-2297-harness-json-schema/notes/check-config-reduction.py` | new | 314 | +314 |
| `tests/fixtures/harness-config-budgets.json` | new | 44 | +44 |
| `tests/harness_config_support.py` | new | 68 | +68 |
| `tests/integration/canonical-reader-classification.json` | 2599 | 2641 | +42 |
| `tests/integration/check_state_support.py` | 191 | 191 | +0 |
| `tests/integration/f58_sparse_fixture.py` | 281 | 286 | +5 |
| `tests/integration/gh_sync_support.py` | 1002 | 1004 | +2 |
| `tests/integration/test-board-lifecycle.py` | 1919 | 1882 | -37 |
| `tests/integration/test-board-station.py` | 348 | 322 | -26 |
| `tests/integration/test-branch-create-gate.py` | 502 | 500 | -2 |
| `tests/integration/test-check-skill-weight.py` | 151 | 148 | -3 |
| `tests/integration/test-check-state-entry.py` | 558 | 524 | -34 |
| `tests/integration/test-check-state-feat59.py` | 1278 | 1267 | -11 |
| `tests/integration/test-check-state-handoff.py` | 740 | 737 | -3 |
| `tests/integration/test-check-state-inv26.py` | 854 | 851 | -3 |
| `tests/integration/test-check-state-inv37-offline.py` | 273 | 274 | +1 |
| `tests/integration/test-check-state-inv51.py` | 95 | 95 | +0 |
| `tests/integration/test-check-state-plans.py` | 1039 | 1029 | -10 |
| `tests/integration/test-check-state-records.py` | 1328 | 1281 | -47 |
| `tests/integration/test-check-state-shipped.py` | 370 | 372 | +2 |
| `tests/integration/test-check-state-table.py` | 276 | 275 | -1 |
| `tests/integration/test-check-state-worktrees.py` | 792 | 786 | -6 |
| `tests/integration/test-check-state.py` | 82 | 84 | +2 |
| `tests/integration/test-code-grade-cli.py` | 402 | 393 | -9 |
| `tests/integration/test-corpus-non-regression.py` | 330 | 328 | -2 |
| `tests/integration/test-factory-integration.py` | 1647 | 1634 | -13 |
| `tests/integration/test-factory-issue-types.py` | 641 | 644 | +3 |
| `tests/integration/test-feature-corpus.py` | 478 | 481 | +3 |
| `tests/integration/test-gh-backlog-issue-types.py` | 384 | 383 | -1 |
| `tests/integration/test-gh-close-gate.py` | 450 | 453 | +3 |
| `tests/integration/test-gh-issue-types.py` | 510 | 509 | -1 |
| `tests/integration/test-gh-sync-abandon.py` | 1250 | 1251 | +1 |
| `tests/integration/test-gh-sync-board-add.py` | 101 | 101 | +0 |
| `tests/integration/test-gh-sync-open.py` | 1529 | 1543 | +14 |
| `tests/integration/test-gh-sync-start-task.py` | 696 | 676 | -20 |
| `tests/integration/test-harness-config-fixtures.py` | new | 424 | +424 |
| `tests/integration/test-harness-config-readers.py` | new | 327 | +327 |
| `tests/integration/test-harness-config-upgrade.py` | new | 132 | +132 |
| `tests/integration/test-hooks-install.py` | 525 | 527 | +2 |
| `tests/integration/test-layout-migration.py` | 438 | 439 | +1 |
| `tests/integration/test-lead-start-return.py` | 714 | 715 | +1 |
| `tests/integration/test-merge-gate.py` | 744 | 749 | +5 |
| `tests/integration/test-omp-native-gate-runtime.py` | 840 | 841 | +1 |
| `tests/integration/test-plan-decision-dispositions.py` | 700 | 697 | -3 |
| `tests/integration/test-plan-merge.py` | 5302 | 5304 | +2 |
| `tests/integration/test-plan-sign-gate.py` | 779 | 781 | +2 |
| `tests/integration/test-post-merge-sweep.py` | 1225 | 1204 | -21 |
| `tests/integration/test-run-unit-tests-kinds.py` | 137 | 130 | -7 |
| `tests/integration/test-upgrade-config.py` | 313 | 313 | +0 |
| `tests/integration/test-validate-digest-shadows.py` | 497 | 499 | +2 |
| `tests/integration/test-validate-digest.py` | 7192 | 7129 | -63 |
| `tests/manual/probe-issue-types.py` | 190 | 189 | -1 |
| `tests/unit/omp-hooks.test.ts` | 4541 | 4549 | +8 |
| `tests/unit/test-artifact-accessors.py` | 405 | 408 | +3 |
| `tests/unit/test-check-state-inv26-routing.py` | 204 | 204 | +0 |
| `tests/unit/test-check-state-inv35.py` | 104 | 106 | +2 |
| `tests/unit/test-check-state-inv37-local-binding.py` | 175 | 175 | +0 |
| `tests/unit/test-check-state-shipped-ctx.py` | 223 | 225 | +2 |
| `tests/unit/test-code-grade.py` | 993 | 981 | -12 |
| `tests/unit/test-factory-config.py` | 1291 | 1042 | -249 |
| `tests/unit/test-feature-record.py` | 1831 | 1834 | +3 |
| `tests/unit/test-feature-schema-build-entry.py` | 267 | 268 | +1 |
| `tests/unit/test-fleet-product-config.py` | 286 | 271 | -15 |
| `tests/unit/test-gate-policy.py` | 125 | 104 | -21 |
| `tests/unit/test-gh-board.py` | 484 | 410 | -74 |
| `tests/unit/test-harness-config.py` | new | 266 | +266 |
| `tests/unit/test-prune-run-evidence.py` | 304 | 304 | +0 |
| `tests/unit/test-wayfind.py` | 156 | 155 | -1 |

- Gate A, pre-existing affected files: -583
- Gate B, new files enumerated below: +1575
- Reported total, both populations: +992
<!-- measured:end -->

## New coverage

| File | Lines | Covers |
|---|---|---|
| `tests/harness_config_support.py` | 68 | D-06, SC-04: the one fixture builder |
| `tests/unit/test-harness-config.py` | 266 | D-01, D-02, D-03, SC-01: schema defaults, refusals and sources |
| `tests/integration/test-harness-config-fixtures.py` | 424 | D-06, SC-04: builder-reach census and budget-fixture freshness |
| `tests/integration/test-harness-config-readers.py` | 327 | D-01, D-04, SC-02, SC-10: every reader and gate refuses; check-state reports |
| `tests/integration/test-harness-config-upgrade.py` | 132 | D-05, SC-03: config-only 2-to-3 upgrade |
| `tests/fixtures/harness-config-budgets.json` | 44 | D-06, D-08, SC-04: builder-generated TypeScript budget configs |
| `.harness/harness/features/FEAT-2297-harness-json-schema/notes/check-config-reduction.py` | 314 | D-06, SC-05: this release-evidence checker |

## Dispositions

| Row | Class | Disposition | Task · replacement coverage | Material deleted or retained, and why |
|---|---|---|---|---|
| `tests/unit/test-factory-config.py:136-139` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-factory-config.py` at `config_doc` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-factory-config.py:300-309` | REMOVABLE | DELETED | T-04 · `tests/integration/test-harness-config-readers.py::RemoteProductConfig` + `tests/unit/test-harness-config.py::Refusals` | Deleted: duplicated remote-config shape/error assertions. |
| `tests/unit/test-factory-config.py:416-509` | REMOVABLE | DELETED | T-04 · `tests/integration/test-harness-config-readers.py::RemoteProductConfig` + `tests/unit/test-harness-config.py::Refusals` | Deleted: duplicated remote-config shape/error assertions. |
| `tests/unit/test-factory-config.py:656-717` | REMOVABLE | DELETED | T-04 · `tests/integration/test-harness-config-readers.py::RemoteProductConfig` + `tests/unit/test-harness-config.py::Refusals` | Deleted: duplicated remote-config shape/error assertions. |
| `tests/unit/test-factory-config.py:719-732` | REMOVABLE | RETAINED | T-04 · `tests/unit/test-factory-config.py` factory board-required operation check | Signed partial retention (research-config-contract.md:73): a missing board defaults to null, but factory `board_for` still refuses; the reader-specific schema-message assertions were deleted. |
| `tests/unit/test-factory-config.py:782-796` | REMOVABLE | DELETED | T-04 · `tests/integration/test-harness-config-readers.py::RemoteProductConfig` + `tests/unit/test-harness-config.py::Refusals` | Deleted: duplicated remote-config shape/error assertions. |
| `tests/unit/test-factory-config.py:829-878` | REMOVABLE | DELETED | T-04 · `tests/integration/test-harness-config-readers.py::RemoteProductConfig` + `tests/unit/test-harness-config.py::Refusals` | Deleted: duplicated remote-config shape/error assertions. |
| `tests/integration/test-check-state-entry.py:27-56` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-entry.py` at `case_a` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-entry.py:94-95` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-entry.py` at `case_e` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-entry.py:117-118` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-entry.py` at `case_f` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-entry.py:151-152` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-entry.py` at `case_k` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-entry.py:187-188` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-entry.py` at `case_t` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-entry.py:204-233` | REMOVABLE | DELETED | T-06 · `tests/integration/test-harness-config-readers.py::CheckState` | Deleted: duplicate missing-config diagnosis block. |
| `tests/integration/test-check-state-entry.py:252-253` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-entry.py` at `_factory_tree` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-validate-digest.py:1373-1374` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-validate-digest.py` at `_isolated_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-validate-digest.py:3734-3736` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-validate-digest.py` at `write_review_config` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-validate-digest.py:3854-3860` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-validate-digest.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-validate-digest.py:4104-4121` | REMOVABLE | DELETED | T-07 · `tests/integration/test-harness-config-readers.py::Readers` (validate-digest._load_test_kinds, _load_matrix_inputs) + `tests/unit/test-harness-config.py::Refusals` | Deleted: shape/error-constructor duplicates. |
| `tests/integration/test-validate-digest.py:4124-4152` | REMOVABLE | DELETED | T-07 · `tests/integration/test-harness-config-readers.py::Readers` (validate-digest._load_test_kinds, _load_matrix_inputs) + `tests/unit/test-harness-config.py::Refusals` | Deleted: shape/error-constructor duplicates. |
| `tests/integration/test-validate-digest.py:4913-4921` | REMOVABLE | DELETED | T-07 · `tests/integration/test-harness-config-readers.py::Readers` (validate-digest._load_test_kinds, _load_matrix_inputs) + `tests/unit/test-harness-config.py::Refusals` | Deleted: shape/error-constructor duplicates. |
| `tests/integration/test-validate-digest.py:5131-5140` | REMOVABLE | DELETED | T-07 · `tests/integration/test-harness-config-readers.py::Readers` (validate-digest._load_test_kinds, _load_matrix_inputs) + `tests/unit/test-harness-config.py::Refusals` | Deleted: shape/error-constructor duplicates. |
| `tests/integration/test-validate-digest-shadows.py:51-59` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-validate-digest-shadows.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-validate-digest-shadows.py:132-136` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-validate-digest-shadows.py` at `_config` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-validate-digest-shadows.py:365-376` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-validate-digest-shadows.py` at `check: qa: FAIL with a failing suite is accepted` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-open.py:27-30` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-sync-open.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-open.py:324-329` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-sync-open.py` at `_product` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-open.py:725-725` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-sync-open.py` at `main` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-open.py:729-729` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-sync-open.py` at `main` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-open.py:738-739` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-sync-open.py` at `main` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-open.py:1195-1196` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-sync-open.py` at `main` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-open.py:1201-1210` | UPDATE-BEHAVIOR | REWRITTEN | T-05 · `tests/integration/test-gh-sync-open.py::main` check "not_onboarded: no harness.json above -> REFUSED at exit 2" | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/unit/test-gh-board.py:46-49` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-gh-board.py` at `write_harness_json` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-gh-board.py:101-168` | REMOVABLE | DELETED | T-04 · `tests/integration/test-harness-config-readers.py::Readers` (gh_board.load_board) + `tests/integration/test-harness-config-readers.py::Boards` | Deleted: board shape duplicates; null/normalisation cases kept. |
| `tests/integration/test-upgrade-config.py:69-89` | UPDATE-FIXTURE | MIGRATED | T-01 · `tests/integration/test-upgrade-config.py` at `version_two` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-upgrade-config.py:250-254` | UPDATE-FIXTURE | MIGRATED | T-01 · `tests/integration/test-upgrade-config.py` at `check: --check never rewrites team-config.yaml (safe_dump would strip its commen` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-upgrade-config.py:277-279` | UPDATE-FIXTURE | MIGRATED | T-01 · `tests/integration/test-upgrade-config.py` at `check: a new budgets key (orchestrator_context_warn_tokens) propagates from the ` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-upgrade-config.py:290-293` | UPDATE-FIXTURE | MIGRATED | T-01 · `tests/integration/test-upgrade-config.py` at `check: panel_era_start ARRIVES in a schema-2 project through the real merge, at ` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-board-lifecycle.py:57-58` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-board-lifecycle.py` at `write_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-board-lifecycle.py:370-376` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-board-lifecycle.py` at `_served_board_contents_b64` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-board-lifecycle.py:1062-1065` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-board-lifecycle.py` at `_served_widget_b64` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-board-lifecycle.py:1823-1847` | REMOVABLE | DELETED | T-05 · `tests/unit/test-harness-config.py::Refusals` (conditional repo) + `tests/integration/test-harness-config-readers.py::Readers` (board_lifecycle._own_repo) | Deleted: obsolete reader exception/message assertions. |
| `tests/integration/test-board-lifecycle.py:1865-1874` | REMOVABLE | DELETED | T-05 · `tests/unit/test-harness-config.py::Refusals` (conditional repo) + `tests/integration/test-harness-config-readers.py::Readers` (board_lifecycle._own_repo) | Deleted: obsolete reader exception/message assertions. |
| `tests/integration/test-factory-integration.py:508-512` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-factory-integration.py` at `default_product_configs` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-factory-integration.py:1406-1409` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-factory-integration.py` at `check: (I) project_single_select_extend: mutates updateProjectV2Field, never ` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-factory-integration.py:1454-1457` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-factory-integration.py` at `check: (J) board_lifecycle.py provision: performs ZERO mutations against a compl` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-factory-integration.py:1497-1500` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-factory-integration.py` at `check: (K) board_lifecycle.py audit: the finding` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-factory-integration.py:1553-1556` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-factory-integration.py` at `check: (L) board_lifecycle.py audit STATUS: the finding names the feature dir, t` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-factory-integration.py:1603-1606` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-factory-integration.py` at `check: (M) board_lifecycle.py reconcile with NO flags: ZERO mutations reached th` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-records.py:69-80` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-records.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-records.py:56-61` | UPDATE-BEHAVIOR | REWRITTEN | T-06 · `tests/integration/test-check-state-records.py::_inv32_run` installs a valid builder config; missing/malformed era refusal in `tests/integration/test-harness-config-readers.py::CheckState` | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-check-state-records.py:775-791` | REMOVABLE | DELETED | T-06 · `tests/unit/test-harness-config.py::Defaults` (absent era is null) + `tests/unit/test-harness-config.py::Refusals` (malformed date) | Deleted: missing-era and malformed-date reader cases. |
| `tests/integration/test-check-state-records.py:802-808` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-records.py` at `_bug1305_invariant_scaffold` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-records.py:924-925` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-records.py` at `_t06_fixture` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-artifact-accessors.py:100-105` | UPDATE-FIXTURE | MIGRATED | T-01 · `tests/unit/test-artifact-accessors.py` at `JsonContracts.test_harness_json_accepts_explicit_text_source_with_context` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-artifact-accessors.py:395-401` | UPDATE-FIXTURE | MIGRATED | T-01 · `tests/unit/test-artifact-accessors.py` at `WriterContract.test_writer_makes_backup_and_writes_mapping` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-close-gate.py:35-40` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-close-gate.py` at `_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-close-gate.py:220-226` | UPDATE-BEHAVIOR | REWRITTEN | T-05 · `tests/integration/test-gh-close-gate.py` check "duplicate harness.json keys refuse a matching close at exit 2" | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-gh-close-gate.py:240-251` | UPDATE-BEHAVIOR | REWRITTEN | T-05 · `tests/integration/test-gh-close-gate.py` check "no harness.json at all: a matching close is refused at exit 2" | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-check-state-inv26.py:28-37` | UPDATE-FIXTURE | MIGRATED | T-06,T-10 · `tests/integration/test-check-state-inv26.py` at `_inv26_write_config` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-inv26.py:303-314` | REMOVABLE | DELETED | T-06,T-10 · `tests/unit/test-harness-config.py::Refusals` (partial board) | Deleted: board-shape duplicate. |
| `tests/integration/test-check-state-inv26.py:315-323` | UPDATE-BEHAVIOR | REWRITTEN | T-06,T-10 · `tests/integration/test-check-state-inv26.py::case_v` "an unusable board declaration is the config violation, with no config-dependent invariant continuing" | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-check-state-inv26.py:555-556` | UPDATE-FIXTURE | MIGRATED | T-06,T-10 · `tests/integration/test-check-state-inv26.py` at `build` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-inv26.py:651-659` | UPDATE-FIXTURE | MIGRATED | T-06,T-10 · `tests/integration/test-check-state-inv26.py` at `_fleet_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-inv26.py:684-693` | UPDATE-FIXTURE | MIGRATED | T-06,T-10 · `tests/integration/test-check-state-inv26.py` at `_fleet_fake` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/gh_sync_support.py:71-81` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/gh_sync_support.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/gh_sync_support.py:612-626` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/gh_sync_support.py` at `write_harness_json_board` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-feature-record.py:1348-1352` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-feature-record.py` at `ProposeReworkTest.setUp` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-plans.py:44-45,76-77,109-110` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-plans.py` at `case_h` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-plans.py:142-148` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-plans.py` at `build` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-plans.py:175-178,193-196` | UPDATE-BEHAVIOR | REWRITTEN | T-06 · `tests/integration/test-check-state-plans.py::case_l` (l6)/(l7): absent budgets count against 20; a malformed present budget refuses | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-check-state-plans.py:179-180,197-198` | REMOVABLE | DELETED | T-06 · `tests/unit/test-harness-config.py::Refusals` (budget type) | Deleted: boolean budget rejection; feature override parsing kept. |
| `tests/integration/test-check-state-plans.py:229,271,344,360,372` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-plans.py` at `case_n` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-plans.py:407-408` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-plans.py` at `_inv6_feature` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-plans.py:573,624,745` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-plans.py` at `_i34_fixture` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-handoff.py:65-66,190-191` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-handoff.py` at `build` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-handoff.py:213-214` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-handoff.py` at `_feat54_fixture_case` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-feat59.py:42-43` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-feat59.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-feat59.py:867-878` | REMOVABLE | DELETED | T-06 · `tests/unit/test-harness-config.py::Defaults` + `tests/integration/test-harness-config-readers.py::Readers` (plan_merge.check._era) | Deleted: era read/default duplicates. |
| `tests/integration/test-check-state-feat59.py:939-947` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-feat59.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-branch-create-gate.py:151-156` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-branch-create-gate.py` at `_fixture` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-branch-create-gate.py:228-235` | UPDATE-BEHAVIOR | REWRITTEN | T-05 · `tests/integration/test-branch-create-gate.py::run_assertion_6` "duplicate harness.json keys refuse the branch creation at exit 2" | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-branch-create-gate.py:264-285` | UPDATE-BEHAVIOR | REWRITTEN | T-05 · `tests/integration/test-branch-create-gate.py::run_config_faults`: missing/invalid config refuses a governed branch at exit 2 | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-branch-create-gate.py:286-290` | REMOVABLE | DELETED | T-05 · `tests/integration/test-harness-config-readers.py::Gates` | Deleted: AttributeError expectation. |
| `tests/integration/test-post-merge-sweep.py:295-296` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-post-merge-sweep.py` at `_seed_bootstrap_repo` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-post-merge-sweep.py:992-994` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-post-merge-sweep.py` at `_t07_sweep` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-post-merge-sweep.py:1080-1085,1088-1122` | REMOVABLE | DELETED | T-07 · `tests/unit/test-harness-config.py::Refusals.test_nested_duplicate_and_nonfinite_values_are_refused` | Deleted: harness.json duplicate-key slice; feature.json retention branch kept. |
| `tests/integration/test-code-grade-cli.py:52-54` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-code-grade-cli.py` at `make_repo` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-code-grade-cli.py:195-196` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-code-grade-cli.py` at `test_bars_follow_test_kinds` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-code-grade-cli.py:242-249` | REMOVABLE | DELETED | T-07 · `tests/unit/test-harness-config.py::Refusals.test_nested_duplicate_and_nonfinite_values_are_refused` | Deleted: duplicate-key reader assertion. |
| `tests/integration/test-code-grade-cli.py:250-251` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-code-grade-cli.py` at `test_bars_follow_test_kinds` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-merge-gate.py:27-28` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-merge-gate.py` at `fixture` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-merge-gate.py:302-309` | UPDATE-BEHAVIOR | REWRITTEN | T-05 · `tests/integration/test-merge-gate.py` check "duplicate harness.json keys deny the merge with the loader's diagnosis" | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-merge-gate.py:427-428` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-merge-gate.py` at `seed_owner` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-feature-corpus.py:38` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-feature-corpus.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-feature-corpus.py:323-325` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-feature-corpus.py` at `BoardStatus.setUp` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-feature-corpus.py:468` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-feature-corpus.py` at `Discovery.test_layout_evidence_reads_this_checkouts_tree_not_its_disk` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-issue-types.py:157-163` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-issue-types.py` at `build_harness_json` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-backlog-issue-types.py:96-102` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-backlog-issue-types.py` at `build_harness_json` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-factory-issue-types.py:196-201` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-factory-issue-types.py` at `harness_json_b64` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-skill-weight.py:40-45` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-check-skill-weight.py` at `_tree` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-skill-weight.py:80-87` | UPDATE-BEHAVIOR | REWRITTEN | T-07 · `tests/integration/test-check-skill-weight.py::WeightTests.test_absent_budget_uses_the_documented_defaults` + `test_malformed_present_budget_refuses` | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/test-check-skill-weight.py:88-92` | REMOVABLE | DELETED | T-07 · `tests/integration/test-check-skill-weight.py::WeightTests.test_malformed_present_budget_refuses` + `tests/integration/test-harness-config-readers.py::Readers` (check-skill-weight._budget) | Deleted: duplicate-key reader assertion. |
| `tests/unit/test-gate-policy.py:24,62` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-gate-policy.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-gate-policy.py:65-68` | UPDATE-BEHAVIOR | REWRITTEN | T-04 · `tests/unit/test-gate-policy.py::check_policy_loading`: an obsolete gate key is a config error | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/unit/test-gate-policy.py:69-93` | REMOVABLE | DELETED | T-04 · `tests/unit/test-harness-config.py::Refusals` + `tests/integration/test-harness-config-readers.py::Readers` (gate_policy.load_policy) | Deleted: shape/missing-key/read duplicates; review evaluation kept. |
| `tests/unit/test-fleet-product-config.py:110-140` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-fleet-product-config.py` at `check: (a) two declared repos, both succeed -> every entry ok, ok count 2, unrea` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-fleet-product-config.py:181-193` | REMOVABLE | DELETED | T-04 · `tests/integration/test-harness-config-readers.py::RemoteProductConfig` | Deleted: raw-JSON reader duplicate; report ordering kept. |
| `tests/unit/test-wayfind.py:94-97` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-wayfind.py` at `case_1_wayfind_directory_probe` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-feature-schema-build-entry.py:255-257` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-feature-schema-build-entry.py` at `check: the shared binding resolver exists` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-code-grade.py:471-479` | REMOVABLE | DELETED | T-04 · `tests/unit/test-harness-config.py::Refusals` + `tests/integration/test-harness-config-readers.py::Readers` (code-grade._load_test_kinds) | Deleted: malformed-kind reader duplicate; grading bars kept. |
| `tests/unit/test-check-state-shipped-ctx.py:71` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-check-state-shipped-ctx.py` at `_tree` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-check-state-inv37-local-binding.py:84-85` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-check-state-inv37-local-binding.py` at `_run` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-check-state-inv35.py:47-49` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-check-state-inv35.py` at `run_checker` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/unit/test-check-state-inv26-routing.py:109-112` | UPDATE-FIXTURE | MIGRATED | T-04 · `tests/unit/test-check-state-inv26-routing.py` at `_run` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-plan-sign-gate.py:54-55` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-plan-sign-gate.py` at `_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-plan-decision-dispositions.py:110-113` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-plan-decision-dispositions.py` at `make_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-plan-decision-dispositions.py:477` | REMOVABLE | DELETED | T-07 · `tests/unit/test-harness-config.py::Defaults` (absent era) + `tests/unit/test-harness-config.py::Refusals` (malformed era) | Deleted: absent/malformed-era reader duplicates; explicit boundaries kept. |
| `tests/integration/test-plan-decision-dispositions.py:483-486` | REMOVABLE | DELETED | T-07 · `tests/unit/test-harness-config.py::Defaults` (absent era) + `tests/unit/test-harness-config.py::Refusals` (malformed era) | Deleted: absent/malformed-era reader duplicates; explicit boundaries kept. |
| `tests/integration/test-hooks-install.py:146-147` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-hooks-install.py` at `_bootstrap_origin` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-start-task.py:389-405` | REMOVABLE | DELETED | T-05 · `tests/unit/test-harness-config.py::Refusals` (partial board) | Deleted: incomplete-board reader-message duplicate. |
| `tests/integration/test-check-state-worktrees.py:62` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_u` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:72` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_u` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:98` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_u` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:147` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_u` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:192-193` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `build` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:381` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:392` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:407` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:443` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:457` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:472` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:518` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:537` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `case_inv29` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-worktrees.py:664-665` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-worktrees.py` at `_inv31_fixture` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-run-unit-tests-kinds.py:103-121` | REMOVABLE | RETAINED | T-07 · `tests/integration/test-run-unit-tests-kinds.py` check "claiming a live probe in the automated matrix is loud" | Signed partial retention (research-config-contract.md:91): mandatory live-probe registration is roster semantics, not schema; the empty-detect shape assertion was deleted. |
| `tests/integration/test-lead-start-return.py:123-124` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-lead-start-return.py` at `make_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-layout-migration.py:358-359` | UPDATE-FIXTURE | MIGRATED | T-07 · `tests/integration/test-layout-migration.py` at `_parity` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-gh-sync-abandon.py:255` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-gh-sync-abandon.py` at `main` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-table.py:85-88` | UPDATE-FIXTURE | MIGRATED | T-06,T-10 · `tests/integration/test-check-state-table.py` at `two_feature_tree` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-shipped.py:301-303` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-shipped.py` at `RetiredMirrorChecks.test_no_milestone_or_pull_request_check_runs_for_a_shipped_f` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-inv51.py:70-71` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-inv51.py` at `tree` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-inv37-offline.py:54-55` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-inv37-offline.py` at `_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-check-state-inv37-offline.py:61-64` | UPDATE-FIXTURE | MIGRATED | T-06 · `tests/integration/test-check-state-inv37-offline.py` at `_root` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-board-station.py:55-58` | UPDATE-FIXTURE | MIGRATED | T-05 · `tests/integration/test-board-station.py` at `write_harness_json` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/test-board-station.py:175-183` | REMOVABLE | DELETED | T-05 · `tests/unit/test-harness-config.py::Defaults` (absent board is null) + `tests/integration/test-board-station.py` check "an explicitly null board still exits 0" | Deleted: missing-board-as-error assertion. |
| `tests/manual/probe-issue-types.py:57-64` | UPDATE-BEHAVIOR | REWRITTEN | T-03 · `tests/manual/probe-issue-types.py::_load_config` refuses at exit 2 + `tests/integration/test-harness-config-readers.py::Readers` (probe-issue-types._load_config) | Now asserts refusal with diagnosis (or the signed absent-key default); no fail-open path remains. |
| `tests/integration/f58_sparse_fixture.py:82` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/f58_sparse_fixture.py` at `_owner_files` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/check_state_support.py:88-96` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/check_state_support.py` at `<module>` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/check_state_support.py:153-156` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/check_state_support.py` at `make_fixture` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/gh_sync_support.py:72-81` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/gh_sync_support.py` at `stage` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/gh_sync_support.py:612-626` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/gh_sync_support.py` at `write_harness_json_board` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |
| `tests/integration/gh_sync_support.py:737-760` | UPDATE-FIXTURE | MIGRATED | T-02 · `tests/integration/gh_sync_support.py` at `stage_fleet` | Valid config now built by `build_config`/`write_config`; census reach proven (0 bypasses). |

## Files

| File | Assessment |
|---|---|
| `tests/integration/canonical-reader-classification.json` | UNAFFECTED only — its contracts are not config-shape checks: board-station.py::main reader collapses onto loader; board_lifecycle.py::_own_repo reader collapses onto loader; branch-create-gate.py::_github_config reader collapses onto loader; check-skill-weight.py::_budget reader collapses onto loader; code-grade.py::_lo. |
| `tests/integration/check_state_support.py` | 2 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/f58_sparse_fixture.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/gh_sync_support.py` | 5 row(s) disposed above; 4 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-board-lifecycle.py` | 5 row(s) disposed above; 3 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-board-station.py` | 2 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-branch-create-gate.py` | 4 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-domain-grant.py` | UNAFFECTED only — its contracts are not config-shape checks: Resolves harness config pathname to its sole granted agent. |
| `tests/integration/test-check-expertise.py` | UNAFFECTED only — its contracts are not config-shape checks: harness.json is an expertise advisory token, not parsed configuration. |
| `tests/integration/test-check-instruction-paths.py` | UNAFFECTED only — its contracts are not config-shape checks: Harness config paths are instruction-linter examples, never parsed configuration. |
| `tests/integration/test-check-plan-routes.py` | UNAFFECTED only — its contracts are not config-shape checks: Plan task names harness config as a granted file; no config is written; Task and station fixtures reuse harness config pathname as routing input; Granted and annotated config path tests exercise domain routing; Static reader classifications name load_harness_j. |
| `tests/integration/test-check-skill-weight.py` | 3 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-entry.py` | 7 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-feat59.py` | 3 row(s) disposed above; 4 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-handoff.py` | 2 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-inv26.py` | 6 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-inv37-offline.py` | 2 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-inv51.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-plans.py` | 7 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-records.py` | 5 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-shipped.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-table.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-check-state-worktrees.py` | 14 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-checker-structure-locks.py` | UNAFFECTED only — its contracts are not config-shape checks: Static mutant detects module-scope config reads; Static invariant mutants prohibit reparsing runner-shared config and feature records. |
| `tests/integration/test-code-grade-cli.py` | 4 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-factory-integration.py` | 6 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-factory-issue-types.py` | 1 row(s) disposed above; 3 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-feature-corpus.py` | 3 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-gh-backlog-issue-types.py` | 1 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-gh-close-gate.py` | 3 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-gh-issue-types.py` | 1 row(s) disposed above; 3 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-gh-sync-abandon.py` | 1 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-gh-sync-open.py` | 7 row(s) disposed above; 6 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-gh-sync-start-task.py` | 1 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-harness-yaml.py` | UNAFFECTED only — its contracts are not config-shape checks: Manifest domain fixture contains harness.json as an ordinary path; schema_version 2 is generic YAML scalar data, not a harness.json fixture. |
| `tests/integration/test-hooks-install.py` | 1 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-layout-migration.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-lead-start-return.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-merge-gate.py` | 3 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-onboarding-split.py` | UNAFFECTED only — its contracts are not config-shape checks: Prose marker ordering describes onboarding branch, fleet registration, and central artifact placement. |
| `tests/integration/test-plan-decision-dispositions.py` | 3 row(s) disposed above; 3 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-plan-sign-gate.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-post-merge-sweep.py` | 3 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-run-unit-tests-kinds.py` | 1 row(s) disposed above; 3 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-upgrade-config.py` | 4 row(s) disposed above; 4 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-validate-digest-shadows.py` | 3 row(s) disposed above; 6 UNAFFECTED row(s) keep non-config contracts. |
| `tests/integration/test-validate-digest.py` | 7 row(s) disposed above; 7 UNAFFECTED row(s) keep non-config contracts. |
| `tests/manual/probe-issue-types.py` | 1 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/omp-hooks.test.ts` | UNAFFECTED only — its contracts are not config-shape checks: Context budget fixture, configured value, and absent-key fallback use documented TypeScript exception; Advisory stays silent exactly at configured/default token threshold; Plan budget fixture, configured value, missing config fallback, and shipped default reta. |
| `tests/unit/test-artifact-accessors.py` | 2 row(s) disposed above; 4 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-check-state-inv26-routing.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-check-state-inv35.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-check-state-inv37-local-binding.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-check-state-shipped-ctx.py` | 1 row(s) disposed above; 0 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-code-grade.py` | 1 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-config-shape-matrix.py` | UNAFFECTED only — its contracts are not config-shape checks: Pins specific matrix predicates and decision provenance, not container shapes or enum validity; Decision headings and verification-skill prose remain independent policy documentation checks. |
| `tests/unit/test-factory-claim.py` | UNAFFECTED only — its contracts are not config-shape checks: Test-side board carriers are stripped from fleet data and supplied through product_config stub; Stub returns an already-loaded product mapping; it neither serializes nor validates harness.json. |
| `tests/unit/test-factory-config.py` | 7 row(s) disposed above; 8 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-feature-record.py` | 1 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-feature-schema-build-entry.py` | 1 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-fleet-product-config.py` | 2 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-gate-policy.py` | 3 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-gh-board.py` | 2 row(s) disposed above; 2 UNAFFECTED row(s) keep non-config contracts. |
| `tests/unit/test-no-distribution.py` | UNAFFECTED only — its contracts are not config-shape checks: Board ownership commentary accompanies fleet.yaml assertions, not harness.json validation; Commentary locates per-repository board assertions elsewhere. |
| `tests/unit/test-orchestrator-playbook.py` | UNAFFECTED only — its contracts are not config-shape checks: Prose names configurable context threshold without hardcoding its numeric value. |
| `tests/unit/test-suite-layout.py` | UNAFFECTED only — its contracts are not config-shape checks: Repository/template detect parity and manual-test discovery policy; Selects active and locally_run discovery kinds; Certifies discovery patterns and checks tracked-file coverage, including positive controls. |
| `tests/unit/test-wayfind.py` | 1 row(s) disposed above; 1 UNAFFECTED row(s) keep non-config contracts. |

## Builder and caller census

`python3 tests/integration/test-harness-config-fixtures.py` (complete tracked population, `git ls-files tests`):
0 findings, negative controls detected (receipts `t10-fixtures-green.txt`, `t10-census-gaps-red.txt`).
T-10 widened the census after its own disposition evidence exposed two gaps: a helper that raw-writes an
expression of its parameter (`content if … else json.dumps(content)`), and a helper that writes its own literal to
a path parameter. Both are now negative controls, and writer calls resolve per module, so an unrelated
`stream.write` is no longer a writer. The three raw fixtures the gaps hid (`test-merge-gate.py::seed_owner`,
`test-validate-digest.py::write_review_config`, `test-artifact-accessors.py::WriterContract`) and three raw configs
merged from main after the inventory (`test-omp-native-gate-runtime.py::make_root`,
`test-prune-run-evidence.py::blocked_feature`, `test-upgrade-config.py::project`) now build through the builder.

## Canonical reader coverage

`CLAUDE_PROJECT_DIR=<checkout> python3 .agents/skills/harness/bin/check-plan-routes.py --canonical-reader-audit`:
`0 unresolved reader site(s) across 101 Python file(s)`, exit 0.

## Fleet

Shipped membership is asserted by the checker at the base and review refs: `mruangutai/harness-factory-smoke` is
absent at review, `mruangutai/kaya` is unchanged, and the parsed review document equals the base with only the smoke
entry removed (operator ruling 2026-11-22, T-03).

Remaining-fleet validation, run from this checkout, `factory_config.product_config_report(load_fleet(".harness/factory/fleet.yaml"))`
(remote default-branch read through the one loader):

```
{"repo": "mruangutai/kaya", "ref": "main", "path": ".harness/harness.json", "ok": false, "detail": "product config invalid: mruangutai/kaya@main:.harness/harness.json \u2014 repair mruangutai/kaya's .harness/harness.json at main: mruangutai/kaya@main:.harness/harness.json: schema_version: 2 is the previous harness.json shape; run upgrade-config.py <project-root> to migrate it to 3 [const]"}
exit=0
```

The refusal is the expected, honest state before T-09: Kaya's main still carries version 2. It is reported, not suppressed;
it does not waive SC-08's remote-main landing.

## Local matrix evidence

Candidate `6f493a25` (after T-01 to T-08, this checker, the simplify pass, and both merges of
`origin/main` up to `837e7096`). Full logs: `notes/receipts/t10-matrix-unit.txt` and
`notes/receipts/t10-matrix-integration.txt`.

| Kind | Command | Result |
|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0: 65 files pass |
| integration | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 1: 94 of 95 files pass; `test-corpus-real-owner.py` fails |
| typecheck | `bun run typecheck` | exit 0 |

**The one integration failure is attributed, not waived.** `test-corpus-real-owner.py` runs
check-state against this repository's *owner* checkout, the main checkout at `main`. Until
this feature merges, that checkout's `.harness/harness.json` is `schema_version` 2, which the
candidate's loader refuses by design (DEC-256): `VIOLATION .harness/harness.json is invalid: …
schema_version: 2 is the previous harness.json shape; run upgrade-config.py`. The candidate's own
`.harness/harness.json` is version 3. In CI the owner checkout is the PR checkout itself, so the
case reads a version-3 file there; PR CI is the confirming run. No other unit or integration file
fails.

**Disposition (advisor ruling #6, E-OWNER, under the operator's delegation).** PR CI's integration
run, which includes this file against a version-3 owner checkout, is the authoritative evidence for
this case, and ship requires it green. The local red is recorded as pre-merge environment state,
not waived. Pre-upgrading the shared main checkout was rejected: other live sessions depend on it,
and an upgrade is triggered per project, never as a side effect of another run.

**Discharged.** PR #2395 CI run
[45080316265](https://github.com/mruangutai/harness/actions/runs/45080316265) ended `success`
at head `be1a0f99`, which is review_sha `15d67484` plus a ledger-only re-pin commit. Every job
passed, including `PASS test-corpus-real-owner.py` (shard 4) and `PASS test-harness-config-readers.py`
(shard 1); no file failed. The earlier run, 45079815601, was red on two defects that local checks
missed: T-10 at 51 DEC-182 items, and the readers test's module loader under CI's Python. Both are
fixed in `15d67484`. Advisor ruling #7 (under the operator's delegation) disposed this post-validation
delta without another validator run, conditional on this green run. That discharges
`fix-c1-validator`'s sole must-fix, so its FAIL verdict is not the record's last word.

Earlier evidence in this run was superseded and repeated. One integration run was invalidated
(`MUTATED harness_config.py`) by an edit made during it. Later runs found three real defects,
each fixed and re-proven: DEC-256's index ruling over the 30-word cap; the schema's `test_kinds`
default missing `classifies_tests` after the merge; and FEAT-2337's receipt fixture, which was
invalid under version 3.
