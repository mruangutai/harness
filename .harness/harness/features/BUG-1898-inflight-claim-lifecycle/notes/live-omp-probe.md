# Live OMP probe: BUG-1898 merge gate (SC-07)

**Status: no live run recorded. The merge is gated on a PASS section below.**

The operator runs the probe live from an OMP-capable shell whose cwd is this feature's linked
worktree. The probe then starts its own `omp --mode rpc` session there, so the hook it exercises
is this worktree's:

```sh
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle
python3 tests/manual/probe-inflight-claim-lifecycle.py            # live; appends a receipt here
python3 tests/manual/probe-inflight-claim-lifecycle.py --dry-run  # prerequisites + plan only
```

Live mode refuses to start in any of these cases:

- `omp` is missing or is not the pinned runtime (`.omp/runtime-pin.json`).
- There is no credential for the model's provider.
- The cwd is not this worktree, or `feature_root` does not place the feature here.
- `HARNESS_PROJECT_DIR` or `VALIDATE_DIGEST_BIN` is set to substitute a fixture.
- The feature registry holds any row. Do the cutover first, per `ship-checklist.md`.

A scenario that runs but is not observed is a FAIL.

| Scenario | What the receipt must show |
|---|---|
| S1-orchestrator-background | Main's background orchestrator starts under a real id, its settlement arrives on the lifecycle bus, and no row is left |
| S2-wake-reclaim | a `hub send` wake of that settled id writes its marker, which the hook authorizes only under an exact-id claim; a row bound to that id is sampled during the wake; the wake settles and no row is left |
| S3-mixed-batch | a background scout plus two orchestrators, one dispatching a nested scout: a suffix id and a lineage id are observed; no row ever carries a non-governed id or crosses personas; every governed child settles and no row is left |
| S4-suite-preservation | a real `tests/integration/test-validate-digest.py` run passes, and the separately seeded sentinel claim is byte-identical |
| S5-settled-empty | every governed child is observed, and the feature registry is empty after the probe releases only its own sentinel |

Each live run appends one `## Live run <UTC>` section below with:

- the command, cwd and OMP runtime identity;
- the session id and file, and every observed id and lifecycle frame;
- registry snapshots before and after;
- the suite verdict;
- every check, and the final PASS or FAIL.

**Dry-run output is a prerequisite print, never a receipt.** At `6fff6bc6` plus T-04, the dry
run reported `prerequisites: READY` from this worktree. That is not evidence that any scenario
passes.
