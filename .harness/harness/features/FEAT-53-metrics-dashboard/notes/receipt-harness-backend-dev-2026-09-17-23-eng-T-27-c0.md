# T-27 receipt — absent fleet clone

The all-repository work payload now preserves readable rows and emits exactly one `{repo, path, reason}` error for an absent configured clone; selecting that unreadable repository remains HTTP 500.

## Hypothesis

`serve._repository_roots()` treated a missing workspace clone as a fatal selection error, so `/api/work?window=all&repo=all` never reached collection. The hypothesis would be falsified if the new fixture returned 200 before changing production code.

## Fail-first

Command:

```sh
python3 tests/integration/test-metrics-dashboard.py MetricsDashboardIntegrationTest.test_absent_fleet_clone_degrades_work_payload
```

Observed before production edit (exit 1): `AssertionError: 200 != 500` at the assertion for `/api/work?window=all&repo=all`; one test ran and failed in 0.294s.

## Focused green evidence

- `python3 tests/integration/test-metrics-dashboard.py MetricsDashboardIntegrationTest.test_absent_fleet_clone_degrades_work_payload` — PASS: 1 test in 0.309s. The fixture keeps `FEAT-101-harness`, has exactly `[{'repo': 'alpha', 'path': <alpha path>, 'reason': 'configured repository alpha cannot be enumerated at <alpha path>'}]`, and confirms `/api/work?repo=alpha` plus `/api/kpis?repo=alpha` are 500.
- `python3 tests/integration/test-metrics-dashboard.py` — PASS: 9 tests in 14.337s. This is T-27's declared verify.
- `python3 tests/integration/test-work-dashboard.py` — PASS: 41 assertions.
- `/opt/homebrew/bin/python3 -c 'import importlib.util, sys; ... serve.py ...'` — PASS: Python `3.14.5 (main, May 10 2026, 10:21:34) [Clang 21.0.0 (clang-2100.0.123.102)]`; `serve import OK`.

No formatters, linters, project-wide build, or project-wide suite ran.

## Commit and changed files

Commit: `5e62c20a106e8875724fa5591da26f7938e29736`

- `.claude/skills/harness/bin/dashboard/serve.py`
- `tests/integration/test-metrics-dashboard.py`

## Recommended T-27 amendment values

```yaml
intent: >-
  Mount GET /api/work on T-12's Flask application without adding a process or changing bind, port, startup or static-file behavior. Recompute from disk on each request. Make GET /api/work and the existing GET /api/kpis accept the same window and repo query parameters, default both to all, reject unsupported values with the existing JSON 400 shape, and return only the selected repository and time slice. Return JSON schema harness-work/1 with attention_order, effective thresholds, items and errors. Every item exposes id, kind, attention, attention_reasons, name, repository, segment, station, phase, run_status, updated_at, elapsed_total, elapsed_by_phase with plan, build and validate, runs, cycles_used, max_total_cycles, tokens, main_path, worktree_path, source_path and a kind-specific detail object; absent values are JSON null. The token object preserves measured_total, measured_runs, total_runs, unmeasured_runs and by_phase and never exposes a dollar-cost field. Return items in D-25 order and preserve explicit source errors instead of dropping rows. An invalid dashboard configuration remains HTTP 500 with one specific unavailable reason. A configured repository that cannot be enumerated becomes one `{repo, path, reason}` entry in a successful all-repository payload whenever at least one requested segment is readable; return HTTP 500 with one specific unavailable reason only when no requested segment is readable. A malformed individual item remains in the successful response and the errors list names its path. /api/kpis applies the same selected-unreadable-repository rule. Extend the existing Flask integration script to build a two-segment temporary control plane, including an absent configured clone fixture; request both APIs with default and explicit window/repo pairs; prove the selected slice, defaults, degradation, all-unreadable behavior, no startup snapshot, complete schema and row order, null-aware token and phase fields with no cost, static routes, and no GitHub executable or import.
files:
  - .claude/skills/harness/bin/dashboard/serve.py
  - tests/integration/test-metrics-dashboard.py
verify: python3 tests/integration/test-metrics-dashboard.py
```
