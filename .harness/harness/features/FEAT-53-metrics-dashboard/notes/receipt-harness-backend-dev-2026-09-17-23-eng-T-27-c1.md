# T-27 cycle-1 backend receipt — collector ownership

`work.py` now owns configured-but-absent workspace-clone degradation at fleet enumeration: readable control rows remain available and the collector returns one fleet error. `serve.py` adapts that result for HTTP selection and payloads.

## Commit

Final correction commit: `daba2af5513a0316f57ed8729576acb0e582708b`

Exact correction-commit files:

- `.claude/skills/harness/bin/dashboard/work.py`
- `.claude/skills/harness/bin/dashboard/serve.py`
- `tests/integration/test-work-dashboard.py`

## Focused evidence

1. Fail-first before production correction:
   `python3 tests/integration/test-work-dashboard.py --case collector`
   exited 1 with `FAIL absent configured clone preserves readable rows and reports one fleet error — AttributeError("module 'dashboard.work' has no attribute 'collect_fleet'")`.
2. `python3 tests/integration/test-work-dashboard.py --case collector` — PASS: 10 collector assertions, including the absent-clone fixture with readable rows and exactly one `{repo, path, reason}` error.
3. `python3 tests/integration/test-metrics-dashboard.py` — PASS: 9 tests in 14.327s; `/api/work?window=all&repo=all` remains 200, while only-absent repo, all-unreadable, and invalid configuration remain 500; KPI behavior remains green.
4. `python3 -c "import importlib.util; from pathlib import Path; path=Path('.claude/skills/harness/bin/dashboard/serve.py'); spec=importlib.util.spec_from_file_location('dashboard_serve_smoke', path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); print('serve import OK')"` — PASS under Python 3.14.5: `serve import OK`.

No formatter, linter, project-wide build, or project-wide suite ran.

## Full UAT-fix file set across c0+c1

- `.claude/skills/harness/bin/dashboard/work.py`
- `.claude/skills/harness/bin/dashboard/serve.py`
- `tests/integration/test-work-dashboard.py`
- `tests/integration/test-metrics-dashboard.py`

## Exact T-27 amendment entries

```yaml
intent:
  was: >-
    Mount GET /api/work on T-12's Flask application without adding a process or changing bind, port, startup or static-file behavior. Recompute from disk on each request. Make GET /api/work and the existing GET /api/kpis accept the same window and repo query parameters, default both to all, reject unsupported values with the existing JSON 400 shape, and return only the selected repository and time slice. Return JSON schema harness-work/1 with attention_order, effective thresholds, items and errors. Every item exposes id, kind, attention, attention_reasons, name, repository, segment, station, phase, run_status, updated_at, elapsed_total, elapsed_by_phase with plan, build and validate, runs, cycles_used, max_total_cycles, tokens, main_path, worktree_path, source_path and a kind-specific detail object; absent values are JSON null. The token object preserves measured_total, measured_runs, total_runs, unmeasured_runs and by_phase and never exposes a dollar-cost field. Return items in D-25 order and preserve explicit source errors instead of dropping rows. An invalid dashboard configuration or failure to enumerate a configured repository returns HTTP 500 with one specific unavailable reason; a malformed individual item remains in the successful response and the errors list names its path. Extend the existing Flask integration script to build a two-segment temporary control plane, request both APIs with default and explicit window/repo pairs, prove the selected slice and defaults, request /api/work twice around a disk mutation to prove no startup snapshot, assert the complete schema and row order, assert null-aware token and phase fields including the absence of cost, prove all prior static routes still behave identically, and make any GitHub executable or import fail the test if touched.
  now: >-
    Mount GET /api/work on T-12's Flask application without adding a process or changing bind, port, startup or static-file behavior. Recompute from disk on each request. Make GET /api/work and the existing GET /api/kpis accept the same window and repo query parameters, default both to all, reject unsupported values with the existing JSON 400 shape, and return only the selected repository and time slice. Return JSON schema harness-work/1 with attention_order, effective thresholds, items and errors. Every item exposes id, kind, attention, attention_reasons, name, repository, segment, station, phase, run_status, updated_at, elapsed_total, elapsed_by_phase with plan, build and validate, runs, cycles_used, max_total_cycles, tokens, main_path, worktree_path, source_path and a kind-specific detail object; absent values are JSON null. The token object preserves measured_total, measured_runs, total_runs, unmeasured_runs and by_phase and never exposes a dollar-cost field. Return items in D-25 order and preserve explicit source errors instead of dropping rows. `work.py` owns fleet enumeration, retaining readable rows and emitting exactly one `{repo, path, reason}` error for each configured workspace clone absent from disk; `serve.py` adapts that collector result into HTTP selection and the work payload. Partial fleet loss is a successful all-repository payload when at least one requested segment remains readable. Return HTTP 500 with one specific unavailable reason when no requested segment is readable, when only an absent configured repository is selected, or when dashboard configuration is invalid. A malformed individual item remains in the successful response and the errors list names its path. Extend the existing Flask integration script to build a two-segment temporary control plane, request both APIs with default and explicit window/repo pairs, prove the selected slice and defaults, request /api/work twice around a disk mutation to prove no startup snapshot, assert the complete schema and row order, assert null-aware token and phase fields including the absence of cost, prove all prior static routes still behave identically, and make any GitHub executable or import fail the test if touched. Add the focused collector fixture for one readable control segment and one configured-but-absent workspace clone.
files:
  was:
    - .claude/skills/harness/bin/dashboard/serve.py
    - tests/integration/test-metrics-dashboard.py
  now:
    - .claude/skills/harness/bin/dashboard/work.py
    - .claude/skills/harness/bin/dashboard/serve.py
    - tests/integration/test-work-dashboard.py
    - tests/integration/test-metrics-dashboard.py
verify:
  was: python3 tests/integration/test-metrics-dashboard.py
  now: python3 tests/integration/test-work-dashboard.py --case collector && python3 tests/integration/test-metrics-dashboard.py
```
