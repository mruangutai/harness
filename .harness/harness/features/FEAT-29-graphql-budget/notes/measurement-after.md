# FEAT-29 T-07 — check-state.sh GraphQL cost AFTER the cutover

Measured by the main session directly (DEC-174 carve-out), 2026-08-19, with no agent run in
flight. The counter is `gh api rate_limit --jq .resources.graphql.used`, which costs 0 points
and so does not contaminate the figure it reports.

**No edit was made to `check-state.sh`.** T-02 replaced the whole-board `item-list` scan inside
`gh_board.board_stations` with the targeted cost-1 query, and INV-26 calls that function. The
block at `check-state.sh:1130-1176` needed no change; `grep -nE "project_items|item-list"` over
the file returns nothing. This task is therefore a measurement, not a diff.

before: 0
after: 5
delta: 5
board_items: 473
sha: 8c2c24d

Against the 506 recorded in `measurement-before.md`, that is a 101-fold reduction, and it is
under the 100-point ceiling REQ-01 sets by a factor of twenty.

`board_items` fell from 486 to 473 between the two runs. The board is live and cards were closed
out in between. It is recorded because a cost figure without its board's item count cannot be
falsified — the rule T-05 wrote after the 2026-08-10 figure of 31 went unreconciled.

The gate exited 1, as it did at the baseline. Complete stdout and stderr follow verbatim.
stderr was empty.

VIOLATIONS-BEGIN
  VIOLATION  .harness/harness/features/FEAT-28-ci-wiring-asserted/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  .harness/harness/features/FEAT-26-pr-linkage-recorded/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-01 (issue #579): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-02 (issue #580): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-03 (issue #581): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-04 (issue #582): plan says done, so the card should read Done — the board reads Backlog.
  note       .harness/harness/features/FEAT-19-central-product-config/plan.yaml approval is pending — awaiting the user.
  note       .harness/harness/features/FEAT-28-ci-wiring-asserted/plan.yaml approval is pending — awaiting the user.
  note       .harness/harness/features/FEAT-26-pr-linkage-recorded/plan.yaml approval is pending — awaiting the user.
  note       .harness/harness/features/FEAT-08-remove-cost-tracking/PLAN.md approval is pending — awaiting the user.
  note       FEAT-27-expertise-repository-tier: run dir 2026-08-18-1-eng exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       INV-22 FEAT-24-config-responsibility-split: 24 runs recorded against a 20-run budget (cycles_used=9 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-21-features-layout-migration: run dir 2026-08-15-1-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-23-ship-flow-fixes: run dir 2026-08-17-15-refix-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-23-ship-flow-fixes: run dir 2026-08-18-16-construct-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-26-pr-linkage-recorded: run dir 2026-08-18-2-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-26-pr-linkage-recorded: run dir 2026-08-18-2-eng exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       INV-22 FEAT-22-docs-layout-migration: 23 runs recorded against a 20-run budget (cycles_used=10 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-13-single-issue-board-lookup: run t01-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run qa-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run t02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run panel-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run goalcheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run fix01-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run sc05recheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-13-single-issue-board-lookup: run distill-product is referenced but its dir is absent (pruned, or never created).
  note       INV-22 FEAT-10-software-factory: 32 runs recorded against a 20-run budget (cycles_used=12 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-09-plan-time-route-check: run plan-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run seg1-main-session is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run t02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run dec179-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run panel-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run goalcheck-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-09-plan-time-route-check: run distill-product is referenced but its dir is absent (pruned, or never created).
  note       INV-22 FEAT-14-feature-json-schema: 21 runs recorded against a 20-run budget (cycles_used=6 counts REWORK only, DEC-157, so it does not see this). Not a defect by itself — check each run is efficient, is resolving issues, and is advancing the SCs. The count is a FLOOR: main-session-direct segments are not runs.
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-01-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-02-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-02-03-product is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-01-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-04-eng is referenced but its dir is absent (pruned, or never created).
  note       FEAT-05-pyyaml-file-parsers: run 2026-08-03-05-validator is referenced but its dir is absent (pruned, or never created).
  note       FEAT-06-team-layer-inv6: run inter-gate-q1q2 is referenced but its dir is absent (pruned, or never created).
  note       FEAT-15-domain-product-base: run dir 2026-08-11-01-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-5-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-4-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-7-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       FEAT-20-migration-detector: run dir 2026-08-14-6-validator exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover it by luck.
  note       INV-17 FEAT-21-features-layout-migration: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-build, handoff-validate.
  note       INV-17 FEAT-22-docs-layout-migration: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan, handoff-build, handoff-validate.
  note       INV-17 FEAT-15-domain-product-base: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan, handoff-build, handoff-validate.
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 165 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
VIOLATIONS-END

## EXPLAINED-DIFFERENCE

The violation set is NOT identical to `measurement-before.md`. Four lines are added; none is
removed and none is altered. The four:

    VIOLATION  INV-26 FEAT-29-graphql-budget T-01 (issue #579): plan says done, so the card should read Done — the board reads Backlog.
    VIOLATION  INV-26 FEAT-29-graphql-budget T-02 (issue #580): plan says done, so the card should read Done — the board reads Backlog.
    VIOLATION  INV-26 FEAT-29-graphql-budget T-03 (issue #581): plan says done, so the card should read Done — the board reads Backlog.
    VIOLATION  INV-26 FEAT-29-graphql-budget T-04 (issue #582): plan says done, so the card should read Done — the board reads Backlog.

**The captured output was not adjusted to make the two sets match.** The difference is a change
in the TREE between the two runs, not a change in INV-26's detection behaviour, and it is the
correct report of the new tree.

At the baseline sha `e1bcdc1` every one of this plan's nine tasks read `status: pending`, so no
card could disagree yet and INV-26 said nothing. Since then T-01 through T-06 and T-08 have
completed while the mirror stays FROZEN by the orchestrator's instruction, so seven done tasks
sit against cards nobody moved. Four of them are reported.

**Why four and not seven — the part that had to be checked rather than assumed.** Reading the
nine cards directly:

| task | plan | card | INV-26 |
| --- | --- | --- | --- |
| T-01 – T-04 | done | Backlog | VIOLATION — correct |
| T-05, T-06, T-08 | done | **Done** | silent — the card agrees |
| T-07, T-09 | pending | Backlog | silent — the card agrees |

Three cards read `Done` and six read `Backlog`. The cheap read returns two different station
values across the nine, which is stronger evidence than the frozen-mirror control below: a
truncating or failing read would return one value or none, and issue #588 records that INV-26
prints nothing in exactly that case. Here it discriminates, live, at 5 points.

## POSITIVE-CONTROL

Amendment 2 requires this. The diff above would pass whether the cheap read works or is silently
broken, because #588 makes INV-26 print nothing on a FAILED board read as well as on an
agreeing one. `measurement-before-positive.md` was captured at **506 points** while the
expensive read still existed, and holds the INV-26 lines a perturbed plan produces.

Procedure, executed here:

1. `plan.yaml` copied aside.
2. Every `status: pending` flipped to `done` — **2 substitutions**, T-07 and T-09 — so
   `derive_station` yields Review against a board that does not.
3. `check-state.sh` run, output captured. Gate exit 1.
4. `plan.yaml` restored from the copy, and the restore PROVEN: `cmp -s` **exit 0**, byte-identical.

Result:

    control cost:   before 20, after 25, delta 5      (against 506 at the baseline capture)
    INV-26 lines:   7 emitted
    expected:       7   (the original 8 less T-08's line, struck by approval amendment)
    missing:        0


The seven lines, verbatim from the control run, between CONTROL-INV26-BEGIN and
CONTROL-INV26-END:

CONTROL-INV26-BEGIN
  VIOLATION  INV-26 FEAT-29-graphql-budget T-01 (issue #579): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-02 (issue #580): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-03 (issue #581): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-04 (issue #582): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-07 (issue #585): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-09 (issue #587): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget parent (issue #571): the plan derives Review — the board reads Building.
CONTROL-INV26-END

**All seven control lines reappear VERBATIM at 5 points instead of 506.** The cheap read is
reading the board. T-07's acceptance condition is met.
