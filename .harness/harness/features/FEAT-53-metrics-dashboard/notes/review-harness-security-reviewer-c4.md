# Security review — FEAT-53 c4

**BLUF:** V-04 is resolved at immutable tip `3b78eb833f12e82e711c6e1b82bf712821ab0a1b`; hostile Host values are rejected before route handlers run, loopback forms remain usable, and the six-path backend delta introduces no new exploitable security defect.

## Evidence

- Pin: `HEAD` resolved to `3b78eb833f12e82e711c6e1b82bf712821ab0a1b`; reviewed range is `ffd9fb0204701cdae968ef0febc86943fb4829bd..3b78eb833f12e82e711c6e1b82bf712821ab0a1b`.
- Targeted regression: `python3 -m unittest tests.integration.test-metrics-dashboard.MetricsDashboardIntegrationTest.test_untrusted_host_cannot_read_dashboard_routes` passed (`Ran 1 test ... OK`).
- Independent matrix against `/`, `/api/work`, and `/api/kpis`: `attacker.example`, attacker host with port, loopback-name/IP suffix attacks, userinfo-shaped input, empty/non-numeric ports, and path-shaped suffixes all returned `400` on every route. `localhost`, `localhost:8971`, `127.0.0.1`, `127.0.0.1:8971`, `[::1]`, and `[::1]:8971` reached the application; uppercase localhost forms also remained usable.
- Pre-routing probe patched `kpi.compute` and `work.collect` to raise if invoked; all three routes returned `400` for `rebinding.attacker.test` without invoking either handler. The guard is registered with `app.before_request` at `.claude/skills/harness/bin/dashboard/serve.py:70-74`.
- Werkzeug normalizes malformed `[::1]:8971:80` such that it reached the app. This does not create DNS-rebinding reachability: the authority remains the literal IPv6 loopback address and cannot name an attacker-controlled DNS host.
- Excluded and not re-gated: the known `/assets/index-hkwR5g06.js` 404 (F-QA-01), bundle/frontend/direct-lane items, and fixed-dark.

## Six-path census

- `.claude/skills/harness/bin/dashboard/serve.py` — security-relevant Host trust-boundary guard; exact loopback allowlist is fail-closed for attacker-controlled DNS names.
- `.claude/skills/harness/bin/dashboard/kpi.py` — computation decomposition only; no new input source, output field, command, URL, credential, or authorization decision.
- `.claude/skills/harness/bin/dashboard/work.py` — token aggregation decomposition only; no widened output or trust decision.
- `tests/integration/test-metrics-dashboard.py` — test-only Host, isolation, and timing coverage; no shipped surface.
- `tests/integration/test-metrics-trend.py` — test-only merge/unavailable coverage; no shipped surface.
- `tests/integration/test-work-dashboard.py` — test-only case decomposition; no shipped surface.

```yaml
VERDICT: PASS
DIGEST:
  headline: "V-04 is resolved: hostile Host values are rejected before routing while intended loopback host forms remain usable; no new security finding exists in the six-path diff."
  in_scope: true
  scope_reason: "serve.py validates an untrusted HTTP Host header before returning repository-derived dashboard data; the other five paths were audited as adjacent diff surface."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "HTTP Host header -> loopback dashboard routes", stride: "S", mitigated: true }
    - { boundary: "HTTP request -> repository-derived KPI/work output", stride: "I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-security-reviewer-c4.md
```
