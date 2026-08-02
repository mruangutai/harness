# /harness-ship — build, validate, and bring a planned feature to the ship decision

Read `.claude/commands/harness.md` and follow it with **mission: ship**. The differences:

- **Precondition, hard:** BRIEF *and* PLAN both `status: approved`. Anything less routes to
  `/harness-plan` — the orchestrator will refuse anyway (playbook step 1), so catch it here.
- The orchestrator sequences the squads (build → qa gate → review panel → goal-check → docs) and
  owns the fix cycles and both budgets.
- **Terminus:** the CEO briefing, presented by you verbatim. The user decides ship / fix first /
  re-scope / stop. PR and merge follow their call — never automatically.
