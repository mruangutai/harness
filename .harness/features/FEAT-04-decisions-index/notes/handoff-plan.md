# Handoff — FEAT-04-decisions-index, plan → build — written at f723194, seq-7

## Next

**Nothing until the user signs.** BRIEF and PLAN are `## Approval: status: pending`
(`BRIEF.md:186`, `PLAN.md:586`) and mission ship is gated on both being `approved`. Once signed,
the first dispatch is **T-01 to eng-lead** — tests for `bin/gen-decisions-index.py`, written first,
`change_type: logic`, six named tests, plus the step that registers `test-gen-decisions-index.py`
in `bin/run-unit-tests.sh`'s `SCRIPTS` array. T-01 → T-02 → T-03..T-08 strictly serial on one file
(`PLAN.md ## Ordering`). Answer Q1 before dispatching T-09.

## Trust

- `check-docs.sh` exit 0, "checked 45 superseded pattern(s) across 94 file(s)" — run by me after
  run 06's last write — verified-at f723194
- 169 LIVE decisions, not the 170 a bare grep reports; the duplicate `## DEC-83` at
  `DECISIONS.md:1583` is inside the fence opened at `:1582` — verified-at f723194
- The `DEC-NNN am.N` form appears **0** times; the real forms are 9 `^### DEC-NNN amendment[ N]`
  headings plus 2 bold-paragraph amendments at `DECISIONS.md:3530` and `:3536` — verified-at f723194
- Every per-feature `.harness/**/*.md` file is a `check-docs.sh` scan target; `/runs/**` is exempt
  (`check-docs.sh:92,95`). Three gate trips in this phase came from that — verified-at f723194
- run 05 confirmed all nine re-verification items at source, `must_fix: []` —
  `runs/2026-08-01-05-eng/digest.md` — verified-at f723194
- Orchestrator cost cumulative for the next delta: opus **231.2868**, fable **40.7239** — the figure
  FEAT-03 had to estimate — `runs/2026-08-01-06-product/state.yaml` — verified-at f723194
- T-09 and T-10 are executable by **no agent in the org** — `team-config.yaml:116,154,193` grants
  neither `CLAUDE.md` nor `.claude/skills/harness-*/SKILL.md` — verified-at f723194
- Nothing is committed. The tree also carries dirt that predates this phase
  (`.harness/logs/2026-08-01.md`) — `git status --porcelain` — verified-at f723194

## Dead ends

- Adding the index to `check-docs.sh`'s exclusion filter — rejected in `PLAN.md` D-01, and run 05
  upheld the pricing — `PLAN.md` D-01 — verified-at f723194
- Citing the SC-08 plant phrase by line anchor instead of the per-line escape — proven unavailable:
  two near-identical stale phrases sit one line apart at `DECISIONS.md:2479-2480`, so an off-by-one
  anchor recovers the wrong one — `runs/2026-08-01-04-product/digest.md` — verified-at f723194
- Re-litigating the destination, documentor's ownership, read-on-demand access, or Supabase — settled
  by the user — `.harness/notes/grilling-decisions-index-2026-08-01.md` `## Settled` — source
- Reading the authority whole. Every agent that did it in this phase was the cost, not the insight —
  `feature.yaml cost_usd` — verified-at f723194

## Working set

- `.harness/features/FEAT-04-decisions-index/PLAN.md` — 10 tasks, 8 decisions, `## Ordering`
- `.harness/features/FEAT-04-decisions-index/BRIEF.md` — 12 SCs, `## Verification gaps`
- `.harness/features/FEAT-04-decisions-index/feature.yaml` — budgets, baseline, open items
- `.harness/features/FEAT-04-decisions-index/runs/2026-08-01-05-eng/digest.md` — the clean review
- `.claude/skills/harness/bin/check-docs.sh` — the gate this feature must not break
