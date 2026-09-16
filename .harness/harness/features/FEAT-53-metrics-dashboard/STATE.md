# STATE

## Current

- feature: FEAT-53-metrics-dashboard
- run: .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-02-09-product/digest.md
- squad: none
- status: awaiting-user

The operator's 2026-09-16 prototype-review rulings supersede the 2026-09-15 four-route composition. The browser now has exactly three product routes: the single dashboard `/`, one KPI `/kpi/$n`, and one feature-or-bug detail `/work/$id`. The separate `/work` route, the header "Work" toggle, `/features`, `/features/$featureId` and every `/kpis` page are retired. The shared window and Repository URL parameters default to `all`, persist on every route, and filter both GET `/api/kpis` and GET `/api/work`.

The single dashboard is a centred max-width container: shared header, attention strip, Repository KPIs first, then the work list. Attention cards are Status filter shortcuts. The work list has Kanban and Table layouts only, filters Station, Status and Kind, has no Repository filter, and names the table column Status. Astryx icons carry status; status does not use text colour or coloured borders or top-lines. Attention cards keep neutral borders and colour only their label text. Labels and controls use Title Case; descriptions use sentence case. Focus rings appear only for keyboard `:focus-visible`, sparklines keep the 14-day daily horizon and fill their tiles, and the honest-state gallery exists only on a fixture-only prototype route.

Decisions D-29 and D-30 and tasks T-05, T-13 and T-28 record that structure. T-27 remains unchanged because it names only the GET `/api/work` endpoint, not a `/work` product page. The inherited KPI computations, API contracts, attention derivation, worktree-wins source selection, local-only collection, phase derivation and null-aware token rules remain unchanged. The plan approval remains pending.

The visual designer must now amend DESIGN.md and the replacement prototype to these rulings, run `npm ci && npm run build`, and observe the prototype in a real browser at 1440x1000 and 1920x1080. DESIGN.md and prototype files are intentionally not changed in this PM pass.

## Open Questions

- None. The visual designer has only the execution gate above; no unresolved product decision remains.