# BRIEF — FEAT-1821 UI verification lane

## Problem

The operator and reviewers cannot rely on the current UI gate to catch visible defects in the served committed dashboard bundle. The `ui` kind has no runner, the UI reviewer audits source instead of pixels, and three FEAT-53 validation rounds passed a bundle whose missing CSS and visible contract divergences were obvious in a browser, making a green validation record materially misleading.

## Done when — by perspective

**operator** — I can rely on a real-browser lane to render the committed client bundle at the two desktop viewports, fail on measurable DESIGN.md violations or missing evidence, and leave reviewable screenshots and structured results. FEAT-53 supplies the first honest signal: its known visual defects are recorded RED here without this feature fixing them.

**code maintainer** — I can extend a DESIGN.md check table and its Playwright specs through one explicit check-id contract, distinguish browser assertions from inspection-only judgment, and understand the versioned evidence without reverse-engineering the runner. Shared-component changes cannot silently evade every affected surface.

**reader (QA / ui-reviewer)** — I can grade the built surface from committed per-test screenshots and results tied to DESIGN.md, rerun the same lane when needed, and fail rather than improvise when a listed dimension has no evidence. Mode B does not depend on ad-hoc CDP or browser scripting.

**orchestrator** — I can route and gate UI work predictably: the `ui` kind is active with a real command, CI installs its browser, the interaction-flow matrix branch fails when a touched surface lacks specs, and enforcement-layer changes remain explicit main-session-direct work.

## Success criteria

- SC-01 (operator): The lane starts `serve.py --root <fixture>`, exercises the served committed dashboard bundle in pinned Chromium projects at 1440 and 1920 widths, and returns a failing status when a measurable DESIGN check fails; fail-first evidence demonstrates that this outcome was not green before the lane existed.
  verify: automated  evidence: ui
- SC-02 (operator): Every executed check leaves a non-empty WebP screenshot and one record in `runs/<id>/ui/results.json`; viewport-sensitive and inspection checks execute at both configured projects, while a row declared viewport-independent executes once at its declared project. Playwright HTML reports and traces remain local and gitignored, while results and screenshots are committable.
  verify: automated  evidence: ui
- SC-03 (operator): FEAT-53's initial lane run is committed as an expected RED result that records the current status of each named header geometry, KPI identity-hue, status-label-colour, and table divergence, fails for every one still present at build time, and does not change FEAT-53 production code.
  verify: automated  evidence: ui
- SC-04 (operator): Pixel baselines do not gate by default; only a DESIGN.md Checks row that explicitly opts into a pixel baseline may use `toHaveScreenshot` as a gate.
  verify: automated  evidence: ui
- SC-05 (code maintainer): DESIGN.md `## Checks` rows carry a unique check id, the plan-pinned exact Playwright spec title, touched surface, method, project applicability, and explicit observable predicates or inspection evidence manifest; the lane fails when a required row or applicable project is absent from results, duplicated, mismatched by title, or lacks its required screenshot evidence.
  verify: automated  evidence: ui
- SC-06 (code maintainer): `results.json` declares schema `harness-ui-results/1` and records the feature, run id, DESIGN path, served bundle commit, projects with viewports, listed, applicable, observed and missing ids, and per-check id, exact title, method, surface, project, status, screenshot evidence with route, fixture state and interaction labels, and errors so QA and the UI reviewer read one contract.
  verify: automated  evidence: ui
- SC-07 (code maintainer): At the pinned `review_sha`, the deterministic FEAT-53 fixture and Playwright config cover attention states, grilling and worktree rows, unavailable KPI states, filtered zero, source-error and request-error states, overflow and long content, fixed browser time, dark colour scheme, reduced motion, locale, timezone, and scale factor without changing production behavior.
  verify: inspection
- SC-08 (reader): At the pinned `review_sha`, UI reviewer Mode B is required to consume the committed lane results and screenshots against DESIGN.md and the approved prototype, verify the recorded route, fixture state, interaction setup, viewport and served-bundle pin, may rerun only the configured lane, never substitutes ad-hoc CDP or browser scripting, and returns FAIL for a listed dimension whose evidence is missing, unreadable, stale, mismatched, or incomplete.
  verify: inspection
- SC-09 (reader): At the pinned `review_sha`, the Checks table and its exact-title specs assign header and KPI geometry, computed identity and status colour placement, keyboard order and every C-3 focus transition or restoration, contrast floors, hatch stops, desktop table overflow and sticky behavior, source-token rules, axe results, and visible non-colour equivalents to executable predicates. Dense-versus-airy hierarchy and holistic prototype fidelity remain explicitly inspection-only under a route, state, interaction, viewport and screenshot manifest.
  verify: inspection
- SC-10 (orchestrator): `test_kinds.ui` is activated only after its non-null command exists, its detect pattern reaches the dashboard Playwright specs, and QA treats runner misconfiguration, contract-parser failure, missing applicable ids, absent screenshots, and a required interaction-flow lane with no Checks contract as blocking or failing states rather than skips.
  verify: automated  evidence: unit
- SC-11 (orchestrator): Any change under the dashboard client package requires the package's complete Checks table contract; the `has_interaction_flow` branch fails before browser execution when that table or any required spec is absent, so a shared-component change cannot evade coverage through route classification.
  verify: automated  evidence: unit
- SC-12 (orchestrator): At the pinned `review_sha`, the required CI job runs pinned Chromium installation from the dashboard client package with `npx playwright install --with-deps chromium` immediately after that package's existing `npm ci` step.
  verify: inspection

## Verification gaps

- `typecheck` has no runner: this feature does not claim a repository-wide static TypeScript proof; Playwright collection and the existing component runner carry executable module-load coverage instead.

## Constraints

- The operator-set base is `feat/FEAT-53`, and this feature merges back there; `main` has no dashboard client and cannot prove this lane against the real consumer.
- DEC-35 SUPPLIES the fixed `has_interaction_flow` matrix predicate and the test-kind command/detection contract.
- DEC-62 SUPPLIES separate DESIGN.md authorship by visual-designer and Mode B audit by ui-reviewer.
- DEC-174 BLOCKS team execution of `harness.json`, enforcement gate scripts and their tests, and `.claude/agents/harness-ui-reviewer.md`; each is main-session-direct.
- DEC-179 SUPPLIES explicit plan-time routing for every ungranted or carved-out surface.
- DEC-187 BLOCKS a required `ui` kind from remaining unresolved, null, empty, or silently skipped.
- Playwright uses `@playwright/test` and `@axe-core/playwright` in the dashboard client package; its `webServer` invokes `serve.py --root <fixture>` and it defines 1440 and 1920 viewport projects.
- visual-designer owns the DESIGN.md Checks table; frontend-dev owns Playwright configuration, support code, fixture extension, and specs; dev-ops owns the CI browser-install step.
- Screenshots are always evidence. Pixel baselines are opt-in only. Committed evidence is `runs/<id>/ui/results.json` plus per-test WebP screenshots; HTML reports and traces are local-only.

## Out of scope

- Fixing FEAT-53's header, hue, status-label, or table defects; FEAT-53 resumes to fix the RED signal.
- Light theme or layouts below 640 px, because DESIGN C-3 and its existing out-of-scope ruling exclude them.
- A baseline-approval workflow for pixel diffs; pixel baselines remain opt-in and no approval touchpoint is added here.
- Storybook or any component gallery; the prototype's `/__fixtures/gap-states` idea remains FEAT-53's choice.
- Retro-auditing older UI features; the lane applies from its landing forward.

## Approval

status: pending
