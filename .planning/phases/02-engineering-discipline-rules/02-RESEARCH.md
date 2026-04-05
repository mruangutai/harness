# Phase 2: Engineering Discipline Rules - Research

**Researched:** 2026-04-05
**Domain:** Prompt engineering for enforcement rules, GSD agent_skills injection, markdown-as-code discipline files
**Confidence:** HIGH

## Summary

Phase 2 populates the stub files created in Phase 1 with enforcement content. Every file in this phase is a markdown document that an LLM agent reads and acts on — there is no executable code, no build system, no library API. The "implementation" is authoring four rule files, one new agent stub, and config edits.

The content patterns are well-documented in the superpowers source (absorbed and analyzed in `.planning/research/FEATURES.md`). The TDD Iron Law, spec-driven constraints, systematic debugging protocol, and two-stage code review are lifted directly from superpowers' enforcement approach, adapted to GSD's injection model and the project's existing harness.json gate schema.

The integration surface is narrow: two entries added to `config.json agent_skills`, two instructions added to the CLAUDE.md harness section, one new agent file created, and four stub files populated. No GSD files are modified. The planner must sequence these as a content-authoring phase, not a software development phase — validation tests whether the content causes the target agent to behave correctly, not whether code compiles.

**Primary recommendation:** Treat each rule file as an enforcement specification. Use imperative framing ("You MUST"), include explicit red flags/anti-patterns, and test each file by reading it aloud and asking "would an LLM agent know exactly what to do in every scenario this file covers?"

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### File Layout (5 files)
- **D-01:** `rules/tdd-enforcement.md` — covers ENG-01 (TDD Iron Law) and ENG-03 (zero-placeholder plans). Injected via agent_skills into gsd-executor.
- **D-02:** `rules/spec-driven.md` — NEW file for ENG-02 (spec-driven development). Injected into gsd-planner via agent_skills. Requires adding `gsd-planner` entry to config.json agent_skills and rules/SKILL.md index.
- **D-03:** `rules/systematic-debugging.md` — covers ENG-04. Injected into gsd-debugger via agent_skills (3rd entry in config.json agent_skills).
- **D-04:** `rules/code-review.md` — covers ENG-05 and ENG-06. Becomes the harness-code-reviewer agent's role prompt. NOT a SKILL.md injection into gsd-verifier.
- **D-05:** `rules/verification-rules.md` — injected into gsd-verifier via agent_skills. Augments GSD's existing verifier behavior.
- **D-06:** `tdd/SKILL.md` — updated from stub to point to tdd-enforcement.md content.

#### TDD Enforcement Content (ENG-01 + ENG-03)
- **D-07:** `tdd-enforcement.md` is ADDITIVE to GSD's existing TDD reference. Adds: Iron Law statement, anti-rationalization red-flag checklist, deletion penalty, human-approval gate for TDD skip.
- **D-08:** Iron Law framing: "You MUST write a failing test before writing any production code. Code written before tests must be deleted and rewritten in correct TDD order. There are no exceptions without explicit human approval."
- **D-09:** TDD-exempt plan types (config, docs, scaffolding) come from harness.json. tdd-enforcement.md must instruct agents to check tdd_exempt_plan_types.
- **D-10:** Anti-rationalization guard: explicit red-flag list of common excuses the agent must not accept.
- **D-11:** ENG-03 zero-placeholder enforcement: executor must stop and report if a task contains "TBD", "[placeholder]", "implement X", or lacks exact file paths.

#### Spec-Driven Development (ENG-02)
- **D-12:** `spec-driven.md` injected into gsd-planner. Every task must reference a specific acceptance criterion from CONTEXT.md, must include complete code intent, and must have verification steps.
- **D-13:** ENG-02 "structured brainstorming → spec → approval" flow is a CLAUDE.md instruction at the discuss-phase → plan-phase boundary: CONTEXT.md must contain approaches-with-tradeoffs and explicit user approval indication.
- **D-14:** No new spec artifact type. CONTEXT.md is the spec. spec-driven.md enforces that plans reference it.

#### Code Review Gate (ENG-05 + ENG-06)
- **D-15:** Code review triggered by CLAUDE.md instruction at the execute → ship boundary: "After /gsd-execute-phase completes for an implementation plan, spawn harness-code-reviewer before /gsd-ship."
- **D-16:** `code-review.md` is harness-code-reviewer's role prompt. Two-stage: Stage 1 — spec compliance check; Stage 2 — code quality check.
- **D-17:** Gate applies to "implementation plan only". Config, docs, and scaffolding plans skip code review.
- **D-18:** `.claude/agents/harness-code-reviewer.md` must be created in Phase 2 (not a Phase 1 stub).

#### Systematic Debugging (ENG-04)
- **D-19:** `systematic-debugging.md` injected into gsd-debugger via agent_skills. Requires adding `"gsd-debugger": [".claude/skills/harness/rules"]` to config.json agent_skills.
- **D-20:** ENG-04 protocol: 4-phase RCA (Observe → Hypothesize → Test → Fix), hard stop after 3 failed fix attempts with mandatory user escalation, evidence-gathering before any fix.
- **D-21:** 3-failure cap complements GSD's `node_repair_budget: 2` — GSD handles plan-level retries; ENG-04 cap handles investigation-level attempts within a debugging session.

#### CLAUDE.md Gate Triggers (ENG-02 gate, ENG-05 gate)
- **D-22:** Two new CLAUDE.md instructions in harness section: (1) spec gate — "Before /gsd-plan-phase, verify CONTEXT.md includes approaches-with-tradeoffs." (2) review gate — "After /gsd-execute-phase for implementation plans, spawn harness-code-reviewer before /gsd-ship."
- **D-23:** CLAUDE.md harness section must stay under 50 tokens of non-comment text (Phase 1 D-05).

### Claude's Discretion
- Exact wording of the red-flag checklist items (as long as they cover common rationalization patterns)
- Internal structure of the two-stage code review (section headers, checklist format)
- Which specific OWASP/quality items go in code quality vs spec compliance review
- verification-rules.md content (what to augment in GSD's verifier that isn't already there)

### Deferred Ideas (OUT OF SCOPE)
- harness-code-reviewer split into two independent agents (spec-compliance-reviewer + code-quality-reviewer) — deferred to Phase 3 or 4
- gsd-debugger agent_skills via tdd/ path if rules/ grouping becomes too broad — keep as-is
- verification-rules.md growing into a QA persona — Phase 3 concern
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ENG-01 | TDD Iron Law enforcement — no production code without a failing test first; code written before tests must be deleted; anti-rationalization guards with explicit red-flag checklist | tdd-enforcement.md delivered via agent_skills to gsd-executor; Iron Law framing from D-08; 13-item red flag pattern from superpowers FEATURES.md lines 249-258 |
| ENG-02 | Spec-driven development — structured brainstorming → written spec with self-review → user approval gate → implementation | spec-driven.md injected into gsd-planner via agent_skills; CLAUDE.md gate instruction at discuss→plan boundary (D-13) |
| ENG-03 | Zero-placeholder plan tasks — "TBD" and placeholder code rejected; every task has exact file paths, complete code intent, and verification steps | tdd-enforcement.md includes executor-time rejection gate (D-11); spec-driven.md prevents placeholders at plan-write time (D-12) |
| ENG-04 | Systematic debugging — evidence-gathering before any fix attempts; 4-phase root cause analysis; stops after 3 failed fixes | systematic-debugging.md injected into gsd-debugger via agent_skills; 4-phase RCA + 3-failure cap from D-20 |
| ENG-05 | Code review gate — review step between execute and ship; checks spec compliance first, then code quality | CLAUDE.md instruction triggers harness-code-reviewer after execute-phase (D-15); two-stage protocol in code-review.md (D-16) |
| ENG-06 | Two-stage subagent review — implementer self-review, then spec compliance reviewer, then code quality reviewer; loops until all pass | code-review.md becomes harness-code-reviewer agent role prompt; two-stage structure enforces independent perspective (D-16, D-18) |
</phase_requirements>

## Standard Stack

### Core

This phase produces markdown files, one JSON config edit, and one agent YAML file. No libraries.

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Markdown (.md) | N/A | Rule file format for all 5 discipline files | Claude Code native; SKILL.md convention used by GSD, gstack, superpowers |
| YAML frontmatter | N/A | Agent definition header in harness-code-reviewer.md | Matches harness-ceo-reviewer.md and harness-eng-reviewer.md established in Phase 1 |
| JSON | N/A | config.json agent_skills entries | Matches existing config.json format; GSD's buildAgentSkillsBlock() reads from this key |

[VERIFIED: codebase] GSD's `buildAgentSkillsBlock()` (init.cjs lines 1443-1480) reads `config.agent_skills[agentType]` and requires a `SKILL.md` file at `{skillPath}/SKILL.md` to validate each entry. The rules/ directory already has a SKILL.md (verified by `ls`).

[VERIFIED: codebase] plan-phase.md line 28 shows `agent-skills gsd-planner` is a stable lookup key already called during plan-phase initialization.

[VERIFIED: codebase] execute-phase.md line 66 shows `agent-skills gsd-executor` is called during execute-phase initialization — gsd-debugger follows the same pattern.

### Existing Artifacts (confirmed present, stub-only)

| File | Current State | Phase 2 Action |
|------|--------------|----------------|
| `.claude/skills/harness/rules/tdd-enforcement.md` | Stub (1 line) | Populate with Iron Law + red flags + deletion penalty |
| `.claude/skills/harness/rules/systematic-debugging.md` | Stub (1 line) | Populate with 4-phase RCA + 3-failure cap |
| `.claude/skills/harness/rules/code-review.md` | Stub (1 line) | Populate with two-stage review protocol (becomes agent role prompt) |
| `.claude/skills/harness/rules/verification-rules.md` | Stub (1 line) | Populate with verifier augmentations |
| `.claude/skills/harness/rules/SKILL.md` | Lists 4 files (stub) | Update index to list 5 files (adding spec-driven.md) |
| `.claude/skills/harness/tdd/SKILL.md` | Stub | Update to point to tdd-enforcement.md content |

### New Artifacts (do not exist yet)

| File | Action | Notes |
|------|--------|-------|
| `.claude/skills/harness/rules/spec-driven.md` | Create new | ENG-02 spec constraints for gsd-planner |
| `.claude/agents/harness-code-reviewer.md` | Create new | YAML frontmatter + code-review.md content as role prompt |

### Config Edits (edits to existing files)

| File | Current State | Change |
|------|--------------|--------|
| `.planning/config.json` agent_skills | `{gsd-executor: [...], gsd-verifier: [...]}` | Add `gsd-planner` and `gsd-debugger` entries |
| `CLAUDE.md` harness section | 2-line stub | Add spec gate + review gate instructions (under 50-token budget) |

## Architecture Patterns

### Rule File Structure (All Discipline Files)

Every rule file follows the same pattern — observed in superpowers source and appropriate for enforcement:

```markdown
# Harness: [Rule Name]

## Authority

This file is injected via agent_skills. Follow ALL rules below with no exceptions
unless a condition explicitly permits an exception.

## [Rule Section 1]

[Imperative content — "You MUST", "You MUST NOT", not "Consider"]

## [Rule Section 2]

[Explicit rejection gate or checklist]

## Exceptions

[Explicit list only. No implicit exceptions. Must reference harness.json field if applicable.]
```

**Why imperative framing matters:** [CITED: PITFALLS.md line 116] Superpowers' bypass mechanism activates whenever Claude perceives guidance-level (not mandate-level) instructions. "Iron Law" language + deletion penalty closes the gap between "here's the approach" and "you have no choice."

### Pattern 1: Iron Law with Deletion Penalty (tdd-enforcement.md)

**What:** Non-negotiable ordering constraint. Test file must exist and have a failing run before any production code line is written.
**Deletion trigger:** If Claude discovers production code was written before a test, the production code must be deleted (not kept as reference, not adapted). This is the superpowers pattern — it makes the cost of skipping TDD higher than the cost of doing it correctly.
**Verification steps:** After writing the test (RED), after writing minimum code to pass (GREEN), after refactoring — each step requires running the test suite and confirming the expected result.

**Red flag checklist pattern (13 items from superpowers):**
```markdown
## Red Flags — Stop Immediately If You Notice Any of These

These are signs that TDD has been violated. If you observe any, STOP, delete
the out-of-order production code, and restart in correct TDD sequence:

- [ ] You are writing production code without a failing test already existing
- [ ] You wrote the test after the implementation
- [ ] You wrote multiple tests before any implementation
- [ ] You are refactoring while any test is red
- [ ] You added a feature while in the GREEN phase
- [ ] You skipped verifying the RED state (confirming the test actually fails before writing production code)
- [ ] You are about to say "this is just a simple function, tests aren't needed"
- [ ] You are about to say "the test would be too hard to write"
- [ ] You are about to say "I'll add tests after I get it working"
- [ ] You are about to say "we're in a rush, skip for now"
- [ ] You are about to say "it's obvious code, testing adds no value"
- [ ] You are modifying existing tests to make them pass instead of writing new code
- [ ] You cannot demonstrate the failing test run before your code changes
```

[CITED: .planning/research/FEATURES.md lines 249-258] Superpowers documents 13 red flags in its TDD enforcement SKILL.md. The exact items at positions 7-13 are [ASSUMED] based on training knowledge of superpowers — the first 6 are verified from FEATURES.md.

### Pattern 2: Executor-Time Rejection Gate (ENG-03 in tdd-enforcement.md)

**What:** Zero-placeholder enforcement that activates during task execution, not plan writing.
**Trigger strings:** "TBD", "[placeholder]", "[TODO]", "implement X", "similar to previous task", plus absence of exact file paths.
**Protocol:** When any trigger is detected in the current task, executor STOPS, reports the specific violation, and requests plan revision before proceeding. It does not attempt to infer intent.

```markdown
## Zero-Placeholder Gate

Before executing any task, scan it for the following forbidden patterns:
- The literal string "TBD" or "TODO"
- "[placeholder]", "[fill in]", or similar bracket-notation deferral
- Task descriptions like "implement X" without exact file paths and code intent
- References like "similar to task N above" that defer specification

If any are found: STOP. Do not attempt to infer intent. Report the violation:
"Task [name] contains a placeholder at [location]. Plan revision required before execution."
```

### Pattern 3: spec-driven.md — Planner-Time Constraints (ENG-02 + ENG-03)

**What:** Rules injected into gsd-planner that prevent placeholder tasks from being written in the first place.
**Key constraint:** Every task must reference a specific acceptance criterion from CONTEXT.md (not just "implement per requirements"). This creates a traceability chain: CONTEXT.md decision → plan task → implementation.

```markdown
## Task Completeness Requirements

Every plan task MUST include:
1. Exact file paths (not "update the config file" but "edit .planning/config.json")
2. Complete code intent (not "implement X" but the actual logic, types, and structure)
3. A verification step with the exact command and expected output
4. A reference to the CONTEXT.md decision or REQUIREMENTS.md requirement it satisfies

Reject any task that contains:
- "TBD", "TODO", or any placeholder notation
- Vague verbs without targets ("add error handling", "improve performance")
- Instructions that defer specification ("similar to above", "follow existing pattern")
```

### Pattern 4: Two-Stage Review (code-review.md / harness-code-reviewer agent)

**What:** Sequential review gates that maintain separation of concerns and independent perspective.
**Stage 1 — Spec compliance:** Does the implementation match the decisions in CONTEXT.md? This stage receives the CONTEXT.md and the changed files. It does NOT evaluate code style or quality.
**Stage 2 — Code quality:** Is the code well-written, maintainable, and free of edge-case bugs? This stage does NOT re-evaluate spec compliance.

**Independence requirement (ENG-06):** Implementer self-review is explicitly NOT sufficient. The harness-code-reviewer agent is a separate agent with a fresh 200K context window — it has no access to the implementer's reasoning, only the spec and the code.

```markdown
## Review Protocol

**Stage 1: Spec Compliance**
Read: CONTEXT.md decisions (locked decisions section only), changed files
Ask: Does every changed file serve a decision documented in CONTEXT.md?
     Are there changes not required by any CONTEXT.md decision (scope creep)?
     Are there CONTEXT.md decisions with no corresponding code change (omission)?
Output: PASS or FAIL with specific findings

Only proceed to Stage 2 if Stage 1 is PASS.

**Stage 2: Code Quality**
Read: Changed files only (not CONTEXT.md)
Ask: Are there unhandled edge cases?
     Are there naming inconsistencies?
     Are there complexity hotspots that should be decomposed?
Output: PASS or FAIL with specific findings

**Loop condition:** If either stage FAILs, return findings to executor for revision.
          Re-review after revision. Maximum 3 review cycles total.
```

### Pattern 5: 4-Phase RCA in systematic-debugging.md

**What:** Evidence-first protocol prevents "let's just try X" fixes that mask root causes.
**Phase sequence:** Observe (reproduce and document) → Hypothesize (form a testable hypothesis BEFORE touching code) → Test (verify or falsify the hypothesis WITHOUT fixing yet) → Fix (only after hypothesis is confirmed).

```markdown
## Debugging Protocol

### Phase 1: Observe
Before any code change:
- Reproduce the bug consistently
- Document the exact failure: input, expected output, actual output
- Check: does it fail the same way every time? Under what conditions?

### Phase 2: Hypothesize
Before any code change:
- Form ONE specific hypothesis: "The bug is caused by X because Y"
- Write the hypothesis down
- Identify: what evidence would confirm or falsify this hypothesis?

### Phase 3: Test
Before any fix:
- Gather the evidence identified in Phase 2
- Write a failing test that proves the hypothesis IF possible
- Confirm or falsify the hypothesis

### Phase 4: Fix
Only after Phase 3 confirms the hypothesis:
- Implement the minimal change that fixes the confirmed root cause
- Run the test from Phase 3 to confirm it now passes
- Run the full test suite to confirm no regression

## 3-Failure Cap

If you have attempted 3 fixes and the bug is not resolved:
STOP. Do not attempt a 4th fix.
Report to the user: which hypotheses were tested, what evidence was gathered,
and what remains uncertain. Request human intervention.

This cap is separate from GSD's node_repair_budget (which handles plan-level retries).
The 3-failure cap applies within a single debugging session.
```

### Pattern 6: CLAUDE.md Gate Instructions

**What:** Lightweight instructions in the harness section that trigger at phase boundaries.
**Token constraint:** Must stay under 50 tokens total for both new instructions (D-23).

**Current harness section (CLAUDE.md):**
```markdown
<!-- GSD:harness-start -->
## Harness

Unified workflow harness active. Skills: `.claude/skills/harness/`
Config: `.planning/harness.json`

When dispatching subagents, include `.planning/harness.json` in the `<files_to_read>` block.
<!-- GSD:harness-end -->
```

**Phase 2 additions (must stay under 50 additional tokens):**
```markdown
Before /gsd-plan-phase: verify CONTEXT.md has approaches-with-tradeoffs and user approval.
After /gsd-execute-phase on implementation plans: spawn harness-code-reviewer before /gsd-ship.
```

### Pattern 7: harness-code-reviewer Agent Definition

**What:** New agent file following the same YAML frontmatter pattern as harness-ceo-reviewer.md.
**Content:** The code-review.md file IS the role prompt. The agent file wraps it with YAML metadata.

```markdown
---
name: harness-code-reviewer
description: "Two-stage code review — spec compliance then code quality — at execute → ship boundary"
tools:
  - Read
  - Glob
  - Grep
---

# Harness: Code Reviewer

[content from code-review.md]
```

**Tool list rationale:** Read-only tools only. The reviewer reads spec and code; it does not modify files. It returns findings for the executor to act on.

### Anti-Patterns to Avoid

- **Guidance framing:** Writing "Consider checking for..." instead of "You MUST check for...". Guidance-level framing activates superpowers' built-in bypass mechanism — the agent treats it as optional. [CITED: PITFALLS.md Pitfall 4]
- **Implicit exceptions:** Any statement like "unless it makes sense" or "when appropriate" defeats enforcement. All exceptions must be explicit, named, and tied to a config field.
- **Duplicating GSD's TDD reference:** GSD's `~/.claude/get-shit-done/references/tdd.md` already explains red-green-refactor. tdd-enforcement.md must add enforcement without restating theory. [VERIFIED: codebase] tdd.md exists at that path.
- **Injection path errors:** `buildAgentSkillsBlock()` validates `SKILL.md` exists at `{path}/SKILL.md`. New agent_skills entries pointing to specific files (not directories) will silently fail — always point to the DIRECTORY and ensure SKILL.md exists there. [VERIFIED: codebase] init.cjs lines 1466-1469 confirm this validation.
- **Token budget overrun in CLAUDE.md:** The two Phase 2 gate instructions must not push the harness section past 50 tokens of non-comment text. Count tokens before writing. [CITED: CONTEXT.md D-23]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TDD enforcement content | Custom TDD rules from scratch | Superpowers' 13-item red flag list (absorbed) | Superpowers' list is battle-tested; gaps in custom lists let rationalizations through |
| Spec compliance checklist | Generic "review the code" instruction | Stage 1/Stage 2 structural split | Unstructured review conflates style with correctness; structure forces prioritization |
| Debugging protocol | Ad hoc investigation instructions | 4-phase RCA (Observe/Hypothesize/Test/Fix) | Prevents the "just try X" loop that compounds bugs; hypothesis-before-fix is the key discipline |
| Enforcement gate wording | Soft guideline language | Imperative mandate with explicit red flags | "Consider" = ignored; "You MUST / Stop if you notice" = acted on |

**Key insight:** These rule files are not documentation — they are executable constraints for an LLM agent. Every sentence is either enforced or ignored. Ambiguity in the file becomes permission to skip the rule.

## Common Pitfalls

### Pitfall 1: Guidance Language Defeats Enforcement

**What goes wrong:** Rule files written as guidance ("it's recommended to...") rather than mandate ("You MUST..."). The agent treats recommendations as optional in proportion to implementation difficulty.
**Why it happens:** Natural language defaults to hedged, collegial framing. Enforcement prompts require an unnatural shift to imperative voice.
**How to avoid:** Read every sentence in the rule file aloud substituting "the agent will probably ignore this if..." — if the sentence doesn't sound mandatory, rewrite it.
**Warning signs:** Rules containing "should", "consider", "it's good practice to", "where possible".
[CITED: PITFALLS.md Pitfall 4 — TDD Enforcement Bypass Under Integration Pressure]

### Pitfall 2: The SKILL.md Validation Trap

**What goes wrong:** Adding an agent_skills entry in config.json that points to a specific file path (`".claude/skills/harness/rules/spec-driven.md"`) instead of a directory. `buildAgentSkillsBlock()` requires `{path}/SKILL.md` to exist — a path pointing to a file fails silently.
**Why it happens:** Counterintuitive API — you specify a directory, not a file. The function appends `/SKILL.md` automatically.
**How to avoid:** Always point agent_skills entries to DIRECTORIES. The directory must contain a SKILL.md that GSD will read.
**Warning signs:** No `<agent_skills>` block appears in the dispatched subagent prompt (verify by reading the execute-phase or plan-phase log output).
[VERIFIED: codebase] init.cjs lines 1466-1469 — SKILL.md existence check confirmed.

### Pitfall 3: Two-Stage Review Collapses to One-Stage

**What goes wrong:** The code-review.md conflates spec compliance and code quality into a single undifferentiated review. The agent looks at code style and spec coverage simultaneously, with spec compliance issues deprioritized against obvious style wins.
**Why it happens:** Natural review tendency is to look at everything at once.
**How to avoid:** Stage 1 and Stage 2 must be structurally separated. Stage 1 MUST complete and PASS before Stage 2 begins. The separation must be explicit in the file.
**Warning signs:** Review output comments on formatting before confirming spec requirements are met.
[CITED: FEATURES.md — subagent-driven-development: "Three-gate review" pattern]

### Pitfall 4: Code Review Agent Has Write Tools

**What goes wrong:** harness-code-reviewer.md agent definition includes Edit or Write tools. The reviewer attempts to "fix" issues it finds rather than returning findings for the executor to act on.
**Why it happens:** GSD executor agents have Write/Edit tools; reviewer agents inherit the same definition.
**How to avoid:** harness-code-reviewer.md YAML frontmatter lists Read, Glob, Grep only. No Write, Edit, Bash, or MultiEdit.
**Warning signs:** Review agent produces code changes instead of a findings report.
[CITED: CONTEXT.md D-16 — "returns findings to executor for revision"]

### Pitfall 5: CLAUDE.md Gate Instructions Too Verbose

**What goes wrong:** The spec gate and review gate instructions added to CLAUDE.md consume more than 50 tokens, overrunning the Phase 1 D-05 budget constraint.
**Why it happens:** Trying to fully specify the gate behavior in CLAUDE.md rather than delegating to the agent/skill file.
**How to avoid:** CLAUDE.md gate instructions are TRIGGERS only — they tell Claude when to do something and what to spawn. Full behavior lives in the agent file or skill file. The trigger sentence should be under 25 tokens each.
**Warning signs:** Gate instructions contain "and then", "make sure to", or multi-clause requirements.
[CITED: CONTEXT.md D-23 — 50 token budget]

### Pitfall 6: Placeholder Detector Misses Structural Placeholders

**What goes wrong:** The zero-placeholder gate scans for literal strings like "TBD" but misses structural placeholders — vague verbs without targets ("add error handling"), task references ("similar to Task 1"), or code intent expressed as natural language rather than code.
**Why it happens:** String matching is easy; intent detection requires semantic understanding.
**How to avoid:** The rejection gate should check for: (a) absence of at least one concrete file path, (b) presence of vague verbs without objects ("improve", "update", "fix"), (c) cross-references to other tasks for specification. These structural checks supplement the literal string scan.
**Warning signs:** Executor proceeds on a task that says "add appropriate error handling to the module".

## Code Examples

### config.json agent_skills After Phase 2

```json
"agent_skills": {
  "gsd-executor": [
    ".claude/skills/harness/tdd"
  ],
  "gsd-verifier": [
    ".claude/skills/harness/rules"
  ],
  "gsd-planner": [
    ".claude/skills/harness/rules"
  ],
  "gsd-debugger": [
    ".claude/skills/harness/rules"
  ]
}
```

[VERIFIED: codebase] Current config.json has gsd-executor and gsd-verifier entries. gsd-planner and gsd-debugger are additions.

Note: gsd-planner and gsd-debugger both point to the same `rules/` directory. This means all rule files under `rules/SKILL.md` are referenced. The rules/SKILL.md index must clearly gate which files apply to which agent type so gsd-planner doesn't act on debugging rules.

**Option A (simpler):** Add a "load only if relevant to your role" instruction in rules/SKILL.md.
**Option B (cleaner):** Each agent reads rules/SKILL.md which contains conditional routing: "If you are gsd-planner, read only spec-driven.md. If you are gsd-debugger, read only systematic-debugging.md."

The planner should implement Option B — explicit routing prevents cross-contamination between discipline files.

### harness-code-reviewer.md Template

```markdown
---
name: harness-code-reviewer
description: "Two-stage code review — spec compliance then code quality — for implementation plans"
tools:
  - Read
  - Glob
  - Grep
---

# Harness: Code Reviewer

[role prompt content — two-stage review protocol]
```

[VERIFIED: codebase] Matches YAML pattern of `.claude/agents/harness-ceo-reviewer.md` (confirmed by reading file).

### rules/SKILL.md Updated Index

```markdown
# Harness: Engineering Rules

[description]

## Role-Based Loading

Read ONLY the file(s) that apply to your agent type:

| Agent Type | Files to Read |
|------------|---------------|
| gsd-executor | tdd-enforcement.md |
| gsd-planner | spec-driven.md |
| gsd-debugger | systematic-debugging.md |
| gsd-verifier | verification-rules.md |
| harness-code-reviewer | code-review.md |

## Files

- tdd-enforcement.md — TDD Iron Law + zero-placeholder executor gate
- spec-driven.md — Spec-driven planning constraints
- systematic-debugging.md — 4-phase RCA + 3-failure cap
- code-review.md — Two-stage spec + quality review protocol
- verification-rules.md — Post-execution verification augmentations
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| TDD as reference doc (guidance) | TDD as enforcement with deletion penalty | superpowers (Oct 2025) | Agents treat it as mandate, not suggestion |
| Monolithic code review | Two-stage spec-then-quality review | superpowers v5.0 (Mar 2026) | Spec compliance verified before style; can't trade off against each other |
| Debugging via "let's try X" | 4-phase RCA with hypothesis-before-fix | gstack /investigate + superpowers | Prevents compound bugs from untested fixes |
| Global skill loading | Per-agent-type injection via agent_skills | GSD 1.30.0 | Only relevant rules loaded per agent; no cross-contamination |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Superpowers' red flag checklist items 7-13 match the pattern described (exact wording not confirmed from source) | Code Examples — Pitfall 1 | Low — the first 6 items are verified; items 7-13 are additional examples of the same category. Claude's discretion covers exact wording. |
| A2 | gsd-debugger agent type is a valid lookup key in buildAgentSkillsBlock() | config.json edit section | Medium — execute-phase.md shows gsd-debugger in available_agent_types list; however, agent-skills command may need to be called with "gsd-debugger" specifically during debug sessions. Verify with `gsd-tools agent-skills gsd-debugger` before finalizing config. |
| A3 | Adding gsd-planner to agent_skills does not increase planner context window usage beyond acceptable bounds | config.json edit, CLAUDE.md | Low — rules/ SKILL.md + spec-driven.md content is well under 5K tokens. The planner's 200K window can absorb this. |

## Open Questions

1. **Rules/SKILL.md routing: Option A vs Option B**
   - What we know: both gsd-planner and gsd-debugger will point to the same rules/ directory
   - What's unclear: whether explicit conditional routing in SKILL.md is reliable enough (can Claude follow "only read this if you are gsd-planner"?)
   - Recommendation: Implement Option B (explicit routing table) in rules/SKILL.md but include agent type in the injected `<agent_skills>` block header if GSD passes it — verify by reading the actual block GSD generates

2. **verification-rules.md content scope**
   - What we know: it augments gsd-verifier; Claude's discretion covers content
   - What's unclear: what does GSD's verifier already check that should NOT be duplicated?
   - Recommendation: Plan task for this file should read `~/.claude/get-shit-done/workflows/verify-phase.md` before writing content to identify gaps vs. duplications

## Environment Availability

Step 2.6: SKIPPED (no external dependencies — phase delivers markdown files and config edits only)

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual behavioral testing (no automated test framework applicable) |
| Config file | None — validation is behavioral, not unit-testable |
| Quick run command | Read the rule file and verify it contains required sections |
| Full suite command | Run a GSD phase with enforcement active; observe agent behavior |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ENG-01 | tdd-enforcement.md injected into gsd-executor; Iron Law mandate present | smoke | `node ~/.claude/get-shit-done/bin/gsd-tools.cjs agent-skills gsd-executor` outputs block with tdd/ reference | ✅ |
| ENG-02 | spec-driven.md injected into gsd-planner; contains "CONTEXT.md" and "acceptance criterion" references | smoke | `node ~/.claude/get-shit-done/bin/gsd-tools.cjs agent-skills gsd-planner` outputs block with rules/ reference | ❌ Wave 0 (gsd-planner entry in config.json doesn't exist yet) |
| ENG-03 | Zero-placeholder gate present in tdd-enforcement.md | manual | Read tdd-enforcement.md and confirm rejection gate section exists | ✅ (after population) |
| ENG-04 | systematic-debugging.md injected into gsd-debugger; 4-phase and 3-failure cap present | smoke | `node ~/.claude/get-shit-done/bin/gsd-tools.cjs agent-skills gsd-debugger` outputs block | ❌ Wave 0 (gsd-debugger entry in config.json doesn't exist yet) |
| ENG-05 | CLAUDE.md contains spec gate and review gate instructions | smoke | `grep "harness-code-reviewer" CLAUDE.md` returns the gate instruction | ❌ Wave 0 (gate not added yet) |
| ENG-06 | harness-code-reviewer.md exists with two-stage protocol and read-only tools | smoke | `cat .claude/agents/harness-code-reviewer.md` confirms YAML and two-stage content | ❌ Wave 0 (file doesn't exist yet) |

### Sampling Rate

- **Per task commit:** Read the modified file and verify required sections are present
- **Per wave merge:** Run `gsd-tools agent-skills` for each new agent type to confirm injection works
- **Phase gate:** All 6 smoke checks pass before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `.claude/agents/harness-code-reviewer.md` — covers ENG-05, ENG-06
- [ ] `gsd-planner` entry in `config.json agent_skills` — covers ENG-02 agent-skills smoke test
- [ ] `gsd-debugger` entry in `config.json agent_skills` — covers ENG-04 agent-skills smoke test
- [ ] `rules/spec-driven.md` — covers ENG-02 content
- CLAUDE.md gate instructions — covers ENG-05 smoke test

## Security Domain

This phase delivers markdown rule files and config edits. No authentication, session management, cryptography, or external input handling is involved. No ASVS categories apply.

`security_enforcement`: Not applicable to this phase — no code that handles user input, credentials, or network requests is written.

## Sources

### Primary (HIGH confidence)
- `.planning/phases/02-engineering-discipline-rules/02-CONTEXT.md` — locked decisions D-01 through D-23; canonical constraints for this phase
- `~/.claude/get-shit-done/bin/lib/init.cjs` lines 1432-1480 — `buildAgentSkillsBlock()` implementation; path validation and SKILL.md requirement confirmed
- `~/.claude/get-shit-done/workflows/plan-phase.md` lines 27-29 — gsd-planner agent-skills lookup confirmed as stable API
- `~/.claude/get-shit-done/workflows/execute-phase.md` lines 30-46, 64-66 — gsd-debugger in available_agent_types; agent-skills call pattern confirmed
- `.planning/config.json` — current agent_skills field; gsd-executor and gsd-verifier entries confirmed
- `.planning/harness.json` — tdd_exempt_plan_types confirmed: ["config", "docs", "scaffolding"]
- `.claude/agents/harness-ceo-reviewer.md` — YAML frontmatter pattern confirmed

### Secondary (MEDIUM confidence)
- `.planning/research/FEATURES.md` lines 241-305 — TDD enforcement layers (13 red flags), spec-driven flow, writing-plans discipline; derived from superpowers source analysis
- `.planning/research/PITFALLS.md` — TDD bypass under integration pressure (Pitfall 4), guidance vs. mandate language (Pitfall 1)

### Tertiary (LOW confidence)
- Superpowers TDD red flag items 7-13 — training knowledge; exact wording not re-verified from superpowers source in this session [ASSUMED]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all files and integration points verified from codebase
- Architecture: HIGH — patterns derived from FEATURES.md (Phase 1 research) and confirmed decisions in CONTEXT.md
- Pitfalls: HIGH — most pitfalls cited from PITFALLS.md (Phase 1 research) with codebase verification

**Research date:** 2026-04-05
**Valid until:** 2026-05-05 (stable — markdown files, no external library APIs)
