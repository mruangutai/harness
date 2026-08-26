@AGENTS.md

# Claude Code compatibility

Claude Code compatibility is an adapter over the provider-neutral Harness:

- Agent definitions are discovered from `.claude/agents/harness-*.md`.
- Skills are discovered from the flat `.claude/skills/harness-*/` layout and loaded through each agent's `skills:` frontmatter.
- Tiered Expertise and the codebase index are delivered through the `SubagentStart` hook in `.claude/settings.json`.
- Claude command hooks in `.claude/settings.json` enforce write domains, branch and Bash policy, dispatch policy, post-write checks, and digest validation.

The canonical project rules are in `AGENTS.md`. Do not duplicate them here.
