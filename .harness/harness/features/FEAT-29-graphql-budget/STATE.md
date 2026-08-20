# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight
- squad: none
- status: Review — close-out complete, awaiting the operator's ship decision

**Nine of nine tasks done. Both suites green.** `--kind unit` exit 0 / 18 of 18 scripts / 0 FAIL;
`--kind integration` exit 0 / 12 of 12 / 0 FAIL. `matrix_ok: true`, panel PASS, `must_fix` empty,
SIMPLIFY four angles and zero applies.

**The result: `check-state.sh` costs 5 GraphQL points against a 506 baseline**, both differenced across
real runs. Board 6 rules out item count as the explanation — 102 vs 1 with `board_items: 4` on both
sides. Discovery survives, on three independent instruments.

**Grading provenance, stated precisely:** eight SCs were graded met by pm's goal-check. SC-08 and SC-09
were graded UNMET there, then amended by the operator; **no agent has re-graded them since**. I
verified both mechanically — `git show 444c611:CLAUDE.md | grep -c "wait loop"` returns 1, and the
grilling note carries its strikes.

**Close-out done.** Distillation: 34 entries across 14 Expertise files, `check-expertise.sh` exit 0 on
16 of 16, every capped section held by displacement. Ship-refresh **skipped and disclosed** — no map
exists in this repository, so `render-map.py` has nothing to refresh.

Briefing: `notes/ship-review-2026-08-20-final.md`, rendered.

Budget: **46 GraphQL points** across the whole feature. **9 cycles of 10; 17 runs of 20** — both inside
budget, and the runs earned their place. The one real waste was **seven premature lead closes** under
the `SubagentStop` hook, which cost more than every other inefficiency combined.

## Open Questions

- Q1 (for the operator): the ship decision. PR, CI and merge are the operator's; the mirror's `ship`
  and `backlog` subcommands are the main session's, not mine.
- Q2 (non-blocking): 27 backlog rows proposed in the briefing, 6 of them new from close-out. Unstruck
  rows become issues on ship acceptance; anything not listed dies silently.
- Q3 (record): SC-08 and SC-09 carry a mechanical verification rather than an independent agent
  re-grade, because both were amended after the goal-check ran.
