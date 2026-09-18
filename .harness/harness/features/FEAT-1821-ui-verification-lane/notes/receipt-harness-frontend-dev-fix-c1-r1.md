# T-03 send-back r1 receipt

**BLUF:** `a71ea2a9c294aa1326f101493a2a5b6709a25334` makes the FEAT-53 browser predicate executable rather than dispatch-only, but the committed dashboard fails its objective and keyboard checks. This receipt is therefore evidence for `FAIL`, not a completion claim.

## Scope

Committed path: `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts`.

## Original-finding closure blocks

1. **Objective predicates — unclosed.** The committed predicate now directly asserts C1 shared semantic header/72px/180px/edge geometry across overview, KPI and work routes; KPI 4+3 geometry/order/equal widths; seven resolved identity tokens and identity marks; six selected status labels; 22-count contrast floors; unavailable hatch/reason semantics; desktop table semantics/sticky headers/sort/no page overflow; source and axe routes. RED: the focused header run fails at `locator('header')` on overview (`feat-53.e2e.spec.ts:137`). The required header does not exist in FEAT-53 production source, which is outside the signed seven-file grant.

2. **C3 keyboard — unclosed.** The committed keyboard predicate now drives document-start tab order through segments, Repository, seven tiles and seven disclosures, six attention cards and filters; pointer and keyboard Selector restoration; KPI route landing and browser Back; attention/filter/layout retained focus; grilling/worktree restoration; KPI/work tab paths; route-title no-ring/fresh-load behavior; InfoDisclosure open/first-control/Escape restoration. RED: the focused keyboard run receives zero KPI links from the copied fixture (`feat-53.e2e.spec.ts:83`), so none of the downstream transitions can be honestly passed.

3. **Copied fixture and all 22 inspection interactions — unclosed.** The existing fixture still writes state sidecars and does not cause the copied runtime data to expose every prescribed state; the fixed-run keyboard result has no loaded KPIs. The 22 inspection entries remain generated and call `interact`, but the current runner cannot establish their state contents or complete interaction flow. Completing this requires deterministic serving/state support beyond the seven named files or a corrected fixture contract.

4. **Source/reporter/parser fail-closed — partially strengthened, unclosed.** `SRC-TOKENS` directly traverses `client/src`, excludes tests and the one theme declaration, checks raw hex, colour-scheme branches, font-size literals, and requires a token-bound chart mount. Existing reporter/parser code was not changed in this correction; no direct mutation proof was added for missing/duplicate/mismatched/absent-evidence/parser/reporter/incomplete accounting cases. Therefore this finding cannot be called closed.

## Evidence

RED header command:

```text
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c1-r1-red npm run test:ui -- --project=desktop-1440 --grep 'shared header geometry matches DESIGN'
1 failed — /?window=all&repo=all must expose a shared header; locator('header') found no elements.
```

RED keyboard command:

```text
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c1-r1-keyboard npm run test:ui -- --project=desktop-1440 --grep 'keyboard focus transitions and restoration match DESIGN'
1 failed — locator('[aria-label="Repository KPIs"] a') expected 7, received 0.
```

Exact T-03 verify:

```text
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=plan-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list
Total: 23 tests in 1 file
```

The focused `SRC-TOKENS` browser case passed (`1 passed (2.7s)`), served committed `dist` assets (`index-BGeYwNXA.css`, `index-Ddotz-pN.js`), and captured CDP WebP after traversing `client/src`; `/api/kpis` returned 500 while `/api/work` returned 200. The repaired full predicates still stop before capture. Generated `test-results/playwright-artifacts` is ignored local runtime output; no tracked runtime artifact was altered.
