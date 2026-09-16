# Reuse assessment — BUG-1563 INV-35

**BLUF: one actionable reuse finding; no product, test, or helper files were mutated.**

## Finding R-01 — shared fixture/root setup is reimplemented

1. **File and line:** `tests/unit/test-check-state-inv35.py:36-54`.
2. **Summary:** `run_checker` rebuilds the isolated Harness root, marker, sync-off config, and dual root environment already provided by `tests/integration/check_state_support.py:40-43,54-99`.
3. **Existing reusable thing:** `HARNESS_JSON_SYNC_OFF`, `make_fixture`, and `_root_env` in `tests/integration/check_state_support.py:40-43,54-99` construct this exact fixture topology and resolver environment.
4. **Concrete cost:** Resolver-marker or root-environment changes now require lockstep edits in both helpers; if the unit copy falls behind, it can silently point `check-state.sh` at a different root than the integration fixture does, invalidating its three required checker outcomes.
5. **Exact alternative:** In the unit test, import the shared fixture vocabulary, replace lines 38-49 with `h = make_fixture(root, HARNESS_JSON_SYNC_OFF, "  parent: none")` and write `plan.yaml` under `Path(h) / "harness" / "features" / "FEAT-TEST"`; replace the hand-built environment with `_root_env(root)`. Retain the unit-local archived-checker materialization and its `bash` invocation because `run()` only targets the live `SCRIPT` and cannot select the `CHECK_STATE_REV` archive.

## Inspection boundary

- Target files inspected: `.claude/skills/harness/bin/check-state.sh:148-279`; `tests/integration/test-check-state-plans.py:729-833,973-1028`; `tests/unit/test-check-state-inv35.py:1-98`.
- Direct helper inspected: `tests/integration/check_state_support.py:12-99`.
- Excluded from findings: the deliberate three-outcome behavioral duplication required by SC-03/DEC-217.
- Mutations: receipt only; no product, test, or helper mutation.
