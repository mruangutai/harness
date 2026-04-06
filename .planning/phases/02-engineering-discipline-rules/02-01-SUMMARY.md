---
phase: 02-engineering-discipline-rules
plan: 01
subsystem: harness-discipline-rules
tags: [tdd, spec-driven, debugging, agent-skills, enforcement]
dependency_graph:
  requires: [01-03]
  provides: [tdd-enforcement, spec-driven, systematic-debugging, agent-skills-injection]
  affects: [gsd-executor, gsd-planner, gsd-debugger]
tech_stack:
  added: []
  patterns: [agent-skills-injection, role-based-loading, imperative-enforcement-files]
key_files:
  created:
    - .claude/skills/harness/rules/spec-driven.md
  modified:
    - .planning/config.json
    - .planning/harness.json
    - .claude/skills/harness/rules/SKILL.md
    - .claude/skills/harness/tdd/SKILL.md
    - .claude/skills/harness/rules/tdd-enforcement.md
    - .claude/skills/harness/rules/systematic-debugging.md
decisions:
  - "Iron Law framing is imperative MUST — no guidance language anywhere in enforcement files"
  - "rules/SKILL.md uses role-based routing table: each agent type reads only its assigned file"
  - "tdd/SKILL.md delegates to ../rules/tdd-enforcement.md rather than duplicating content"
metrics:
  duration: ~10 minutes
  completed: 2026-04-05
  tasks_completed: 3
  tasks_total: 3
  files_changed: 7
---

# Phase 2 Plan 1: Config Infrastructure and Discipline Rule Files Summary

Populated config injection paths and wrote three enforcement rule files — TDD Iron Law (tdd-enforcement.md), spec-driven planning constraints (spec-driven.md), and systematic debugging protocol (systematic-debugging.md) — completing the agent_skills injection layer for gsd-executor, gsd-planner, and gsd-debugger.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Config infrastructure and SKILL.md indexes | 6186ac9 | config.json, harness.json, rules/SKILL.md, tdd/SKILL.md |
| 2 | TDD enforcement rule file (ENG-01 + ENG-03) | 86bed3b | rules/tdd-enforcement.md |
| 3 | Spec-driven and systematic-debugging rule files (ENG-02 + ENG-04) | 4b0fc13 | rules/spec-driven.md, rules/systematic-debugging.md |

## Decisions Made

- **Iron Law framing:** Imperative throughout — "You MUST", "MUST NOT", "STOP". No "should", "consider", or "recommended" anywhere.
- **Role-based loading table:** rules/SKILL.md routes each agent type to only its relevant file. Cross-contamination between discipline files is explicitly prohibited.
- **tdd/SKILL.md delegates:** Points to `../rules/tdd-enforcement.md` rather than duplicating content. Exemption check instruction lives in tdd/SKILL.md; full rules live in tdd-enforcement.md.
- **CONTEXT.md as the spec:** spec-driven.md names CONTEXT.md as the only spec artifact — no secondary spec documents.
- **3-failure cap scoped correctly:** systematic-debugging.md explicitly distinguishes ENG-04's session-level cap from GSD's plan-level `node_repair_budget`.

## Verification Results

All 3 `gsd-tools agent-skills` smoke tests pass:
- `gsd-executor` returns tdd/ reference
- `gsd-planner` returns rules/ reference
- `gsd-debugger` returns rules/ reference

Content checks:
- tdd-enforcement.md: Iron Law text present, 13 red flag checklist items, zero-placeholder gate with 6 forbidden patterns, exemptions section
- spec-driven.md: Task Completeness Requirements, Placeholder Rejection, Spec Traceability, Verification Requirements
- systematic-debugging.md: 4-phase protocol (Observe/Hypothesize/Test/Fix), 3-Failure Cap, Forbidden Patterns, node_repair_budget reference

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all files written to full enforcement specification.

## Threat Flags

None — plan produces markdown rule files and JSON config edits only. No new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

## Self-Check: PASSED

Files exist:
- .planning/config.json — FOUND
- .planning/harness.json — FOUND
- .claude/skills/harness/rules/SKILL.md — FOUND
- .claude/skills/harness/tdd/SKILL.md — FOUND
- .claude/skills/harness/rules/tdd-enforcement.md — FOUND
- .claude/skills/harness/rules/spec-driven.md — FOUND
- .claude/skills/harness/rules/systematic-debugging.md — FOUND

Commits exist:
- 6186ac9 — FOUND
- 86bed3b — FOUND
- 4b0fc13 — FOUND
