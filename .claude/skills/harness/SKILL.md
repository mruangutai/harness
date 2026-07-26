# Harness: Unified Workflow Router

Route-not-stack architecture. Each lifecycle phase has one framework authority.

## Selective Loading

Rules are **flat skills** at `.claude/skills/harness-<name>/SKILL.md`, delivered by each agent's
`skills:` frontmatter field — Claude Code injects the full content at spawn. Nothing needs to "read"
them, and there is no `agent_skills` config. The eight: `handoff` and `expertise` (all 15 agents),
plus `tdd-enforcement`, `systematic-debugging`, `spec-driven`, `verification-rules`, `code-review`,
`zero-micro-management` (role-scoped).

> This file is otherwise still GSD-era and is scheduled for rewrite (BUILD.md migration item #9).

Only load a rule file if it appears in your `<agent_skills>` block.

## Config

Gate toggles and role triggers: `.planning/harness.json`
Skill injection paths: `.planning/config.json` `agent_skills` field

## Lifecycle Routing

| Phase | Owner | Injected Skills |
|-------|-------|-----------------|
| Project init | GSD | CEO gate at boundary (agent) |
| Requirements -> Roadmap | GSD | None |
| Phase Discussion | GSD | Eng gate at boundary (agent) |
| Phase Planning | GSD | None |
| Implementation execution | GSD | tdd-enforcement via agent_skills |
| Non-implementation execution | GSD | None |
| Phase Verification | GSD | verification-rules via agent_skills |
| Code Review | Harness | code-review via agent_skills |
| Bug Investigation | Harness | systematic-debugging via agent_skills |
| Pre-ship QA | Harness | QA gate (agent) |
| Pre-ship Security | Harness | Security audit (agent) |

## Subagent Dispatch Note

When dispatching subagents, include `.planning/harness.json` in the `<files_to_read>` block so they can read gate configuration.
