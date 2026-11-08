# Receipt — harness-dev-ops — 2026-10-05-7-simplify-eng — EFFICIENCY (plan surface, c2)

Angle file followed: `.agents/skills/harness-simplify/references/angle-efficiency.md` (only this angle). FLAG-ONLY; no plan/BRIEF/DESIGN/source edits, nothing run. Costs are static [INFERENCE], not measurements. Prior E-1/E-2/E-3 not re-raised.

**BLUF: PASS. Five advisory findings, all on the browser/runner path c2 added. None touches DESIGN. Independent nonempty suite assertions and predecessor-only gates are untouched by every alternative.**

Boundary runs deliberately left (not waste): T-09 cumulative `pnpm verify:platform` (plan.yaml:574-576), T-07/T-08 task-local Playwright gates, T-06 `--project functional --project integration` (one invocation, already combined), T-03/T-04/T-05 targeted file lists, T-09 per-runner zero-selection/assertion-fail demonstrations (reuse QA receipts, one-time).

## Findings

### EF-1 (med) — Browser state cross-product vs workers 1 and the 60 s target
1. File/line: plan.yaml:320 (T-02 intent), :241 (workers 1), :576 (target under 60s).
2. Summary: chat.e2e.spec.ts is specified as light/dark x {320px, 200%, both} x {provider, DB/readback, renewal, network, restoration failure} x {before, busy, failed recovery, success}, serial, retries 0.
3. Cost: [INFERENCE] about 2x3x5x4 = 120 page-level cases run serially, and that spec reruns at T-02/T-07 red, T-07 green and T-09. The same T-09 chain also has to fit four Vitest suites, typecheck, lint, a Next build and smoke:offline inside the stated 60 s target. The target looks unreachable on this text, so the plan is self-inconsistent.
4. Alternative: keep every assertion, but cut combinations that cannot differ. Error kinds change only text in one panel component, so cover the full kind list at one theme/size and the theme x size x state grid on one representative error. Reuse one page via `page.emulateMedia` and `setViewportSize` instead of reloading per case. The chat spec is stateless intercepted HTTP, so per-file parallelism is plausible even with workers 1 kept for platform.e2e.
5. Disposition: **apply** (pm, plan T-02 intent + T-01 Playwright text). It trades against resolved ui-reviewer finding PF-1481f39…, so pm must keep each distinct observable. If pm declines, restate the 60 s target as advisory.

### EF-2 (med) — Browser red run has no per-test/expect timeout bound
1. File/line: plan.yaml:241-242 (only startup is bounded), :511 (T-07 browser red run), :320.
2. Summary: T-07's red run executes the whole chat.e2e.spec.ts against a bare shell, so every case fails on a missing control.
3. Cost: [INFERENCE] each failure waits Playwright's default expect/test timeout, which is about 5-30 s, with workers 1 and retries 0. Times about 120 cases, that is tens of minutes for one red receipt. Reds repeat when the first fix misses.
4. Alternative: T-01 sets a short expect/test timeout in playwright.config.ts (local intercepted fixtures need a few seconds). Red receipts use one named case per behavior or `--max-failures`. The per-behavior receipt requirement (:511) is kept, and no assertion is weakened.
5. Disposition: **apply** (pm, T-01 line 241 and T-07 line 511). Hang-prone failing runs are the avoidable cost here, so this has the best cost/benefit of the five.

### EF-3 (low) — T-08 gate cold-starts Next twice on overlapping unmocked assertions, then T-09 repeats both
1. File/line: plan.yaml:534 (`pnpm smoke:offline && pnpm test:ui tests/e2e/platform.e2e.spec.ts`), :576, T-08 intent.
2. Summary: smoke:offline starts a real Next and checks controls, 401 before external calls and authorized 503. platform.e2e.spec.ts starts another real Next (webServer) and checks bootstrap, denial, missing-config and no fabricated reply.
3. Cost: [INFERENCE] two cold Next startups plus first-request compile per gate. T-09 repeats both through the Playwright suite and smoke:offline.
4. Alternative: no deletion, because merging the two would weaken an independent assertion. In T-08 intent, state that smoke:offline is the CLI-surface assertion owner and the 401/503 facts are asserted once per surface. Re-evaluate merging after T-09 timings exist.
5. Disposition: **briefing-row backlog**, per the harness-simplify rule that a duplicate-assertion finding is never applied. No apply, no DESIGN touch.

### EF-4 (low) — Playwright webServer mode and T-09 build ordering unspecified
1. File/line: plan.yaml:242 ("actual Next webServer"), :575 (chain lists "typecheck/lint/Next build" without order).
2. Summary: the plan does not say dev or start for the Playwright server, or whether the T-09 build precedes Playwright.
3. Cost: [INFERENCE] `next dev` compiles each route on demand inside the timed browser cases and again in smoke:offline. If the build ran first, `next start` would reuse its output. Task-local gates (T-07/T-08) have no prior build, so they need dev, which makes this a real mode choice.
4. Alternative: T-01 states the webServer mode. Order verify:platform as build, then browser/smoke on `next start`, only if the config can select the mode per invocation. Otherwise leave dev and accept the compile cost.
5. Disposition: **briefing-row backlog**. T-01/T-09 are main-session-direct and the implementer owns the choice.

### EF-5 (low) — typecheck detect glob omits generated/vendor exclusions
1. File/line: plan.yaml:567 (`apps/*/**/*.ts|apps/*/**/*.tsx|tsconfig.base.json`). The unit detector at :565-566 has the exclusions but typecheck does not.
2. Summary: this glob can match `apps/web/node_modules`, `.next` and next-env output, and any `.claude/worktrees` checkout.
3. Cost: [INFERENCE] a diff scan multiplies matches and can trigger a whole-project tsc where no source changed. It is a seconds-scale hot path on every scan.
4. Alternative: restate the same generated/vendor exclusion list as the unit detector, e.g. `apps/*/src/**`, and exclude worktree, `node_modules` and `.next`. Keep discovery otherwise unchanged.
5. Disposition: **apply** (pm, T-09 intent line 567). It is a wording-only change with no assertion impact.

## Checked and left (no finding)
- GET readback with `perPage:false` (plan.yaml:431) and the post-finish confirmation GET return the full single thread each turn, so the cost is O(n) per turn. A tail-only confirmation would need a second API contract plus a stricter predicate. Left: the local single-conversation operator scope makes it negligible, and splitting it would add a seam.
- D-02 HMAC and cookie checks per request, the Supabase admin client reuse and the storage pool (max 2) are not hot enough to cost anything.
- Lane serialization: T-01 and T-09 are main-session-direct by settled constraint. T-03/T-04/T-07 are parallel off T-02. T-05's dependency on T-04 does not lengthen the critical path.
- Per-kind unit/component/functional/integration invocations at the T-07 gate: same mechanism as the sealed E-1. Not re-raised.

## DESIGN-touching findings
None. EF-1 changes browser-test combination coverage only, not DESIGN text. pm should re-check that against PF-1481f39… when applying.

## Principles applied
- **Build the Lever** (`harness-craft/references/build-the-lever.md`): the cost analysis reused the plan's own task text and the prior digests rather than a new tool. No script was added because the assignment forbids running tools, so I cite the principle only as the reason none was built.
