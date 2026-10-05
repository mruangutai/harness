# Receipt — harness-dev-ops — FEAT-01-kaya-platform — simplify EFFICIENCY (plan draft)

Angle: EFFICIENCY. Angle file read: `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-efficiency.md` (plus `harness-simplify/SKILL.md`).
Scope: `plan.yaml` (10 tasks) and `BRIEF.md`, read-only. Nothing run, nothing applied. All alternatives advisory; routes to harness-pm.

## BLUF
3 low-cost findings, all seconds-scale and none blocking. The plan's runner costs are otherwise targeted. Per-task verifies name files or projects, and only T-06 and T-09 run wider sets.

## Findings (five-part shape)

### E-1 — T-07 verify starts two vitest processes
- File/line: `plan.yaml:253` (T-07 `verify:`).
- Summary: `vitest run --project unit src/app/layout.test.ts && vitest run --project component src/app/page.test.tsx` makes two pnpm/vitest startups for two files.
- Concrete cost: one extra pnpm-filter plus vitest cold start, about 1–3 s ([INFERENCE]; not measured). This is a one-shot task gate, so it is cosmetic.
- Alternative: one invocation, `vitest run --project unit --project component src/app/layout.test.ts src/app/page.test.tsx`. The two projects are mutually exclusive by T-01 design, so selection is identical. Keep the zero-selection failure per project.

### E-2 — Root `test` may be four process launches
- File/line: `plan.yaml:150` (T-01 intent: "test as these four offline suites"). The T-09 gate at `plan.yaml:289` pays this cost again, and so does the SC-01 README sequence (`BRIEF.md:15`).
- Summary: the draft does not say whether `pnpm test` chains `test:unit && test:functional && test:integration && test:component` or runs one `vitest run`. Chaining costs four pnpm and vitest cold starts plus four config and project resolutions.
- Concrete cost: about 4–10 s of the 60 s `verify:platform` target at `plan.yaml:289` ([INFERENCE]). It is paid at every full-gate run and by every operator following SC-01.
- Alternative: keep the per-kind scripts, because `harness.json` needs one cmd per kind. Define `test` as a single `vitest run` across all four projects. The projects are already mutually exclusive and zero-selection-failing. State this in T-01 so the choice is not left open.

### E-3 — `verify:platform` ordering is unstated, and its serial total counts against the 60 s target
- File/line: `plan.yaml:285,289` (T-09). The script's definition is not visible in the T-01 text I could read, which was truncated.
- Summary: the gate runs typecheck, lint, the four suites, `next build`, and the offline probe. The probe starts a real Next process and may run its own compile or build.
- Concrete cost: if the probe runs `next dev` or a second `next build` after the gate's own `build`, the Next compile is paid twice. That is tens of seconds against a stated target under 60 s. If `build` then `next start` is used, nothing is wasted. I could not confirm which (`plan.yaml:271` truncated).
- Alternative: specify in T-01 or T-08 that the offline probe reuses the `.next` output from the gate's `build` through `next start`. Run typecheck and lint concurrently (`pnpm -r --parallel` or `&`-joined) ahead of the sequential build and probe. Neither check depends on the other.

## Not flagged (deliberate, costed as boundary evidence)
- T-09 `pnpm verify:platform` is the one cumulative full run, at the terminal boundary.
- T-08 `pnpm smoke:offline` and T-09's re-run of the probe: T-08's is its own task gate and T-09's is the boundary, so neither is waste.
- T-06 `--project functional --project integration`: its first run covers the T-02 integration file whose subject finishes at T-05, so it is not a redundant earlier suite.
- T-03, T-04 and T-05 verifies name explicit files or projects, so they are targeted. T-02 is MANUAL by design.
- T-01 exact-release engine, peer and type inspection, and T-10's reuse of those results: one-time registry and metadata reads, documented once.
- T-09 temporary-TypeScript-error and zero-selection demonstrations: one-shot proof of gate behaviour, required by SC-08.
- T-10 `git diff --check`: trivial.
- No repeated whole-file reads across sequential tasks beyond ARCHITECTURE.md and DECISIONS.md. Those are read by T-01 and cited by dependents, which is cheap.
