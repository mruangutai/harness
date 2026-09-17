```yaml
VERDICT: FAIL
DIGEST:
  headline: "V-02, V-17, and V-18 are resolved; V-03 remains open because /kpi/$n expects a response member absent from the live API."
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "V-03: the KPI route crashes on the real successful API payload.", why: "routes.tsx expects kpis[] while the endpoint returns top-level features, aggregate, and trend; T-14/T-28 own the panel/drill surface." }
  must_fix:
    - "V-03: consume the live top-level KPI payload on /kpi/$n and test that response shape."
  spec_violations:
    - { kind: mismatch, path: ".claude/skills/harness/bin/dashboard/client/src/routes.tsx", ref: D-30 }
  code_grade: n_a
  reviewed: "9b34c65246136666bc69f220824bb262965e75c0..fa921782d8404c8b635520be0cc1230d23fed6be"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-code-reviewer-c1.md
```

# Dispositions and evidence

- **V-02 — resolved.** `routes.tsx:54-63` owns KPI and work requests independently, renders a KPI-specific failure region without suppressing `WorkView`, and retains work failure behavior without suppressing `KpiTiles`. `tiles.tsx:9-30` accepts the real aggregate/trend payload and falls back to the seven signed labels. The asymmetric-failure case at `routes.test.tsx:84-99` proves a KPI rejection leaves the work heading and row usable.
- **V-03 — open.** `routes.tsx:69-72` casts `fetchKpis()` to a payload containing `kpis`, then executes `kpis.data?.kpis.find(...)`. The live producer returns top-level `features`, `aggregate`, and `trend`, with no `kpis` member (`dashboard/kpi.py:42-50`; `dashboard/serve.py:70-79`). A successful real response therefore throws before `KpiPanel` renders. The test at `routes.test.tsx:101-131` fabricates `kpis[]` and nests escaped-defect data inside one descriptor, so it cannot detect the mismatch. Even under that fabricated shape, `routes.tsx:72` passes the descriptor rather than the full top-level panel payload. This is a high substance mismatch against D-30/REQ-12/REQ-21, owned by T-14/T-28 (route carrier T-13).
- **V-17 — resolved.** `routes.tsx:23-42` records only an in-app KPI/work link target and focuses its route title; `routes.tsx:66-79` uses `h1` and `tabIndex=-1` on both landings. `routes.tsx:49-51` supplies the 2px text-token `:focus-visible` ring and suppresses both focus states only for route titles. Fresh loads remain unfocused.
- **V-18 — resolved.** `routes.tsx:49-51` declares the centred `1600px` maximum, `24px` desktop gutter, and `16px` gutter at `max-width:831px`.

No scope creep or additional defect class was found in the four frontend source/test files. Exact route names and fixed-dark semantics remain unchanged. Dist, Host security, backend/fleet/KPI/trend logic, Python code grade, unrelated SC fail-first work, T-24/T-25/T-30, and docs were not reviewed.

Scoped verification: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx src/work-view.test.tsx` passed 2 files / 18 tests. That green result does not discharge V-03 because the mock uses the wrong response contract.
