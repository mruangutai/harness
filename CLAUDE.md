
# CLAUDE.md

## Project

**Harness**
A Claude Code agent-team framework for AI-assisted software development and is **self-hosted**: this repo builds
the harness and runs on it. 

**Core Value:** Enable a CTO to take a software idea from product validation through architecture, disciplined implementation, and QA — with Claude executing reliably at each stage without context drift, scope creep, quality shortcuts, or unchallenged assumptions.

### Constraints

- **Context budget** — the harness must not bloat context: selective loading, never everything-at-once.
(TDD scope lives in `harness.json` `test_matrix` + the `tdd-enforcement` skill — enforced there, not restated here.)

## Harness

Harness is active and **self-hosted, with one carve-out** — this repo builds it and runs on it. There
is no GSD dependency: no `.planning/` root, no `agent_skills`, no `<files_to_read>` blocks. **The carve-out (DEC-174): the harness PLANS its own work but does not EXECUTE changes to its own enforcement layer.**

**Working in a worktree is a MUST.** `main` is behind by construction while
harness code is being changed, so a stale copy silently tests the wrong logic.

| What | Where |
| --- | --- |
| Project state | `.harness/` — see `.harness/README.md` for the layout and who writes what |
| Config | `.harness/harness.json` (gates, `test_matrix`, `test_kinds`, budgets) |
| The org, as data | `.harness/team-config.yaml` |
| Rule skills | `.claude/skills/harness-<name>/` — **flat**, one level under `.claude/skills/` |
| Agents | `.claude/agents/harness-*.md` |
| The constitution | `docs/PRINCIPLES.md` — what the factory is FOR. States intent, not mechanism; parts describe the destination, not what is built. Reaches all 16 agents distilled, as the preloaded `harness-principles` skill |
| Design docs | `.harness/harness/docs/SPEC.md` (what it is) · `DECISIONS-INDEX.md` (**the entry point** — one row per decision) · `DECISIONS.md` (why — **the authority**) · `BUILD.md` (what is left) |

**The org is 16 agents in four tiers:** main session (layer 0, the only user channel) →
`harness-orchestrator` (layer 1, one per in-flight feature) → three domain leads (layer 2) →
members (layer 3, always leaves). Rules reach agents by native `skills:` preload, and Expertise by
a `SubagentStart` hook — nothing needs to be told to go read a file.

**Before changing any harness doc, read `.harness/harness/docs/DECISIONS-INDEX.md`**, grep it for the
surface you are touching, and open the two or three entries it names. The authority
`.harness/harness/docs/DECISIONS.md` is never read in its entirety (DEC-150) — the index exists so that it
need not be. Cited decisions are a floor, not a ceiling: go broader via the index when a cited entry
points at one nobody named. A row is an open-or-skip filter, so open the entry before acting on it.

**A decision the tree flatly contradicts is STRUCK, never marked** (DEC-188): removed from every
gate, its entry kept with a strike record so citations still land somewhere. There is no propagation
checker — nothing detects a falsified statement left standing, so the striking has to actually
happen.

## Conventions

- Every claim in prose that a command can check gets checked before it is written.
- Check `.claude/skills/harness/bin/check-state.sh` BEFORE committing, never after.
- Never write a shell wait loop. A Bash foreground timeout detaches rather than kills, so a loop outlives its own bound. Use Monitor (its timeout_ms terminates) or run_in_background.
