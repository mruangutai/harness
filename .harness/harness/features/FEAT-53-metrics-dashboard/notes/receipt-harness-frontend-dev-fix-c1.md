# FEAT-53 frontend repair receipt — c1

**Commit:** `fa921782d8404c8b635520be0cc1230d23fed6be`

## Owned paths

- `.claude/skills/harness/bin/dashboard/client/src/routes.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/routes.test.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/tiles.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/work-view.test.tsx`

## Finding evidence

- **V-02:** RED: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx` failed the new `keeps the available dashboard region usable when the other query fails` assertion because no `Repository KPIs unavailable` region existed. GREEN: the same command passed 13/13; independent KPI/work queries now retain the settled region and show its exact error plus Retry.
- **V-03:** RED: that command failed `renders a complete KPI panel and lands focus after an in-app KPI transition` because `/kpi/$n` rendered only the label. GREEN: 13/13; `/kpi/$n` now mounts `KpiPanel`, disclosure, and `/work/$id` row drill-down.
- **V-17:** RED: the new route test failed because no level-one KPI landing, focus transfer, or focus-visible rule existed. GREEN: 13/13; route titles are `tabIndex=-1`, in-app KPI/work link transitions land on them, and the shell supplies the signed `:focus-visible` ring / title exception.
- **V-18:** RED: the new geometry assertion failed against the prior `1200px` shell and no responsive rule. GREEN: 13/13; the shell declares `max-width:1600px`, 24px desktop padding, and 16px at `max-width:831px`.

## Verification

Passing focused tests (verbatim command):

```text
npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx src/work-view.test.tsx
Test Files  2 passed (2)
Tests  18 passed (18)
```

T-14 bounded source conjunct (build deliberately not run under the no-dist instruction):

```text
python3 -c "import pathlib,sys;s=''.join(p.read_text() for p in pathlib.Path('.claude/skills/harness/bin/dashboard/client/src').rglob('*.tsx') if not p.name.endswith('.test.tsx'));[sys.exit('missing '+k) for k in ['NoShipRecords','PreCapability','GradingCaveat','UnavailableValue','/kpi/','/work/'] if k not in s];[sys.exit('forbidden '+k) for k in ['107','122','/features','/kpis'] if k in s]"
# exit 0
```

Source runtime: started Vite from the client root and confirmed `curl -I http://127.0.0.1:5173/` returned `200 OK`. Headless Chrome loaded source at 1440×1000 and 831×1000; both DOMs carried `data-theme="dark"` and Vite `/src/main.tsx`. The standalone Vite server has no API proxy, so its `/api/*` requests cannot exercise real payload interactions; partial failures, KPI panel/drill-down, focus transitions, and responsive CSS are therefore proven by the focused source-runtime component suite above, not claimed as an end-to-end server/browser scenario. No build was run and no dist path was staged.
