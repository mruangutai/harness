# Red-first receipt — slice S1a (build-entry and runs-agent exemptions)

Baseline pin: `4a05030d` (origin/main). The baseline clone `/private/tmp/feat71-base-S1a` was made with `git clone --no-local` and `checkout --detach 4a05030d`. All 7 changed test files were copied into it unmodified, run there, and then run in the worktree. The clone was removed afterwards. Both runs used `CLAUDE_PROJECT_DIR` and `HARNESS_PROJECT_DIR` set to the root being tested.

## How the tests stay corpus-free and still go red

None of the new assertions names a real feature. Each probes synthetic ids (`FEAT-90-fixture`, `BUG-9-x`, `PR-9-fixture`, `FEAT-9106-fixture`). Each also probes every feature-id-shaped string (`^(FEAT|BUG|PR)-[0-9]+`) that `feature_schema` holds as module-level collection data, read from the module at run time.

- **On the baseline,** that discovery returns the old exemption tables: 33 runs-agent ids and 75 build-entry ids. The uniform-rule assertions then fail and name the exempt ids. This is the intended historical dependency.
- **In the worktree,** the module holds no such table, and the synthetic ids carry the assertion. The unit test additionally asserts that the table set is empty.

## Per changed test

### tests/unit/test-feature-schema-build-entry.py
Command: `python3 tests/unit/test-feature-schema-build-entry.py`
- **Baseline: exit 1.**
  - `FAIL FEAT-71 feature_schema holds no per-feature id table {'RUNS_AGENT_EXEMPT': "33 ids, e.g. ['FEAT-01', ...]", 'BUILD_ENTRY_ERA_EXEMPT': "75 ids, e.g. ['BUG-1030-stale-anchor-write-hazard', ...]"}`
  - `FAIL BE-02 a building plan with no task done is open for every feature id 150 short-circuited, e.g. [('BUG-1030-stale-anchor-write-hazard', False, 'recover-terminal'), ...]`
  - `FAIL BE-10 no receipt allows no merge for any feature id 150 allowed, e.g. [('BUG-1030-stale-anchor-write-hazard', None), ('BUG-1030-stale-anchor-write-hazard', 'recovery-required'), ...]`
  - `FAIL FEAT-71 a runs entry without agent is refused at index 0 for every feature id 33 exempt, e.g. ['FEAT-01', 'FEAT-02', 'FEAT-03-subissue-mirror']`
- **Worktree: exit 0.** 29 PASS, 0 FAIL.

### tests/integration/test-validate-feature-json.py
Command: `python3 tests/integration/test-validate-feature-json.py`
- **Baseline: exit 1.**
  - `FAIL t15_b_every_entry_without_agent_is_refused_for_every_feature 33 displays exempted entries, e.g. [('/tmp/x/.harness/harness/features/FEAT-01/feature.json', 4), ...]`
- **Worktree: exit 0.** `ALL PASS` (82 PASS lines). The red proof `t15_e_the_agent_rule_is_load_bearing` reports `original 1, mutant 0`.

### tests/unit/test-gh-sync-build-entry.py
Command: `python3 tests/unit/test-gh-sync-build-entry.py`
- **Baseline: exit 1.**
  - `FAIL BE-31 an absent receipt refuses the Build start for every feature id 75 not refused, e.g. [('BUG-1030-stale-anchor-write-hazard', None), ...]`
  - `FAIL BE-32 recovery-required warns that the merge is refused, for every feature id 75 exempt, e.g. ['BUG-1030-stale-anchor-write-hazard', ...]`
- **Worktree: exit 0.** 17 PASS, 0 FAIL.

### tests/integration/test-merge-gate.py
Command: `python3 tests/integration/test-merge-gate.py`
- **Baseline: exit 1.**
  - `FAIL  T-05 absent or recovery-required build_entry denies for every feature id` — `150 not denied, e.g. [('BUG-1030-stale-anchor-write-hazard', None, None), ('BUG-1030-stale-anchor-write-hazard', 'recovery-required', None), ...]`
- **Worktree: exit 0.** `ALL PASSED` (40 ok).

### tests/integration/test-post-merge-sweep.py
Command: `python3 tests/integration/test-post-merge-sweep.py`
- **Baseline: exit 1.**
  - `FAIL: T-07 no receipt keeps the worktree for every feature id — BUG-1030-stale-anchor-write-hazard entry=None was swept after 5 probes`
  - The case stops at the first swept worktree, which keeps the cost bounded on the baseline.
- **Worktree: exit 0.** 69 PASS, 0 FAIL.

### tests/integration/test-check-domain-post.py
Command: `python3 tests/integration/test-check-domain-post.py`
- **Baseline: exit 0. Worktree: exit 0.**
- No red is possible here. The only changes are these:
  - **Deleted assertion:** the assertion that the fixture name is absent from the frozen map, which read the deleted symbol.
  - **Renamed fixtures:** `FEAT-Z-absent-from-the-frozen-map` became `FEAT-90-fixture-agent-write`, and `BUG-1480-wt*` became `BUG-9-handoff-wt*`.
  - **Wording:** "positional" became "agent" in the docstring and a case label.

  The SC-07 write-path behaviour assertions are unchanged, and they pass on both trees because the synthetic id was never exempt.

### tests/unit/test-feature-record.py
Command: `python3 tests/unit/test-feature-record.py`
- **Baseline: exit 0. Worktree: exit 0** (`Ran 118 tests ... OK`).
- Docstring-only change: the provenance `BUG-285-canonical-reader` was reduced to the bare id `BUG-285`. No behaviour changed, so no red is possible.

## Files changed
- `.claude/skills/harness/bin/feature_schema.py`:
  - Deleted `RUNS_AGENT_EXEMPT`, `BUILD_ENTRY_ERA_EXEMPT`, `_FEATURES_SEGMENT`, `_feature_dir_name` and their D-23/#718/BUG-1309 rationale blocks.
  - `_runs_agent_problems` now requires `agent` on every entry.
  - Removed the era short-circuit from `recovery_command_for`.
  - Removed the `era_requires_absent` parameter and the era branch from `receipt_allows_merge`. A missing receipt is now always `False`.
- `.claude/skills/harness/bin/feature-schema.json`:
  - The `feature_id` example no longer names a dead feature (`e.g. FEAT-<n>-<slug>`).
  - The `agent` description now states the uniform requirement.
  - The `code_grade` description no longer contrasts itself with an "absent `agent` is benign" default, which no longer exists.
- `.claude/skills/harness/bin/gh-sync.py`:
  - `_build_entry_preflight` refuses every absent receipt.
  - `_build_entry_recovery_notice` lost its era branch and its now-unused `feature_id` parameter.
- `.claude/skills/harness/bin/merge-gate.py`: removed the era "predates" notice.
- `.claude/skills/harness/bin/post-merge-sweep.py`: calls `receipt_allows_merge` without the removed keyword, and the era "predates" notice is removed.
- `.claude/skills/harness/bin/feature_json_write.py`: rewrote the docstring sentence that cited `RUNS_AGENT_EXEMPT` as a precedent.
- `tests/unit/test-feature-schema-build-entry.py`:
  - Replaced BE-02 (era member) and BE-10 (exact membership against the real `FEAT-01`) with uniform-rule cases over synthetic and module-held ids.
  - Added a "no per-feature id table" check and a runs-agent uniformity check.
  - Dropped "non-era" wording.
- `tests/integration/test-validate-feature-json.py`: rewrote the T15 cases. Cases A, B, C and D used the real `FEAT-10-software-factory` and the map. They are now:
  - A: index-0 refusal.
  - B: every index is refused under every probed display.
  - D: the value check.
  - E: the red mutant, now on a synthetic id.
- `tests/integration/test-check-domain-post.py`: dropped the frozen-map assertion and replaced the dead-id fixtures (`BUG-1480-wt*`) with synthetic ones.
- `tests/unit/test-gh-sync-build-entry.py`: added BE-31 and BE-32, preflight uniformity over synthetic and module-held ids.
- `tests/integration/test-merge-gate.py`:
  - Replaced the two era-exempt `BUG-1030-stale-anchor-write-hazard` allow cases with one uniform-deny case.
  - Deleted the "duplicate era-exempt claimant" case. The synthetic duplicate-claimant case directly above it already covers the behaviour.
- `tests/integration/test-post-merge-sweep.py`:
  - Removed the two `BUG-1030-stale-anchor-write-hazard` rows from the T-07 matrix and factored the sweep into `_t07_sweep`.
  - Added `case_t07_no_feature_id_is_exempt`.
  - Renamed every fixture id that reused a dead real id (`FEAT-01/02/20/21/22/30/31/32/33/40/41/42/43/44/50/64-*`) to `FEAT-9NN-*`.
- `tests/unit/test-feature-record.py`: docstring provenance reduced to the bare id.
