# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: goal-check in flight — `runs/2026-08-19-11-product/` returned BLOCKED with pm still live; resumed
- squad: product
- status: Building — all nine tasks `done`; goal-check then close-out remain

**All nine tasks read `status: done`.** T-07 and T-09 landed as main-session-direct work at
`4f2e5d0`; I re-ran both `verify:` blocks myself and both exit 0. `review_sha` pinned at **`4f2e5d0`**,
verified equal to the branch tip.

**The headline result, verified by me rather than relayed.** `check-state.sh` costs **5 GraphQL
points against a 506 baseline**. T-07 needed no code edit — T-02 had already made INV-26's path cheap.
Board 6 rules out the competing explanation: **old 102, new 1, `board_items: 4` on both sides**, so
item count cannot account for it — it is the query shape.

**SC-04's violation sets differ legitimately and I diffed them myself: 4 lines added, 0 removed, 0
altered.** All four are T-01–T-04 cards reading `Backlog` against the deliberately frozen mirror.
`EXPLAINED-DIFFERENCE` and `POSITIVE-CONTROL` are both present, and the control's seven expected
lines reappeared verbatim at 5 points.

**The provenance objection is closed.** The goal-check asked whether evidence measured at `8c2c24d`
describes the code pinned at `4f2e5d0`. `git diff --stat 8c2c24d..4f2e5d0 -- .claude/skills/harness/bin/`
is **empty**; the whole delta is the two measurement files plus two `plan.yaml` status lines.

Gate state at `c472a02`, unchanged since by any source byte: `matrix_ok: true`, panel PASS,
`must_fix` empty, `severity_max: low`. SIMPLIFY: four angles, zero applies.

Next: goal-check verdict → close-out, **ship-refresh and distillation dispatched as two dispatches in
ONE message** → final CEO briefing.

Budget: **46 GraphQL points** spent by me across the feature. **7 cycles of 10; 11 runs of 20.**
Four lead runs closed with a member still in flight; three bought no artifact.

## Open Questions

- Q1 (non-blocking, operator): a `.gitignore` rule for `.harness/logs/gh-cost-*.jsonl` — the narrow
  form, **not** blanket `.harness/logs/`, whose sibling session logs are tracked. The stray log itself
  was removed at ship, so this is backlog rather than tree dirt.
- Q2 (non-blocking, harness defect, 4th occurrence): the `SubagentStop` hook forces a digest out of a
  lead with a member still in flight, and nothing preloaded tells a lead that an in-flight `BLOCKED`
  is the correct response. Compounding it, leads hold no `SendMessage`, so a lead cannot course-correct
  a live member. Being filed by the operator after ship.
- Q3 (non-blocking, harness defect): `factory_config.harness_root()` falls back to the real checkout
  when `CLAUDE_PROJECT_DIR` lacks `SPEC.md`, so an ad-hoc benchmark wrote thousands of synthetic
  records into the operator's tree before self-catching. Being filed by the operator after ship.
- Q4 (record, mine): `STATE.md` drifted stale on the pin twice and was caught both times by a
  validator and then a product lead. `plan.yaml` and `feature.json` are authoritative over it.
