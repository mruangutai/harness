```yaml
VERDICT: FAIL
DIGEST:
  headline: "All four original must-fix findings remain open at a71ea2a9c294aa1326f101493a2a5b6709a25334."
  mode: B
  in_scope: true
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: ui-reviewer
      summary: "Seven objective predicates — OPEN"
      why: "Each of the seven browser-spec branches materially narrows the corresponding signed Checks row instead of implementing every required clause."
    - kind: substance
      scope: task
      severity: high
      reader: ui-reviewer
      summary: "C3 keyboard and accessibility/focus transitions — OPEN"
      why: "The implementation neither covers nor reaches the full signed C-3 keyboard, restoration, focus-visible, route, announcement, and non-colour-equivalent transition contract."
    - kind: substance
      scope: task
      severity: high
      reader: ui-reviewer
      summary: "Deterministic copied fixture and all 22 inspection setups/interactions — OPEN"
      why: "The copied fixtures do not materialize the required state-specific inputs, and the inspection path does not establish and prove all 22 manifest states before capture and prototype comparison."
    - kind: substance
      scope: task
      severity: high
      reader: ui-reviewer
      summary: "SRC-TOKENS and reporter/parser fail-closed evidence — OPEN"
      why: "Reporter evidence accounting accepts missing, duplicate, mismatched, empty, and invalid evidence shapes without the required fail-closed negative proof."
  must_fix:
    - "Implement every clause of the seven T-02 objective rows, rather than representative selectors/counts."
    - "Implement and actually reach every C-3 keyboard, restoration, focus-visible, route, announcement and non-colour-equivalent transition."
    - "Materialize state-specific copied fixture inputs and prove every one of the 22 manifest setups/interactions before capture and prototype comparison."
    - "Make reporter evidence accounting exact and fail-closed, and provide negative proof for parser/reporter/accounting failure shapes."
  states_unspecified: []
  contract_violations:
    - path: "feat-53.e2e.spec.ts:156-229"
      actual: "Representative selectors, counts, and partial checks implement narrowed versions of all seven objective predicates."
      specified: "Every clause of the seven T-02 objective rows in DESIGN.md:873-880."
    - path: "feat-53.e2e.spec.ts:76-151"
      actual: "Only part of the keyboard and focus transition contract is implemented and the live run stops before downstream transitions."
      specified: "The full signed C-3 contract in DESIGN.md:638-691."
    - path: "fixture.ts:8-29; feat-53.e2e.spec.ts:233-261"
      actual: "Eleven copies of one fixture and five interaction branches do not establish all 22 manifest states."
      specified: "State-specific copied fixture inputs and proven setup/interaction for every inspection capture."
    - path: "ui-reporter.ts:22-43"
      actual: "Generic fallback evidence and at-least-one-attachment validation permit incomplete or mismatched evidence."
      specified: "Exact, fail-closed evidence accounting with negative proof for parser, reporter, and incomplete-accounting failures."
  a11y:
    - "The full C-3 keyboard, focus restoration, focus-visible, announcement, and non-colour-equivalent transition contract is not implemented or reached."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-c1.md
```

# FEAT-1821 T-03 UI fix review — c1

**BLUF:** FAIL. All four original must-fix findings remain open at `a71ea2a9c294aa1326f101493a2a5b6709a25334`. The lane now contains real browser operations, source traversal, CDP WebP capture, and fail-closed partial-run accounting, but it does not faithfully implement the signed predicates, keyboard contract, deterministic inspection states, or negative reporter/accounting contract. The observed FEAT-53 product failures are legitimate RED product evidence only for the predicates reached; they do not excuse code paths that never exercise the remainder.

## Original finding dispositions

### 1. Seven objective predicates — OPEN (high, substance, task)

T-03 binds “Implement every objective predicate … named in T-02” (`plan.yaml`, T-03). The browser spec has branches for all seven named predicates, but each materially narrows the signed Checks row (`DESIGN.md:873-880`):

- `C1-HEADER-GEOMETRY` checks minimum header height, Repository width **at least** 180px, one left-edge equality, and visibility of three radios (`feat-53.e2e.spec.ts:156-169`); it omits exact 180px width, product/breadcrumb composition and order, controls-before-selector order, footer edges, and right-edge equality.
- `KPI-R1` checks names rather than printed ordinals 1…7, two y-groups, and within-row equal widths (`:170-181`); it does not prove no span/empty slot or the signed grid occupancy.
- `DIR-KPI-IDENTITY` only proves seven tokens resolve and seven dot/sparkline marker nodes exist (`:182-187`); it never checks computed paint, required marks across panels/tables, alpha, or forbidden uses.
- `DIR-STATUS-LABEL` only finds one `[data-status-label]` per selected card (`:188-195`); it never compares computed status/token colours or neutral icon/count/background/border/top-line/selection.
- `C3-CONTRAST` builds 22 token values and compares all to the body background, then arbitrarily reuses the first 19 (`:197-206`). The contract requires exactly 20 named non-text pairings, 19 informational rendered-text pairings, and hatch stroke against hatch ground—not 22 values against one background.
- `C4-HATCH` checks one KPI route, text fragments, and a regex containing `45deg` (`:207-215`); it omits every S-2/S-4 overview/work-detail use, 1px/6px stops, computed stroke/neutral tokens, and the non-zero/nonblank invariant.
- `TBL-DESKTOP` checks only tables present on the initially loaded overview, sticky CSS, clickable headers, and page overflow (`:216-229`); it does not force/scroll region overflow, verify sticky geometry, verify sort changes, exercise every KPI table, or compare chart/table values and denominators.

The focused header failure reported at tip—no `<header>` on FEAT-53 production—is a live product defect caught by the portion that ran. It does not close the omitted assertions or downstream predicates.

### 2. C3 keyboard and accessibility/focus transitions — OPEN (high, substance, task)

`keyboard()` covers part of the overview order, pointer/keyboard Selector Escape, one KPI tile transition/Back, one disclosure Escape, attention-to-Status, one filter update, layout retained focus, grilling/worktree toggles, a short KPI order, and a short work-route order (`feat-53.e2e.spec.ts:76-151`). It does not cover the full signed C-3 contract (`DESIGN.md:638-691`): optional linked Overview breadcrumbs; Clear Filters; Kanban/Table, sortable/lane and row-control order; KPI sortable headers and FEAT/BUG links; work source links, KPI info icons, headers and row links; nonfocusability of badges/state marks/hatch/caveat/figures; pointer selection (not only Escape); keyboard selection; pointer outside-close; pointer attention/filter/layout no-ring states; every header/work filter; announced selected status; announced layout label; KPI-row and dashboard FEAT/BUG route landings; exact Back restoration for card/tile/row; outside-click disclosure restoration; and keyboard-restored ring assertions for disclosure/Back. It checks `aria-hidden` on all SVG/chart candidates on one KPI page but never proves adjacent same-value tables or the visible icon/label/reason equivalents required by C-3 clause 4.

The run that receives zero KPI links stops before these transitions. That is valid evidence that the live product/fixture combination fails, but not evidence that the unexecuted transition implementation is complete. Accessibility is therefore gating high severity. Dark-only is correctly configured and light mode is explicitly out of scope (`DESIGN.md:596-600`); no light-theme defect is filed.

### 3. Deterministic copied fixture and all 22 inspection setups/interactions — OPEN (high, substance, task)

`fixture.ts:8-29` copies the same `FIX-SHIPPED` directory eleven times, changes a small `feature.json`, and writes `fixture-state.json` plus a global `fixture-states.json`. It does not materialize the state-specific dashboard inputs promised by T-03 (attention, grilling/worktree rows, unavailable KPI payloads, zero-match combination, source failures with valid rows, request failures, overflow, or long content). The fixed-run receipt confirms `/api/kpis` returned 500 and the keyboard predicate saw zero KPIs, demonstrating that the copied fixture does not realize the required loaded state.

All 22 manifest rows are enumerated by the Python authority, but `interact()` has behavior for only five labels (`kpi-unavailable`/`disclosure-open`, `kpi-drill`, `work-drill`, `table-overflow`, `initial-request-error`; `feat-53.e2e.spec.ts:233-253`). `filtered-zero` does not apply filters or wait; source-error and long-content do not select or establish their fixtures; overview-default performs no state assertion; table overflow does not assert sticky ID remains visible; initial error merely focuses a button without establishing the error state; and inspection never compares against the approved prototype. `inspection()` then records the manifest’s fixture/setup strings regardless of realized browser state (`:256-261`), so the result can claim a state the screenshot never exercised.

The inspected `SRC-TOKENS--execution.webp` is a usable dark dashboard capture, but it shows a degraded default surface with “Repository KPIs unavailable” and a populated work table. It is useful live evidence for that run, not evidence for the 22 distinct inspection states. Rendered prototype/layout fidelity for those absent captures remains unverified; human/UAT comparison is still required once state realization works.

### 4. SRC-TOKENS and reporter/parser fail-closed evidence — OPEN (high, substance, task)

The source half is substantially improved: `sourceTokens()` recursively reads client TS/TSX, excludes the theme declaration and tests, rejects raw hex/theme branches/font-size literals, requires source presence, and requires at least one chart binding (`feat-53.e2e.spec.ts:45-68`). CDP capture validates RIFF/WEBP bytes (`:8-24`), and the reporter writes `harness-ui-results/1` with missing-accounting that correctly fails focused/list-only runs (`ui-reporter.ts:34-43`). The `plan-list` result at the pinned tip honestly reports zero observed and all applicable checks missing.

The finding nevertheless remains open. `ui-reporter.ts:22-29` silently substitutes a generic evidence object when an attachment label has no matching manifest row instead of failing the mismatch. `invalidEvidence` only asks whether a check has at least one attachment (`:37`), so inspection checks can omit 10 of 11 required per-project captures and still satisfy that condition. It does not reject extra/missing evidence labels, duplicate evidence labels, wrong route/state/setup metadata, empty files, non-WebP files, or a check status inconsistent with its method. No focused negative evidence demonstrates missing/duplicate/mismatched/absent-evidence/parser/reporter/incomplete-accounting cases. Parser invocation remains single-authority through `ui_contract.py` (`ui-manifest.ts:12-18`), and no pixel baseline was introduced, but those preserved constraints do not discharge reporter completeness.

## Gate

`must_fix`:

1. Implement every clause of the seven T-02 objective rows, rather than representative selectors/counts.
2. Implement and actually reach every C-3 keyboard, restoration, focus-visible, route, announcement and non-colour-equivalent transition.
3. Materialize state-specific copied fixture inputs and prove every one of the 22 manifest setups/interactions before capture and prototype comparison.
4. Make reporter evidence accounting exact and fail-closed, and provide negative proof for parser/reporter/accounting failure shapes.

No pixel-baseline requirement was added or inferred. The lane preserves 12 exact titles, 23 applicable project executions, CDP WebP, the Python parser authority, and `harness-ui-results/1`; those structural successes are insufficient for contract fidelity.
