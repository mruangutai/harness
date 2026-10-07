# T-04 evidence — sharded integration jobs behind the unchanged `integration` context (SC-02..SC-05, SC-09, SC-10)

Uncommitted on worktree HEAD (after T-02). File: `.github/workflows/tests.yml` only.

## Job graph
- `checks` (ubuntu-latest, no needs/if): checkout, Bun, PyYAML+jsonschema, Unit suite, Validate feature execution state, Plan-route gate, Canonical-reader audit, Instruction-path gate, Layout gate, Repository-state gate. All `run:` bodies byte-identical to the old `integration` job (parsed comparison against `git show HEAD:`: zero differing bodies; only `Integration suite` left the job).
- `integration-shards` (ubuntu-latest, matrix shard [1,2,3,4], fail-fast false): same setup; `run-unit-tests.py --kind integration --shard N/4 --manifest $RUNNER_TEMP/integration-manifest-N.json`; `Upload shard manifest` with `if: always()`, actions/upload-artifact@v4, name `integration-manifest-<run_id>-N`, `if-no-files-found: warn` (nothing fabricated), `overwrite: true` for re-runs.
- `integration` (no `name:` key, so context = `integration`; needs [checks, integration-shards]; `if: always()`): checkout@v4 (default ref), actions/download-artifact@v4 pattern `integration-manifest-<run_id>-*` merge-multiple into `$RUNNER_TEMP/integration-manifests`; `Validate shard completeness` (`if: always()`) runs `check-integration-shards.py --commit github.sha --shards 4 --checks-result needs.checks.result --matrix-result needs.integration-shards.result --manifest-dir DIR`, then fails if the download step outcome is not `success`, else exits with the validator's code.

## Tested SHA
`github.sha`. On pull_request it is the merge commit of `refs/pull/N/merge`, which is exactly what actions/checkout@v4 checks out by default in every job, so shard manifests' `tested_commit` (`git rev-parse HEAD`) and the validator's `git ls-tree` target are the same commit; on push to main it is the pushed commit.

## Fail-closed paths
missing artifact → nothing downloaded → `mkdir -p` dir → validator "no manifest for shard N" exit 1; download error → job already red, validator still prints, then explicit exit 1; checks/matrix failure/skipped/cancelled → validator rejects (T-02 matrix). No `continue-on-error` anywhere. Triggers, concurrency group and main no-cancel expression unchanged; no `container:`; no history fetch.

## Verify
- `python3 -c 'import yaml; yaml.safe_load(...)'` → exit 0
- `python3 tests/integration/test-integration-shard-aggregation.py` → exit 0, "0 failed", 2.3s
- actionlint: not installed (`which actionlint` exit 1); not run.
- Live scheduling, shard-only cancellation conclusion, required-context identity and timing remain SC-09/SC-10 user UAT.

## First live run and precompile fix (2026-10-05)

Run 37324916242 (draft PR #2100, head d30bd390): checks success; shards 1, 2, 4 success, shard 3 failure; `integration` failure with `INCOMPLETE: matrix-result is failure`, `runner_exit 1`, and `tests/integration/test-check-domain-artifact.py returned 1`. Wall from first shard start 14:27:58Z to `integration` completion 14:29:31Z: 93s. The aggregator failed closed on a real shard failure.

Cause: shutil.copytree of the live bin/ raced a concurrent `.pyc` temp-file write in bin/check_state/__pycache__ (ENOENT on `brief.cpython-312.pyc.<n>`). Pre-existing: about 15 tests copy bin/ without ignoring __pycache__; the shard mix surfaced it. Fix: a `Precompile harness bin` step (`python3 -m compileall -q .claude/skills/harness/bin`) in `checks` and `integration-shards`, before any test, so no test writes into the tree it copies.

## Re-pin f2791446 -> ccb1732d4c7d06bf9ebe9dc5bfb9e2c983b35de2 (2026-10-05, operator-directed)

Main gained #2095 (panel findings hold the template shape; INV-32), so the UAT throwaway's merge commit failed the Repository-state gate on this feature's plan.yaml finding `resolution:` key (run 37385539005; that U-01 attempt is void and PR #2111 was closed unmerged). ccb1732d merges origin/main and removes that key through `plan-merge.py set-panel`. `git diff --stat f2791446 ccb1732d` over run-unit-tests.py, run_pool.py, check-integration-shards.py, check-plan-routes.py, tests.yml and integration-durations.json is empty: the reviewed feature code is unchanged. Full unit, integration and layout runs exit 0 at ccb1732d. The cycle-2 panel's YAML record was transcribed by the main session because of #2110 (see runs/2026-10-05-03-validator/digest.md).

## Re-pin ccb1732d -> b886dbcf53777cb3139c04e5b973ed77244f8dcf (2026-10-06)

The throwaway UAT PR conflicted with main (canonical-reader-classification.json: both sides appended rows), so GitHub created no pull_request run. b886dbcf53777cb3139c04e5b973ed77244f8dcf merges origin/main 2d28b79e and keeps both sides' rows; `--canonical-reader-audit` reports 0 unresolved across 100 files. The merge also brought FEAT-1559's sparse feature worktrees; this worktree was repaired with `worktree-state.py --repair`. Over the feature's code, workflow, weights and plan.yaml the diff ccb1732d..b886dbcf53777cb3139c04e5b973ed77244f8dcf is shown in the commit message's check as merge-only (check-plan-routes.py auto-merged main's change). Unit and integration (83 files) exit 0 at b886dbcf53777cb3139c04e5b973ed77244f8dcf.

## Weights re-measured after UAT SC-10 miss (operator ruling, 2026-10-06)

UAT P1 took 108s; shard 1 was longest in all six UAT runs, and 7 files added on main (test-check-state-corpus.py, test-corpus-non-regression.py, test-corpus-real-owner.py, test-feature-corpus-census.py, test-feature-corpus.py, test-worktree-state-hooks.py, test-worktree-state.py) had no weight. integration-durations.json now holds the per-file median over UAT runs U-01, U-05, U-06, U-07 (83 files). Predicted LPT shard sums: [157.5, 157.5, 157.6, 157.7]. SPEC §9 describes the optional `source_runs` list.
