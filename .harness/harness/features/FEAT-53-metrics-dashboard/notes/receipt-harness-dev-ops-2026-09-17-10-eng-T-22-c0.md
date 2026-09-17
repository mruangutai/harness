# T-22 receipt

## DEC-229 amendment record

- Signed files (`was`): `.claude/skills/harness/bin/test-metrics-client-render.py`, `.claude/skills/harness/bin/run-unit-tests.sh`, `.github/workflows/tests.yml`.
- Amended files (`now`): `tests/integration/test-metrics-client-render.py`, `.claude/skills/harness/bin/run-unit-tests.py`, `.claude/skills/harness/bin/suite_layout.py`, `tests/unit/test-suite-layout.py`, `.github/workflows/tests.yml`.
- Signed verify (`was`): `bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds && python3 .claude/skills/harness/bin/test-metrics-client-render.py`
- Amended verify (`now`): `python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-client-render.py && python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration`

## Fail-first evidence

`python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout` exited 2 before the layout exception, naming five tracked Vitest source tests under `.claude/skills/harness/bin/dashboard/client/src/` as outside `tests/`.

## Verification

- `python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout` now exits 0.
- `python3 tests/integration/test-metrics-client-render.py` emitted:
  `passed: grading panel mounts the Shape A histogram`;
  `passed: trend panel mounts the Shape B time series`;
  `passed: merged PR panel mounts the Shape B weekly line`.
  It also removed both `.vitest/` and `node_modules/.vite/vitest/`.
- A temporary carrier probe rejected each required label when absent, `pending`, or `failed`, with the respective `missing assertion`, `skipped assertion`, and `failing assertion` diagnostics.
- The exact amended command was run. Its layout and adapter portions passed; its integration pool completed 77 files in 144.13s but exited 1 on unrelated concurrent failures in `test-harness-yaml.py`, `test-check-plan-routes.py`, `test-hooks-install.py`, `test-metrics-dashboard.py`, and `test-work-dashboard.py`. The earlier generated-Vitest-cache snapshot failure did not recur.
