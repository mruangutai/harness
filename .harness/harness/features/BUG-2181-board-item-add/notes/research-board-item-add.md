# Guarded board addition — intake evidence

The unsigned patch is ready for signature: one direct task, three traced SCs, five owned files. Main session builds; harness-validator-lead validates. No production files or tests were changed or executed.

## Findings

- Authority: .harness/notes/grilling-board-item-add-2026-11-08.md, Settled; acceptance: runs/2026-11-08-01-product/digest.md.
- PRODUCT is /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2181-board-item-add. Direct reads of PRODUCT/docs/spec.md, PRODUCT/docs/decisions.md and PRODUCT/docs/architecture.md each returned not found. Their missing requirements, decision and architecture guidance is disclosed in BRIEF; no substitute contents were assumed.
- gh_board.py#set_station currently raises on a None lookup within its GhError wrapper. Guarded addition belongs there, preserving every caller.
- Read-only integration reuse: tests/integration/gh_sync_support.py symbols FAKE_GH_STATIONS, stage_station, install_gh, run, calls; tests/integration/test-gh-sync-start-task.py station cases demonstrate both fake-binary variables and per-card identity assertions.
- Existing refusal search covered PRODUCT/tests. tests/integration/test-board-station.py FAKE_GH_NOT_ON_BOARD and case 3 need updated comments and an explicit add failure; T-01 owns this file. tests/unit/test-gh-board.py existing set_station cases cover failing gh, present item and vocabulary validation, not absence refusal. tests/unit/test-factory-land.py M2c owns a different no-item path and remains unchanged.
- New basenames are distinct: test-gh-board-item-add.py (unit), test-gh-sync-board-add.py (integration). Both directories match active configured test kinds. No existing shared helper needs editing.
- Backlog command gh issue list --repo mruangutai/harness --state open --limit 100 exited 0; #2181 matches this scope. No adjacent backlog work imported.

## Exact planning checks

Commands ran from PRODUCT, except feature-root and revision lookup. All paths below are literal command arguments.

1. python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/inflight_registry.py feature-root --feature BUG-2181-board-item-add
   Exit 0; returned PRODUCT above.
2. git rev-parse HEAD (cwd /Users/molchairuangutai/GitHub/harness)
   Exit 0; b7af829c0207522b43f978b5275a2ebdc96b3210, recorded as lanes.resolved_at.
3. python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py apply --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2181-board-item-add/.harness/harness/features/BUG-2181-board-item-add/plan.yaml --proposal -
   Proposal supplied on stdin; exit 0, APPLIED. Automatic check-state reported unsigned BRIEF and absent Build-entry receipt (expected pre-signature), pending plan and historical attribution notes. No APPROVAL-RESET receipt; no remote status call made.
4. python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2181-board-item-add/.harness/harness/features/BUG-2181-board-item-add/plan.yaml
   Exit 0; MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; OK T-01: declared main-session-direct (.claude/skills/harness/references/repo-board-provisioning.md ungranted); 0 violation(s) across 1 plan(s).
5. python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2181-board-item-add/.harness/harness/features/BUG-2181-board-item-add/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2181-board-item-add
   Exit 0; OK T-01 5 anchor(s) resolved; 1 task(s), 5 anchor(s) resolved, 0 failure(s).

Interface discovery: plan-merge.py apply --help exited 0. check-plan-routes.py --help exited 2 (interprets --help as a nonexistent plan path); the actual feature-scoped route command above succeeded.

## Open questions

None. No implementation outcomes are claimed; failing/passing evidence remains the build/validation obligation. SC-01 integration, SC-02 unit, SC-03 pinned inspection; no personal UAT required. Pending BRIEF and plan require main-session signature.
