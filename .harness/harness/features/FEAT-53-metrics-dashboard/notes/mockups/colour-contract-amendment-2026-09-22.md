# Colour contract amendment — 2026-09-22

## Decision

Approve a predicate-only amendment to `DIR-KPI-IDENTITY` and `DIR-STATUS-LABEL`. The palette, placements, required marks, surfaces, projects, routes, neutral treatments and captures do not change. This amendment needs operator approval because it changes the executable wording of the design contract. It needs no new prototype because it does not change the user-visible design or interaction.

## Why the previous predicates were impossible

`colour-placement.e2e.spec.ts`'s `expectNoOtherPaint` excludes only the selector passed to `body *:not(...)` (`expectNoOtherPaint`, lines 46–51). `kpiIdentity` passes `[data-kpi-identity-mark="N"]` (line 76), but the eight required marks are descendants with their own data selectors (lines 68–75). CSS `:not([data-kpi-identity-mark="N"])` excludes the wrapper itself, not its descendants, so the predicate first requires those descendants to use the KPI colour and then reports the same descendants as forbidden. The round-2 results record ten false offenders for KPI 1–3 and 5–7 and eleven for KPI 4 in both desktop projects (`runs/2026-09-22-t32-round2-eng/ui/results.json`, `DIR-KPI-IDENTITY` records); the T-32 receipt independently identifies the same wrapper/descendant contradiction.

`statusLabels` resolves each status token to a computed colour and asks `expectNoOtherPaint` to reject that colour everywhere except the matching label (lines 80–103). The immutable token table assigns both `kpi-4` and `status-over-budget` `#F58BC2` (`DESIGN.md`, token table rows `kpi-4` and `status-over-budget`). The round-2 `DIR-STATUS-LABEL` records therefore report KPI 4's required marks as Over Budget offenders at both widths. Computed RGB equality cannot identify which semantic custom property owns a declaration.

## Exact predicate contract

### `DIR-KPI-IDENTITY`

For every KPI `N = 1…7`, the allow-list is exactly these selector/property roles:

| Semantic mark | Selector | Owned paint |
|---|---|---|
| 8px label dot | `[data-kpi-identity-dot="N"]` | `background-color: var(--color-metrics-kpi-N)` |
| sparkline stroke | `[data-kpi-sparkline-stroke="N"]` | `stroke: var(--color-metrics-kpi-N)` |
| 12%-alpha sparkline fill | `[data-kpi-sparkline-fill="N"]` | `fill: var(--color-metrics-kpi-N)` and `fill-opacity: 0.12` |
| sparkline end dot | `[data-kpi-sparkline-end-dot="N"]` | `fill: var(--color-metrics-kpi-N)` |
| panel accent | `[data-kpi-panel-accent="N"]` | `border-top-color: var(--color-metrics-kpi-N)` |
| Shape B line | `[data-kpi-shape-b-line="N"]` | `stroke: var(--color-metrics-kpi-N)` |
| Shape B y-title | `[data-kpi-shape-b-y-title="N"]` | `fill: var(--color-metrics-kpi-N)` |
| column-header dot | `[data-kpi-column-dot="N"]` | `background-color: var(--color-metrics-kpi-N)` |

The E2E predicate must make both assertions:

1. **Required use:** every required rendered instance exists, its unresolved winning authored declaration references exactly `--color-metrics-kpi-N` on the named property, and its computed paint equals that token's resolved value; the sparkline fill also computes to `fill-opacity: 0.12`.
2. **Exclusive ownership:** no other rendered selector/property declaration references `--color-metrics-kpi-N`. This exclusion covers deltas, grades, statuses, text, other borders/backgrounds, gaps and every unnamed role. It is a token-reference scan, not a resolved-colour uniqueness scan.

`[data-kpi-identity-mark="N"]` is an unrelated structural wrapper. It is not the allow-list or exclusion boundary. A descendant is allowed only when it independently matches one of the eight selectors and the corresponding property above.

### `DIR-STATUS-LABEL`

Use the exact pairs Needs You/`needs-you`, Blocked/`blocked`, Stalled/`stalled`, Over Budget/`over-budget`, Running/`running`, and Stale/`stale`. For each slug `S`:

1. `[data-status-label="S"]` must have an unresolved winning `color` declaration that references exactly `--color-metrics-status-S`, and its computed colour must equal that token's resolved value.
2. No other rendered selector/property declaration may reference `--color-metrics-status-S`.
3. On the same surface, each KPI token reference remains legal only on the eight KPI selector/property roles above. In particular, the KPI 4 marks must reference `--color-metrics-kpi-4`, while the Over Budget label must reference `--color-metrics-status-over-budget`. Their common resolved value `#F58BC2` neither violates nor proves semantic ownership, and neither token may substitute for the other.
4. Before selection and again after selecting each card, assert that card's icon, count, background, border, top-line and selected treatment compute to their required neutral tokens.

“Unresolved winning authored declaration” means the declaration value before custom-property substitution, whether supplied by a CSS property or SVG presentation attribute. Computed style remains the appearance check; it must not be used to infer semantic token identity when two tokens resolve equally.

## Strictness and preserved coverage

The corrected checks are equally strict: they still require every intended coloured mark, prohibit each semantic token on every other role, and additionally prevent equal-valued tokens from being swapped. Only the impossible proxy boundaries are removed. `DIR-KPI-IDENTITY` remains `all-routes`, automated independently in `desktop-1440` and `desktop-1920`, with the overview plus active-KPI full-page capture. `DIR-STATUS-LABEL` remains `overview-attention`, automated in the same two projects, with the six-card selected-state capture. No palette value, route, surface, mark, neutral assertion or capture requirement changes.

## Evidence inspected

- `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts`: `expectNoOtherPaint`, `kpiIdentity`, `statusLabels`, and the eight current KPI data selectors.
- `.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md`: token table and Checks rows `DIR-KPI-IDENTITY` / `DIR-STATUS-LABEL`.
- `.harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-22-t32-round2-eng/ui/results.json`: both failed colour checks in both desktop projects.
- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-frontend-dev-T-32-c2.md`: engineering-round contradiction report.
