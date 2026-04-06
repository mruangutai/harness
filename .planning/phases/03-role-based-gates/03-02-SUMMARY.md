---
phase: 03-role-based-gates
plan: 02
subsystem: agents
tags: [qa, security, role-gates, owasp, stride]
dependency_graph:
  requires: [03-01-SUMMARY.md]
  provides: [harness-qa-reviewer, harness-security-reviewer, CLAUDE.md-gate-triggers]
  affects: [CLAUDE.md]
tech_stack:
  added: []
  patterns: [spec-then-verify, self-scoping-audit, advisory-reports]
key_files:
  created:
    - .claude/agents/harness-qa-reviewer.md
    - .claude/agents/harness-security-reviewer.md
  modified:
    - CLAUDE.md
decisions:
  - "QA reviewer uses two-phase spec-then-verify: Phase 1 generates test cases from CONTEXT.md before reading any source files; Phase 2 verifies each test case against implementation"
  - "Security reviewer self-scopes via keyword scan of PLAN.md/SUMMARY.md — skips full audit if no security-sensitive keywords found (valid first-class outcome)"
  - "CLAUDE.md harness section stays within token budget with 5 total instruction lines"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-06"
  tasks_completed: 3
  files_changed: 3
---

# Phase 3 Plan 02: QA and Security Gate Agents Summary

Created harness-qa-reviewer and harness-security-reviewer advisory agents, and wired all four role gates into CLAUDE.md trigger instructions.

## Tasks Completed

### Task 1: harness-qa-reviewer.md (ROLE-03)

Created `.claude/agents/harness-qa-reviewer.md` with a two-phase spec-then-verify protocol:

- **Phase 1 (Spec Analysis):** Reads CONTEXT.md and ROADMAP.md success criteria only. Produces test cases (TC-01, TC-02, ...) with source, description, and expected outcome. Explicit "STOP" instruction prevents reading source files prematurely.
- **Phase 2 (Implementation Verification):** Uses Glob/Grep to find source files. Verifies each test case with PASS/FAIL/PARTIAL status. Identifies spec gaps and generates regression test suggestions.
- Output format: test case table, verification results table, spec gaps, regression suggestions, advisory verdict.
- 91 lines. Zero gstack-specific references.

### Task 2: harness-security-reviewer.md (ROLE-04)

Created `.claude/agents/harness-security-reviewer.md` with self-scoping + OWASP/STRIDE protocol:

- **Step 1 (Scope Assessment):** Scans PLAN.md/SUMMARY.md for 25+ security-sensitive keywords across 6 categories (authentication, data protection, input handling, access control, network, data storage). If no keywords found: outputs "Not in scope" declaration and stops — valid first-class outcome.
- **Step 2 (OWASP Top 10):** All 10 categories (A01–A10) with specific checks per category.
- **Step 3 (STRIDE):** All 6 threat categories against identified trust boundaries.
- Dual output format: skip declaration (not in scope) and full audit report (in scope).
- 118 lines. Zero gstack-specific references.

### Task 3: CLAUDE.md Gate Triggers (D-19)

Added two lines to the `<!-- GSD:harness-start/end -->` section:

```
At new-project init or scope-change: spawn harness-ceo-reviewer.
Before /gsd-ship: spawn harness-qa-reviewer and harness-security-reviewer.
```

All existing lines preserved unchanged. Harness section now has 5 instruction lines total.

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `.claude/agents/harness-qa-reviewer.md` | Created | 91 |
| `.claude/agents/harness-security-reviewer.md` | Created | 118 |
| `CLAUDE.md` | Modified (+2 lines in harness section) | — |

## Deviations from Plan

None. Plan executed exactly as written.

One note: the plan's verification command `grep -c "harness-ceo-reviewer\|harness-code-reviewer\|harness-qa-reviewer\|harness-security-reviewer" CLAUDE.md` returns 3 (not 4) because `grep -c` counts matching lines, and harness-qa-reviewer and harness-security-reviewer appear on the same line. All 4 agent names are present in CLAUDE.md (confirmed via `grep -o`).

## Verification Status (must_haves)

| Truth | Status |
|-------|--------|
| harness-qa-reviewer.md contains two-phase protocol with spec-only Phase 1 | PASS |
| harness-security-reviewer.md contains self-scoping step | PASS |
| harness-security-reviewer.md runs OWASP Top 10 + STRIDE when security-sensitive | PASS |
| CLAUDE.md harness section contains CEO trigger and QA/Security pre-ship triggers | PASS |
| Neither agent contains gstack-specific references | PASS |
| Both agents produce advisory reports, not hard blocks | PASS |

## Known Stubs

None. Both agent files are fully populated with complete protocols and output formats.

## Commit

`86ea69c` — feat(03): create harness-qa-reviewer, harness-security-reviewer agents and CLAUDE.md gates

## Self-Check

- `.claude/agents/harness-qa-reviewer.md` — FOUND (91 lines)
- `.claude/agents/harness-security-reviewer.md` — FOUND (118 lines)
- `CLAUDE.md` harness section — contains all 4 reviewer names
- Commit `86ea69c` — FOUND
