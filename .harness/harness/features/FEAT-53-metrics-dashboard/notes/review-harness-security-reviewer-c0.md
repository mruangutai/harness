# FEAT-53 security review — cycle 0

**VERDICT: FAIL.** The pinned dashboard is loopback-bound and read-only, but it accepts arbitrary HTTP `Host` values. A remote site can use DNS rebinding to read local dashboard JSON after a victim starts the dashboard and visits the site, exposing repository/worktree paths, feature state, errors, and operational metadata. This is a high-severity T-12 boundary failure.

- review_sha: `9b34c65246136666bc69f220824bb262965e75c0`
- merge_base: `a18d6a9f1f832084df84be22097a409d73bf4f61` (repository-derived with `git merge-base origin/main <review_sha>`; origin default branch is `main`)
- reviewed_range: `a18d6a9f1f832084df84be22097a409d73bf4f61...9b34c65246136666bc69f220824bb262965e75c0`
- cycles_used: 0
- severity_max: high
- known deferred work: T-17/METRICS.md, recorded only as operator-deferred completion work; not a finding. T-25 was treated as ratified and not relitigated.

## Finding

1. **kind: substance; task: T-12; reader: harness-security-reviewer; severity: high — arbitrary Host acceptance permits DNS-rebinding disclosure from the loopback dashboard.** `dashboard/serve.py:62,70-108,296` creates Flask without `TRUSTED_HOSTS`/equivalent host validation, exposes unauthenticated data APIs, and relies only on binding `127.0.0.1`. Probe against the pinned checkout: `GET /` with `Host: attacker.example` returned 200; Flask configuration reported `SERVER_NAME=None` and `TRUSTED_HOSTS=None`. An attacker who gets a dashboard operator to visit attacker-controlled JavaScript while the dashboard is running can rebind that origin to `127.0.0.1:8971`, issue same-origin requests to `/api/work` and `/api/kpis`, and read absolute source/main/worktree paths, feature/run state, repository identity, malformed-source errors, and git-derived operational metadata. The same route can repeatedly trigger the synchronous whole-repository KPI/code-grade workload. Require an allowlist of loopback Host values (including the selected port as Flask expects) or an equivalent anti-rebinding request-origin capability before serving API/static responses.

## Tested threat surfaces and evidence

- **Routing/query input:** only `window` (`30d|90d|all`) and configured repository names are accepted (`serve.py:112-138`); invalid values fail with JSON 400. No query value reaches subprocess argv.
- **Subprocess/injection:** all introduced git and code-grade calls use list-form argv with `shell=False` by default (`serve.py:260-266`, `grading.py:27-65`, `kpi.py:139-196`, `defects.py:68-82`, `attribution.py:117-125`). Repository roots are CLI/config-derived paths; feature branch values are checked against enumerated refs before `git diff`. No shell interpolation was found.
- **Filesystem/static serving:** `/assets/<path>` uses Flask/Werkzeug `send_from_directory` rooted at committed `client/dist/assets`; every other non-API route returns the fixed committed `client/dist/index.html`. Focused traversal probe `/assets/../serve.py` returned 404. No request-controlled filesystem path is served.
- **Read-only guarantee:** API paths call `trend.read`, collectors, git read operations, and code-grade only. The sole dashboard writer is `trend.record_ship`/`append`, which is not reachable from `create_app`; the integration contract snapshots git status around real API execution (`tests/integration/test-metrics-dashboard.py:90-106,160-170`). No HTTP method or route mutates viewed repositories.
- **JSON/error exposure:** responses intentionally include absolute source/main/worktree/project paths and source error strings (`serve.py:156-215,244-251`), and `_unavailable` returns raw exception text (`serve.py:255-257`). This becomes exploitable through the Host-validation defect above; it is not duplicated as a second finding.
- **Prerequisite failure:** version, PyYAML, Flask, harness config, and committed bundle checks happen before bind (`serve.py:29-57,270-296`); failures exit rather than serve partially.
- **Network exposure:** bind is hard-coded to `127.0.0.1`, with no bind-address option, debug and reloader disabled (`serve.py:285-296`). No route changes the bind. Host header enforcement is absent, as demonstrated above.
- **Dependency/secrets census:** the full pinned diff was swept beyond named server files. No credential/private-key material was identified. The new Flask dependency is runtime-gated; the client lockfile is pinned. Dashboard implementation exists in mirrored `.claude`/`.omp` trees; the security-relevant server behavior is the same surface.

## Assessed and dismissed

- **Static traversal:** dismissed; Werkzeug's safe directory join rejected `../serve.py`, and SPA fallbacks return only the fixed index.
- **Shell/argument injection:** dismissed; request values never enter argv, subprocesses are list-form, and code-grade receives absolute tracked Python paths (not option-shaped relative names).
- **Repository mutation through viewing:** dismissed; the write/commit functions in `trend.py` are ship-hook operations and are not called by either HTTP route.
- **Remote socket exposure:** dismissed as a separate issue; the process listens only on IPv4 loopback. DNS rebinding is retained because browser same-origin semantics can cross that boundary despite the bind.
- **CORS-based disclosure:** dismissed; no CORS relaxation was introduced. DNS rebinding does not require CORS.
- **Configured fleet path traversal:** dismissed for the request boundary; clients select only exact enumerated repo basenames. Fleet configuration is operator-controlled and duplicate/missing repositories fail closed.

## STRIDE threat model

| Boundary | STRIDE | Mitigated | Evidence |
|---|---|---:|---|
| Browser/network request → loopback Flask app | S, I, D | no | Arbitrary Host accepted; DNS-rebinding scenario above |
| Query parameters → repository/window selection | T, E | yes | Exact allowlists; values do not reach subprocess/filesystem joins |
| Dashboard → git/code-grade subprocesses | T, E | yes | List argv, no shell, selected refs constrained to enumerated refs |
| URL path → committed client bundle | T, I | yes | Fixed index plus `send_from_directory`; traversal probe 404 |
| Repository artifacts → JSON response | I | no | Paths/errors are returned; intended locally, but exposed by Host defect |
| GET APIs → CPU/process resources | D | no | Unbounded threaded GET can invoke whole-repo grading; materially reachable through the same rebinding defect |
| GET APIs → viewed repository state | T, R | yes | No reachable writer; status-preservation integration evidence |

## Required fix

- T-12 must reject non-loopback/untrusted Host values before any route is served, and retain a focused probe proving an attacker-controlled Host cannot receive `/`, `/api/work`, or `/api/kpis` while valid loopback hosts still work.

Open questions: none.
