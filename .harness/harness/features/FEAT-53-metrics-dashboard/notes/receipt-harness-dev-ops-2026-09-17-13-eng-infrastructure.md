# FEAT-53 infrastructure/native-runner repair

**BLUF:** PASS. Commit `55fd11004a20e092831feaaefbb426599bb9e3da` repairs all five owned failure groups without weakening certification, bypassing fixtures, suppressing exits, or removing the production trend import/call.

## Pre-fix reproductions

All commands ran from the FEAT-53 worktree and exited `1` before the repair.

| Group | Exact command | Grounded failing evidence |
|---|---|---|
| `test-suite-layout.py` | `python3 tests/unit/test-suite-layout.py` | Integration detect config diverged from the template and three `.claude/.../test-metrics-*.py` patterns were uncertified. |
| `test-suite-independence.py` | `python3 tests/unit/test-suite-independence.py` | Two live-checkout mutation findings at `tests/integration/test-metrics-client-render.py:86-87`. |
| `test-check-plan-routes.py` | `python3 tests/integration/test-check-plan-routes.py` | `case_20_touchpoints_py_probes_the_manifest` failed on the metrics path lacking the manifest contract. |
| `test-harness-yaml.py` | `python3 tests/integration/test-harness-yaml.py` | The child control failed and the guarded-import cap rejected intentional `check-state.py`. |
| `test-hooks-install.py` | `python3 tests/integration/test-hooks-install.py` | SC-14 merge fixture retained its worktree because copied `gh-sync.py` could not import dashboard `trend`. |

## Repairs

- Restored integration discovery to the certified `tests/integration/**` contract.
- Redirected the Vitest JSON carrier and Vite cache to a temporary carrier through `VITEST_CACHE_DIR`; no test cleanup touches the live checkout.
- Required `team-config.yaml` for touchpoints' cwd route and routed epoch construction through a helper, preserving the real manifest contract.
- Allowed the intentional T-25 `check-state.py` guarded import while retaining the cap for every other file.
- Copied the real dashboard Python dependency seam into the hooks clone fixture and force-removes any test-created linked worktree in `finally`; `gh-sync.py` still imports `trend` and calls `trend.record_ship`.

## Focused post-fix proofs

Each command exited `0`.

| Command | Evidence |
|---|---|
| `python3 tests/unit/test-suite-layout.py` | All layout checks passed, including certified running-kind discovery. |
| `python3 tests/unit/test-suite-independence.py` | Discovered 119 tests; 0 live-tree mutation sites. |
| `python3 tests/integration/test-check-plan-routes.py` | `case_20_touchpoints_py_probes_the_manifest` passed; runner reported `ALL PASS`. |
| `python3 tests/integration/test-harness-yaml.py` | Guarded-import test and its repointed-root child control passed. |
| `python3 tests/integration/test-hooks-install.py` | SC-14 green merge removed the worktree; red proof observed survival before guaranteed fixture teardown; `EXIT=0`. |

## Commit and cleanup

Committed files: `.harness/harness.json`, `.claude/skills/harness/bin/touchpoints.py`, `.claude/skills/harness/bin/dashboard/client/vitest.config.ts`, `tests/integration/test-harness-yaml.py`, `tests/integration/test-hooks-install.py`, and `tests/integration/test-metrics-client-render.py`.

The focused cleanup check found neither `client/.vitest/json/output.json` nor `client/node_modules/.vite/vitest`; no test-created worktree remains. No formatter, linter, project-wide/full-suite gate, or client Vitest run was executed.
