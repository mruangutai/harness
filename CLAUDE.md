# CLAUDE.md

## Project

**Harness**

A Claude Code agent-team framework for AI-assisted software development. It absorbed and now owns
the best patterns of three ancestors — GSD's context discipline, gstack's role-based review gates,
superpowers' engineering discipline (TDD, spec-driven) — and is **self-hosted**: this repo builds
the harness and runs on it. Built as portable files (CLAUDE.md, skills, agents) first, with a path
to global installation and a distributable package.

**Core Value:** Enable a CTO to take a software idea from product validation through architecture, disciplined implementation, and QA — with Claude executing reliably at each stage without context drift, scope creep, quality shortcuts, or unchallenged assumptions.

### Constraints

- **Files-only, no dependencies** — no CLI, no build step, nothing to `pip install`. This one is
  load-bearing: it has decided real questions (no YAML parser dependency, no template generator).
- **Context budget** — the harness must not bloat context: selective loading, never everything-at-once.

(TDD scope lives in `harness.json` `test_matrix` + the `tdd-enforcement` skill — enforced there, not
restated here.)

## Harness

Harness is active and **self-hosted** — this repo builds it and runs on it. There is no GSD
dependency: no `.planning/` root, no `agent_skills`, no `<files_to_read>` blocks.

| What | Where |
|---|---|
| Project state | `.harness/` — see `.harness/README.md` for the layout and who writes what |
| Config | `.harness/harness.json` (gates, `test_matrix`, `test_kinds`, budgets) |
| The org, as data | `.harness/team-config.yaml` |
| Rule skills | `.claude/skills/harness-<name>/` — **flat**, one level under `.claude/skills/` |
| Agents | `.claude/agents/harness-*.md` |
| Design docs | `docs/harness/SPEC.md` (what it is) · `DECISIONS.md` (why — **the authority**) · `BUILD.md` (what is left) |

**The org is 16 agents in four tiers:** main session (layer 0, the only user channel) →
`harness-orchestrator` (layer 1, one per in-flight feature) → three domain leads (layer 2) →
members (layer 3, always leaves). Rules reach agents by native `skills:` preload, and Expertise by
a `SubagentStart` hook — nothing needs to be told to go read a file.

**Before changing any harness doc, read `docs/harness/DECISIONS.md`** and run
`.claude/skills/harness/bin/check-docs.sh`. It is the propagation checker, and its registry is
DECISIONS.md itself.

## Conventions

- Every claim in prose that a command can check gets checked before it is written.
- Check `bin/check-docs.sh` BEFORE committing, never after.
- The GSD-era stack analysis that once filled this file lives in git history only (removed at DEC-135).
