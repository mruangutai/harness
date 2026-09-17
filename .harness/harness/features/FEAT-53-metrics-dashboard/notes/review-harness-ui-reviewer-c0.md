# UI review — FEAT-53 metrics dashboard — c0

**BLUF: FAIL.** The committed bundle at `9b34c65246136666bc69f220824bb262965e75c0` does not provide a usable three-route dashboard: direct loads of both detail routes are blank because their relative asset URL resolves below the route, and `/` either exposes only a partial error shell or crashes after the KPI request settles. This prevents SC-15 and SC-20 from passing and blocks meaningful runtime exercise of the specified KPI, disclosure, drill-down, gap-state, and work-detail interactions.

- review_sha: `9b34c65246136666bc69f220824bb262965e75c0`
- merge_base (repository-derived against `origin/main`): `a18d6a9f1f832084df84be22097a409d73bf4f61`
- mode: B
- cycles_used: 0
- launch: `python3 .claude/skills/harness/bin/dashboard/serve.py --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53 --port 8971`; real Flask entry point, committed `client/dist` bundle, Chrome headless CDP.
- pin integrity: tracked drift from the pin was confined to the feature ledger `feature.json`; dashboard source and bundle bytes were inspected from the pinned tree/current byte-identical paths. No mutable post-pin ledger content is used as review evidence.
- inspected: `/` at 1440×1000, 1920×1000, 831×1000 and 640×1000; `/kpi/1?window=90d&repo=harness`; `/work/FEAT-53-metrics-dashboard?window=90d&repo=harness`; invalid work id; default and explicit URL selection; 24 sequential Tab inputs; computed theme/focus; API unavailable state. Dark is the sole contracted theme, so light parity is not applicable.

## Findings

1. **HIGH — substance — T-16 — reader: harness-ui-reviewer. Direct product-route loads render blank.** `client/dist/index.html:7` loads `./assets/index-hkwR5g06.js`; Flask returns that same index for the resulting `/kpi/assets/...` and `/work/assets/...` requests (`serve.py:73-77`). Runtime evidence: both direct URLs returned HTTP 200 but had empty body text, no headings, links, buttons, tables, or SVGs; server log showed `GET /kpi/assets/index-hkwR5g06.js` and `/work/assets/index-hkwR5g06.js` returning 200 HTML. **Failure scenario:** an operator reloads or bookmarks `/kpi/1` or `/work/FEAT-53-metrics-dashboard` and sees a blank page, so the exact-three-route contract is nominal rather than usable.

2. **HIGH — substance — T-14/T-28 — reader: harness-ui-reviewer. The root route never reaches the contracted dashboard surface.** At initial settlement `/` showed the shared header and empty Status/filter controls, omitted Repository KPIs entirely, and showed `Work list unavailable — Dashboard request failed: 500`; after the `all/all` KPI request completed, the page became TanStack's `Something went wrong! / Show Error` boundary. Explicit `repo=harness` made both API calls return 500 because the configured fleet includes an unavailable repository, despite selecting one repository. `routes.tsx:15` owns this coupled surface. **Failure scenario:** the operator starts the documented server on this real checkout and cannot see the seven KPIs, 4+3 geometry, sparklines, real Status counts, rows, Kanban/Table contents, or any gap state.

3. **HIGH — substance — T-13 — reader: harness-ui-reviewer. Keyboard focus styling and route focus do not meet the accessibility contract.** Across the reachable shell, Tab focus computed as the browser default `rgb(0,95,204) auto 1px`, not the specified 2px text-token ring offset 2px; after the first cycle, focus reached `<body>` and then the error boundary. `routes.tsx:12-17` contains no route-transition focus management, and KPI route headings are `h2` rather than programmatic `h1` landings. **Failure scenario:** a keyboard user cannot reliably see the specified focus treatment or retain a meaningful landing when the page state/route changes. Accessibility failures gate at high.

4. **MED — substance — T-13/T-28 — reader: harness-ui-reviewer. The responsive container contradicts the pinned geometry.** `routes.tsx:13` hard-codes `maxWidth="1200px"`; DESIGN specifies 1600px. Runtime measured content width 1200px at both 1440 and 1920 (x=120 and x=360 respectively), so the accepted 1552px-wide 1920 reference cannot occur. At 831px and 640px, content begins at x=8, not the specified 16px gutter below 832px. **Failure scenario:** on the required desktop widths the KPI grid and table lose hundreds of pixels of intended scan width; at the narrow breakpoint controls sit half as far from the viewport edge as contracted.

5. **HIGH — substance — T-14/T-28 — reader: harness-ui-reviewer. SC-20's disclosure/drill-down surface is unreachable and the KPI route implementation cannot render the required panel.** Even aside from the direct-load asset failure, `routes.tsx:16` renders only a KPI label when data exists, rather than the panel/chart/table; `FeatureKpiContent` is imported at `routes.tsx:6` but used only from the work route. The root never rendered KPI tile links or InfoDisclosure controls in the live run. **Failure scenario:** an operator cannot open the escaped-defect or merged-PR sourcing rule one click from the number, then follow a row to `/work/$id`; SC-20 and the `/kpi/$n` part of SC-15 fail.

## Contract violations

- `client/dist/index.html:7`: relative bundle asset; specified: every one of the three product routes renders on direct load/reload.
- `routes.tsx:13`: actual `maxWidth="1200px"`; specified `max-width: 1600px`, 24px desktop and 16px sub-832 gutters.
- `routes.tsx:16`: actual KPI route is a label/loading card; specified one full KPI panel with chart, disclosure, and feature table.
- Runtime focus: actual browser-default 1px blue outline and body landing; specified 2px text-token ring offset 2px and preserved named landings.

## Accessibility

- High: focus-visible treatment is not the specified ring, and focus falls to body/error UI after state failure.
- High: detail routes expose no document content or route heading on direct entry.
- Accessible names observed on the reachable shell were mixed: Status buttons had names and icons were hidden; Selector triggers exposed only their current text (for example `All`) rather than an observed control name in the inspected DOM. The catastrophic route/root failures prevented a complete disclosure, table, chart-adjacent-text, and inline-expansion name/role audit.

## Assessed and dismissed

- Light/dark parity: dismissed as not applicable; pinned DESIGN C-3 explicitly makes dark the only theme. The runtime nevertheless computed `color-scheme: normal` and transparent body because the app never reached a stable painted dashboard; this is supporting evidence, not a separate light-theme finding.
- Horizontal overflow: not observed at 1440, 1920, 831, or 640 in the partial error shell (`clientWidth === scrollWidth`), but that does not validate the missing KPI/table layouts.
- Exact route registration: source registers only `/`, `/kpi/$n`, `/work/$id` (`routes.tsx:8,18`); retained as conforming registration, while finding 1 covers unusable direct routing.
- URL defaults: `/` normalized to `window=all&repo=all`; explicit `window=90d&repo=harness` remained in the root URL. Cross-route persistence could not be validated because detail routes were blank.
- Unavailable/gap states, sparklines, 4+3 grid, InfoDisclosure, real work rows, filters, inline grilling/worktree expansion, and detail ordering: not passed or silently dropped; runtime failures made each unreachable. Source tracing above identifies direct divergences where determinable.
- T-17/METRICS.md: known operator-deferred completion work, not a finding. T-25: operator-ratified and not relitigated.

## Gate disposition

- severity_max: high
- must_fix: restore direct-load assets for both nested product routes; make `/` survive real API success/failure and render its complete surface; implement the contracted KPI panel route; restore keyboard focus contract; use the pinned responsive container/gutters.
- SC-15: **FAIL** — the actual bundled surface does not conform and two product routes are blank.
- SC-20: **FAIL** — required disclosures and drill-down path are not operable in the bundle.
- Rendered visual completeness beyond the recorded measurements remains unverified because the bundle crashes before those regions exist; a human/UAT check is still required after these blockers are fixed.
