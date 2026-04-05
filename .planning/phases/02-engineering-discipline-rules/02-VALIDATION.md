---
phase: 2
slug: engineering-discipline-rules
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-05
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual behavioral testing (no automated test framework applicable) |
| **Config file** | None — validation is behavioral, not unit-testable |
| **Quick run command** | Read the modified file and verify required sections are present |
| **Full suite command** | Run `node ~/.claude/get-shit-done/bin/gsd-tools.cjs agent-skills <type>` for each new injection; observe output contains harness rules block |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Read the modified file and verify it contains required sections
- **After every plan wave:** Run `gsd-tools agent-skills` for each new agent type to confirm injection works
- **Before `/gsd-verify-work`:** All 6 smoke checks must pass
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2-xx-01 | TBD | 1 | ENG-01 | — | N/A | smoke | `node ~/.claude/get-shit-done/bin/gsd-tools.cjs agent-skills gsd-executor` outputs block with tdd/ reference | ✅ | ⬜ pending |
| 2-xx-02 | TBD | 1 | ENG-02 | — | N/A | smoke | `node ~/.claude/get-shit-done/bin/gsd-tools.cjs agent-skills gsd-planner` outputs block with rules/ reference | ❌ W0 | ⬜ pending |
| 2-xx-03 | TBD | 1 | ENG-03 | — | N/A | manual | Read tdd-enforcement.md and confirm zero-placeholder rejection gate section exists | ✅ after write | ⬜ pending |
| 2-xx-04 | TBD | 1 | ENG-04 | — | N/A | smoke | `node ~/.claude/get-shit-done/bin/gsd-tools.cjs agent-skills gsd-debugger` outputs block with systematic-debugging reference | ❌ W0 | ⬜ pending |
| 2-xx-05 | TBD | 2 | ENG-05 | — | N/A | smoke | `grep "harness-code-reviewer" CLAUDE.md` returns gate instruction | ❌ W0 | ⬜ pending |
| 2-xx-06 | TBD | 2 | ENG-06 | — | N/A | smoke | `cat .claude/agents/harness-code-reviewer.md` confirms YAML frontmatter and two-stage review content | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.claude/agents/harness-code-reviewer.md` — agent stub needed for ENG-05, ENG-06 smoke tests
- [ ] `gsd-planner` entry in `.planning/config.json agent_skills` — needed for ENG-02 agent-skills smoke test
- [ ] `gsd-debugger` entry in `.planning/config.json agent_skills` — needed for ENG-04 agent-skills smoke test
- [ ] `.claude/skills/harness/rules/spec-driven.md` — content file needed for ENG-02
- [ ] CLAUDE.md spec gate and review gate instructions — needed for ENG-05 smoke test

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| TDD Iron Law mandate present in tdd-enforcement.md | ENG-01 | File content check, not executable | Read file; confirm "Iron Law" / "failing test first" mandate section exists with deletion/rewrite guard language |
| Zero-placeholder rejection gate | ENG-03 | Behavioral enforcement, not unit-testable | Read tdd-enforcement.md; confirm section rejecting TBD/placeholder content with explicit re-planning guard |
| Systematic debugging 4-phase protocol | ENG-04 | Agent behavioral prompt, not executable | Read systematic-debugging.md; confirm 4-phase structure (Observe, Hypothesize, Test, Fix) and 3-failure cap |
| Two-stage review protocol in code-reviewer agent | ENG-06 | Agent instruction file | Read harness-code-reviewer.md; confirm Stage 1 = spec compliance, Stage 2 = code quality, tools = Read-only |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
