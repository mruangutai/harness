# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight
- squad: none
- status: Building — **the build phase is CLOSED**; two main-session-direct tasks remain

All nine tasks are written. **`matrix_ok: true`** — `--kind unit` exit 0 with 175 `^PASS ` lines
(18 runner-level scripts) and 0 FAIL; `--kind integration` exit 0, 12 of 12, 0 FAIL. **Panel PASS**,
`must_fix` empty, `severity_max: low`. **SIMPLIFY: four angles, zero applies** — so the code is final
and `git diff` on `.claude/skills/harness/bin/` against the reviewed commit is empty.

`review_sha` pinned at **`e7104ca`**, verified equal to the branch tip.

**SC status:** SC-02, SC-05, SC-06, SC-07, SC-10 **met**. SC-01, SC-03, SC-04 **pending on T-07 and
T-09**, both main-session-direct and unrun. SC-08 and SC-09 **not-assessed** — both on `NOBODY` paths,
so no agent domain covers them; they are pre-ship steps for the operator, not gaps.

**THE MIRROR REMAINS FROZEN.** No `start-task`, no `close-task`, for any task, until T-07's
after-measurement lands. Seven positive-control lines quote cards reading `Backlog`; closing #586
already destroyed the eighth. Board measured directly: T-01/02/03/04/07/09 `Backlog`, T-05/06/08
`Done`, parent `Building`.

Handover for the operator is `notes/layer0-batch-b-FEAT-29.md` — **T-07 first, then T-09**.

Next once batch B lands: pm's goal-check through product-lead over all ten SCs → close-out
(ship-refresh and distillation dispatched in ONE turn) → final CEO briefing.

Budget: **46 GraphQL points** spent across the whole feature by me. **7 cycles of 10; 11 runs of 20.**
Three runs bought no artifact — two premature lead closes under stop-hook pressure, and one duplicate
angle I caused by asserting a negative in a dispatch brief.

## Open Questions

- Q1 (non-blocking, operator): `.harness/logs/gh-cost-2026-08-19.jsonl` is untracked **and**
  un-ignored, so the tree is dirty at ship. The security reviewer's remedy is a narrow
  `.harness/logs/gh-cost-*.jsonl` rule — **not** blanket `.harness/logs/`, whose sibling session logs
  are tracked. This is B-8, un-struck.
- Q2 (non-blocking, harness defect): three lead runs on this feature emitted a digest under
  `SubagentStop` pressure while their members were still in flight. One produced a roll-up built on a
  sibling run's receipt with two claims later retracted; one became a resume brief's factual basis two
  contexts later. No preloaded rule tells a lead that an in-flight `BLOCKED` is the correct response.
- Q3 (non-blocking, harness defect): `factory_config.harness_root()` falls back to the real checkout
  when `CLAUDE_PROJECT_DIR` points at a directory lacking `SPEC.md`, so an ad-hoc benchmark wrote
  thousands of synthetic records into the operator's tree before self-catching. The
  assert-the-redirect-took-effect guard exists inside `test-gh-cost-log.py`'s helper but nothing
  enforces it outside that file.
