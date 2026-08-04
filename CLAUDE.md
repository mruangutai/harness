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

- **Files-only** — no CLI, no build step. Still load-bearing: it decided no template generator.
  **The no-dependency clause is reversed (DEC-171 + am.1):** PyYAML is **required**, and a real
  `safe_load` replaces hand-rolled regex wherever the harness reads YAML. There is no line-scan
  fallback — a fallback would keep the brittle parser in the tree, which is the point of removing it.
  A missing PyYAML is a loud error: `harness-init`'s prerequisite gate stops, and the two
  `PreToolUse` hooks fail CLOSED with a one-session bootstrap escape.
- **Context budget** — the harness must not bloat context: selective loading, never everything-at-once.

(TDD scope lives in `harness.json` `test_matrix` + the `tdd-enforcement` skill — enforced there, not
restated here.)

## Harness

Harness is active and **self-hosted, with one carve-out** — this repo builds it and runs on it. There
is no GSD dependency: no `.planning/` root, no `agent_skills`, no `<files_to_read>` blocks.

**The carve-out (DEC-174): the harness PLANS its own work but does not EXECUTE changes to its own
enforcement layer.** Changes to `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
`check-state.sh` or `check-docs.sh` are made **directly** — ordinary edits, tests run explicitly, a
human reading the diff — never dispatched through a team run whose gates are the thing being changed.
Green gates cannot vouch for the code that produces them: on 2026-08-03 all four gates passed while
four `.harness` YAML files did not parse and the validator rejected its own normative template.
Grilling, BRIEF, PLAN and the review panel remain self-hosted and are unaffected.

**Working in a worktree, run everything from the worktree.** `main` is behind by construction while
harness code is being changed, so a stale copy silently tests the wrong logic.

| What | Where |
|---|---|
| Project state | `.harness/` — see `.harness/README.md` for the layout and who writes what |
| Config | `.harness/harness.json` (gates, `test_matrix`, `test_kinds`, budgets) |
| The org, as data | `.harness/team-config.yaml` |
| Rule skills | `.claude/skills/harness-<name>/` — **flat**, one level under `.claude/skills/` |
| Agents | `.claude/agents/harness-*.md` |
| Design docs | `docs/harness/SPEC.md` (what it is) · `DECISIONS-INDEX.md` (**the entry point** — one row per decision) · `DECISIONS.md` (why — **the authority**) · `BUILD.md` (what is left) |

**The org is 16 agents in four tiers:** main session (layer 0, the only user channel) →
`harness-orchestrator` (layer 1, one per in-flight feature) → three domain leads (layer 2) →
members (layer 3, always leaves). Rules reach agents by native `skills:` preload, and Expertise by
a `SubagentStart` hook — nothing needs to be told to go read a file.

**Before changing any harness doc, read `docs/harness/DECISIONS-INDEX.md`**, grep it for the
surface you are touching, and open the two or three entries it names. The authority
`docs/harness/DECISIONS.md` is never read in its entirety (DEC-150) — the index exists so that it
need not be. Cited decisions are a floor, not a ceiling: go broader via the index when a cited entry
points at one nobody named. A row is an open-or-skip filter, so open the entry before acting on it.

Then run `.claude/skills/harness/bin/check-docs.sh`. It is the propagation checker, and its registry
is DECISIONS.md itself.

## Conventions

- Every claim in prose that a command can check gets checked before it is written.
- Check `bin/check-docs.sh` BEFORE committing, never after.
- The GSD-era stack analysis that once filled this file lives in git history only (removed at DEC-135).
