# Receipt — harness-backend-dev — BUG-1016 T-01 simplify, REUSE angle (read-only)

Verdict: PASS, 2 advisory findings. Scope: diff 8d79d63d..89b7d960, `.omp/extensions/harness-hooks.ts` (tests read for impact only). No edits, no commands run for verification.

Reuse done well: EDIT_TARGET (hooks.ts:76) is shared by extractEditPaths (:83) and rootedInput; URI_SCHEME (BUG-2003) reused by rootTarget (:356); the existing `feature-root` CLI is the only resolver; policyRunner/PolicyResult reused.

## R1 — spend advisory re-implements feature-root lookup (reuse)
- hooks.ts:1396-1400 (pre-existing FEAT-59 block, now a second spelling beside new `featureRoot()` :983-1004). It spawns `inflight_registry.py feature-root` and takes `.trim().split("\n").pop()`, with no absolute/single-root validation, and declares a local `const featureRoot` (:1399) shadowing the new helper of the same name.
- Cost: two spellings of "resolve this run's checkout" with divergent validation (last-line vs exactly-one-absolute); the shadowed name invites misreading; an edit to the resolver contract must be made twice.
- Alternative: `const resolved = featureRoot(ctx.cwd); if ("root" in resolved) spendFeatureJson = featureJsonPath(resolved.root, currentFeature);` (keep try/non-blocking).
- Test impact: spend/stamp tests stub feature-root as `${root}\n` (omp-hooks.test.ts:1952, :2097), which satisfies the helper. Behavior CHANGE otherwise: multi-line or relative stdout would now be refused (no spend line) rather than last-line-accepted, and one lookup is cached per run. BUG-1016 lookup-count tests (rooted hooks, :1306-1307, :1397) use write/read/edit/main, not the orchestrator task path, so they are unaffected [INFERENCE: not run]. Worth doing only if the stricter validation is acceptable; it was pre-existing code, so optional.

## R2 — quote-strip spelled twice (reuse), low value
- hooks.ts:84 (extractEditPaths) and :355 (rootTarget) both spell `.trim().replace(/^"(.*)"$/, "$1")`.
- Cost: lockstep edit if quoting rules change (e.g. single quotes); two lines, small.
- Alternative: one `unquote(raw)` const used by both. No behavior change; all named BUG-1016 tests (quoting/whitespace survival) unaffected. Marginal; acceptable to leave.

No other reuse candidates: the test file's helpers (fixture/rootedHooks) extend the existing fixture via the `featureRoot` option rather than restating it.
