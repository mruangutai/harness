# Harness: Engineering Rules

Engineering discipline rules injected into GSD agents via `agent_skills`. Each rule file is an enforcement specification — imperative, not guidance.

## Role-Based Loading

Read ONLY the file(s) that apply to your agent type:

| Agent Type | Files to Read |
|------------|---------------|
| gsd-executor | tdd-enforcement.md |
| gsd-planner | spec-driven.md |
| gsd-debugger | systematic-debugging.md |
| gsd-verifier | verification-rules.md |
| harness-code-reviewer | code-review.md |

Do NOT read files not listed for your agent type. Cross-contamination between discipline files causes conflicting instructions.

## Files

- tdd-enforcement.md — TDD Iron Law + zero-placeholder executor gate (ENG-01, ENG-03)
- spec-driven.md — Spec-driven planning constraints (ENG-02)
- systematic-debugging.md — 4-phase RCA + 3-failure cap (ENG-04)
- code-review.md — Two-stage spec + quality review protocol (ENG-05, ENG-06)
- verification-rules.md — Post-execution verification augmentations
