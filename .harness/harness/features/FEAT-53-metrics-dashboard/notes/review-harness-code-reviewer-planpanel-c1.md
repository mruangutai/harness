# Plan-panel review — scope reader — FEAT-53 — cycle 1

**BLUF: REQ/SC coverage is clean (14/14 REQ traced, 16/16 SC accounted for, no dangling traces, no
DAG cycles or dangling edges). One dependency-direction defect (S1, high) means the plan's own task
graph cannot deliver the grading panel's chart-beside-table composition as DESIGN.md requires it, and
mirrors the exact "component built, never wired" pattern the plan's authors already had to patch twice
(T-19 for `trend.append()`, T-20 for `touchpoints.record()`) — this is very plausibly a third instance
they missed. Two more findings are lower-stakes verify-integrity gaps (S2, S3, both med).**

## Findings

| id | sev | plan ids | summary | consequence |
|---|---|---|---|---|
| S1 | high | T-14, T-15, T-18 | `T-15` (builds `charts.tsx`, the only task that creates the Shape A/B chart components) `depends_on: [T-14, T-18]` — i.e. it runs **after** `T-14` (builds `panels.tsx`). But DESIGN.md C-1 requires the grading panel to render "the histogram and the **named** grade-1/grade-2 outlier list… side by side in one panel" (KPI 1 and KPI 3's panels need Shape B too, per C-1's panel-inventory table), and `T-14`'s own intent text says the same thing. No task's `files:` list ever touches `panels.tsx` again after `T-14`, and `T-15`'s sole file is `charts.tsx` with no reference back into `panels.tsx`. | `T-14` cannot literally satisfy its own intent when it runs — `charts.tsx` does not exist yet at `T-14`'s dispatch, so an import of it would break `T-14`'s own `npm run build` verify. The realistic outcome is `T-14` ships `panels.tsx` without the chart wired in, and nothing catches that: `T-14`'s verify greps for four gap-state component names and two forbidden literals, never for a chart import; `T-15`'s verify greps `charts.tsx` in isolation for `strokeDasharray`/`keyboard`/`scaleUtc`, never for a caller. REQ-07's flagship "distribution plus named outliers, never a bare mean" panel — the one DESIGN calls "the surface that does not collapse to a figure" — ships with its chart silently absent, and the only backstop left is SC-15's manual ui-reviewer inspection, not the automated gate the plan otherwise relies on everywhere else. A weaker, structurally identical concern exists one layer up: `T-13` (routes.tsx, shell) correctly precedes `T-14` (tiles/panels), but no task's `files:` list ever shows `routes.tsx` being edited again to mount `tiles.tsx`/`panels.tsx` either — direction is right there, but the wiring step is equally unassigned. |
| S2 | med | SC-07 (BRIEF), T-10 | BRIEF declares SC-07 (`"every trend KPI in the payload is marked unavailable with a reason… for a feature with no ship record"`) `verify: automated  evidence: unit`. The only place this exact scenario is actually asserted is `T-10`'s addition to `test-metrics-trend.py` — "a feature with no record reports unavailable-with-reason for every trend field rather than zero" — and `T-10` registers `test-metrics-trend.py` in `run-unit-tests.sh`'s **INTEGRATION_SCRIPTS**, not `UNIT_SCRIPTS`. No task assigns this assertion to `test-metrics-kpi.py` (the file that actually is unit-registered, by `T-06`). | A test-matrix / qa-gate reconciliation that resolves SC-07's declared `unit` evidence against the plan's own test registrations finds no unit-kind test covering it — either the gate reports SC-07 unproven at the evidence kind BRIEF names (spurious block), or a reviewer transcribing BRIEF's evidence column to a downstream gate config wires the wrong test kind. Every other automated SC's declared evidence kind matches where its task actually registers the test (checked all 12); this is the one mismatch. |
| S3 | med | T-13, T-14, T-15 | `T-13`'s verify greps every `.ts*` file under `client/src` (at `T-13`'s own dispatch, i.e. only `main.tsx`, `routes.tsx`, `theme.ts`, `api.ts`) for the forbidden tokens `prefers-color-scheme` and `isDark`, enforcing DESIGN C-3's "no `prefers-color-scheme` query and no `isDark` ternary in any component… that is the check" rule. `T-14` and `T-15` together add five more `.tsx` files (`tiles.tsx`, `panels.tsx`, `gapstates.tsx`, `tables.tsx`, `charts.tsx`) — exactly the component-level files most likely to contain ad hoc theme logic — and neither task's verify re-runs that grep, and no later task runs a repo-wide sweep for it either (unlike SC-06's `107`/`122` literals, which `T-07`'s unit test sweeps at `HEAD` across the whole `bin/dashboard/` tree, catching any file committed by any later task). | A raw `prefers-color-scheme` media query or `isDark` boolean added in `T-14` or `T-15` (e.g. a component reaching for a quick local dark-mode check instead of the theme token) ships committed and green, with only SC-15's manual ui-reviewer inspection as a backstop — despite `T-13`'s own intent text asserting "That is what the verify greps for," which is true only for 4 of the 9 client source files that exist by the time the feature ships. |

## REQ / SC census

- **REQ-NN:** 14 exist in BRIEF (`REQ-01`…`REQ-14`). **14/14 traced** by at least one task's `traces:`
  (REQ-01×6, REQ-02×3, REQ-03×2, REQ-04×2, REQ-05×3, REQ-06×2, REQ-07×4, REQ-08×3, REQ-09×1,
  REQ-10×6, REQ-11×6, REQ-12×3, REQ-13×1, REQ-14×3). **0 orphan REQs.** Every `traces:` id across
  all 20 tasks resolves to an existing REQ-01…REQ-14 — **0 dangling traces**.
- **SC-NN:** 16 exist in BRIEF. **16/16 accounted for**: 12 automated SCs each map to a task that
  produces the asserted evidence (SC-01/03/12/16 → T-12; SC-04 → T-06+T-07+T-08+T-09+T-11 jointly;
  SC-05/06 → T-07; SC-07 → T-10 [see S2 — evidence-kind mismatch]; SC-09 → T-10; SC-10 → T-11;
  SC-13 → T-08; SC-14 → T-09); 3 are `verify: uat` with no producing task by design (SC-02, SC-08,
  SC-11); 1 is `verify: inspection`, ui-reviewer's job, not a build task (SC-15).

## DAG integrity

Built the full graph from every task's `depends_on:`. **No cycle. No edge to a non-existent task id.**
File order (`T-01…T-05, T-18, T-06…T-17, T-19, T-20`) was checked against dependency order per-task
and, aside from S1's missing edges, every declared dependency sits earlier in file order than its
dependent — the `T-18` mid-file placement the dispatch warned about does **not** in fact hide a
forward-reference defect; `T-18`'s own deps (`T-01`, `T-04`) are both earlier in the file. Domain/lane
coherence checked against `plan.yaml`'s `lanes:` table and `team-config.yaml`'s live grants for every
task's `execution_agent`/`execution_mode` — no misrouted task found (including the `touchpoints.jsonl`
runtime-write question: `check-domain.sh` only governs `Write|Edit` tool calls and `bash-write-guard.sh`
only pattern-matches known shell write shapes — `sed -i`/`tee`/redirects/`cp`/`mv`/`rm` — neither
governs a Python script's internal `open(path, "a")`, so `touchpoints.py record` invoked by pm or the
validator at runtime is not blocked by either guard despite neither being granted `.harness/*/features/*/touchpoints.jsonl` in `team-config.yaml` — confirmed a non-issue, not reported as a finding).

## Not restated (per dispatch)

Goal-check F3 (stale `107`/`122` literals) and the D-03/D-08/D-20 open-decision status are not
repeated here; none of S1–S3 materially changes how the operator should decide those three.

---
Binding: `plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`. No `review_sha` (DEC-207) — plan review, not code review.
