# T-02 evidence — shard aggregation against independent tested-commit discovery (SC-02, SC-03, SC-05)

Worktree HEAD d89f9b23, uncommitted. Files: `.claude/skills/harness/bin/check-integration-shards.py` (new gate),
`tests/unit/test-integration-shard-validation.py`, `tests/integration/test-integration-shard-aggregation.py`,
`tests/integration/canonical-reader-classification.json`.

## Gate contract
`check-integration-shards.py --commit SHA --shards 4 --checks-result VALUE --matrix-result VALUE --manifest-dir PATH`.
Run-unit-tests.py trusted-root prologue copied verbatim (accepted duplication, DEC-234 shape). Results accepted:
success/failure/skipped/cancelled/missing; anything else or an absent flag is exit 2. Expected coverage =
`git ls-tree -r -z --full-tree --name-only SHA` filtered by fullmatch `tests/integration/test-[^/]*\.py`.
Every file under the manifest dir is a manifest. Exit 0 exact success / 1 incomplete-or-failed / 2 malformed or
unusable; each defect printed as `INCOMPLETE:`/`MALFORMED:` then a final `PASS integration: …` or `FAIL integration: …` line.
Validation functions (`conclusion_defects`, `evidence_defects`, `coverage_defects`, `integration_paths`,
`discover_expected`, `load_manifest_dir`, `exit_status`) are importable.

## Red-first (tests written before the gate)
Pre-gate: `python3 tests/unit/test-integration-shard-validation.py` → exit 1 ("FAIL cannot load gate: … No such file");
`python3 tests/integration/test-integration-shard-aggregation.py` → exit 1 (FileNotFoundError copying the absent gate).

Per-defect discrimination: each validation branch individually disabled in the implemented gate (one mutation at a
time, file restored after), both suites run. Columns: exit: failing cases. Every mutation turns at least one named case red.

| mutation | unit | integration |
|---|---|---|
| C-failure: treat failure as success | 1: checks-result failure rejected; matrix-result failure rejected | 1: checks-result failure; matrix-result failure |
| C-skipped: treat skipped as success | 1: checks-result skipped rejected; matrix-result skipped rejected | 1: checks-result skipped; matrix-result skipped |
| C-cancelled: treat cancelled as success | 1: checks-result cancelled rejected; matrix-result cancelled rejected | 1: checks-result cancelled; matrix-result cancelled |
| C-missing: treat missing as success | 1: checks-result missing rejected; matrix-result missing rejected | 1: checks-result missing; matrix-result missing |
| C-unrecognized: accept unknown value | 1: checks-result unrecognized rejected; matrix-result unrecognized rejected | 1: checks-result unrecognized; integration: 1 defect(s), exit 1; matrix-result unrecognized |
| C-absent: no explicit absent branch | 1: checks-result absent rejected; matrix-result absent rejected | 1: checks-result absent; integration: 1 defect(s), exit 2; matrix-result absent |
| S-missing manifest | 1: missing manifest for shard 3 | 1: integration: 1 defect(s), exit 1; missing manifest |
| S-duplicate shard id | 1: duplicate shard id | 1: duplicate shard id |
| S-extra manifest | 1: extra manifest beyond shard count | 1: extra manifest |
| S-foreign commit | 1: foreign commit | 1: wrong commit (HEAD) in manifest |
| S-foreign kind | 1: foreign suite kind | 1: foreign suite kind |
| S-foreign shard_count | 1: foreign shard count | 0: - |
| S-malformed JSON tolerated | 0: - | 1: integration: 10 defect(s), exit 2; malformed JSON |
| S-non-object tolerated | 1: manifest_set_cases ran TypeError: list indices must be integers or slices, not str | 0: - |
| F-path normalization off | 1: absolute path; non-normalized path | 0: - |
| F-bool/str returncode accepted | 1: boolean return code; non-integer return code | 0: - |
| R-runner_exit ignored | 1: runner_exit nonzero | 0: - |
| R-failed returncode ignored | 1: completed file failed | 1: failing completed file |
| R-within-shard duplicate | 1: within-shard duplicate | 1: integration: 1 defect(s), exit 1; within-shard duplicate |
| R-selected without completion | 1: selected without completion | 1: integration: 1 defect(s), exit 1; selected without completion |
| R-completed without selection | 1: completed without selection | 0: - |
| V-omitted | 1: omitted file; selection union is not coverage | 1: HEAD's own coverage is not the tested commit's; integration: 5 defect(s), exit 1; omitted file (absent at HEAD too) |
| V-cross-shard duplicate | 1: cross-shard duplicate | 1: cross-shard duplicate |
| V-unexpected | 1: unexpected file | 1: HEAD-only file is unexpected; working-tree-only file is unexpected |
| V-empty expected suite | 1: empty expected suite | 1: empty expected suite |
| X-expected from current HEAD | 0: - | 1: HEAD's own coverage is not the tested commit's; HEAD-only file is unexpected; all-success exact coverage at the tested commit; empty expected suite; integration: 1 defect(s), exit 1; integration: 2 defect(s), exit 1; integration: 4 defect(s), exit 1; omitted file (absent at HEAD too); unknown tested commit |
| X-expected from working-tree glob | 0: - | 1: HEAD's own coverage is not the tested commit's; HEAD-only file is unexpected; all-success exact coverage at the tested commit; empty expected suite; integration: 2 defect(s), exit 1; integration: 3 defect(s), exit 1; integration: 5 defect(s), exit 1; omitted file (absent at HEAD too); unknown tested commit; working-tree-only file is unexpected |
| X-expected from selected_files union | 1: empty expected suite; omitted file; unexpected file | 1: HEAD's own coverage is not the tested commit's; HEAD-only file is unexpected; integration: 4 defect(s), exit 1; omitted file (absent at HEAD too); working-tree-only file is unexpected |
| X-coverage from selection, not completion | 1: selection union is not coverage | 0: - |

Notes: X-rows are the forbidden-oracle witnesses — using current HEAD or the working-tree glob turns the positive
control and the HEAD/worktree cases red (the fixture repo has an empty-suite commit, the tested commit with test-a..d,
a HEAD commit dropping test-d and adding test-e, and an untracked test-f); using the selected_files union as
expected fails omitted/unexpected cases; counting selections instead of completions fails "selection union is not
coverage". Rows with integration `0: -` are pure field branches covered by unit cases (plan: unit covers pure branches).
`FAIL integration: …` fragments in the integration column are the gate's own summary lines echoed in diagnostics.

## Verify (post-fix, each < 60s)
- `python3 tests/unit/test-integration-shard-validation.py` → exit 0, 0 failed (0.1s)
- `python3 tests/integration/test-integration-shard-aggregation.py` → exit 0, 0 failed (2.1s)
- `python3 .agents/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` → exit 0,
  "0 unresolved reader site(s) across 97 Python file(s)". Before T-02 it exited 2 (T-01's
  `run-unit-tests.py::_load_weights` unclassified); after adding the gate also `check-integration-shards.py::_read_manifest`
  and the scanned-file manifest. Both classified `exempt/module_internal_format` as non-canonical suite evidence with
  concrete reasons; gate added to scanned_files. Audit code untouched.
- Affected: `tests/integration/test-check-plan-routes.py` ALL PASS; `tests/unit/test-code-grade.py` PASS;
  `code-grade.py check-integration-shards.py` RESULT PASS (23 functions passing).

## SC-05 note
SC-05 is workflow inspection (T-04's tests.yml). T-02 supplies the aggregation's success condition: it fails unless
the checks-job result (the non-integration gates) and the matrix result are both exactly `success`.
