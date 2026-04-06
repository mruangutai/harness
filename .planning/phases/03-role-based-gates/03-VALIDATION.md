---
phase: 3
slug: role-based-gates
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-06
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual verification (no automated test framework — agent files are markdown) |
| **Config file** | none |
| **Quick run command** | `ls .claude/agents/harness-*.md` |
| **Full suite command** | `ls .claude/agents/harness-*.md && grep -l "## ROLE-" .claude/agents/harness-*.md` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `ls .claude/agents/harness-*.md`
- **After every plan wave:** Verify file exists and contains role prompt content (grep)
- **Before `/gsd-verify-work`:** All 4 agent files present and contain role prompt; CLAUDE.md has 2 new trigger lines
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 3-CEO-01 | CEO | 1 | ROLE-01 | — | N/A | file_check | `test -f .claude/agents/harness-ceo-reviewer.md` | ❌ W0 | ⬜ pending |
| 3-ENG-01 | ENG | 1 | ROLE-02 | — | N/A | file_check | `test -f .claude/agents/harness-eng-reviewer.md` | ❌ W0 | ⬜ pending |
| 3-QA-01 | QA | 2 | ROLE-03 | — | N/A | file_check | `test -f .claude/agents/harness-qa-reviewer.md` | ❌ W0 | ⬜ pending |
| 3-SEC-01 | SEC | 2 | ROLE-04 | — | N/A | file_check | `test -f .claude/agents/harness-security-reviewer.md` | ❌ W0 | ⬜ pending |
| 3-CLAUDE-01 | CLAUDE | 3 | ROLE-01, ROLE-03, ROLE-04 | — | N/A | grep | `grep -c "harness-ceo-reviewer\|harness-qa-reviewer\|harness-security-reviewer" CLAUDE.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] No test framework to install — validation is file/grep based
- [ ] All 4 agent files will be created/populated during Wave 1 & 2

*Existing infrastructure covers all phase requirements (agent files and CLAUDE.md already exist as stubs).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CEO reviewer asks forcing questions relevant to scope | ROLE-01 | LLM output quality — not mechanically verifiable | Invoke harness-ceo-reviewer on a sample PROJECT.md, verify output contains scope questions, mode recommendation, and advisory findings |
| Eng reviewer produces architecture verdict | ROLE-02 | LLM output quality | Invoke harness-eng-reviewer on a sample CONTEXT.md, verify output contains verdict, data flow assessment, edge cases |
| QA reviewer completes spec phase before reading implementation | ROLE-03 | Sequential read discipline — not grep-verifiable | Invoke harness-qa-reviewer, verify it outputs test cases before referencing any source files |
| Security reviewer self-scopes correctly | ROLE-04 | LLM judgment call — keyword scan calibration | Invoke harness-security-reviewer on auth-touching phase and non-auth phase; verify triggers vs. skips correctly |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
