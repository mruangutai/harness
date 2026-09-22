# REUSE simplify receipt — FEAT-1821

**Findings: 2.** Both are behavior-preserving UI-test-support extractions; neither touches assertions. Suggested owner: `harness-frontend-dev` (the dashboard client/e2e surface).

## Findings

1. **File / line:** `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts:58` (also `contrast-hatch.e2e.spec.ts:37`, `geometry.e2e.spec.ts:24`, `keyboard.e2e.spec.ts:25`, and `tables-a11y.e2e.spec.ts:25`).
   - **Summary:** Five new tests reimplement the same WebP capture, duplicate-prevention, evidence-path, and attachment routine already implemented in `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts:12-30`.
   - **Concrete cost:** A change to evidence naming, RIFF/WEBP validation, duplicate handling, or capture stabilization now requires six lockstep edits; the divergent keyboard variant already has distinct soft-failure semantics that can silently drift from the other five.
   - **Alternative:** Extract the complete routine into an importable dashboard-client e2e support module, parameterized by `UiCheck` and optional evidence label, then import it from all six specs. **Behavior-preserving:** yes. **Assertion impact:** none; retain each spec's existing assertions and `afterEach` placement. **Owner:** `harness-frontend-dev`.

2. **File / line:** `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts:17` (also `contrast-hatch.e2e.spec.ts:25`, `geometry.e2e.spec.ts:12`, `keyboard.e2e.spec.ts:13`, and `tables-a11y.e2e.spec.ts:13`).
   - **Summary:** Five new specs duplicate the deterministic-clock, navigation, visible-body, and network-idle loader already present at `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts:32-42`.
   - **Concrete cost:** The fixed-clock and load-readiness protocol has six spellings, so a future fixture-time or page-ready adjustment can leave a subset of the UI lane executing with different setup.
   - **Alternative:** Export one `loadFixturePage(page, route)` helper from the same e2e support module and retain caller-specific assertion hardness only as an explicit option if needed. **Behavior-preserving:** yes. **Assertion impact:** none; preserve the current assertion forms/messages at call sites or in the helper. **Owner:** `harness-frontend-dev`.

## Skipped candidates

- **Settled:** The signed 23-test split, exact check titles/projects, `harness-ui-results/1` reporter/gate contract, CI Chromium installation, Mode B policy, active `ui` test kind, and committed WebP evidence are dispatch-settled and not reuse findings.
- **False-positive:** Repeated `loadManifest()` calls use the new canonical importable helper at `ui-manifest.ts:12-17`; they do not reimplement parsing or manifest normalization.
- **False-positive:** Per-file `test.afterEach` registrations are test-framework-local wiring; extracting the shared capture implementation removes the duplicated procedure without coupling independent spec registration.
- **Out-of-scope:** Plan/BRIEF and feature-history surfaces were not assessed for implementation reuse; plan-surface findings are flag-only and no plan duplication was evaluated.
