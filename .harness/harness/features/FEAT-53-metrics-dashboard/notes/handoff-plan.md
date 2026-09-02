# Handoff — FEAT-53-metrics-dashboard, plan → build — written at 38dd3622, seq-7

## Next

Do not dispatch a build segment. The plan is unsigned and the panel returned FAIL at high, so
the next act belongs to the operator: read
`notes/ship-review-2026-09-01-plan.md` and rule on DEC-1..DEC-5 there. Once rulings exist,
dispatch harness-product-lead with pm to remediate `panel.findings` `PF-328f8f3c` (KPI 4
fabricated zeros, T-11/T-06/D-19) and `PF-7408d83a` (chart wiring, T-14/T-15/T-18) — and settle
the Shape-B deferral (`PF-6aa9faae`) BEFORE remediating `PF-7408d83a`, because deferring Shape B
changes or deletes T-15. Only the main session signs (`plan-merge.py sign-approval`).

## Trust

- plan.yaml carries 20 tasks, 20 decisions, `status: plan`, `approval.status: pending`, and
  `panel:` with both readers `ran` and 8 open findings, 8 distinct PF- ids — re-loaded with
  yaml.safe_load myself — verified-at 38dd3622
- The two high panel findings are unremediated by design: DEC-176 routes them to the operator's
  one batched signature review, not to a pre-signature fix — `runs/2026-09-01-06-validator/digest.md`
  — verified-at 38dd3622
- D-03 reverses the operator's settled "real web framework"; engineering endorsed the stdlib server
  on merit, so this is a disclosure question, not a defect — `notes/research-FEAT-53-goalcheck-plan-c1.md`
  — verified-at 38dd3622
- plan.yaml has exactly one write route: proposal written with the Write tool to a notes/research-*.md
  path, then `plan-merge.py apply --proposal <that path>`. Shell redirects and `--proposal -` are
  refused; direct Write exits 2; `amend` handles text scalars but exits 4 on a list — measured
  myself against this checkout — verified-at 38dd3622
- The prototype has never been rendered by anyone, author or reviewer — `DESIGN.md`,
  `runs/2026-09-01-03-product/digest.md` — verified-at 38dd3622

## Dead ends

- Do not re-litigate `web/src/**` as the client's home: every product-side glob resolves NOBODY in
  the harness base, so only control-plane targets are grantable —
  `notes/research-FEAT-53-routing-and-signals.md` — verified-at 38dd3622
- Do not name `react-charts` as the charting fallback: dead package, React 16 peer, last published
  2023-11-02 — `notes/receipt-harness-frontend-dev-a2.md` — verified-at 38dd3622
- Do not expect a code grade or a review_sha for any plan-phase validator run: DEC-207 grades a
  pending specification and `code_grade: n_a` is correct — `runs/2026-09-01-06-validator/digest.md`
  — verified-at 38dd3622

## Working set

- .harness/harness/features/FEAT-53-metrics-dashboard/notes/ship-review-2026-09-01-plan.md
- .harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml
- .harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md
- .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-01-06-validator/digest.md
- .harness/harness/features/FEAT-53-metrics-dashboard/notes/research-FEAT-53-routing-and-signals.md
