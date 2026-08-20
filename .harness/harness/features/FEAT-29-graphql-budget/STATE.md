# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: final independent grade of SC-08 and SC-09 dispatched under the settled wording
- squad: product
- status: Review — budget raised to 12 by operator ruling (DEC-157), spent on this grade

**Three operator rulings applied to the artifacts, struck in place with provenance, never deleted.**
I transcribed them rather than delegating the edit, so that pm stays a clean grader instead of
grading wording it wrote itself.

- **Ruling 1 — THREE conditions govern**: board, item count, and the commit measured at. Signed
  decision D-03 named only two; its text is struck in `plan.yaml` and points at the recording rule,
  so one definition survives rather than two. A figure without its commit cannot be re-derived, which
  is how the 31 survived nine days unfalsifiable.
- **Ruling 2 — the condition binds PER DOCUMENT**, not per figure: a document states its condition
  once and its figures inherit it. Read per-figure, the signed `BRIEF.md` and `plan.yaml` would become
  violations of a rule they define.
- **Ruling 3 — SC-09's conduct conjunct is DROPPED**, struck as ungradable by its own `verify:`
  method. Ten-second polling was live conduct in a terminal, never an artifact. SC-09 is graded on the
  rule conjunct alone, which `git show <pin>:CLAUDE.md` can settle.

`check-plan-routes.py` still reports `0 violation(s)`; the YAML parses and the strike is a block
scalar because the ruling's own text contains a colon.

**The record correction stands and the operator confirmed it.** `review_sha` read `4f2e5d0` when pm
graded — two committed copies of `feature.json` prove it — and at that sha the rule count was 0.
pm graded correctly on the tree it was handed. Re-pinning was the remedy, not evidence there was
nothing to remedy.

**The most valuable finding of the feature was against myself.** Repository-tier Expertise G-01, which
is injected into *every* orchestrator spawn, carried a bare "roughly 500 points" hours after the fix
made it 5. My own corpus sweep missed it because I grepped `item-list` and `project_items` and that
line named neither — **a cost-claim enumeration has to be built from the claim, not the call's
spelling.** Corrected, with both figures and their conditions.

The result, conditions stated once for this document: all figures below are board 3 unless named,
measured in this repository, 2026-08-19 to 08-20. `check-state.sh` costs **5 points** (473 items,
`8c2c24d`) against **506** before (486 items, `e1bcdc1`). Board 6, four items, both shapes at
`8c2c24d`: **old 102, new 1**, item count identical on both sides. Orchestrator spend: **46 points**.

Nine of nine tasks done, both suites green, `matrix_ok: true`, panel PASS, SIMPLIFY zero applies,
close-out complete.

## Open Questions

- Q1 (blocking, operator): the final grade's verdict on SC-08 and SC-09 under the settled wording.
  Cycles are 12 of 12 afterwards; any further work needs another recorded raise.
- Q2 (non-blocking): 18 backlog rows are command-ready for the operator. `cmd_backlog` is the main
  session's, is not idempotent, and I have not run it.
- Q3 (non-blocking, harness defect, row 18): repository-tier Expertise under
  `.harness/harness/expertise/` is injected every spawn but belongs to no feature, so nothing
  re-checks its factual claims when a feature falsifies one.
- Q4 (informational): this run makes **20 of 20** recorded runs. The bound is informational and never
  stops a branch — each run here resolved something and the criteria advanced, so the count is
  earned rather than drift.
