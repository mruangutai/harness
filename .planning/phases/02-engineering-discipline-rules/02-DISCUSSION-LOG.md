# Phase 2: Engineering Discipline Rules - Discussion Log (Assumptions Mode)

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-04-05
**Phase:** 02-engineering-discipline-rules
**Mode:** assumptions + user corrections
**Areas analyzed:** File Layout, TDD Enforcement, Spec-Driven Development, Code Review Gate, Systematic Debugging

## Assumptions Presented

### File Layout and Grouping
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| 4-file grouping matching existing stubs (ENG-01+03 together, ENG-04 alone, ENG-05+06 together) | Likely | `.claude/skills/harness/rules/SKILL.md` indexes exactly 4 files; ENG-01 and ENG-03 both enforced at executor time |

### TDD Enforcement Content
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| tdd-enforcement.md adds Iron Law + red-flag checklist + deletion penalty + permission model (not duplicating GSD's tdd.md) | Confident | GSD's tdd.md is advisory guidance; FEATURES.md documents 7 enforcement layers superpowers adds |

### Spec-Driven Development
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| No new spec artifact; ENG-02 as CLAUDE.md gate instruction requiring CONTEXT.md to have approaches+tradeoffs | Likely | Phase 1 D-03 established CLAUDE.md for phase-gate triggers; ROADMAP.md success criterion says spec "exists", not spec "file" |

### Code Review Gate
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| CLAUDE.md → Task() spawning harness-code-reviewer agent (not agent_skills into gsd-verifier) | Likely | ENG-06 independence requirement; Phase 1 D-04 established gate roles as Task()-spawned agents |

### Systematic Debugging
| Assumption | Confidence | Evidence |
|------------|-----------|----------|
| Inject into gsd-debugger via agent_skills (not gsd-executor or CLAUDE.md global) | Unclear | gsd-debugger is a registered subagent type; current agent_skills only has gsd-executor + gsd-verifier |

## Corrections Made

### File Layout
- **Original assumption:** 4-file layout, ENG-02 as CLAUDE.md gate instruction
- **User correction:** 5-file layout — add `spec-driven.md` injected into gsd-planner via agent_skills
- **User question:** Does injecting into gsd-planner via agent_skills break compatibility if we run /gsd-update?
- **Resolution:** Risk is LOW. agent_skills config is project-local (.planning/config.json) — GSD updates never touch project files. Lookup key `gsd-planner` confirmed stable in plan-phase.md line 28 and buildAgentSkillsBlock() API. If it changes, injection silently stops (no error) — detectable via `gsd-tools agent-skills gsd-planner`. User accepted the risk.

### Spec-Driven (ENG-02) correction
- **Original assumption:** ENG-02 stays as CLAUDE.md gate instruction only
- **User correction:** spec-driven.md file added to rules/, injected into gsd-planner — spec constraints apply at plan-writing time, not just as a gate
- **Rationale:** Belt AND suspenders: CLAUDE.md gate checks CONTEXT.md completeness before plan-phase; spec-driven.md injected into gsd-planner ensures plan tasks reference acceptance criteria and have no TBD content at source

## Auto-Resolved

- Systematic debugging injection: user selected "gsd-debugger via agent_skills (Recommended)" — confirmed cleanest selective-loading approach
- Code review gate: user selected "CLAUDE.md → Task() harness-code-reviewer agent (Recommended)" — confirmed independence requirement upheld

## External Research

None performed — codebase provided sufficient evidence for all areas.
