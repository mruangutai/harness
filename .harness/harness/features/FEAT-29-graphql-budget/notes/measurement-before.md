# Measurement — before the cheap-read cutover (T-06)

One `check-state.sh` run, differenced across `gh api rate_limit --jq .resources.graphql.used`.
That endpoint is REST and costs zero GraphQL points — re-confirmed here, since `before` was
read immediately after the counter reset and the reads themselves moved it by nothing.

**Nothing else was in flight.** Confirmed before starting: zero background shells, zero live
agent runs, and the only long-lived `claude` processes were the VS Code extension host (29h)
and this session (26h) — both idle, evidenced by a separate 60-second drift test that showed
the counter unchanged. A contaminated reading proves nothing, so this is stated rather than
assumed.

before: 14
after: 520
delta: 506
board_items: 486
sha: e1bcdc1

The plan predicted about 506. Measured 506 at 486 board items, against 490-506 measured at
473-476 items earlier the same day by two separate parties. Gate exit code was 1.

VIOLATIONS-BEGIN
  VIOLATION  .harness/harness/features/FEAT-28-ci-wiring-asserted/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  .harness/harness/features/FEAT-26-pr-linkage-recorded/BRIEF.md is NOT approved — halt that flow and surface to the user.
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
