# Layout boundary capture — PRE-MOVE — 2026-08-14

HEAD: 5afa7e3d2acd017da49e0d4263086c724abd8ac8

## layout_migration.py (verbatim)
```
features: CLEAN — evidence legacy
docs: CLEAN — evidence legacy
examined 21 feature dir(s), 1 doc root(s), 7 reader file(s)
layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify
exit: 0
```

## check-state.sh (verbatim)
```
  note       FEAT-19-central-product-config/plan.yaml approval is pending — awaiting the user.
  note       FEAT-08-remove-cost-tracking/PLAN.md approval is pending — awaiting the user.
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
  note       INV-17 FEAT-15-domain-product-base: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed. Suppressed handoff-plan, handoff-build, handoff-validate.
  note       INV-23 FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 FEAT-05-pyyaml-file-parsers/STATE.md is 165 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
exit: 0
```
