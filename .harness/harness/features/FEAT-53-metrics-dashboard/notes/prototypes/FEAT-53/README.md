# FEAT-53 metrics dashboard prototype

High-fidelity, dark-only Astryx prototype for the operator's three-route dashboard composition. It uses an invented fixture and never reads repository data.

## Run

```sh
npm ci && npm run dev -- --host 127.0.0.1
```

Open <http://127.0.0.1:5273/?window=all&repo=all&station=all&status=all&kind=all&layout=table>.

Production-build proof:

```sh
npm ci && npm run build
```

The prototype pins `@astryxdesign/core` and `@astryxdesign/theme-neutral` 0.5.2. `src/theme.js` adds feature semantic tokens; the application fixes `<Theme mode="dark">`. `InfoDisclosure` is the only popover pattern and uses the Astryx `Popover` and `IconButton` primitives.

## Contract represented

The product routes are:

- `/` — the shared Window and Repository header, Repository KPIs, then the Work List; its six Status shortcuts appear first, before the filters and layout toggle.
- `/kpi/$n` — one KPI panel; its FEAT/BUG rows open work detail.
- `/work/$id` — operational header first, then the selected FEAT/BUG KPI content.

There is no `/work` product route and no Work header toggle. The prototype-only `/__fixtures/gap-states` route makes S-1 through S-7 simultaneously judgeable without putting the honest-state gallery on the dashboard or in product navigation.

The shared header owns `window=30d|90d|all` and `repo=<id>|all`; both default to `all`, remain in the URL, and survive product-route navigation. The Work List owns its six Status shortcuts plus `station`, `status`, `kind`, and `layout=kanban|table`; Table is the default. Repository is deliberately not repeated as a list filter.

Status order is Needs You, Blocked, Stalled, Over Budget, Running, Stale. Each Status has an Astryx icon; work rows and cards keep neutral text and borders. Only the matching attention-card label uses the Status colour. Attention cards act as Status filter shortcuts without leaving `/`; the card matching the current `status` value carries the neutral selected treatment and `aria-current="true"`.

Both Work List layouts carry ID, Repository, Station / Phase, Status with reason, Elapsed / Phases, Runs, Cycles / Max, and Tokens. Grilling and worktree items expand inline; FEAT and BUG items drill to `/work/$id`. Partial token coverage reads exactly `unmeasured n of m runs`; an absent measurement is never displayed as zero, and no dollar cost appears.

At desktop widths the seven KPI tiles use a 4+3 split: tiles 1–4 are equal-width in row 1 and tiles 5–7 are equal-width in row 2, with no spanning tile or empty slot. This keeps the longest label, Usage by Agent / Model Tier, in the wider row while the narrower 339px tiles still hold the `display-1` figure, delta chip, and full-width sparkline without overflow. Below 1024px the existing two-column and single-column fallbacks remain. Every sparkline contains the latest fourteen daily points and spans the tile's inner width. Labels, dropdown items, and toggles use Title Case; supporting descriptions use sentence case.

## Browser observation

The current composition was observed in the running Vite application with Google Chrome over CDP on 2026-09-16. [observed-1440.png](./observed-1440.png) records the current 1440×1000 surface after selecting Needs You. [observed-1920.png](./observed-1920.png) is the earlier same-day KPI-width reference; card relocation was intentionally re-observed only at the 1440px design floor.

### Focus verification with real input

Observed with Google Chrome pointer and keyboard input on 2026-09-16:

1. **Fresh document load:** `document.activeElement` was `BODY`, the document contained zero
   `:focus-visible` elements, and the measured body outline was
   `rgb(255, 255, 255) none 3px` (`outline-style: none`).
2. **Repository pointer selection:** mouse-opening Repository and mouse-picking Harness restored the
   trigger as the active element with `:focus-visible = false` and
   `outline: rgb(250, 250, 250) none 3px`. Mouse-opening it again and dismissing with Escape produced
   that same no-ring value. Keyboard-opening and dismissing the same trigger preserved
   `outline: rgb(250, 250, 250) solid 2px`.
3. **Layout pointer selection:** mouse-clicking Table and then Kanban left each active segment with
   `:focus-visible = false` and `outline: rgb(250, 250, 250) none 3px`. The selected segment measured
   `background-color` and `border-color: rgba(255, 255, 255, 0.1)`, plus the neutral 1px inset edge
   and 2px bottom indicator; Astryx's white pill was absent.
4. **Keyboard entry:** after focus was placed on `BODY`, pressing Tab landed on the first control,
   the selected `All` window segment, with `:focus-visible = true` and
   `outline: rgb(250, 250, 250) solid 2px`.
5. **Dashboard Tab order:** after the Window and Repository controls, focus traversed each KPI tile
   and its InfoDisclosure in order 1…7, then Needs You → Blocked → Stalled → Over Budget → Running
   → Stale, then the Station, Status and Kind Selectors and the Table layout control. The Status
   cards therefore follow all KPI controls and precede every Work List filter.

The title exception was also exercised through a mouse-opened KPI route transition: `Rework` became
the active `<h1>` while retaining `outline: rgb(250, 250, 250) none 3px`; the same title received no
focus on a fresh document load.

### 1440×1000

- `clientWidth = scrollWidth = 1440`: no page-level horizontal overflow.
- The centred content frame measured 1440px including its 24px inline padding; the KPI grid's usable width was 1392px.
- The dashboard rendered Repository KPIs first, then the Work List heading, six ordered Status shortcuts, and finally the Station / Status / Kind filters with Table as the default layout. Their measured top edges were 113.98px, 619.98px, 683.98px and 769.98px respectively. Row 1 held KPI tiles 1–4 at 339px each; row 2 held tiles 5–7 at 456px each. No Work header toggle, `/work` list link, or honest-state gallery was present.
- No tile or text node overflowed and no label collided with its info control. The `display-1` figures and delta chips remained legible; row-1 sparklines measured 315px and row-2 sparklines 432px after card padding.
- The Work List opened with the six cards; its filters were exactly Station, Status, and Kind.
- Pointer interaction left the title, Repository selector, selected repository option, Kanban
  toggle, and Table toggle without an outline; the measured values are recorded above.
- Selecting Harness updated `repo=harness`; choosing Kanban and Table updated the URL in place. The
  active layout used the neutral surface and border tokens with the inset mark, not a white pill.
- Activating Needs You kept pathname `/`, set `status=needs-you`, reduced the table to two fixture rows, and marked only that shortcut `aria-current="true"` with the neutral selected treatment.
- GRILL-208 expanded inline and focus remained on its row control.
- Activating KPI 2 landed focus on the `Rework` `<h1>`; Browser Back restored focus to the exact KPI 2 tile.
- The fixture-only route showed S-1 through S-7 simultaneously and exposed no product-navigation link to itself.

### Earlier 1920×1080 KPI geometry reference

- `clientWidth = scrollWidth = 1920`: no page-level horizontal overflow.
- The centred content frame measured 1600px from x=160 to x=1760, proving the desktop max-width cap; the KPI grid's usable width was 1552px.
- The same 4+3 rows measured 379px per tile and 509.33px per tile respectively. No tile or text node overflowed and no label collided with its info control; sparklines measured 355px and 485.33px after card padding.
- The default table's `clientWidth` and `scrollWidth` both measured 1550px: no internal horizontal overflow.

## Fixture boundary and deviations

All names, counts, elapsed values, runs, cycles, tokens, repository ids, trend points, defect rows, and grading values in `src/fixture.js` are synthetic. They exist only to make every route, layout, drill, and honest state judgeable.

There are no known deviations from the operator-set route, layout, column, filter, icon, colour, focus, URL-parameter, or dark-only contract. The prototype uses plain SVG for the compact daily sparklines rather than selecting the product chart package; chart-substrate selection remains an implementation probe, while the approved visual and interaction contract is unchanged.
