# T-33 verification receipt

## Result

The amended predicates now model authored token ownership by explicit selector/property roles, rather than resolved-colour equivalence or the identity wrapper. Only `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts` was changed for T-33.

## Signed verification

```text
$ HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t33-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›"
23

$ git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client | grep -c "e2e/colour-placement.e2e.spec.ts"
1
```

The list still reports 23 project-expanded titles. A scoped diff check found no title, project applicability, capture, evidence, trace, or other predicate edit.

## Focused UI evidence

```text
$ HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t33-focused-final npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/colour-placement.e2e.spec.ts
4 failed
```

The KPI predicate correctly rejects every panel accent because its winning authored `border-top-color` is `currentcolor`, not the required `var(--color-metrics-kpi-N)`. The rerun also encountered pre-existing duplicate failure-evidence labels for both projects; no application or evidence code was changed. The first focused run completed the status predicate in both projects (2 passed) while KPI ownership failed (2 failed).

## Pre-existing T-32 work

Separately present and untouched client changes: `dist/assets/index-Ddotz-pN.js` (deleted), `dist/assets/index-mJo09rBC.js` (untracked), `dist/index.html`, `fixture.ts`, `src/gapstates.tsx`, `src/main.tsx`, `src/routes.tsx`, `src/theme.tsx`, `src/tiles.tsx`, `src/work-view.tsx`, and `vite.config.ts`.

## Principles applied

- Foundational Thinking: represented the eight selector/property roles and their token ownership as data, so required-use and exclusive-ownership checks share the same semantic allow-list.
