# FEAT-53 · plan/product-c2 — the batched write pass

**BLUF: every MF-1..MF-8 finding is applied, none declined. 17 tasks → 20, 19 decisions → 20, no
pre-image id dropped, `check-plan-routes.py` exits 0 with 0 violations. THREE items are recorded as
operator decisions outstanding at signature — D-08's unnamed fallback (MF-2), D-20's
client-build-at-all (eng Q1), and nothing else: MF-7's third branch did not arise.** Approval stays
`pending`; no `approval:` key exists in plan.yaml.

## Counts, and the recreate's honesty check

| | before | after |
|---|---|---|
| tasks | **17** | **20** (added T-18, T-19, T-20) |
| decisions | **19** | **20** (added D-20) |

Pre-image kept at `/tmp/FEAT-53-plan-preimage.yaml`. Diffed the id sets with `yaml.safe_load`:
`dropped tasks []`, `dropped decisions []`. `status: plan`, `approval` key absent,
`lanes.resolved_at: 38dd36222258240b5dab251eb48ef869fde35447` = live worktree HEAD
(`git rev-parse HEAD`).

**Route: one recreate, not 25 amends.** MF-3 added a task, which recreates the file anyway, so every
text change rode the same corrected proposal rather than ~25 sha-guarded `amend` calls. The proposal
(`notes/research-FEAT-53-plan-proposal.md`) was rebuilt from the pre-image by 34 exact-substring
replacements, each asserted to match **exactly once** — the transform refuses at the first
ambiguous or missing anchor, which is what makes a whole-file recreate as safe as an amend.
Route used: `plan-merge.py apply` (missing target → writes whole) then `set-feature-station`.

## `check-plan-routes.py` — verbatim

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01: declared main-session-direct (.harness/team-config.yaml ungranted)
OK T-02: declared main-session-direct (.claude/skills/harness/templates/gitignore.snippet, .gitignore ungranted)
OK T-03 granted to harness-dev-ops
OK T-04 granted to harness-backend-dev, harness-dev-ops
OK T-05 granted to harness-orchestrator, harness-visual-designer
OK T-18 granted to harness-backend-dev, harness-dev-ops
OK T-06 granted to harness-backend-dev, harness-dev-ops
OK T-07 granted to harness-backend-dev, harness-dev-ops
OK T-08 granted to harness-backend-dev, harness-dev-ops
OK T-09 granted to harness-backend-dev, harness-dev-ops
OK T-10 granted to harness-backend-dev, harness-dev-ops
OK T-11 granted to harness-backend-dev, harness-dev-ops
OK T-12 granted to harness-backend-dev, harness-dev-ops
OK T-13 granted to harness-backend-dev, harness-dev-ops
OK T-14 granted to harness-backend-dev, harness-dev-ops
OK T-15 granted to harness-backend-dev, harness-dev-ops
OK T-16 granted to harness-backend-dev, harness-dev-ops
OK T-17 granted to harness-documentor
OK T-19 granted to harness-backend-dev, harness-dev-ops
OK T-20: declared main-session-direct (.claude/commands/harness-plan.md, .claude/commands/harness.md, .claude/skills/harness-uat/SKILL.md ungranted)
0 violation(s) across 1 plan(s)
```
Exit 0.

## MF-1..MF-8 — each one, applied

- **MF-1 — both write paths had no caller. APPLIED as two tasks, merged with ALT-3's homing fix.**
  **T-19** (`cross_module`, backend-dev) adds `trend.record_ship()` and calls it from
  `gh-sync.py`'s `cmd_ship` (`gh-sync.py:1423`), the code that runs at the user-gated ship step;
  its verify is an **AST check** that `cmd_ship` contains a call named `record_ship` — discriminating,
  because that name does not exist today. Wrapped so a metrics failure never aborts a ship.
  **T-20** (`docs`, main-session-direct) adds the three `record()` call sites at the three moments
  D-16 names: `commands/harness-plan.md` (approval_request), `commands/harness.md`'s `awaiting_user`
  row (escalation), `skills/harness-uat/SKILL.md` (uat_request). All three resolve `NOBODY` under
  `check-domain.sh --resolve`, hence the lane. **ALT-3**: `touchpoints.py` moved out of
  `bin/dashboard/` to `bin/touchpoints.py` in the same recreate.
- **MF-2 — D-08 named a dead package. APPLIED (the correction) + ESCALATED (the choice).** D-08 no
  longer names `react-charts`; it states that no fallback library is named, records both live options
  and recommends accepting the alpha with a rollback, **because T-18 now probes before any client UI
  exists** so a STOP costs one toolchain task. Marked an operator decision outstanding at signature.
  BRIEF `## Constraints` carried the same false fact and is corrected there too.
- **MF-3 — the probe ran after the client was built. APPLIED as T-18.** Probe-only, `depends_on:
  [T-01, T-04]`, writes `client/CAP-probe.md`, writes no chart and no UI. **T-13 and T-15 both now
  wait on T-18**, so a STOP changes course before *any* client work is sunk, not just before T-15.
  CAP list unchanged, CAP-01..CAP-13 (LD-1).
- **MF-4 — the verify could not pass on the STOP branch. APPLIED.** T-18's verify asserts all 13 CAP
  rows plus a final line matching `^VERDICT: (PROCEED|STOP)$` — satisfiable on **both** branches, and
  its intent says so explicitly ("recording an honest STOP is this task succeeding"). T-15's verify
  no longer references the probe at all, because on STOP T-15 is never dispatched. Literal `|`
  blocks throughout; no folded `>` anywhere in the plan.
- **MF-5 — `T-12.depends_on` omitted T-08. APPLIED.** Now `[T-03, T-08, T-10, T-11]`.
- **MF-6 — `/assets/` had no Content-Type. APPLIED, with a gate.** T-12's intent requires
  `mimetypes.guess_type` plus an explicit fallback table (.js/.mjs/.css/.html/.svg/.woff2/.map), and
  **T-12's own verify now runs a test case asserting a `/assets/` JS response's `Content-Type` names a
  JavaScript type and never `text/plain`** — against a temp root with a stub `dist`, so the case does
  not wait on T-16's real bundle. T-16's smoke fetch reports the real header too.
- **MF-7 — the ceiling was inside its own measurement. APPLIED, both of the two branches that are
  mine; the third did not arise.** (1) T-06 is pinned to ONE `git diff --numstat main...branch`
  subprocess per feature, never merge-base + diff (33.5ms vs 56ms/branch, ≈1s of budget). (2) T-09
  memoises the plan read by `feature_id` (≈0.78s, 15–18% of budget) and T-06/T-09 both load through
  `harness_yaml.load_plan`. (3) **The ceiling is now 8.0s, not 5.0s**, with the measured basis
  written into the task: honest total 4.3–5.3s at today's scale, ≈3.6s projected with the two pins.
  D-06's and D-09's false 1.1s baselines are corrected — a decision may not rest on a false fact —
  and T-12's intent says that exceeding 8.0s is a finding about D-09, not a number to raise again.
  **D-09's cache deferral is NOT revisited**, because the two pins hold the budget with headroom.
- **MF-8 — SC-06 declared unit evidence nothing produced. APPLIED as BOTH halves, and here is why.**
  *A task now produces it:* T-07's `test-metrics-kpi.py` (a UNIT script) gains a case that sweeps
  **every tracked path under `bin/dashboard/`** — backend `.py` included, which nothing covered — for
  `107` and `122`, reading each path's committed bytes via `git show HEAD:<path>` so an uncommitted
  file cannot evade it, with a non-empty-path-list precondition (an errored `git` must not read as a
  clean sweep) and a demonstrated failing state. *And BRIEF.md is corrected,* because the criterion as
  written was **unreachable by its own method** for two of its five tokens: `12` and `3` occur inside
  `1024`, `3x2` and `ES2022`, all of which this feature legitimately ships, so no grep can
  discriminate them. SC-06 now names exactly the two grep-discriminating literals, and a new
  `## Verification gaps` bullet records that `12` and `3` are **not machine-checked** and are carried
  by SC-15's inspection. That is a narrowing of scope declared at the signature, not a criterion
  reworded until it passes: the residue is named, not deleted.

## The other findings

**Applied:** D-19 folded in the two clauses T-06 implements (specific-sentence reason, never
interpolate/substitute) so the named authority is no longer weaker than its restatement — T-06 keeps
its self-contained paragraph, now equal in force rather than stronger. B-reuse F1/F2
(`harness_yaml.load_plan`; read `code-grade.py`'s own `passing` instead of re-deriving
`at_or_above_bar`). ALT-1 (`kpi.resolve_window` exposed once, cited by T-08/T-09/T-10). ALT-2 (T-10
pre-segments every series unconditionally; T-15's conditional server-side branch, which pointed a
frontend task at an ungranted backend file, is gone). EFF-2. A1 F02 (unbounded thread count named as
accepted) and F03 (`jsonschema` dropped from the gate — no dashboard module imports it). A2 F4
(`@tanstack/charts` + `/react`, not the legacy compat package), F5 (`d3-scale` + `@types/d3-scale`
pinned; `scaleUtc`/`scaleTime` required, and T-15's verify greps for it), F6 (`createMark` for
square/triangle), F7 (`keyboard: false` beside `aria-hidden`). A4 F1 (merge-duplicate `feature_id`
resolves to the later `shipped_at`, discarded one named), F2 (3 worktrees / 2 sequential merges), F5
(unrecognised `schema` rejected loudly), F6 (nested objects atomic, no dotted-path partial). A3
F-A3b-1 (T-05's `files:` gains `package.json`, `vite.config.js`, `.gitignore`, `src/`). The staged
T-15 `files:` correction. **Also fixed while the file was open:** T-05's verify
`UnicodeDecodeError` (suffix filter + `errors='ignore'` + a positive control), and T-11 gains
`test-metrics-kpi.py` so its `kpi.py` wiring has a unit-level assertion.

**Declined, one line each:** A3 F-A3a-1 and F-A3c-1 — recorded by their own reporter as residuals to
carry, not defects, and neither has an edit that would change what gets built. **CAP-08 decided, not
declined:** three stacked single-series plots sharing one x-axis, written into T-15 with A2d's
reasoning (three incommensurable units; series-1/series-2 at 1.51:1 light, 1.21:1 dark; faceting is
the library's most documented path). Cheap, reversible, local — mine to decide. It resolves DESIGN
Q2, which is the designer's file, so **the plan carries the resolution and DESIGN.md was not touched.**

## Task ordering, deliberately non-monotonic

File order is `T-01..T-05, T-18, T-06..T-17, T-19, T-20`. Ids are not monotonic on purpose: A1c
verified that file order was a valid topological order and that property is load-bearing against a
file-order scheduler, so the probe sits physically where it must run — before T-06 — rather than at
the end of the file where its `depends_on` would be the only thing holding the gate.

## Open questions

- **Q1 (blocking, operator):** MF-2/eng Q2 — accept the TanStack Charts alpha with a documented
  rollback, or name a second live charting library? D-08 recommends the former and T-18 makes it
  cheap. **The correction is applied; the choice is not mine.**
- **Q2 (blocking, operator):** eng Q1 — D-20 records that a server-rendered HTML surface with no npm
  was never weighed. The user settled React + TanStack at the grilling
  (`.harness/notes/grilling-metrics-dashboard-2026-09-01.md:76-78`) and settled against the
  `render-brief.py` static-HTML convention (`:20-22`) — but a server-rendered surface off this
  feature's own stdlib server is neither of those, so it is genuinely new information. D-20
  recommends keeping the client build; it needs an explicit yes or no.
- **Q3 (non-blocking, harness defect):** BRIEF.md:59 and D-20 cite
  `.harness/notes/grilling-metrics-dashboard-2026-09-01.md`, which exists in the owner checkout's
  working tree but is **untracked on `feat/FEAT-53` at 38dd3622** — so the citation does not resolve
  from inside the branch a reviewer reads. Commit the grilling artifact.
- **Q4 (non-blocking, harness defect, re-raised from the eng digest):** the A2 dispatch's read-only
  context7 doc lookup was refused by the **write**-domain hook, forcing library facts to come from
  `registry.npmjs.org` and `unpkg.com`. A read blocked by a write guard is worth the harness owner's
  look.
