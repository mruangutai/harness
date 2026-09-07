# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: .harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-07-02-validator/state.yaml
- squad: validator
- status: in-flight
- station: review — all thirteen tasks done and each verified at the orchestrator tier by running
  its own verify verbatim. The blocking qa test_matrix gate PASSES (full integration 50 files
  exit 0, full unit 33 files exit 0, no cell MISSING, T-07's unit cell not-applicable per D-12).
  SIMPLIFY returned an empty pass, so the tip is unmoved and review_sha pins the reviewed work.
- build entry outcome: opened — milestone 54, parent 1407, sub-issues 1408-1416. The
  github.build_entry field did not exist when this feature's own Build entry ran, which is why the
  plan declares BUG-1309 era-exempt.
- held for the ship decision, not applied: merge-gate.py:11 imports feature_schema at module
  scope, paying a measured ~50-60ms jsonschema import on every Bash call in the repo though main()
  exits at the merge_ref early return first. Two-line fix, main-session-direct lane. Any post-pin
  apply requires a re-pin and re-running whatever validator work has landed.

## Open Questions

- Ship backlog awaiting operator disposition: B-1 gate-dispatcher plus the HOOK_SPECS gaps, B-2
  gh-sync.py:247's no-op remedy, B-3 the 17 unrecovered sync-enabled features, B-4 the nonexistent
  gen-decisions-index --check clause in four features, B-5 gh-sync.py:1234's unguarded int(), B-6
  the merge-gate module-scope import above.
