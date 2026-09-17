# FEAT-53 security review — cycle 3

**FAIL.** At immutable review pin `ffd9fb0204701cdae968ef0febc86943fb4829bd`, the complete dashboard remains loopback-bound but accepts arbitrary HTTP `Host` values. The final frontend repair does not touch this server boundary. A remote site can use DNS rebinding to read unauthenticated local dashboard JSON, including repository/worktree paths, source errors, feature state, token/run metadata, and operational data.

- merge base: `a18d6a9f1f832084df84be22097a409d73bf4f61`
- reviewed range: `a18d6a9f1f832084df84be22097a409d73bf4f61...ffd9fb0204701cdae968ef0febc86943fb4829bd`
- planned-post-gate: T-17 documentation; not a finding
- closed direct-lane V-09 (T-24/T-25/T-30), V-10, V-11, V-16, and V-20 were not reopened

## Finding

1. **kind: substance; severity: high; task owner: T-12; reader: security-reviewer — arbitrary Host acceptance permits DNS-rebinding disclosure from the loopback dashboard.** `dashboard/serve.py:67-68,70-108,296` creates Flask without `TRUSTED_HOSTS` or an equivalent request-host guard, exposes unauthenticated APIs, and relies only on `127.0.0.1` socket binding. An attacker who can induce an operator running the dashboard to visit attacker-controlled JavaScript can rebind that origin to `127.0.0.1:8971`, then read same-origin `/api/work` and `/api/kpis`. The attacker gains absolute local paths, feature/worktree state, source errors, run/token metadata, and KPI data; repeated KPI requests can also consume git/code-grade subprocess capacity. The earlier pinned direct probe recorded `Host: attacker.example` receiving HTTP 200 (`review-harness-security-reviewer-c0.md`), and inspection of the exact c3 pin confirms that no host-validation control exists. Reject non-loopback/untrusted Host values before routing, covering `/`, `/api/work`, and `/api/kpis`.

## Full-surface disposition

- **Path/root and static routes:** request-controlled asset paths are contained by `send_from_directory`; all other browser routes return one fixed index. Repository selection is an exact configured-name allowlist before selecting a root. No request value becomes an arbitrary filesystem path.
- **Local files, git, and subprocesses:** calls use list-form argv without a shell. Request inputs do not enter argv; feature refs are constrained to enumerated refs. HTTP routes call readers only; `trend.record_ship`/append is not reachable from Flask.
- **API validation / SSRF / deserialization:** `window` is restricted to `30d|90d|all`; `repo` is restricted to enumerated repositories. No outbound HTTP request, user-selected URL, unsafe YAML loader, pickle, or dynamic code path is exposed.
- **Rendering and drill-down:** API strings remain React text and route parameters go through TanStack Router/`URLSearchParams`; no raw HTML, script evaluation, external redirect, or data-dependent stylesheet sink was found. The final repair narrows KPI labels to local constants and adds no security regression.
- **Secrets/dependencies:** no credential or private-key material was found in the dashboard source/bundle. Flask is locally served and the client lockfile is pinned; no new dependency was added by the final repair.
- **Data exposure/errors:** `/api/work` intentionally returns absolute paths and source errors, while `_unavailable` returns exception text. This is locally useful but becomes exploitable through the Host defect; it is not duplicated as a second finding.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The full pinned dashboard still permits DNS-rebinding disclosure because its loopback Flask app accepts arbitrary Host values."
  in_scope: true
  scope_reason: "The feature crosses browser-to-loopback HTTP, query-to-root selection, local file/git/subprocess, repository-artifact-to-JSON, and API-to-DOM boundaries; the final frontend repair was reconciled with the complete server surface."
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: security-reviewer, summary: "T-12: arbitrary Host acceptance permits DNS-rebinding access to unauthenticated dashboard JSON.", why: "An attacker who gets a dashboard operator to visit attacker-controlled JavaScript can rebind its origin to loopback and read local paths, errors, feature/worktree state, run/token metadata, and KPIs." }
  must_fix:
    - "T-12: reject non-loopback/untrusted Host values before routing and prove attacker-controlled Host values cannot receive /, /api/work, or /api/kpis while valid loopback hosts remain usable."
  threat_model:
    - { boundary: "browser/network request -> loopback Flask app", stride: "S/I/D", mitigated: false }
    - { boundary: "query parameters -> repository/window selection", stride: "T/E", mitigated: true }
    - { boundary: "dashboard -> local files/git/code-grade subprocesses", stride: "T/E/D", mitigated: true }
    - { boundary: "URL path -> committed client bundle", stride: "T/I", mitigated: true }
    - { boundary: "repository artifacts/errors -> JSON response", stride: I, mitigated: false }
    - { boundary: "API payload and identifiers -> React DOM/internal drill-down", stride: "T/I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-security-reviewer-c3.md
```
