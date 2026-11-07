# T-01 evidence — weighted sharding and completed-file manifests (SC-01, SC-07, SC-08)

Worktree HEAD ad119cb8, uncommitted.

## Duration weights
`gh run view 37264903064 --repo mruangutai/harness --log`, Integration suite step, lines
`----- <file> (exit N, X.XXs) -----`: 73 unique attributed records (no duplicates), sum 614.50s,
median 6.24s → `default_seconds`. The 73 names equal the current `tests/integration/test-*.py`
set exactly. Written to `tests/integration/integration-durations.json` (schema 1, source_run_url
…/runs/37264903064, source_commit b046bdfed9fa262a25f53a41d566db2b90cd140b).

## SC-01 red-first (pre-fix runner, new test written first)
`python3 tests/integration/test-run-unit-tests-shards.py` → exit 1, 25 FAIL / 8 PASS:
- completeness: "every discovered integration file appears in exactly one shard", "sharding applies to the selected unit suite too"
- weighting: "longest-processing-time weighting, not round-robin"
- ties: "equal weights break ties by path, then lowest shard"
- unknown file: "unknown new file uses default_seconds and is included once"
- empty shard: "empty shard succeeds without invoking the pool" (pre-fix ran test-a.py), "empty shard writes an empty completed-file manifest"
- malformed args (14): missing value, malformed fraction, non-decimal, signed, zero index, zero count, negative, i>n, repeated shard, repeated manifest, manifest without shard, missing manifest value, check-layout+shard, check-layout+manifest; plus manifest-inside-bin refusal and `--shard` before `--kind`
- manifest: "manifest records actual completed files and their return codes", "manifest identity fields"
Pre-fix passes were the positive controls (checked-in document provenance/73 positive records/median default) and vacuous determinism/stale-key/nonzero-exit checks.

Post-fix: exit 0, 32 PASS, 0 failed. One intermediate failure (completed paths rendered relative to the
symlink-resolved ROOT on macOS) fixed by normalising the cwd-relative pool paths.

## run_pool seam red-first
Seam reverted in place (kwarg removed), `python3 tests/integration/test-run-pool.py` → exit 1,
`TypeError: main() got an unexpected keyword argument 'completed'`. Restored → exit 0.

## SC-07 / SC-08 targeted runner mutations
`tests/unit/test-runner-unsharded.py` (unit, integration and no-arg unsharded forms) against the
implemented runner with one mutation applied at a time, file restored afterwards:
| mutation | file | exit | failing checks |
|---|---|---|---|
| M1 drop first discovered file (`*_scripts(patterns)[1:]`) | run-unit-tests.py | 1 | discovery + count for unit, integration, no-arg |
| M2 destroy attribution (child output printed before header) | run_pool.py | 1 | attribution for unit, integration, no-arg |
| M3 mask child failure (`run_pool.main(...) and 0`) | run-unit-tests.py | 1 | failure propagation for unit, integration, no-arg |
Unmutated: exit 0. SC-08 omitted-integration-file and masked-integration-failure witnesses are the
`--kind integration` rows of M1 and M3.

## Verify (post-fix, each independently, all < 60s)
- tests/unit/test-runner-unsharded.py exit 0 (2s)
- tests/integration/test-run-unit-tests-shards.py exit 0 (6s)
- tests/integration/test-run-unit-tests-kinds.py exit 0 (1s)
- tests/integration/test-run-unit-tests-layout.py exit 0 (4s)
- tests/integration/test-run-pool.py exit 0 (3s)
- tests/unit/test-code-grade.py: PASS
