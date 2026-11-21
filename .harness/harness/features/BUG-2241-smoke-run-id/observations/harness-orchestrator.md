# Observations — harness-orchestrator — BUG-2241-smoke-run-id

- 2026-11-21: Dispatch framed T-01 as "documentor via eng-lead"; check-domain --resolve returns NOBODY for every squad persona on .agents/skills/harness-spec-driven/SKILL.md (rule skills reserved to the human, SPEC §6), so the plan records main-session-direct. Run the resolver before framing a route in a dispatch.
- 2026-11-21: check-state.py resolves its root from its own script directory, not cwd or --feature; the control-plane copy cannot see a worktree-only feature and exits 0 — run the worktree's copy.
- 2026-11-21: A pending patch intake always shows two check-state violations (BRIEF not approved; INV-37 no build-entry receipt) until sign-approval + gh-sync open; neither is fixable before signature.
- 2026-11-21: Terminal yield with an object `data` (validate-digest.py harness-orchestrator: ok on the same bytes) refused 3x by the hook's RETURN_THE_OBJECT branch — #2171 recurrence despite #2230 in HEAD; the loaded extension or the host's data encoding is the suspect. Return object persisted at notes/orchestrator-return-2026-11-21-01.json; reported to Main and xd://report_issue.
