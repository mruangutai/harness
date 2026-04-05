# Harness

## What This Is

A unified Claude Code workflow that combines the best of three frameworks — GSD (Get Shit Done), gstack, and superpowers — into a cohesive harness for AI-assisted software development. It uses GSD's context engine as the backbone, integrates gstack's role-based perspectives (CEO, Architect, Lead Engineer, QA) at key workflow gates, and enforces superpowers' engineering discipline (TDD, spec-driven development) during implementation. Built as portable files (CLAUDE.md, skills, agent definitions) first, with a path to global installation and distributable package.

## Core Value

Enable a CTO to take a software idea from product validation through architecture, disciplined implementation, and QA — with Claude executing reliably at each stage without context drift, scope creep, quality shortcuts, or unchallenged assumptions.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Deep analysis of each framework (GSD, gstack, superpowers) — what each part does, strengths, weaknesses, integration points
- [ ] Determine which parts of gstack and superpowers are most valuable for integration into GSD's subagent model
- [ ] Role-based perspective gates: CEO/Product (idea validation, market fit, scope challenge), Architect/Eng (architecture review, pattern enforcement, tech decisions), Lead Engineer (production-quality code, TDD, best practices), QA (testing, edge cases, requirement verification)
- [ ] Strict TDD enforcement for implementation code (RED-GREEN-REFACTOR as non-negotiable gate, with anti-skip guards) — scaffolding/config exempt
- [ ] PRD/spec layer integrated into the workflow — acceptance criteria, edge cases, non-goals defined before code is written. Explore whether to enhance GSD's existing artifacts or add a separate spec document (research superpowers' approach)
- [ ] Context management via GSD's subagent/orchestrator pattern — the harness must prevent context bloat by design
- [ ] Files-first deliverable: CLAUDE.md, skills/, agents/ that can be dropped into any project
- [ ] Validation on a real project before going global
- [ ] Path to global installation (~/.claude/) and distributable package

### Out of Scope

- Building a standalone CLI or programmatic tooling (for v1 — files-only approach)
- Wiring against live upstream repos (gstack, superpowers) as dependencies — copy and own the prompts
- Real-time collaborative features or multi-user workflow
- Replacing GSD's core infrastructure — we extend it, not rebuild it

## Context

- Mike is CTO of Implentio (seed-stage AI startup), primary user of Claude Code for development
- Has daily experience with GSD but has not hands-on used gstack or superpowers — knowledge of those two is research-based
- Council research (council/unified-harness-gsd-gstack-superpowers/shared_reasoning.md) identified key architectural insight: **route, don't stack** — exclusive ownership per phase, not simultaneous constraint activation
- Existing proof-of-concept: mattjaikaran/unified-workflow bridges GSD + superpowers using routing-not-nesting pattern
- All four pain points are real and felt daily: context drift, code quality shortcuts, scope creep, lack of pushback from Claude
- Target: personal CTO tool first, team-adoptable for Implentio second, distributable third
- Lean toward enhancing GSD's existing artifact chain (PROJECT.md → REQUIREMENTS.md → PLAN.md) with spec/PRD capabilities rather than adding new documents, but want to research superpowers' approach before committing

## Constraints

- **Delivery format**: Files-only for v1 (CLAUDE.md, skills, agents) — no CLI, no build step, no dependencies
- **GSD compatibility**: Must work within GSD's existing subagent/orchestrator model, not fight against it
- **Context budget**: The harness itself must not bloat Claude's context — selective loading, not everything-at-once
- **Copy-and-own**: Absorb gstack/superpowers patterns into harness-owned files, not live external dependencies
- **TDD scope**: Mandatory for implementation code, exempt for config/scaffolding/one-off scripts

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| GSD's context engine as backbone | Only framework architecturally designed for context management (thin orchestrator, subagent isolation) | — Pending validation during exploration |
| Files-first delivery | Fastest path to validation; content is the same regardless of delivery mechanism | — Pending |
| Route-not-stack architecture | Council research: stacking three authority-claiming systems produces governance conflicts; routing assigns exclusive ownership per phase | — Pending validation |
| Copy-and-own gstack/superpowers prompts | Decouples from upstream breakage; gstack is single-author personal tooling with uncertain long-term maintenance | — Pending |
| Explore PRD/spec integration approach | User leans toward enhancing GSD artifacts but wants to understand superpowers' approach first | — Pending research |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-04 after initialization*
