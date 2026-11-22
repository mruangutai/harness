# Test inventory — harness.json schema (#2297) — 2026-11-22

Read-only classification of the 67 test files that mention harness.json, by three scouts at main c1724230.

Classes: REMOVABLE (per-reader shape or malformed-config checks the schema and loader cover once), UPDATE-FIXTURE (configs invalid under the new rules), UPDATE-BEHAVIOR (asserts fail-open behavior that becomes fail-closed), UNAFFECTED.

Line counts are the scouts' approximations.


## Group A (TestScanA)

Approximate counts cover the listed assertion/fixture groups, not entire surrounding tests. Overlapping fixture and behavior rows describe different work; totals are planning estimates, not deletion sizes. Missing-version fixtures are flagged as requested, even though the settled missing-key/default policy needs to document schema_version explicitly. Intentionally invalid inputs in removable tests are not separately counted as fixture migration work.

### Reader inventory

These are inventory records, not executable assertions. All 21 describe sites whose configuration decoding/validation converges on the one loader; retain inventory coverage. `product_config` and migration `load_json` currently name “documented source route” rather than the loader.

 tests/integration/canonical-reader-classification.json:71-83 | UNAFFECTED | board-station.py::main reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:84-96 | UNAFFECTED | board_lifecycle.py::_own_repo reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:150-162 | UNAFFECTED | branch-create-gate.py::_github_config reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:462-474 | UNAFFECTED | check-skill-weight.py::_budget reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:529-541 | UNAFFECTED | code-grade.py::_load_test_kinds reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:740-752 | UNAFFECTED | factory_config.py::product_config remote reader; source-route metadata must name loader | 13
 tests/integration/canonical-reader-classification.json:963-975 | UNAFFECTED | feature-record.py::_budgets_for reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:1070-1082 | UNAFFECTED | gate_policy.py::_load_config reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:1083-1095 | UNAFFECTED | gh-close-gate.py module reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:1295-1307 | UNAFFECTED | gh_board.py::load_board reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:1482-1494 | UNAFFECTED | layout_migration.py::_declared_segments reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:1495-1507 | UNAFFECTED | merge-gate.py::_github_config already uses loader; caller must stop swallowing errors | 13
 tests/integration/canonical-reader-classification.json:1729-1741 | UNAFFECTED | plan_merge/check.py::_era already uses loader | 13
 tests/integration/canonical-reader-classification.json:1768-1780 | UNAFFECTED | post-merge-sweep.py::_read_build_receipt reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:1807-1819 | UNAFFECTED | upgrade-config.py::load_json migration reader; source-route metadata must name loader | 13
 tests/integration/canonical-reader-classification.json:1848-1860 | UNAFFECTED | validate-digest.py::_load_test_kinds reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:1952-1964 | UNAFFECTED | validate-digest.py::_load_matrix_inputs already uses loader | 13
 tests/integration/canonical-reader-classification.json:1978-1990 | UNAFFECTED | wayfind.py::cfg reader collapses onto loader | 13
 tests/integration/canonical-reader-classification.json:2176-2188 | UNAFFECTED | check_state/ctx.py::Ctx._load_config already uses loader | 13
 tests/integration/canonical-reader-classification.json:2283-2295 | UNAFFECTED | feature_schema.py::_owner_mirror_binding already uses loader | 13
 tests/integration/canonical-reader-classification.json:2296-2308 | UNAFFECTED | gh-sync.py::_unbound_project_config already uses loader | 13

### Factory configuration

 tests/unit/test-factory-config.py:136-139 | UPDATE-FIXTURE | Remote document helper omits schema_version 3 | 4
 tests/unit/test-factory-config.py:300-309 | REMOVABLE | Board number boolean rejection duplicates configuration validation | 10
 tests/unit/test-factory-config.py:312-321 | UNAFFECTED | Numeric-string board number normalization is domain behavior, not specified schema tightening | 10
 tests/unit/test-factory-config.py:401-414 | UNAFFECTED | Valid board normalization preserves identity and converts stations to tuple | 14
 tests/unit/test-factory-config.py:416-509 | REMOVABLE | Missing, renamed, reordered, mapping, five-station and seventh-station declarations duplicate schema rules | 94
 tests/unit/test-factory-config.py:656-717 | REMOVABLE | Eight malformed remote board shapes duplicate load_board and schema checks | 62
 tests/unit/test-factory-config.py:719-732 | REMOVABLE | Missing github/board reader-specific refusal conflicts with centralized missing-key defaults | 14
 tests/unit/test-factory-config.py:734-766 | UNAFFECTED | Board resolution reads each repository’s own remote declaration | 33
 tests/unit/test-factory-config.py:768-780 | UNAFFECTED | Canonical loader accepts remote text with retained context | 13
 tests/unit/test-factory-config.py:782-796 | REMOVABLE | Per-reader non-finite remote JSON rejection duplicates canonical strict loader | 15
 tests/unit/test-factory-config.py:799-827 | UNAFFECTED | Remote transport failure preserves repository, path and branch context | 29
 tests/unit/test-factory-config.py:829-878 | REMOVABLE | Invalid JSON and nonmapping remote documents duplicate canonical loader checks | 50
 tests/unit/test-factory-config.py:880-970 | UNAFFECTED | Remote authority, no checkout fallback, success memoization and failure recovery remain required | 91
 tests/unit/test-factory-config.py:972-1006 | UNAFFECTED | Board station derivation and unknown station/repository refusal are domain behavior | 35
 tests/unit/test-factory-config.py:341-365 | UNAFFECTED | Fleet rejection mentions harness.json only as destination for relocated board configuration | 25

Other fleet YAML, station-table, CLI and workspace tests remain unaffected; they do not validate harness.json.

### Matrix routing policy

 tests/unit/test-config-shape-matrix.py:35-114 | UNAFFECTED | Pins specific matrix predicates and decision provenance, not container shapes or enum validity | 80
 tests/unit/test-config-shape-matrix.py:117-147 | UNAFFECTED | Decision headings and verification-skill prose remain independent policy documentation checks | 31

Despite its name, this file is not removable: the schema’s allowed values do not require these particular routing rows or provenance signatures.

### Check-state entry

 tests/integration/test-check-state-entry.py:27-56 | UPDATE-FIXTURE | Cases consume versionless shared HARNESS_JSON_SYNC_ON/OFF fixtures | 30
 tests/integration/test-check-state-entry.py:94-95 | UPDATE-FIXTURE | Validator-run fixture writes versionless shared config | 2
 tests/integration/test-check-state-entry.py:117-118 | UPDATE-FIXTURE | Malformed feature-record case writes versionless shared config | 2
 tests/integration/test-check-state-entry.py:151-152 | UPDATE-FIXTURE | Cost-block cases write versionless shared config | 2
 tests/integration/test-check-state-entry.py:187-188 | UPDATE-FIXTURE | Runs-directory crash fixture writes empty configuration without schema_version 3 | 2
 tests/integration/test-check-state-entry.py:204-233 | REMOVABLE | Reader-specific missing harness.json diagnosis duplicates centralized loader failure handling | 30
 tests/integration/test-check-state-entry.py:252-253 | UPDATE-FIXTURE | Factory invariant fixture writes versionless shared config | 2

The shared constants are defined at tests/integration/check_state_support.py:88-96. Assertions about INV-6, INV-21, costs, filesystem crash shapes and factory claims remain unaffected after fixture migration.

### Validate-digest, configuration-related parts only

 tests/integration/test-validate-digest.py:1373-1374 | UPDATE-FIXTURE | Isolated hook root writes review policy without schema_version 3 | 2
 tests/integration/test-validate-digest.py:3734-3736 | UPDATE-FIXTURE | write_review_config emits versionless policy documents for review tests | 3
 tests/integration/test-validate-digest.py:3854-3860 | UPDATE-FIXTURE | Graded checkout policy lacks schema_version 3; unit entry already carries status | 7
 tests/integration/test-validate-digest.py:4104-4121 | REMOVABLE | Reader-specific absent test_kinds refusal conflicts with documented missing-key default | 18
 tests/integration/test-validate-digest.py:4124-4152 | REMOVABLE | Missing detect reaches grader and requires TestKindsError; centralized validation replaces this path | 29
 tests/integration/test-validate-digest.py:4381-4389 | UNAFFECTED | Repository builder writes shared graded-checkout fixture; update its definition rather than every caller | 9
 tests/integration/test-validate-digest.py:4910-4912 | UNAFFECTED | Advisory review policy accepts the guarded digest | 3
 tests/integration/test-validate-digest.py:4913-4921 | REMOVABLE | Missing gates must raise ValueError naming gates; missing-key defaults supersede reader check | 9
 tests/integration/test-validate-digest.py:5131-5140 | REMOVABLE | Validator-specific duplicate harness.json key rejection duplicates strict loader | 10
 tests/integration/test-validate-digest.py:1784-1825 | UNAFFECTED | RUN_UNIT_TESTS_BIN wires independent QA reruns, not configuration validation | 42
 tests/integration/test-validate-digest.py:1828-1833 | UNAFFECTED | Missing runner fails open; no harness.json load failure is involved | 6
 tests/integration/test-validate-digest.py:1906-1920 | UNAFFECTED | Empty claimed kind list uses runner’s default test set | 15
 tests/integration/test-validate-digest.py:1923-1977 | UNAFFECTED | Runner spawn errors/timeouts fail open independently of config loading | 55
 tests/integration/test-validate-digest.py:63-63 | UNAFFECTED | test_kinds_written is a digest field, not harness.json configuration | 1

No `_GRADE_PREFIX` identifier exists in this checkout: both the requested search and an alternate GRADE/grade_prefix search were performed. No additional budgets/test_matrix configuration sections were found in this file. RUN_UNIT_TESTS fail-open assertions must not be swept into the configuration fail-closed change.

### Validate-digest shadows

 tests/integration/test-validate-digest-shadows.py:51-59 | UPDATE-FIXTURE | Shared checkout policy lacks schema_version 3; both test kinds already carry status | 9
 tests/integration/test-validate-digest-shadows.py:132-136 | UPDATE-FIXTURE | Standalone review config lacks schema_version 3 | 5
 tests/integration/test-validate-digest-shadows.py:179-184 | UNAFFECTED | Whitespace change under .harness is ignored by dirty-tree review scope | 6
 tests/integration/test-validate-digest-shadows.py:195-220 | UNAFFECTED | QA digest states and claims are cross-checked against valid configured kinds | 26
 tests/integration/test-validate-digest-shadows.py:292-292 | UNAFFECTED | harness.json is an inspection citation path, not configuration validation | 1
 tests/integration/test-validate-digest-shadows.py:324-324 | UNAFFECTED | Grade-two checkout reuses shared policy fixture | 1
 tests/integration/test-validate-digest-shadows.py:365-376 | UPDATE-FIXTURE | Synthetic service/widget change-type matrix rows require supported enum values; inherited version also missing | 12
 tests/integration/test-validate-digest-shadows.py:394-418 | UNAFFECTED | Matrix floor satisfaction, exclusions and unstarted task handling are semantic behavior | 25
 tests/integration/test-validate-digest-shadows.py:450-482 | UNAFFECTED | Empty-floor suite gating remains semantic; unknown change_type belongs to plan, not configuration | 33

The synthetic rows must be migrated together with their plan consumers (service/widget in `_STILL_GATED` and empty-floor cases), preserving both excluded-kind and active-null-command scenarios. This is fixture migration, not evidence that those semantic tests are removable.

### GitHub sync open

 tests/integration/test-gh-sync-open.py:27-30 | UPDATE-FIXTURE | Imported stage/stage_fleet helpers emit versionless local and remote configurations | 4
 tests/integration/test-gh-sync-open.py:324-329 | UPDATE-FIXTURE | Remote _product helper omits schema_version 3 | 6
 tests/integration/test-gh-sync-open.py:332-366 | UNAFFECTED | Remote unavailability, repository mismatch, sync-off and undeclared binding refuse before mutations | 35
 tests/integration/test-gh-sync-open.py:721-723 | UNAFFECTED | Missing gh binary is environmental skip, not config-load fail-open | 3
 tests/integration/test-gh-sync-open.py:725-725 | UPDATE-FIXTURE | Disabled-sync configuration lacks schema_version 3 | 1
 tests/integration/test-gh-sync-open.py:726-727 | UNAFFECTED | Explicit valid github.sync false still skips synchronization | 2
 tests/integration/test-gh-sync-open.py:729-729 | UPDATE-FIXTURE | Enabled-sync configuration lacks schema_version 3 | 1
 tests/integration/test-gh-sync-open.py:730-731 | UNAFFECTED | Unpinned repository skips synchronization; absent optional key is not malformed configuration | 2
 tests/integration/test-gh-sync-open.py:738-739 | UPDATE-FIXTURE | Main open fixture lacks schema_version 3 | 2
 tests/integration/test-gh-sync-open.py:1195-1196 | UPDATE-FIXTURE | Depth-walk configuration lacks schema_version 3 | 2
 tests/integration/test-gh-sync-open.py:1197-1199 | UNAFFECTED | Root discovery works at migrated feature directory depth | 3
 tests/integration/test-gh-sync-open.py:1201-1210 | UPDATE-BEHAVIOR | Missing harness.json currently skips at exit zero instead of failing closed | 10
 tests/integration/test-gh-sync-open.py:1295-1315 | UNAFFECTED | Removed closes command test uses onboarded fixture to reach dispatch | 21

Shared fixture writers are tests/integration/gh_sync_support.py:72-81, 613-626, 737-754; stage_fleet’s remote product also needs schema_version 3. The feature.json corruption tests around lines 1040-1119 are unaffected: they do not read harness.json.

### GitHub board

 tests/unit/test-gh-board.py:46-49 | UPDATE-FIXTURE | Shared local configuration writer emits schema_version 1 | 4
 tests/unit/test-gh-board.py:96-99 | UNAFFECTED | Explicit null board means no configured board | 4
 tests/unit/test-gh-board.py:101-168 | REMOVABLE | Eight missing-key/wrong-type/incomplete-board cases duplicate centralized configuration validation | 68
 tests/unit/test-gh-board.py:170-175 | UNAFFECTED | Digit-string board number normalizes to integer; change does not settle numeric representation | 6

Remaining station derivation, GraphQL board reads and writes are unaffected. Do not delete the whole 484-line file.

### Upgrade configuration

 tests/integration/test-upgrade-config.py:69-89 | UPDATE-FIXTURE | Shared project/template fixtures use schema versions 1 and 2 | 21
 tests/integration/test-upgrade-config.py:132-140 | UNAFFECTED | Unrelated RuntimeError escapes loader boundary instead of becoming an input-error diagnostic | 9
 tests/integration/test-upgrade-config.py:250-254 | UPDATE-FIXTURE | Budget merge inputs use schema versions 1 and 2 | 5
 tests/integration/test-upgrade-config.py:255-263 | UNAFFECTED | Generic merge propagates new budget leaf at template’s actual value | 9
 tests/integration/test-upgrade-config.py:277-279 | UPDATE-FIXTURE | Era-gap merge inputs use schema versions 1 and 2 | 3
 tests/integration/test-upgrade-config.py:280-288 | UNAFFECTED | Merge adds missing panel era key with template null value | 9
 tests/integration/test-upgrade-config.py:290-293 | UPDATE-FIXTURE | Existing-era merge inputs use schema versions 1 and 2 | 4
 tests/integration/test-upgrade-config.py:294-300 | UNAFFECTED | Project’s existing era boundary survives template merge | 7

YAML manifest tests are unaffected after migrating shared JSON fixtures. These are not version-rejection tests: old versions are setup for merge/YAML assertions, so UPDATE-FIXTURE, not wholesale deletion.

### Board lifecycle

 tests/integration/test-board-lifecycle.py:57-58 | UPDATE-FIXTURE | Shared root writer emits schema_version 1 | 2
 tests/integration/test-board-lifecycle.py:90-91 | UNAFFECTED | Fixture copies configured repository pin into feature receipt | 2
 tests/integration/test-board-lifecycle.py:370-376 | UPDATE-FIXTURE | Served-board remote fixture emits schema_version 1 | 7
 tests/integration/test-board-lifecycle.py:1062-1065 | UPDATE-FIXTURE | Served-widget remote fixture emits schema_version 1 | 4
 tests/integration/test-board-lifecycle.py:1074-1100 | UNAFFECTED | Label ownership requires repository-bound, resolver-proven configuration; failures remain non-writable residuals | 27
 tests/integration/test-board-lifecycle.py:1823-1847 | REMOVABLE | Missing github.repo reader-specific exception type/message tests duplicate centralized missing-key handling | 25
 tests/integration/test-board-lifecycle.py:1850-1863 | UNAFFECTED | Explicit null board returns empty findings and preserves CLI no-board message | 14
 tests/integration/test-board-lifecycle.py:1865-1874 | REMOVABLE | Empty github.repo reader-specific refusal duplicates invalid configuration validation | 10

The missing-repo fixture’s board remains configured, so its operational precondition may still require refusal after defaults. Preserve that domain precondition separately if needed; the obsolete GhError constructor and per-reader message checks are the removable material.

### Factory integration

 tests/integration/test-factory-integration.py:508-512 | UPDATE-FIXTURE | Default remote product configurations omit schema_version 3 | 5
 tests/integration/test-factory-integration.py:1234-1237 | UNAFFECTED | Two-repository fixtures reuse helper to prove each remote board resolves independently | 4
 tests/integration/test-factory-integration.py:1406-1409 | UPDATE-FIXTURE | Provision subprocess configuration uses schema_version 1 | 4
 tests/integration/test-factory-integration.py:1454-1457 | UPDATE-FIXTURE | Audit REASON subprocess configuration uses schema_version 1 | 4
 tests/integration/test-factory-integration.py:1497-1500 | UPDATE-FIXTURE | Audit STATUS subprocess configuration uses schema_version 1 | 4
 tests/integration/test-factory-integration.py:1553-1556 | UPDATE-FIXTURE | Reconcile subprocess configuration uses schema_version 1 | 4
 tests/integration/test-factory-integration.py:1603-1606 | UPDATE-FIXTURE | Retitle subprocess configuration uses schema_version 1 | 4

All five subprocess behavior groups remain required after fixture migration; they verify dispatch, findings, exit status and no-default-mutations, not config shape. Comments about remote harness.json resolution are incidental.

### Check-state records

 tests/integration/test-check-state-records.py:69-80 | UPDATE-FIXTURE | Era fixture writes schema_version 2 when configured | 12
 tests/integration/test-check-state-records.py:56-61 | UPDATE-BEHAVIOR | Most INV-32 fixtures deliberately omit harness.json and rely on continued grading | 6
 tests/integration/test-check-state-records.py:741-772 | UNAFFECTED | Project-specific boundary and explicit null boundary control actual plan exemption | 32
 tests/integration/test-check-state-records.py:775-791 | REMOVABLE | Missing era key and malformed date have reader-specific violations instead of centralized defaults/validation | 17
 tests/integration/test-check-state-records.py:802-808 | UPDATE-FIXTURE | Run-identity invariant config lacks schema_version 3 | 7
 tests/integration/test-check-state-records.py:924-925 | UPDATE-FIXTURE | Terminal mirror invariant config lacks schema_version 3 | 2

For the no-config INV-32 fixtures, write valid minimal configuration to retain the intended plan tests rather than turning their absence into centralized loader-failure tests. The malformed-era case also asserts continued INV-32 grading; that continuation must not survive fail-closed loading.

### Artifact accessors

 tests/unit/test-artifact-accessors.py:56-62 | UNAFFECTED | Canonical loader rejects non-finite constants; retain this single centralized contract | 7
 tests/unit/test-artifact-accessors.py:100-105 | UPDATE-FIXTURE | Successful remote text fixture uses unknown nested key and omits schema_version 3 | 6
 tests/unit/test-artifact-accessors.py:107-119 | UNAFFECTED | Canonical loader rejects duplicate keys, non-finite constants and nonmapping roots with context | 13
 tests/unit/test-artifact-accessors.py:121-126 | UNAFFECTED | Loader requires exactly one file/text source | 6
 tests/unit/test-artifact-accessors.py:161-165 | UNAFFECTED | Shared strict JSON primitive serves multiple artifact types, not only harness.json | 5
 tests/unit/test-artifact-accessors.py:395-401 | UPDATE-FIXTURE | Backup/writer test writes schema versions 1 and 2; migrate payloads without losing backup assertions | 7

Central accessor tests are the coverage retained once per reader duplicates disappear. Invalid unknown keys inside deliberately malformed JSON are not successful configuration fixtures needing migration: strict decoding should reject them first.

### Totals

| Class | Distinct assigned files | Approximate lines involved |
|---|---:|---:|
| REMOVABLE | 6 | 550 |
| UPDATE-FIXTURE | 11 | 220 |
| UPDATE-BEHAVIOR | 2 | 20 |
| UNAFFECTED | 12 | 1,100 |

No entire assigned file is REMOVABLE. Counts exclude unlisted unrelated portions of large files, include the 273 inventory-record lines, and round overlapping helper/group estimates. No tests, builds or other verification commands were executed.


## Group B (TestScanB)

# Classification

Counts concern the listed configuration-related items, not complete dependent tests. File counts overlap between classes. REMOVABLE malformed fixtures should disappear with their tests, rather than be made schema-valid. Missing optional keys must exercise documented defaults, not be mechanically filled everywhere. The TypeScript exception includes its synthetic fixtures.

## tests/integration/test-gh-close-gate.py
- tests/integration/test-gh-close-gate.py:35-40 | UPDATE-FIXTURE | Shared gate fixture lacks schema_version 3. | ~4
- tests/integration/test-gh-close-gate.py:213-218 | UNAFFECTED | Explicit github.sync false disables close policy. | ~6
- tests/integration/test-gh-close-gate.py:220-226 | UPDATE-BEHAVIOR | Duplicate config keys silently disable close policy. | ~7
- tests/integration/test-gh-close-gate.py:240-251 | UPDATE-BEHAVIOR | Missing config permits issue closes without output. | ~12

## tests/integration/test-check-state-inv26.py
- tests/integration/test-check-state-inv26.py:28-37 | UPDATE-FIXTURE | Board-backed config writer lacks schema_version 3. | ~3
- tests/integration/test-check-state-inv26.py:303-314 | REMOVABLE | Reader-specific missing board stations validation duplicates centralized config validation. | ~12
- tests/integration/test-check-state-inv26.py:315-323 | UPDATE-BEHAVIOR | Invalid board declaration still completes later invariants instead of stopping configuration loading. | ~9
- tests/integration/test-check-state-inv26.py:326-335 | UNAFFECTED | Explicit null board disables board auditing. | ~10
- tests/integration/test-check-state-inv26.py:385-400 | UNAFFECTED | Historical comment explains deleted renamed-board test. | ~16
- tests/integration/test-check-state-inv26.py:555-556 | UPDATE-FIXTURE | Abandoned-feature fixture writes missing-version HARNESS_JSON_SYNC_OFF. | ~2
- tests/integration/test-check-state-inv26.py:651-659 | UPDATE-FIXTURE | Fleet owner config lacks schema_version 3. | ~5
- tests/integration/test-check-state-inv26.py:684-693 | UPDATE-FIXTURE | Fake remote product and broken-product configs lack schema_version 3. | ~4

## tests/integration/gh_sync_support.py
- tests/integration/gh_sync_support.py:71-81 | UPDATE-FIXTURE | stage writes missing-version GitHub config, including explicit null board. | ~3
- tests/integration/gh_sync_support.py:151-163 | UNAFFECTED | Fixture helper reads configured repository to populate feature provenance. | ~13
- tests/integration/gh_sync_support.py:612-626 | UPDATE-FIXTURE | Shared board config writer lacks schema_version 3. | ~7
- tests/integration/gh_sync_support.py:835-859 | UNAFFECTED | Fake GitHub serves caller-supplied remote config payloads; no fixed config shape. | ~25
- tests/integration/gh_sync_support.py:922-928 | UNAFFECTED | Ship fixture commentary describes root resolution, not configuration validation. | ~7

## tests/unit/test-feature-record.py
- tests/unit/test-feature-record.py:971-990 | UNAFFECTED | Empty config file is an outside-feature decision-path sentinel, never loaded as configuration. | ~20
- tests/unit/test-feature-record.py:1348-1352 | UPDATE-FIXTURE | Rework proposal fixture writes budgets without schema_version 3. | ~3
- tests/unit/test-feature-record.py:1370-1392 | UNAFFECTED | Proposal rounds, minutes, cycle cap, and basis derive from valid configured budgets. | ~23

## tests/integration/test-check-state-plans.py
- tests/integration/test-check-state-plans.py:44-45,76-77,109-110 | UPDATE-FIXTURE | Review-SHA fixtures write missing-version shared sync-off config. | ~6
- tests/integration/test-check-state-plans.py:142-148 | UPDATE-FIXTURE | Run-budget fixture constructs missing-version config. | ~4
- tests/integration/test-check-state-plans.py:159-164,173-174,182-192 | UNAFFECTED | Valid configured run budgets and per-feature overrides control informational counting. | ~19
- tests/integration/test-check-state-plans.py:175-178,193-196 | UPDATE-BEHAVIOR | Missing budget key or block currently reports counting inactive instead of applying defaults. | ~8
- tests/integration/test-check-state-plans.py:179-180,197-198 | REMOVABLE | Boolean run-budget rejection belongs in centralized schema validation. | ~4
- tests/integration/test-check-state-plans.py:229,271,344,360,372 | UPDATE-FIXTURE | Five make_fixture calls write empty configs without schema_version 3. | ~5
- tests/integration/test-check-state-plans.py:407-408 | UPDATE-FIXTURE | Plan-phase INV-6 helper writes missing-version shared config. | ~2
- tests/integration/test-check-state-plans.py:573,624,745 | UPDATE-FIXTURE | INV-34 and INV-35 helpers write missing-version shared config. | ~3

## tests/integration/test-check-state-handoff.py
- tests/integration/test-check-state-handoff.py:65-66,190-191 | UPDATE-FIXTURE | Handoff fixture builders write missing-version shared sync-off config. | ~4
- tests/integration/test-check-state-handoff.py:213-214 | UPDATE-FIXTURE | FEAT-54 fixture overwrites config without schema_version 3. | ~2
- tests/integration/test-check-state-handoff.py:336-351 | UNAFFECTED | Project and template must not embed feature-specific exemption paths. | ~16

## tests/integration/test-check-state-feat59.py
- tests/integration/test-check-state-feat59.py:42-43 | UPDATE-FIXTURE | Default GitHub, seam-era, and budget config lacks schema_version 3. | ~2
- tests/integration/test-check-state-feat59.py:98-106 | UNAFFECTED | Fixture writes supplied config text; migrate its constants rather than helper behavior. | ~9
- tests/integration/test-check-state-feat59.py:228-279 | UNAFFECTED | Feature cycles and recorded budget raises remain semantic ledger checks. | ~52
- tests/integration/test-check-state-feat59.py:840-864 | UNAFFECTED | Valid seam-era dates determine retrospective note versus violation. | ~25
- tests/integration/test-check-state-feat59.py:867-878 | REMOVABLE | Missing or unreadable seam-era config validation belongs in schema/default coverage. | ~12
- tests/integration/test-check-state-feat59.py:939-947 | UPDATE-FIXTURE | INV-49 config already has kind statuses but lacks schema_version 3. | ~9
- tests/integration/test-check-state-feat59.py:969-1042 | UNAFFECTED | Active and excluded runners determine verification-gap requirements, not config shape. | ~74

## tests/integration/test-branch-create-gate.py
- tests/integration/test-branch-create-gate.py:151-156 | UPDATE-FIXTURE | Shared self-gating fixture emits empty or GitHub-only config without version. | ~6
- tests/integration/test-branch-create-gate.py:167-192 | UNAFFECTED | Absent GitHub block, false sync, and unpinned repository exercise valid default-based self-gating. | ~26
- tests/integration/test-branch-create-gate.py:228-235 | UPDATE-BEHAVIOR | Duplicate config keys silently disable branch policy. | ~8
- tests/integration/test-branch-create-gate.py:264-285 | UPDATE-BEHAVIOR | Compatibility reader converts missing, malformed, and non-object config into successful false-dash fallback. | ~22
- tests/integration/test-branch-create-gate.py:286-290 | REMOVABLE | Wrong-type GitHub block producing AttributeError is superseded by loader validation. | ~5
- tests/integration/test-branch-create-gate.py:291-292 | UNAFFECTED | Reader source must not contain broad exception catches. | ~2

## tests/integration/test-post-merge-sweep.py
- tests/integration/test-post-merge-sweep.py:295-296 | UPDATE-FIXTURE | Bootstrap repository config lacks schema_version 3. | ~2
- tests/integration/test-post-merge-sweep.py:992-994 | UPDATE-FIXTURE | Sync-off config rewrite lacks schema_version 3. | ~3
- tests/integration/test-post-merge-sweep.py:1080-1085,1088-1122 | REMOVABLE | Harness-config duplicate-key retention case duplicates centralized malformed-config rejection. | ~15
- tests/integration/test-post-merge-sweep.py:1073-1079,1088-1122 | UNAFFECTED | Parallel duplicate feature.json retention case is outside harness-config schema scope. | ~15

## tests/integration/test-code-grade-cli.py
- tests/integration/test-code-grade-cli.py:52-54 | UPDATE-FIXTURE | Base unit-kind config lacks schema_version 3; its status already exists. | ~3
- tests/integration/test-code-grade-cli.py:195-196 | UPDATE-FIXTURE | Custom configured kind violates fixed kind names and lacks schema_version 3. | ~2
- tests/integration/test-code-grade-cli.py:197-241 | UNAFFECTED | Configured detect globs select grading bars and severities. | ~45
- tests/integration/test-code-grade-cli.py:242-249 | REMOVABLE | Per-reader duplicate harness-config key rejection duplicates shared loader coverage. | ~8
- tests/integration/test-code-grade-cli.py:250-251 | UPDATE-FIXTURE | Config reset repeats unsupported configured kind and omits schema_version 3. | ~2

## tests/unit/omp-hooks.test.ts
- tests/unit/omp-hooks.test.ts:2351-2369 | UNAFFECTED | Context budget fixture, configured value, and absent-key fallback use documented TypeScript exception. | ~19
- tests/unit/omp-hooks.test.ts:2451-2465 | UNAFFECTED | Advisory stays silent exactly at configured/default token threshold. | ~15
- tests/unit/omp-hooks.test.ts:2590-2614 | UNAFFECTED | Plan budget fixture, configured value, missing config fallback, and shipped default retain exception. | ~25
- tests/unit/omp-hooks.test.ts:2989-2999 | UNAFFECTED | schema_version 2 belongs to inflight claims, not harness.json. | ~11

## tests/integration/test-merge-gate.py
- tests/integration/test-merge-gate.py:27-28 | UPDATE-FIXTURE | Base receipt-gate config lacks schema_version 3. | ~2
- tests/integration/test-merge-gate.py:114-123 | UNAFFECTED | Unpinned repository denial and explicit sync-off allowance remain receipt policy. | ~10
- tests/integration/test-merge-gate.py:302-309 | UPDATE-BEHAVIOR | Duplicate config keys silently disable merge policy. | ~8
- tests/integration/test-merge-gate.py:427-428 | UPDATE-FIXTURE | Distillation owner config lacks schema_version 3. | ~2

## tests/integration/test-feature-corpus.py
- tests/integration/test-feature-corpus.py:29-37 | UNAFFECTED | schema_version 1 describes team manifest, not harness configuration. | ~9
- tests/integration/test-feature-corpus.py:38 | UPDATE-FIXTURE | Shared GITHUB_ON config lacks schema_version 3. | ~1
- tests/integration/test-feature-corpus.py:146-148,236-238 | UNAFFECTED | Gate setup commits shared GITHUB_ON; migrate the constant rather than these calls. | ~6
- tests/integration/test-feature-corpus.py:323-325 | UPDATE-FIXTURE | Board-audit owner config lacks schema_version 3. | ~3
- tests/integration/test-feature-corpus.py:468 | UPDATE-FIXTURE | Layout-evidence owner config contains only GitHub repository, without schema_version 3. | ~1

## tests/integration/test-check-plan-routes.py
- tests/integration/test-check-plan-routes.py:733-754 | UNAFFECTED | Plan task names harness config as a granted file; no config is written. | ~22
- tests/integration/test-check-plan-routes.py:767-796 | UNAFFECTED | Task and station fixtures reuse harness config pathname as routing input. | ~30
- tests/integration/test-check-plan-routes.py:900-916 | UNAFFECTED | Granted and annotated config path tests exercise domain routing. | ~17
- tests/integration/test-check-plan-routes.py:2000-2040 | UNAFFECTED | Static reader classifications name load_harness_json as canonical remedy. | ~41
- tests/integration/test-check-plan-routes.py:2050-2080 | UNAFFECTED | Raw parse inside accessor module still requires explicit classification. | ~31
- tests/integration/test-check-plan-routes.py:2115-2127,2152-2177 | UNAFFECTED | Remedy metadata mutants and extra raw readers test classification enforcement. | ~39

## tests/integration/test-check-domain-grant.py
- tests/integration/test-check-domain-grant.py:919-922 | UNAFFECTED | Resolves harness config pathname to its sole granted agent. | ~4

## tests/integration/test-gh-issue-types.py
- tests/integration/test-gh-issue-types.py:50 | UNAFFECTED | Task title mentions harness config incidentally. | ~1
- tests/integration/test-gh-issue-types.py:157-163 | UPDATE-FIXTURE | Shared issue-type config writer lacks schema_version 3. | ~7
- tests/integration/test-gh-issue-types.py:296-315 | UNAFFECTED | Legal Bug, Task, and parent overrides map to repository-specific issue types. | ~20
- tests/integration/test-gh-issue-types.py:318-340,468-491 | UNAFFECTED | Missing remote issue types cause semantic refusals, not malformed-config errors. | ~47

## tests/integration/test-gh-backlog-issue-types.py
- tests/integration/test-gh-backlog-issue-types.py:96-102 | UPDATE-FIXTURE | Shared backlog config writer lacks schema_version 3. | ~7
- tests/integration/test-gh-backlog-issue-types.py:105-111 | UNAFFECTED | Fixture commentary and root nesting describe config discovery. | ~7
- tests/integration/test-gh-backlog-issue-types.py:309-330,342-357 | UNAFFECTED | Repository lacking required issue types causes semantic refusal. | ~38

## tests/integration/test-factory-issue-types.py
- tests/integration/test-factory-issue-types.py:77 | UNAFFECTED | Task title mentions harness config incidentally. | ~1
- tests/integration/test-factory-issue-types.py:128-130 | UNAFFECTED | Fake GitHub serves supplied base64 remote config. | ~3
- tests/integration/test-factory-issue-types.py:196-201 | UPDATE-FIXTURE | Encoded remote config writer lacks schema_version 3. | ~6
- tests/integration/test-factory-issue-types.py:374 | UNAFFECTED | Legal Bug and parent issue-type overrides remain supported. | ~1

## tests/integration/test-checker-structure-locks.py
- tests/integration/test-checker-structure-locks.py:245 | UNAFFECTED | Static mutant detects module-scope config reads. | ~1
- tests/integration/test-checker-structure-locks.py:403-415 | UNAFFECTED | Static invariant mutants prohibit reparsing runner-shared config and feature records. | ~13

## tests/integration/test-check-skill-weight.py
- tests/integration/test-check-skill-weight.py:40-45 | UPDATE-FIXTURE | Shared skill-budget fixture lacks schema_version 3. | ~6
- tests/integration/test-check-skill-weight.py:69-78 | UNAFFECTED | Exceeding valid preload budgets remains advisory and never a skill error. | ~10
- tests/integration/test-check-skill-weight.py:80-87 | UPDATE-BEHAVIOR | Missing and malformed preload budgets degrade to UNBUDGETED instead of validated defaults or failure. | ~8
- tests/integration/test-check-skill-weight.py:88-92 | REMOVABLE | Per-reader duplicate config keys rejection duplicates centralized loader coverage. | ~5

## tests/integration/test-check-instruction-paths.py
- tests/integration/test-check-instruction-paths.py:33-46 | UNAFFECTED | Harness config paths are instruction-linter examples, never parsed configuration. | ~14

## Totals

| Class | Files | Approximate lines |
|---|---:|---:|
| REMOVABLE | 7 | 61 |
| UPDATE-FIXTURE | 16 | 122 |
| UPDATE-BEHAVIOR | 7 | 92 |
| UNAFFECTED | 19 | 1,016 |

No assigned file is wholly REMOVABLE. Shared malformed-artifact branches count only their harness-config slice; unaffected feature-record branches remain. No tests or checks were run.


## Group C (TestScanC)

## Classification

Counts cover harness.json-related spans, not unrelated test bodies. Approximate lines count the relevant code within each range. Classes can overlap within a file. No assigned file is wholly REMOVABLE.

### Unit files

`tests/unit/test-suite-layout.py:84-91 | UNAFFECTED | Repository/template detect parity and manual-test discovery policy. | ~8`
`tests/unit/test-suite-layout.py:353-355 | UNAFFECTED | Selects active and locally_run discovery kinds. | ~3`
`tests/unit/test-suite-layout.py:491-609 | UNAFFECTED | Certifies discovery patterns and checks tracked-file coverage, including positive controls. | ~119`

`tests/unit/test-no-distribution.py:179-188 | UNAFFECTED | Board ownership commentary accompanies fleet.yaml assertions, not harness.json validation. | ~10`
`tests/unit/test-no-distribution.py:299-306 | UNAFFECTED | Commentary locates per-repository board assertions elsewhere. | ~8`

`tests/unit/test-gate-policy.py:24,62 | UPDATE-FIXTURE | Review-only fixture lacks schema_version 3. | ~2`
`tests/unit/test-gate-policy.py:65-68 | UPDATE-BEHAVIOR | Accepts obsolete gate keys with arbitrary values; unknown keys must now fail. | ~4`
`tests/unit/test-gate-policy.py:69-93 | REMOVABLE | Duplicates invalid policy, wrong type, missing keys, malformed JSON, and unreadable-config validation. | ~25`
`tests/unit/test-gate-policy.py:96-118 | UNAFFECTED | Evaluates review policies and rejects invalid evaluation severity. | ~23`

`tests/unit/test-fleet-product-config.py:110-140 | UPDATE-FIXTURE | Four successful remote responses use unknown read key and omit schema_version 3. | ~8`
`tests/unit/test-fleet-product-config.py:142-178 | UNAFFECTED | Reports per-member success and transport failures in declaration order. | ~37`
`tests/unit/test-fleet-product-config.py:181-193 | REMOVABLE | Checks reader-specific invalid-JSON detection and diagnostic labeling. | ~13`
`tests/unit/test-fleet-product-config.py:195-286 | UNAFFECTED | Checks exception propagation, report structure, ordering, and failing CLI exit status. | ~92`

`tests/unit/test-wayfind.py:94-97 | UPDATE-FIXTURE | Real-root github config omits schema_version 3. | ~4`
`tests/unit/test-wayfind.py:103-111 | UNAFFECTED | Root discovery must bypass markerless decoy directories. | ~9`

`tests/unit/test-orchestrator-playbook.py:95-105 | UNAFFECTED | Prose names configurable context threshold without hardcoding its numeric value. | ~11`

`tests/unit/test-feature-schema-build-entry.py:255-257 | UPDATE-FIXTURE | Sync-off config with null repo and board omits schema_version 3. | ~3`
`tests/unit/test-feature-schema-build-entry.py:258-266 | UNAFFECTED | Null-board binding semantics and invalid feature.factory.repo rejection remain domain behavior. | ~9`

`tests/unit/test-factory-claim.py:205-233 | UNAFFECTED | Test-side board carriers are stripped from fleet data and supplied through product_config stub. | ~29`
`tests/unit/test-factory-claim.py:450-455 | UNAFFECTED | Stub returns an already-loaded product mapping; it neither serializes nor validates harness.json. | ~6`

`tests/unit/test-code-grade.py:292-297 | UNAFFECTED | Reads live test_kinds to derive self-grading bars. | ~6`
`tests/unit/test-code-grade.py:416-449 | UNAFFECTED | In-memory kind mappings test classification bars and active/locally_run/unresolved semantics. | ~34`
`tests/unit/test-code-grade.py:471-479 | REMOVABLE | Rejects malformed test_kinds mappings and missing detect through reader-specific TestKindsError. | ~9`

`tests/unit/test-check-state-shipped-ctx.py:71 | UPDATE-FIXTURE | Shared tree builder writes empty harness.json without schema_version 3. | ~1`

`tests/unit/test-check-state-inv37-local-binding.py:84-85 | UPDATE-FIXTURE | Owner config serialized from ctx.cj omits schema_version 3. | ~2`

`tests/unit/test-check-state-inv35.py:47-49 | UPDATE-FIXTURE | run_checker writes versionless sync-off config. | ~3`

`tests/unit/test-check-state-inv26-routing.py:109-112 | UPDATE-FIXTURE | Routing fixture writes owner github config without schema_version 3. | ~4`

### Integration files

`tests/integration/test-plan-sign-gate.py:54-55 | UPDATE-FIXTURE | Root helper writes schema_version 1. | ~2`

`tests/integration/test-plan-decision-dispositions.py:110-113 | UPDATE-FIXTURE | Every make_root config uses rejected schema_version 2. | ~4`
`tests/integration/test-plan-decision-dispositions.py:464-476 | UNAFFECTED | Tests era activation boundaries, timezone comparison, and explicit-null activation semantics. | ~13`
`tests/integration/test-plan-decision-dispositions.py:477 | REMOVABLE | Reader-specific missing-era-key default check moves to centralized loader coverage. | ~1`
`tests/integration/test-plan-decision-dispositions.py:478-479 | UNAFFECTED | Undated legacy plan behavior is not harness.json shape validation. | ~2`
`tests/integration/test-plan-decision-dispositions.py:483-486 | REMOVABLE | Rejects malformed and date-only config era timestamps. | ~4`
`tests/integration/test-plan-decision-dispositions.py:487-490 | UNAFFECTED | Invalid drafted_at belongs to plan.yaml, not harness.json. | ~4`

`tests/integration/test-hooks-install.py:146-147 | UPDATE-FIXTURE | Bootstrap origin writes github config without schema_version 3. | ~2`
`tests/integration/test-hooks-install.py:186-187 | UNAFFECTED | Copies configured repository identity into feature receipts. | ~2`

`tests/integration/test-gh-sync-start-task.py:354-382 | UNAFFECTED | Explicit-null board preserves issue lifecycle while avoiding board writes. | ~29`
`tests/integration/test-gh-sync-start-task.py:389-405 | REMOVABLE | Unusable board fixture checks missing station_field rejection and reader-specific stderr handling. | ~17`

`tests/integration/test-check-state-worktrees.py:62 | UPDATE-FIXTURE | INV-25 allowed-worktree fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:72 | UPDATE-FIXTURE | INV-25 sibling-worktree fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:98 | UPDATE-FIXTURE | INV-25 own-root worktree fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:147 | UPDATE-FIXTURE | Missing-module refusal fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:192-193 | UPDATE-FIXTURE | Layout-invariant builder writes shared versionless sync-off config. | ~2`
`tests/integration/test-check-state-worktrees.py:381 | UPDATE-FIXTURE | Terminal-feature standing-worktree fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:392 | UPDATE-FIXTURE | Nonterminal standing-worktree control passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:407 | UPDATE-FIXTURE | Worktree removal-guidance fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:443 | UPDATE-FIXTURE | Working-tree/default-branch disagreement fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:457 | UPDATE-FIXTURE | Reverse default-branch disagreement fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:472 | UPDATE-FIXTURE | Dirty-worktree refusal fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:518 | UPDATE-FIXTURE | Second fleet repository fixture passes empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:537 | UPDATE-FIXTURE | Missing, abbreviated, malformed, and valid landed-record fixtures share empty config. | ~1`
`tests/integration/test-check-state-worktrees.py:664-665 | UPDATE-FIXTURE | INV-31 hook-installation builder writes versionless sync-off config. | ~2`

`tests/integration/test-run-unit-tests-kinds.py:36-49 | UNAFFECTED | Enforces exact live-probe registration, runner instructions, matrix exclusion, and existing probe paths. | ~14`
`tests/integration/test-run-unit-tests-kinds.py:87-100 | UNAFFECTED | Checks actual live-kind inventory and forbids automated-matrix claims for live probes. | ~14`
`tests/integration/test-run-unit-tests-kinds.py:103-121 | REMOVABLE | Negative registration checks cover missing kinds and empty detect configuration. | ~19`
`tests/integration/test-run-unit-tests-kinds.py:123-138 | UNAFFECTED | Runner excludes credentialed probes and accepts their manual layout. | ~16`

`tests/integration/test-onboarding-split.py:87-112 | UNAFFECTED | Prose marker ordering describes onboarding branch, fleet registration, and central artifact placement. | ~26`

`tests/integration/test-lead-start-return.py:123-124 | UPDATE-FIXTURE | make_root writes review gate config without schema_version 3. | ~2`

`tests/integration/test-layout-migration.py:358-359 | UPDATE-FIXTURE | Session-entry parity fixture writes versionless sync-off config. | ~2`

`tests/integration/test-harness-yaml.py:67 | UNAFFECTED | Manifest domain fixture contains harness.json as an ordinary path. | ~1`
`tests/integration/test-harness-yaml.py:185-188 | UNAFFECTED | schema_version 2 is generic YAML scalar data, not a harness.json fixture. | ~4`

`tests/integration/test-gh-sync-abandon.py:255 | UPDATE-FIXTURE | Sync-disabled override omits schema_version 3. | ~1`
`tests/integration/test-gh-sync-abandon.py:258-259 | UNAFFECTED | Valid sync-disabled config still skips GitHub synchronization. | ~2`

`tests/integration/test-check-state-table.py:85-88 | UPDATE-FIXTURE | two_feature_tree writes versionless github, budgets, and era settings. | ~4`

`tests/integration/test-check-state-shipped.py:301-303 | UPDATE-FIXTURE | Shipped-feature GitHub-check fixture replaces owner config without schema_version 3. | ~3`

`tests/integration/test-check-state-inv51.py:70-71 | UPDATE-FIXTURE | tree writes versionless sync-off config. | ~2`

`tests/integration/test-check-state-inv37-offline.py:54-55 | UPDATE-FIXTURE | Owner config omits schema_version 3. | ~2`
`tests/integration/test-check-state-inv37-offline.py:61-64 | UPDATE-FIXTURE | Remote product response also omits schema_version 3. | ~4`

`tests/integration/test-check-expertise.py:168-188 | UNAFFECTED | harness.json is an expertise advisory token, not parsed configuration. | ~21`

`tests/integration/test-board-station.py:55-58 | UPDATE-FIXTURE | Shared local writer stamps every config with schema_version 1. | ~4`
`tests/integration/test-board-station.py:166-172 | UNAFFECTED | Explicit-null board remains an intentional no-write configuration. | ~7`
`tests/integration/test-board-station.py:175-183 | REMOVABLE | Reader-specific missing github.board refusal check moves to loader/default coverage. | ~9`
`tests/integration/test-board-station.py:330-341 | UNAFFECTED | Valid sync-off config suppresses writes before validating the requested CLI station. | ~12`

### Manual probe

`tests/manual/probe-issue-types.py:57-64 | UPDATE-BEHAVIOR | Actual probe catches config read/parse errors and returns empty mapping. | ~8`
`tests/manual/probe-issue-types.py:173-185 | UNAFFECTED | Missing credentials or valid disabled/unpinned configuration causes an environmental SKIP. | ~13`

### Assigned shared helpers

`tests/integration/f58_sparse_fixture.py:82 | UPDATE-FIXTURE | _owner_files writes empty owner config inherited by linked worktrees and clones. | ~1`

`tests/integration/check_state_support.py:88-96 | UPDATE-FIXTURE | Shared sync-on and sync-off JSON constants omit schema_version 3. | ~9`
`tests/integration/check_state_support.py:153-156 | UPDATE-FIXTURE | make_fixture writes caller-provided versionless or empty JSON unchanged. | ~4`

## Shared-fixture fan-out

Caller counts below mean distinct test files, not individual test cases.

- **check_state_support.py:** **12 importing test files**. The actual `make_fixture` writer has **4 caller files**: `test-check-state-entry.py`, `test-check-state-plans.py`, `test-check-state-records.py`, and `test-check-state-worktrees.py`. Its sync constants have **5 consumer files**: entry, handoff, inv26, plans, and worktrees. Updating constants repairs those uses; updating constants alone does **not** repair callers passing `'{}'` directly. This assignment's worktrees file contains **12** such calls.
- **f58_sparse_fixture.py:** **7 caller files** inherit `_owner_files()` through `SparseFixture.build()`: `test-check-state-corpus.py`, `test-check-state-shipped.py`, `test-corpus-non-regression.py`, `test-corpus-real-owner.py`, `test-feature-corpus.py`, `test-worktree-state-hooks.py`, and `test-worktree-state.py`. One owner-config correction repairs their inherited fixture. The shipped suite's explicit override still needs its own correction.
- **gh_sync_support.py:** **8 importing test files**, of which **6 gh-sync suites** consume its config-writing fixture family: abandon, board-add, open, record, ship, and start-task. The two other importers use `install_gh`, not these local writers. Update both `stage()` and `write_harness_json_board()`; `stage_station()`, `stage_depends_on()`, and `stage_ship()` delegate to the latter. `stage_fleet()` additionally constructs a remote product config that needs its own migration.

Additional shared-helper spans, outside the assigned-file totals:

`tests/integration/gh_sync_support.py:72-81 | UPDATE-FIXTURE | stage writes versionless github config for lifecycle fixtures. | ~10`
`tests/integration/gh_sync_support.py:612-626 | UPDATE-FIXTURE | write_harness_json_board writes versionless board config for multiple fixture wrappers. | ~15`
`tests/integration/gh_sync_support.py:737-760 | UPDATE-FIXTURE | stage_fleet supplies versionless remote product config through install_gh. | ~6`
`tests/integration/gh_sync_support.py:150-164 | UNAFFECTED | Feature-record helper reads configured repository identity; it does not write harness.json. | ~15`

**Important distinctions:** Explicit null boards and valid sync-off configurations are not malformed-config fallbacks. GitHub transport/authentication failures and board-write failures are not harness.json validation failures. Product-config report rows marked `ok: false` already produce failing CLI status; their aggregation is not fail-open execution. In-memory stubs standing in for an already-validated `product_config()` result are not serialized harness.json fixtures.

## Per-class totals

Assigned files only; file counts are nonexclusive, line counts approximate:

| Class | File count | Approximate lines |
|---|---:|---:|
| REMOVABLE | 7 | 97 |
| UPDATE-FIXTURE | 22 | 99 |
| UPDATE-BEHAVIOR | 2 | 12 |
| UNAFFECTED | 19 | 584 |

Additional shared helper `gh_sync_support.py`: UPDATE-FIXTURE **1 file / ~31 lines**; UNAFFECTED **1 file / ~15 lines**.

Read-only investigation; no files changed and no tests executed.
