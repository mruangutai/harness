# Receipt — harness-frontend-dev — FEAT-01-kaya-platform — SIMPLIFICATION (plan surface)

Angle file read: `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-simplification.md`
Also read: `harness-simplify/SKILL.md`, BRIEF.md, plan.yaml (all 10 tasks; some intents truncated at 768 chars by the reader). Flag-only; nothing applied. Altitude disposition: n/a (not the altitude angle). Verify commands not run.
Angle: SIMPLIFICATION. 6 findings (none blocking; none touch the settled set).

## S-1 — False dependency edge T-07 -> T-06 (low-med)
- File/line: plan.yaml:247 (`T-07 depends_on: [T-02, T-06]`); also :264 (`T-08 depends_on: [T-07]`).
- Summary: The static landing page is declared dependent on the API route task, while T-07's own intent (:257) forbids any browser import of server/mastra and the page is a static document.
- Cost: Landing waits behind the whole T-03..T-06 backend chain; T-08 reaches T-06 only transitively through T-07, so the real edge (probe needs route) is hidden behind a fake one (landing needs route). A reader reordering/dropping T-07 would silently break T-08's ordering.
- Alternative: `T-07 depends_on: [T-02]`; `T-08 depends_on: [T-06, T-07]`.

## S-2 — "Approved-system treatment" is a dead reference (low)
- File/line: plan.yaml:256 (T-07 intent); BRIEF.md SC-01 (line 15) carries the same phrase "native/system colours or approved-system counterparts".
- Summary: Styling spelled as two alternatives, "native/system colours ... or an existing approved-system treatment with both light and dark counterparts", in the same breath as "no additional presentation dependencies" and "do not invent a styling system". No approved system exists in the tree (Astryx is not a dependency in this plan per :149).
- Cost: The second branch has no referent, so an implementer or ui-reviewer must decide what qualifies; two acceptance spellings of one rule invite drift between BRIEF and plan.
- Alternative: One spelling in both places: "native/system colours with `color-scheme: light dark`; no styling dependency." Reintroduce the second branch only if/when a design system is actually adopted.

## S-3 — Landing acceptance restated across SC-01, T-02 and T-07 (low)
- File/line: plan.yaml:177 (T-02 page.test.tsx contract) and :255-257 (T-07 intent) both restate BRIEF.md:15 (SC-01): one main, one h1, README as plain text with no link, 320px/200% wrap, WCAG AA, no client state/chat/login. The T-07 title ("Render only the static ...") already says the exclusion.
- Summary: Same list of conditions written three times in three spellings (T-07 additionally re-lists exclusions that BRIEF "Out of scope" and PF-86e4a4c3 already carry).
- Cost: Any edit to the landing contract (e.g. h1 wording, breakpoint) needs three synchronised edits; a missed one yields T-02 tests and T-07 intent that disagree and an unresolvable red/green gate.
- Alternative: Keep the full condition list once (SC-01); T-02 and T-07 intents say "per SC-01" and keep only what is task-specific (file ownership, "no test/config edits", red-receipt requirement). Do not delete any assertion in the test contract; only de-duplicate prose.

## S-4 — Overlapping/subsumed lane rows (low)
- File/line: plan.yaml:46-54. Row `apps/web/src/app/*.tsx` (frontend-dev) matches `page.test.tsx` (a QA-owned T-02 file); row `apps/web/src/**/__tests__/*.test.ts` (:52) is a strict subset of `apps/web/src/**/*.test.*` (:49), same agent.
- Summary: One path routes to two agents by pattern overlap (page.test.tsx -> frontend-dev and qa), and one row is redundant.
- Cost: Resolution depends on first-match/ordering rules rather than the plan text; a reader can't tell who may edit `page.test.tsx`, which matters because T-07 forbids frontend-dev from touching tests. Redundant row is dead weight that can drift.
- Alternative: Replace `apps/web/src/app/*.tsx` with `apps/web/src/app/layout.tsx` and `apps/web/src/app/page.tsx` (the exact T-07 files), and drop the `__tests__` row (:52-54).

## S-5 — Test-selection rule stated twice inside T-01 and re-spelled in T-09 (low)
- File/line: plan.yaml:150 (Vitest projects selected "mutually exclusively") and :151 ("Unit discovery explicitly excludes subsystem __tests__ ...") restate one rule; :287 (T-09) respells all detect globs for harness.json.
- Summary: One fact (unit/component/functional/integration partition) has three spellings across two tasks.
- Cost: Glob drift between vitest.config.ts and harness.json detect yields double-selection or zero-selection, which SC-08 exists to forbid, and the plan gives no single source to compare against.
- Alternative: State the partition once (T-01), and have T-09 say "detect patterns mirror the T-01 Vitest project globs exactly" plus only the harness.json-specific parts (null runners, ui narrowing).

## S-6 — "No empty/speculative packages, Turbo/Nx, flat src" repeated in T-01, T-07, T-10 (low)
- File/line: plan.yaml:148 (T-01), :257 (T-07 "No speculative @kaya packages"), :305 (T-10 README directive); source rule at BRIEF.md:44 and SC-06 (:25).
- Summary: Same prohibition restated in four places, each in slightly different wording.
- Cost: Wording drift gives reviewers multiple non-identical standards for one inspection (SC-06); T-07 and T-10 can't violate it anyway (T-07 owns two app files, T-10 is docs).
- Alternative: Keep it in SC-06 and T-01 (the only task that can create a package); drop it from T-07 and T-10 intents.

## Not flagged (deletion test kept them)
- T-07 layout.tsx + page.tsx as separate files and two tests (framework-required, metadata vs render are distinct assertions).
- T-02 as separate red task (BRIEF Verification gaps :38 makes it a deliberate gate).
- Two-invocation T-07 verify (unit vs component projects are mutually exclusive by design).
