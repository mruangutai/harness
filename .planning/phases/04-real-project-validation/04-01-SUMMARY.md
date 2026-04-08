---
phase: 04-real-project-validation
plan: 01
subsystem: harness-eng-reviewer
tags: [agent, pre-discuss, architecture-review, claude-md]
dependency_graph:
  requires: []
  provides: [harness-eng-reviewer-pre-discuss-mode, claude-md-eng-reviewer-triggers]
  affects: [harness-eng-reviewer, CLAUDE.md]
tech_stack:
  added: []
  patterns: [dual-mode-agent, mode-detection-from-task-description]
key_files:
  created: []
  modified:
    - .claude/agents/harness-eng-reviewer.md
    - CLAUDE.md
decisions:
  - "Pre-discuss output format is numbered questions list (not a report) — distinct from post-discuss Architecture Review format"
  - "Mode detection is plaintext: agent reads task description to determine pre-discuss vs post-discuss"
  - "Operating Modes section placed between Role and Protocol sections for logical reading order"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-08"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
---

# Phase 4 Plan 01: Add Pre-Discuss Mode to harness-eng-reviewer Summary

**One-liner:** Dual-mode harness-eng-reviewer with 3-step pre-discuss architectural questions protocol and two CLAUDE.md spawn triggers.

## Tasks Completed

| Task | Name | Commit | Files Modified |
|------|------|--------|----------------|
| 1 | Add Pre-Discuss Mode Protocol to harness-eng-reviewer.md | 6a9fa38 | .claude/agents/harness-eng-reviewer.md |
| 2 | Add eng reviewer trigger lines to CLAUDE.md harness section | 6a9fa38 | CLAUDE.md |

## What Was Built

### Task 1: harness-eng-reviewer.md

Added two new sections to the agent file without modifying any existing content:

**`## Operating Modes`** (inserted between `## Role` and `## Protocol`):
- Explains the two modes and how to self-detect which applies
- Mode detection: reads task description — "pre-discuss mode" in the text triggers `## Pre-Discuss Mode Protocol`, otherwise defaults to `## Protocol` (post-discuss)

**`## Pre-Discuss Mode Protocol`** (inserted immediately before `## Protocol`):
- 3-step process: (1) read ROADMAP.md phase goal, (2) inspect codebase with Glob/Grep for relevant patterns and integration points, (3) generate 5-10 load-bearing architectural questions
- Output format: `# Architecture Pre-Questions` with numbered questions grouped by concern area (system interfaces, data models, integration points, trust boundaries, behavioral contracts)
- Output is questions only — no verdict, no tables, no Architecture Review report

All existing post-discuss content (`## Protocol`, `## Inputs`, `## Output Format`) is fully preserved. Verification: `grep -c "Data Flow|Edge Case|Test Matrix|Advisory Verdict"` returns 7 (required ≥ 4).

### Task 2: CLAUDE.md

Added two trigger lines to the `<!-- GSD:harness-start -->` / `<!-- GSD:harness-end -->` block, after the existing 5 trigger lines:

```
Before /gsd-discuss-phase on architectural phases (agents, APIs, data models, schemas): spawn harness-eng-reviewer in pre-discuss mode.
After /gsd-discuss-phase: spawn harness-eng-reviewer.
```

`grep -c "harness-eng-reviewer" CLAUDE.md` returns exactly 2.

## Verification Results

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| Pre-Discuss Protocol section exists | `grep -q "## Pre-Discuss Mode Protocol"` | Found | PASS |
| Operating Modes section exists | `grep -q "## Operating Modes"` | Found | PASS |
| Post-discuss format preserved | `grep -c "Data Flow\|Edge Case\|Test Matrix\|Advisory Verdict"` | 7 (need ≥ 4) | PASS |
| Exactly 2 eng-reviewer references in CLAUDE.md | `grep -c "harness-eng-reviewer" CLAUDE.md` | 2 | PASS |
| Pre-discuss trigger exists | `grep -q "pre-discuss mode" CLAUDE.md` | Found | PASS |
| Post-discuss trigger exists | `grep -q "After /gsd-discuss-phase: spawn harness-eng-reviewer"` | Found | PASS |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None. Both new sections are complete protocol definitions, not placeholders.

## Threat Flags

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Agent files are local markdown only.

## Self-Check: PASSED

- `.claude/agents/harness-eng-reviewer.md` — exists and contains both new sections
- `CLAUDE.md` — contains exactly 2 harness-eng-reviewer references in harness block
- Commit `6a9fa38` — verified in git log
