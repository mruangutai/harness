# Phase 4: Real-Project Validation - Research

**Researched:** 2026-04-08
**Domain:** Agent prompt extension (pre-discuss mode), validation execution guide structure, token budget measurement, pain-point evidence collection
**Confidence:** HIGH

## Summary

Phase 4 has two distinct parts that require different plan formats. Part 1 is a conventional harness improvement: add a pre-discuss operational mode to `harness-eng-reviewer.md` and wire it via a new CLAUDE.md trigger line. Part 2 is unconventional: Plans 02-04 are validation execution guides for running the harness on the Implentio PDF editor feature across three sub-phases. These are structured checklists, not code implementation plans. Part 3 is a post-validation measurement task that collects empirical token counts and pain-point evidence.

A critical gap was discovered during research: `harness-eng-reviewer` has no CLAUDE.md trigger line at all. The Phase 3 research noted "trigger already referenced" but the existing line (`Before /gsd-plan-phase: verify CONTEXT.md has approaches-with-tradeoffs`) is a spec gate that verifies a condition — it does not spawn the agent. Both the post-discuss spawn trigger and the new pre-discuss trigger need to be added to CLAUDE.md in Plan 01.

The CLAUDE.md full file currently measures approximately 3,670 tokens (chars/4 estimation), far exceeding the INFRA-01 1K threshold. The inflation is entirely in the `<!-- GSD:stack-start -->` section (approx. 2,814 tokens of design notes that should be in a reference doc, not CLAUDE.md). Plan 05 measures this and flags it — fixing it is Phase 1 scope, not Phase 4 scope.

**Primary recommendation:** Plan 01 modifies one agent file and one CLAUDE.md section. Plans 02-04 are execution guides with observable success criteria (artifacts produced, git evidence). Plan 05 is a measurement script + report.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01: Validation Project**
Implentio PDF editor — invoice annotation tool for 3PL invoices. Ingests PDFs, uses OCR + AI to extract key fields (invoice date, billing period, charge description, charge amount, biller/3PL name, customer name). Routes by confidence: ≥90% auto-ingest, <90% block and route to human review queue. Existing partial extraction pipeline in Implentio codebase — no confidence scoring, no routing logic, no annotation UI yet. Tech stack: TanStack + TypeScript (full-stack). Backend TBD via codebase exploration during discuss-phase for each sub-phase.

**D-02: Confidence Threshold**
<90% = human review queue. Binary threshold. No separate 70-90% tier.

**D-03: Validation Sub-Phase Breakdown**
Three sub-phases, each run with the full harness (discuss → plan → execute → code review → verify → QA/security gate):
- Sub-Phase A: Confidence scoring + data blocking logic
- Sub-Phase B: Annotation UI (split-screen PDF viewer + annotation form)
- Sub-Phase C: Re-parse flow + unblock

**D-04: Pain Point Evidence Criteria (VAL-03)**
Observable and verifiable from git history and planning artifacts:
| Pain Point | Required Evidence |
|---|---|
| Context drift | At least one executor subagent SUMMARY.md shows only files listed in the plan — no off-plan edits |
| Quality shortcuts | At least one plan has a test file committed before its implementation file (verifiable via `git log`) |
| Scope creep | At least one discuss-phase session produces a `<deferred>` section showing a scope item caught and redirected |
| Lack of pushback | At least one role-gate agent fires and produces a report with ≥1 finding or forcing question |

**D-05: Token Budget Measurement (VAL-02)**
Post-phase dedicated measurement task, after all 3 sub-phases complete. Measures: CLAUDE.md token count, each skill file in `.claude/skills/harness/`, each agent definition in `.claude/agents/harness-*.md`, actual agent_skills injection paths from harness.json. Output: `MEASUREMENTS.md` with pass/fail for each threshold.

**D-06: Harness Improvement — Eng Reviewer Pre-Discuss Mode**
`harness-eng-reviewer` gains a second operational mode:
- **Pre-discuss mode (new):** Spawned BEFORE discuss-phase on architectural phases. Reads phase goal from ROADMAP.md, generates architectural questions for the user to consider during discuss session. Output: questions list, not a review report.
- **Post-discuss mode (existing):** Spawned after discuss-phase to review CONTEXT.md decisions for edge cases, trust boundaries, test matrix gaps. Unchanged.

CLAUDE.md trigger to add: "Before /gsd-discuss-phase on architectural phases (agents, APIs, data models, schemas): spawn harness-eng-reviewer in pre-discuss mode."

Detection heuristic: phase goal contains keywords `agent`, `API`, `schema`, `data model`, `interface`, `contract`, or deliverable is a set of files that define system behavior rather than implement it.

### Claude's Discretion

None specified — all six decisions are locked.

### Deferred Ideas (OUT OF SCOPE)

- VIS-01/VIS-02/VIS-03: Browser automation + visual regression testing — v2
- ADV-01: Cross-model review — v2
- DIST-01: Global ~/.claude/ installation — v2
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VAL-01 | Harness validated on a real project (500+ LOC scope, multiple phases, at least one bug requiring debugging) before distribution | Plans 02-04 are execution guides for the Implentio PDF editor (D-01, D-03) — three sub-phases covering confidence scoring, annotation UI, and re-parse flow |
| VAL-02 | Token budget measured empirically — CLAUDE.md under 1K tokens, skill files measured for actual consumption when injected into subagents | Plan 05 produces MEASUREMENTS.md; baseline measurements documented in this research; measurement approach: chars/4 estimation (no tiktoken available on this machine) |
| VAL-03 | All four pain points verified resolved: context drift, quality shortcuts, scope creep, lack of pushback | Plan 05 collects evidence from git history and planning artifacts per D-04 evidence criteria; VALIDATION-REPORT.md produced |
</phase_requirements>

---

## Plan Structure

Phase 4 produces 5 plans:

| Plan | Type | What It Does |
|------|------|--------------|
| 04-01-PLAN.md | Implementation | Add pre-discuss mode to harness-eng-reviewer.md; add 2 trigger lines to CLAUDE.md |
| 04-02-PLAN.md | Execution guide | Validation run guide for Sub-Phase A (confidence scoring) |
| 04-03-PLAN.md | Execution guide | Validation run guide for Sub-Phase B (annotation UI) |
| 04-04-PLAN.md | Execution guide | Validation run guide for Sub-Phase C (re-parse flow) |
| 04-05-PLAN.md | Measurement task | Post-validation token measurement + pain-point evidence collection |

Plans 01 and 05 execute in the harness repo. Plans 02-04 guide work in the Implentio repo.

---

## Plan 01: Pre-Discuss Mode Implementation

### What Needs to Change

**File 1: `.claude/agents/harness-eng-reviewer.md`**

Current state: single-mode agent (post-discuss review). The file has a `## Role`, `## Protocol` (4 steps), `## Inputs`, and `## Output Format` section. It is 868 words / ~1,501 tokens.

Required change: add a second operational mode. The agent needs to detect which mode it is in at spawn time and execute the correct protocol.

**Mode detection approach:** The spawning instruction provides the mode explicitly in the Task() prompt — either "run in pre-discuss mode" or "run in post-discuss mode". The agent reads the invocation context (what it was told when spawned) to determine which mode applies. No frontmatter flag needed — the mode is passed via the task description text.

**Pre-discuss mode protocol (new section):**

```
## Pre-Discuss Mode Protocol

When spawned in pre-discuss mode, you receive a phase goal (from ROADMAP.md) and produce
architectural questions for the user to consider before their discuss-phase session.

Step 1: Read the phase goal and success criteria from ROADMAP.md.
Step 2: Identify the architectural decisions implied by the phase goal that the user will
        need to resolve during discuss-phase. Focus on:
        - System interfaces: what APIs, contracts, or data schemas does this phase define?
        - Data models: what entities, fields, relationships, or constraints are introduced?
        - Integration points: what existing systems does this phase connect to or modify?
        - Trust boundaries: what data crosses system boundaries, and what validation is needed?
        - Behavioral contracts: what invariants must hold, and what failure modes exist?
Step 3: Produce 5-10 architectural questions the user should have answers to before
        the discuss-phase session begins. Questions must be:
        - Specific to the phase goal (not generic architecture questions)
        - Answerable by the user (not "what does the codebase do" — explore the codebase first)
        - Load-bearing: the answer meaningfully changes how the phase is implemented

Output: a list of architectural questions with brief rationale for each.
```

**Output format for pre-discuss mode:**

```markdown
# Architecture Pre-Questions

**Phase:** [phase name]
**Mode:** Pre-discuss (questions for user before discuss session)

## Architectural Questions

1. **[Question title]** — [1-sentence rationale for why this matters]
   Question: [specific, answerable question]

2. **[Question title]** — [rationale]
   Question: [question]

[5-10 questions total]

## Why These Questions Matter

[2-3 sentences on what decisions these questions unlock — what the executor and planner need that discuss-phase must produce]
```

**File 2: `CLAUDE.md` harness section**

Current state (the 5 trigger lines that exist):
```
When dispatching subagents, include `.planning/harness.json` in the `<files_to_read>` block.
Before /gsd-plan-phase: verify CONTEXT.md has approaches-with-tradeoffs and user approval.
After /gsd-execute-phase on implementation plans: spawn harness-code-reviewer before /gsd-ship.
At new-project init or scope-change: spawn harness-ceo-reviewer.
Before /gsd-ship: spawn harness-qa-reviewer and harness-security-reviewer.
```

**Critical finding:** `harness-eng-reviewer` has NO spawn trigger in CLAUDE.md. Two lines need to be added:

1. Pre-discuss trigger (D-06): "Before /gsd-discuss-phase on architectural phases (agents, APIs, data models, schemas): spawn harness-eng-reviewer in pre-discuss mode."

2. Post-discuss trigger (missing from Phase 3): "After /gsd-discuss-phase: spawn harness-eng-reviewer."

The post-discuss trigger was referenced in Phase 3 research as "already in CLAUDE.md" but what existed was only the spec-gate verification line (`Before /gsd-plan-phase: verify CONTEXT.md...`), not an agent spawn trigger. This is a Phase 3 carry-forward gap. [VERIFIED: read CLAUDE.md lines 201-212]

**Token budget for new trigger lines:** The harness section currently has ~146 tokens (~584 chars). Two new lines of ~15 tokens each = ~176 tokens total. Well within the ~50-word budget for the harness section. [VERIFIED: measured CLAUDE.md sections]

### Architectural Phase Detection

D-06 specifies keyword detection: `agent`, `API`, `schema`, `data model`, `interface`, `contract`.

There is no existing GSD mechanism for phase-type detection. The CLAUDE.md trigger instruction is the detection mechanism — Claude reads the phase goal at discuss-phase time, matches keywords, and decides whether to spawn the pre-discuss reviewer. This is consistent with how all other harness triggers work: they are instructions to Claude (the main session), not automated hooks. [VERIFIED: read discuss-phase.md — no phase-type detection logic exists]

### Plan 01 Must-Haves

- `harness-eng-reviewer.md` contains both `## Post-Discuss Mode Protocol` (or retitled existing `## Protocol`) and `## Pre-Discuss Mode Protocol` sections
- Pre-discuss output format produces a numbered list of 5-10 architectural questions
- CLAUDE.md harness section contains pre-discuss trigger line matching D-06 wording
- CLAUDE.md harness section contains post-discuss spawn trigger ("After /gsd-discuss-phase: spawn harness-eng-reviewer.")
- Total CLAUDE.md harness section stays within readable bounds (7 trigger lines max)
- harness-eng-reviewer.md file does not lose any existing post-discuss content

---

## Plans 02-04: Validation Execution Guide Structure

### What a Validation Execution Guide Is

Plans 02-04 are NOT implementation plans. They are structured guides for running the harness on an external project (Implentio repo). The executor following these plans produces evidence artifacts, not code in the harness repo.

A validation execution guide differs from an implementation plan:

| Dimension | Implementation Plan | Validation Execution Guide |
|-----------|--------------------|-----------------------------|
| Primary output | Code files, config files | Evidence artifacts (CONTEXT.md, SUMMARY.md, git log) |
| Executor | gsd-executor subagent in harness repo | Human (CTO) running harness commands |
| Verification | `grep` + `git log` in harness repo | Observable evidence from Implentio repo + harness agent outputs |
| Must-haves format | File-level truths + key links | Stage-level completion criteria + evidence checklist |
| Autonomous | Can run autonomously | Requires human interaction at each harness step |

### Template Structure for a Validation Execution Guide

Each guide (Plans 02-04) follows this structure:

```markdown
---
phase: 04-real-project-validation  
plan: 0X
type: validation-guide
sub_phase: [A|B|C]
target_repo: implentio-app (packages/api-v2)
autonomous: false
requirements:
  - VAL-01
  - VAL-03

must_haves:
  truths:
    - "discuss-phase session for Sub-Phase [X] produced a CONTEXT.md with at least 3 locked decisions"
    - "harness-eng-reviewer post-discuss mode was spawned and produced an architecture review report"
    - "At least one planning artifact from this sub-phase has a <deferred> section with ≥1 item"
    - "gsd-executor ran the implementation and produced a SUMMARY.md"
    - "harness-code-reviewer was spawned after execution and produced a code review report"
    - "harness-qa-reviewer was spawned before ship and produced a QA report"
  evidence:
    - type: git-log
      repo: implentio-app
      check: "test file committed before implementation file in at least one plan"
    - type: file-exists
      path: ".planning/phases/[sub-phase]/CONTEXT.md"
      check: "has <deferred> section"
---

<objective>
Run the full harness on Sub-Phase [X] of the Implentio PDF editor feature.
Each stage produces an observable artifact that proves the harness constraint was active.
</objective>

<stages>
### Stage 1: Discuss Phase
...
### Stage 2: Research Phase
...
### Stage 3: Plan Phase
...
### Stage 4: Execute Phase
...
### Stage 5: Code Review Gate
...
### Stage 6: Verify Phase
...
### Stage 7: QA/Security Gate
...
</stages>

<evidence_checklist>
[ ] CONTEXT.md with locked decisions created
[ ] harness-eng-reviewer post-discuss report exists
[ ] <deferred> section with ≥1 item in CONTEXT.md
[ ] SUMMARY.md from executor subagent references only in-plan files
[ ] Test files precede implementation files in git log (verify with command below)
[ ] harness-code-reviewer report exists
[ ] harness-qa-reviewer report exists
[ ] harness-security-reviewer report exists (or documented as out-of-scope)

Verification commands:
git -C [implentio-app path] log --oneline --name-status [plan branch] | grep -E "\.(test|spec)\." 
</evidence_checklist>
```

### Sub-Phase-Specific Content

**Sub-Phase A (Plan 02): Confidence Scoring + Data Blocking**
- Focus: backend logic (confidence calculation, routing to queue)
- Architecture keywords in phase goal: `API`, `schema`, `data model` — triggers pre-discuss eng reviewer
- TDD note: confidence scoring has clear unit test surface (given extraction result with N fields, confidence = X)
- Scope creep risk: annotation UI will be requested early — must be deferred to Sub-Phase B

**Sub-Phase B (Plan 03): Annotation UI**
- Focus: split-screen UI (PDF viewer left, annotation form right)
- Architecture keywords: `interface`, `API` (annotation endpoints)
- Note in guide: UI screenshots will be provided at discuss session — guide should prompt user to attach them
- TDD note: UI components are harder to TDD — guide should note this is a known challenge and document how the harness handles it (vitest/playwright for UI)

**Sub-Phase C (Plan 04): Re-parse Flow + Unblock**
- Focus: post-annotation re-parse, re-score, status transition
- Architecture keywords: `API`, `contract` (unblock endpoint), `schema` (status field transitions)
- This sub-phase completes the routing loop — verify the full flow can be tested end-to-end

### Validation Guide Must-Haves (Each Plan)

Each validation guide must produce at minimum:
1. One CONTEXT.md with locked decisions and at least one `<deferred>` item
2. One harness-eng-reviewer post-discuss report
3. One SUMMARY.md from executor subagent
4. One harness-code-reviewer report
5. One harness-qa-reviewer or harness-security-reviewer report
6. Git log entries showing test file committed before implementation file in at least one wave

---

## Plan 05: Measurement Task

### Token Measurement Approach

No tiktoken is available on this machine. The Anthropic API `count_tokens` endpoint would give exact counts but requires an API key. [VERIFIED: checked npm, python tiktoken, ANTHROPIC_API_KEY — all unavailable]

**Recommended measurement command (chars/4 approximation):**

```python
python3 -c "
import os, glob

def measure(path, label=None):
    with open(path) as f:
        content = f.read()
    chars = len(content)
    words = len(content.split())
    est_tokens = chars // 4
    name = label or os.path.basename(path)
    return name, chars, words, est_tokens

files = [
    '/path/to/harness/CLAUDE.md',
]
# Add skill files, agent files...

print('| File | Chars | ~Tokens | Pass (< threshold) |')
for f in files:
    name, chars, words, tokens = measure(f)
    status = 'PASS' if tokens < 1000 else 'FAIL'
    print(f'| {name} | {chars} | {tokens} | {status} |')
"
```

**Alternative using wc:**
```bash
# Word count (words * 1.3 ≈ tokens is less accurate than chars/4)
wc -c CLAUDE.md  # char count
wc -w CLAUDE.md  # word count
```

**Thresholds for MEASUREMENTS.md:**

| File | Threshold | Current Estimate | Status |
|------|-----------|-----------------|--------|
| CLAUDE.md (full) | <1,000 tokens | ~3,670 tokens | FAIL |
| CLAUDE.md harness section only | <200 tokens | ~146 tokens | PASS |
| harness/SKILL.md | <500 tokens | ~339 tokens | PASS |
| tdd/SKILL.md | ~168 tokens | ~168 tokens | PASS |
| rules/tdd-enforcement.md | <1,000 tokens | ~725 tokens | PASS |
| rules/code-review.md | <1,000 tokens | ~515 tokens | PASS |
| rules/spec-driven.md | <1,000 tokens | ~544 tokens | PASS |
| rules/systematic-debugging.md | <1,000 tokens | ~513 tokens | PASS |
| rules/verification-rules.md | <1,000 tokens | ~521 tokens | PASS |
| harness-eng-reviewer.md | <2,000 tokens | ~1,501 tokens | PASS |
| harness-ceo-reviewer.md | <2,000 tokens | ~1,330 tokens | PASS |
| harness-qa-reviewer.md | <2,000 tokens | ~893 tokens | PASS |
| harness-security-reviewer.md | <2,000 tokens | ~1,294 tokens | PASS |
| harness-code-reviewer.md | <500 tokens | ~284 tokens | PASS |

Note: all estimates are chars/4 approximation. Actual API-measured tokens may differ by 10-20%.

The CLAUDE.md full-file failure is a Phase 1 carry-forward issue. The `<!-- GSD:stack-start -->` section contains approximately 2,814 tokens of design notes that belong in a reference doc. MEASUREMENTS.md should flag this as "Phase 1 debt: CLAUDE.md exceeds 1K threshold due to GSD:stack section — fix in Phase 1 execution."

### Pain-Point Evidence Collection

For VAL-03, Plan 05 collects evidence from git history after all three sub-phases complete.

**Evidence collection commands:**

```bash
# 1. Context drift: verify executor SUMMARY.md lists only in-plan files
cat [implentio-path]/.planning/phases/[sub-phase]/SUMMARY.md
# Look for: "Files modified" list matches plan task file list

# 2. Quality shortcuts (TDD): test before implementation
git -C [implentio-path] log --oneline --name-status --diff-filter=A \
  --pretty=format:"%H %s" | head -100
# Look for: *.test.ts or *.spec.ts committed before the corresponding non-test file

# 3. Scope creep: deferred section in CONTEXT.md
grep -l "<deferred>" [implentio-path]/.planning/phases/*/CONTEXT.md
cat [matching CONTEXT.md] | grep -A 20 "<deferred>"

# 4. Pushback: role gate report with ≥1 finding
ls [harness-repo]/.planning/phases/04-real-project-validation/
# Look for: ARCHITECTURE-REVIEW-*.md, CODE-REVIEW-*.md, QA-REPORT-*.md
grep -l "Finding\|Concern\|Risk\|Question" [report files]
```

**VALIDATION-REPORT.md structure:**

```markdown
# Harness Validation Report

**Project:** Implentio PDF Editor (invoice annotation tool)
**Sub-phases completed:** A, B, C
**Date:** [date]

## VAL-01: Real Project Completion
[confirm 500+ LOC, multiple phases, debugging scenario]

## VAL-02: Token Budget
[link to MEASUREMENTS.md, summary of pass/fail]

## VAL-03: Pain Points Resolved

### Context Drift
Evidence: [SUMMARY.md file reference + observation]
Status: RESOLVED / NOT RESOLVED

### Quality Shortcuts
Evidence: [git log output showing test-before-implementation]
Status: RESOLVED / NOT RESOLVED

### Scope Creep
Evidence: [CONTEXT.md deferred section reference + quote]
Status: RESOLVED / NOT RESOLVED

### Lack of Pushback
Evidence: [role gate report reference + finding quote]
Status: RESOLVED / NOT RESOLVED

## Overall Verdict
PASS / PARTIAL / FAIL
```

---

## Architecture Patterns

### Two-Mode Agent Pattern

The `harness-eng-reviewer.md` extension follows a pattern already implicit in the agent but not explicit: mode as a runtime parameter, not a file-level configuration.

**How mode selection works:**
- The spawning orchestrator (main Claude session) passes the mode in the Task() description text
- The agent reads: "You are being run in pre-discuss mode" or "You are being run in post-discuss mode"
- The agent selects the matching protocol section and executes it
- No frontmatter changes needed — frontmatter is static metadata, not runtime config

**Why not use separate agent files:**
- Two files would require two separate CLAUDE.md trigger lines pointing to different agents
- One file with two modes keeps the logical unit together — these are the same role (eng reviewer) at different trigger points
- Consistent with how gstack /plan-eng-review works: the same persona adapts based on what it's reviewing

**Structural approach for the agent file:**

```markdown
## Operating Modes

This agent has two modes. Read your invocation context to determine which applies.

### Pre-Discuss Mode
[Triggered when: spawned before /gsd-discuss-phase on architectural phases]
[Input: ROADMAP.md phase goal]
[Output: architectural questions list]

### Post-Discuss Mode  
[Triggered when: spawned after /gsd-discuss-phase]
[Input: CONTEXT.md locked decisions + codebase access]
[Output: architecture review report]
```

### Validation Execution Guide vs Implementation Plan

Key structural differences that the planner must handle:

| Property | Implementation Plan | Validation Guide |
|----------|--------------------|--------------------|
| `type` field | `execute` | `validation-guide` |
| `autonomous` | `true` | `false` |
| `must_haves.truths` | File content assertions | Artifact existence + content assertions |
| Verification commands | `grep` on harness files | `git log` + file existence on Implentio repo |
| "Files modified" | Harness repo files | Implentio repo (external) |

The planner should treat validation guides as a distinct plan type. The executor following a validation guide is the human (CTO), not a gsd-executor subagent.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Token counting | Custom tokenizer | chars/4 Python approximation + note error margin |
| Mode detection | Frontmatter flag + conditional loading | Plain-English mode instruction in Task() prompt |
| Architectural phase detection | New config field + detection logic | CLAUDE.md keyword instruction (consistent with all other triggers) |
| Evidence collection tooling | Custom script | Standard git log commands + grep (document commands in Plan 05) |

---

## Common Pitfalls

### Pitfall 1: Missing Post-Discuss Trigger

**What goes wrong:** Plan 01 only adds the pre-discuss trigger line, leaving harness-eng-reviewer with no post-discuss spawn trigger (the existing gap from Phase 3).

**Why it happens:** D-06 explicitly describes the pre-discuss trigger. The post-discuss trigger was assumed to exist from Phase 3 but was never added — it was confused with the spec-gate verification line.

**How to avoid:** Plan 01 must-haves must explicitly check for BOTH trigger lines: `grep "harness-eng-reviewer" CLAUDE.md` should return 2 matches after the plan executes.

**Warning signs:** `grep -c "harness-eng-reviewer" CLAUDE.md` returns 0 after Plan 01 (it currently returns 0).

### Pitfall 2: Validation Guide Treated as Autonomous Plan

**What goes wrong:** The planner marks Plans 02-04 as `autonomous: true`, and a gsd-executor subagent tries to "implement" the Implentio sub-phases by editing the Implentio codebase from within the harness repo context.

**Why it happens:** gsd-executor always expects to make file edits. Validation execution guides have no file edits in the harness repo.

**How to avoid:** Plans 02-04 must have `autonomous: false`. Their "must-haves" are evidence checklists, not file-modification assertions. The plan executor is the human (CTO) who runs harness commands on the Implentio repo.

### Pitfall 3: Measuring the Wrong CLAUDE.md Scope

**What goes wrong:** Measurement task reports harness section (~146 tokens) as passing the 1K threshold and marks INFRA-01 complete. The full CLAUDE.md is actually ~3,670 tokens.

**Why it happens:** The INFRA-01 requirement says "Harness CLAUDE.md router stays under 1,000 tokens" — "Harness CLAUDE.md" could mean the harness section only OR the full CLAUDE.md file.

**How to avoid:** Plan 05 must measure BOTH the full CLAUDE.md (flag as FAIL) AND the harness section specifically (likely PASS). Include a note that the full file failure is Phase 1 debt (GSD:stack section bloat). VAL-02 says "CLAUDE.md under 1K tokens" — measure the file, not the section.

### Pitfall 4: Agent File Loses Existing Post-Discuss Content

**What goes wrong:** When adding pre-discuss mode to harness-eng-reviewer.md, the edit overwrites or restructures the existing Protocol section, removing the data flow analysis, edge case enumeration, or test matrix sections.

**Why it happens:** Adding a new `## Operating Modes` structure requires reorganizing existing `## Protocol` content.

**How to avoid:** Plan 01 must-haves explicitly check that all four post-discuss outputs still exist: `grep -c "Data Flow\|Edge Case\|Test Matrix\|Verdict" harness-eng-reviewer.md` should return ≥4.

### Pitfall 5: Evidence Artifacts Not Created During Sub-Phases

**What goes wrong:** The validation sub-phases run successfully but role-gate agents produce no reports because they were not triggered (no architectural keywords in phase goal, or gate was bypassed).

**Why it happens:** The validation guides (Plans 02-04) do not explicitly remind the user to run each gate trigger at the correct point.

**How to avoid:** Each validation guide stage should include an explicit checkpoint: "Checkpoint: have you run [gate]? If yes, record artifact path. If no, document why (out-of-scope determination)."

---

## Code Examples

### CLAUDE.md Harness Section After Plan 01

```markdown
<!-- GSD:harness-start -->
## Harness

Unified workflow harness active. Skills: `.claude/skills/harness/`
Config: `.planning/harness.json`

When dispatching subagents, include `.planning/harness.json` in the `<files_to_read>` block.
Before /gsd-plan-phase: verify CONTEXT.md has approaches-with-tradeoffs and user approval.
After /gsd-execute-phase on implementation plans: spawn harness-code-reviewer before /gsd-ship.
At new-project init or scope-change: spawn harness-ceo-reviewer.
Before /gsd-ship: spawn harness-qa-reviewer and harness-security-reviewer.
Before /gsd-discuss-phase on architectural phases (agents, APIs, data models, schemas): spawn harness-eng-reviewer in pre-discuss mode.
After /gsd-discuss-phase: spawn harness-eng-reviewer.
<!-- GSD:harness-end -->
```

Note: 7 trigger lines total, all imperative single-sentence format consistent with existing pattern. Estimated new harness section: ~200 tokens. [ASSUMED — not yet verified post-edit]

### Token Measurement Script (Plan 05)

```python
python3 - << 'EOF'
import os

HARNESS = "/path/to/harness"

def measure(path):
    with open(path) as f:
        content = f.read()
    return len(content), len(content) // 4

targets = {
    "CLAUDE.md (full)": f"{HARNESS}/CLAUDE.md",
    "harness/SKILL.md": f"{HARNESS}/.claude/skills/harness/SKILL.md",
    "tdd/SKILL.md": f"{HARNESS}/.claude/skills/harness/tdd/SKILL.md",
    "rules/tdd-enforcement.md": f"{HARNESS}/.claude/skills/harness/rules/tdd-enforcement.md",
    "rules/code-review.md": f"{HARNESS}/.claude/skills/harness/rules/code-review.md",
    "rules/spec-driven.md": f"{HARNESS}/.claude/skills/harness/rules/spec-driven.md",
    "rules/systematic-debugging.md": f"{HARNESS}/.claude/skills/harness/rules/systematic-debugging.md",
    "rules/verification-rules.md": f"{HARNESS}/.claude/skills/harness/rules/verification-rules.md",
    "harness-eng-reviewer.md": f"{HARNESS}/.claude/agents/harness-eng-reviewer.md",
    "harness-ceo-reviewer.md": f"{HARNESS}/.claude/agents/harness-ceo-reviewer.md",
    "harness-qa-reviewer.md": f"{HARNESS}/.claude/agents/harness-qa-reviewer.md",
    "harness-security-reviewer.md": f"{HARNESS}/.claude/agents/harness-security-reviewer.md",
    "harness-code-reviewer.md": f"{HARNESS}/.claude/agents/harness-code-reviewer.md",
}

print("| File | Chars | ~Tokens (chars/4) |")
print("|------|-------|------------------|")
for label, path in targets.items():
    chars, tokens = measure(path)
    print(f"| {label} | {chars} | ~{tokens} |")
EOF
```

[ASSUMED — no tiktoken available; chars/4 has ~10-20% error margin]

### Pain Point Evidence: TDD Order Verification

```bash
# Verify test committed before implementation in Implentio sub-phase
IMPLENTIO=/path/to/implentio-app
BRANCH=[sub-phase-branch]

git -C $IMPLENTIO log --oneline --name-only --diff-filter=A $BRANCH \
  | awk '
    /^[a-f0-9]/ { commit=$0 }
    /\.(test|spec)\.(ts|tsx)/ { print "TEST_FILE:", $0, "in", commit }
    !/^[a-f0-9]/ && !/\.(test|spec)/ && /\.(ts|tsx)/ { print "IMPL_FILE:", $0, "in", commit }
  '
```

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| python3 | Plan 05 token measurement | Yes | 3.x | wc -c + divide by 4 manually |
| git | Plan 05 evidence collection | Yes | system | — |
| ANTHROPIC_API_KEY | Exact token count via API | No | — | chars/4 approximation (document in MEASUREMENTS.md) |
| Implentio repo (implentio-app) | Plans 02-04 validation | Yes | local at /Users/molchairuangutai/GitHub/implentio-app | — |
| tiktoken (npm or python) | Accurate token counting | No | — | chars/4 approximation |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Adding 2 trigger lines to CLAUDE.md keeps harness section under 200 tokens | Plan 01 / Code Examples | Low — current section is 146 tokens, two short lines add ~30 tokens |
| A2 | chars/4 approximation has 10-20% error margin vs actual Claude tokenizer | Plan 05 / Token Measurement | Medium — CLAUDE.md might be closer to 3,000 or 4,000 actual tokens; direction of FAIL verdict is unchanged |
| A3 | Implentio PDF editor's existing extraction pipeline is in implentio-app/packages/api-v2 | Plans 02-04 | Medium — invoice-ingestion repo exists but is empty; the generated toolbelt client points to a "File Processor API" that may be a separate deployed service; codebase exploration during Sub-Phase A discuss will clarify |
| A4 | The File Processor API (PreviewProcessorResponse, ValidationResult) is the extraction pipeline referenced in D-01 | Plans 02-04 | Medium — this is a generated OpenAPI client, suggesting the pipeline is a separate Python service, not TypeScript; this affects where confidence scoring lives |
| A5 | Post-discuss trigger "After /gsd-discuss-phase: spawn harness-eng-reviewer." should be added as a new line (not replacing the existing spec gate) | Plan 01 | Low — Phase 3 research confirmed the spec gate is a separate, independent instruction |

---

## Open Questions

1. **Where does the extraction pipeline actually live?**
   - What we know: `implentio-app/packages/toolbelt/src/generated/ingestion/` has an auto-generated OpenAPI client for a "File Processor API" with `PreviewProcessorResponse` and `ValidationResult` types. The `invoice-ingestion` repo directory is empty.
   - What's unclear: Is the File Processor a Python service? Is it deployed separately? Where does OCR + AI field extraction happen?
   - Recommendation: Sub-Phase A discuss-phase must begin with codebase exploration (as D-01 specifies). The validation guide should prompt the user to explore the File Processor API source before beginning discuss-phase.

2. **Is the post-discuss trigger for harness-eng-reviewer conditional or unconditional?**
   - What we know: D-06 says the pre-discuss trigger applies to "architectural phases". Post-discuss mode is described as the "existing" mode.
   - What's unclear: Should the post-discuss trigger also only fire on architectural phases, or on all phases?
   - Recommendation: Make post-discuss trigger fire on all phases (unconditional). The agent already has a verdict that can be "Proceed" when nothing interesting is found. Selective triggering adds detection complexity with minimal benefit.

---

## Sources

### Primary (HIGH confidence)

- `.claude/agents/harness-eng-reviewer.md` — verified current file structure and content [VERIFIED]
- `CLAUDE.md` GSD:harness-start section — verified current trigger lines (5 lines, no harness-eng-reviewer spawn) [VERIFIED]
- `.planning/phases/04-real-project-validation/04-CONTEXT.md` — all 6 locked decisions [VERIFIED]
- `.planning/REQUIREMENTS.md` — VAL-01, VAL-02, VAL-03 exact wording [VERIFIED]
- `.planning/ROADMAP.md` — Phase 4 success criteria [VERIFIED]
- `.planning/phases/03-role-based-gates/03-RESEARCH.md` — Phase 3 trigger line history [VERIFIED]
- `.planning/phases/03-role-based-gates/03-UAT.md` — Phase 3 UAT confirms no eng reviewer spawn trigger [VERIFIED]
- `node gsd-tools.cjs init phase-op 04` — init metadata (commit_docs: true, phase_dir, agent paths) [VERIFIED]

### Secondary (MEDIUM confidence)

- `~/.claude/get-shit-done/workflows/discuss-phase.md` — no existing architectural phase detection, confirmed trigger is CLAUDE.md instruction-based [VERIFIED]
- Python chars/4 token estimation — standard heuristic, ~10-20% error vs actual tokenizer [ASSUMED]

### Tertiary (LOW confidence)

- File Processor API identity — generated OpenAPI client found in toolbelt, but source service location unknown [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Plan 01 scope: HIGH — current file states verified, exact gaps identified
- Plans 02-04 structure: HIGH — pattern clear, validation guide template well-defined
- Plan 05 measurement: MEDIUM — measurement commands correct, token estimates approximate
- Implentio codebase specifics: LOW — extraction pipeline source not located (empty invoice-ingestion repo)

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (stable — harness files are static markdown, not fast-moving)
