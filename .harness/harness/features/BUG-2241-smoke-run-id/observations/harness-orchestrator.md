# Observations — harness-orchestrator — BUG-2241-smoke-run-id

- 2026-11-21: Dispatch framed T-01 as "documentor via eng-lead"; check-domain --resolve returns NOBODY for every squad persona on .agents/skills/harness-spec-driven/SKILL.md (rule skills reserved to the human, SPEC §6), so the plan records main-session-direct. Run the resolver before framing a route in a dispatch.
- 2026-11-21: check-state.py resolves its root from its own script directory, not cwd or --feature; the control-plane copy cannot see a worktree-only feature and exits 0 — run the worktree's copy.
- 2026-11-21: A pending patch intake always shows two check-state violations (BRIEF not approved; INV-37 no build-entry receipt) until sign-approval + gh-sync open; neither is fixable before signature.
