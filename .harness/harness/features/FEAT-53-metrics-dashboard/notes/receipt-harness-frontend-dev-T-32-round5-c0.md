# T-32 round 5 receipt

## Repeatedly failed premise and census

The repeatedly failed premise was that C3's timeout represented a focus-restoration failure after navigation. The rerunnable DOM/focus/state census at `.claude/skills/harness/bin/dashboard/client/dom-focus-census.mjs` disproved it before this fix: `/kpi/4` had no `FEAT`/`BUG` link, while `/work/FEAT-53-UNAVAILABLE` rendered an empty `aria-label="Work item"` link to `/work/undefined`; the KPI 7 disclosure left focus on its trigger because its only dialog button was Astryx's excluded fallback close control. The focused C3 trace showed dashboard-row navigation and route-title focus passing before the test timed out waiting for KPI 4's missing row link.

Census command:

```sh
node dom-focus-census.mjs
```

Observed state before the fix:

```text
empty work link: aria-label="Work item", href="/work/undefined?window=all&repo=all"
KPI 4 FEAT/BUG links: none
KPI 7 disclosure active element: About Merged PRs Over Time trigger
KPI 7 dialog buttons: only generated Close popover fallback; not focused
```

The next premise — that restoring KPI/work row links alone would make their C3 Tab clauses pass — also failed. The same census after the mapping fix found the first restored KPI 4 work link behind `Feature`, `Cycles Used`, and `Maximum Cycles` header buttons; C3 requires the info trigger followed directly by displayed row controls. The disclosure portion now passes its state census: the caller-owned `Close` control is focused and the generated fallback remains second.

```text
KPI 4 tabs 1–8: Overview, 30d, 90d, All, Repository, About Escaped Defects, Feature, Cycles Used
KPI 7 disclosure first button: Close (focused)
```

The header-focus correction exposed a third premise failure: unfiltered generic KPI data preserves the expected row sequence. Its leading `FIX-*` rows are legitimate links but C3's KPI-row contract scopes the displayed controls to `FEAT|BUG`; the first matching link was behind those `FIX-*` links. The rerunnable census established the actual order as `About Escaped Defects → FIX-EMPTYDATE → FIX-NOAPPROVAL`, so the KPI row set must use the contract's FEAT/BUG identity domain.

The fourth premise — that the module-local route target survives every direct KPI-to-work transition — failed. C3 now reached the KPI row and rendered `/work/FEAT-53`, but the route title remained inactive. Route-intent persistence must therefore use the navigation boundary rather than a component-local variable.

The persisted-target attempt exposed its own failed premise: the route-title ref exists when the landing effect first runs. Query-backed routes initially render loading content, so that effect consumed the pending target while `title.current` was null. Landing must wait for the loaded title.

With route landing repaired, the full C3 flow exposed two remaining state facts: pointer-opened Astryx Selectors regained a keyboard ring after their keyboard selection/dismissal, and attention-card filtering updated URL state without restoring focus to Status. Both are post-interaction state transitions, not route/data failures.

