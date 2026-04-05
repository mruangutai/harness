# Phase 2: Engineering Discipline Rules - Context

**Gathered:** 2026-04-05 (assumptions mode + user corrections)
**Status:** Ready for planning

<domain>
## Phase Boundary

Populate the harness rule stub files with actual enforcement content — TDD Iron Law, spec-driven development constraints, systematic debugging protocol, and code review gate. Phase 2 delivers the discipline layer that makes Claude follow engineering rigor during implementation, not just guidance. Role-based perspectives (Phase 3) and end-to-end validation (Phase 4) are separate phases.

</domain>

<decisions>
## Implementation Decisions

### File Layout (5 files)

The existing 4-file stub layout gains one additional file:

- **D-01:** `rules/tdd-enforcement.md` — covers ENG-01 (TDD Iron Law) and ENG-03 (zero-placeholder plans). Both are executor-time constraints enforced by the same agent (gsd-executor). Injected via agent_skills.
- **D-02:** `rules/spec-driven.md` — NEW file for ENG-02 (spec-driven development). Injected into gsd-planner via agent_skills. Spec constraints apply at plan-writing time, not execution time. Requires adding `gsd-planner` entry to config.json agent_skills and rules/SKILL.md index.
- **D-03:** `rules/systematic-debugging.md` — covers ENG-04. Injected into gsd-debugger via agent_skills (3rd entry in config.json agent_skills). Debugging protocol activates only in dedicated debugging sessions, not during normal implementation.
- **D-04:** `rules/code-review.md` — covers ENG-05 and ENG-06. Delivered as harness-code-reviewer agent instructions, NOT as a SKILL.md injection into gsd-verifier. code-review.md becomes the agent's role prompt (two-stage review requiring independent perspective).
- **D-05:** `rules/verification-rules.md` — injected into gsd-verifier via agent_skills. Contains post-execution verification constraints augmenting GSD's existing verifier behavior.
- **D-06:** `tdd/SKILL.md` — the TDD subdirectory index. Updated from stub to point to tdd-enforcement.md content (the tdd/ directory is the agent_skills injection path for gsd-executor, per Phase 1 D-02).

GSD update risk for gsd-planner injection: LOW. agent_skills config is project-local (.planning/config.json); GSD updates don't touch project files. Lookup key `gsd-planner` is stable API in plan-phase.md line 28. If it changes, injection silently stops — detectable via `gsd-tools agent-skills gsd-planner`.

### TDD Enforcement Content (ENG-01 + ENG-03)

- **D-07:** `tdd-enforcement.md` is ADDITIVE to GSD's existing `~/.claude/get-shit-done/references/tdd.md`. It adds what GSD lacks: Iron Law statement (imperative mandate, not guidance), anti-rationalization red-flag checklist, deletion penalty for code written before tests, and human-approval gate for any TDD skip. Does NOT duplicate the red-green-refactor cycle explanation that GSD already provides.
- **D-08:** Iron Law framing: "You MUST write a failing test before writing any production code. Code written before tests must be deleted and rewritten in correct TDD order. There are no exceptions without explicit human approval."
- **D-09:** TDD-exempt plan types (from harness.json) are: config, docs, scaffolding. The enforcement file must check tdd_exempt_plan_types from harness.json before applying the Iron Law — agents read harness.json via `<files_to_read>` per Phase 1 D-08.
- **D-10:** Anti-rationalization guard: explicit red-flag list of common excuses the agent must not accept (e.g., "it's just a simple function", "the test would be too hard to write", "I'll add tests after"). Any of these triggers a mandatory stop.
- **D-11:** ENG-03 (zero-placeholder plan tasks) is enforced here at execution time as a rejection gate: if a task contains "TBD", "[placeholder]", "implement X", or lacks exact file paths, the executor must stop and report the gap before proceeding.

### Spec-Driven Development (ENG-02)

- **D-12:** `spec-driven.md` is injected into gsd-planner. It constrains what plans are allowed to contain: every task must reference a specific acceptance criterion from CONTEXT.md, must include complete code intent (not "implement X"), and must have verification steps. "TBD" at plan-writing time is rejected at source.
- **D-13:** ENG-02 "structured brainstorming → spec → approval" flow is delivered as a CLAUDE.md instruction at the discuss-phase → plan-phase boundary: CONTEXT.md must contain approaches-with-tradeoffs and explicit user approval indication before plan-phase begins. This is a gate, not a file.
- **D-14:** No new spec artifact type. CONTEXT.md is the spec — the discuss-phase already captures approaches, tradeoffs, and decisions. spec-driven.md in gsd-planner enforces that plans reference this existing spec rather than introducing a second source of truth.

### Code Review Gate (ENG-05 + ENG-06)

- **D-15:** Code review is triggered by a CLAUDE.md instruction at the execute → ship boundary: "After /gsd-execute-phase completes for an implementation plan, spawn harness-code-reviewer before /gsd-ship."
- **D-16:** `code-review.md` is the harness-code-reviewer agent's role prompt (not a SKILL.md injection). The file contains the two-stage review protocol: Stage 1 — spec compliance check (does implementation match CONTEXT.md decisions?), Stage 2 — code quality check (style, maintainability, edge cases).
- **D-17:** Gate trigger is "implementation plan only" — determined by the plan type frontmatter. Config, docs, and scaffolding plans skip the code review gate, matching the TDD-exempt list.
- **D-18:** harness-code-reviewer agent stub already exists at `.claude/agents/harness-code-reviewer.md` — wait, Phase 1 created harness-ceo-reviewer and harness-eng-reviewer only. Phase 2 must create `.claude/agents/harness-code-reviewer.md` as a new agent stub.

### Systematic Debugging (ENG-04)

- **D-19:** `systematic-debugging.md` is injected into gsd-debugger via agent_skills. Requires adding `"gsd-debugger": [".claude/skills/harness/rules"]` to config.json agent_skills (or the specific systematic-debugging.md path).
- **D-20:** ENG-04 protocol structure: 4-phase root cause analysis (Observe → Hypothesize → Test → Fix), hard stop after 3 failed fix attempts with mandatory user escalation, evidence-gathering before any fix attempt (no "let's just try X").
- **D-21:** The 3-failure cap complements GSD's `node_repair_budget: 2` config — GSD's repair budget handles plan-level retries; the ENG-04 cap handles investigation-level attempts within a debugging session.

### CLAUDE.md Gate Triggers (ENG-02 gate, ENG-05 gate)

- **D-22:** Two new CLAUDE.md instructions added to the harness section (within GSD:harness-start/end markers): (1) spec gate — "Before /gsd-plan-phase, verify CONTEXT.md includes approaches-with-tradeoffs." (2) review gate — "After /gsd-execute-phase for implementation plans, spawn harness-code-reviewer before /gsd-ship."
- **D-23:** CLAUDE.md harness section must stay under 50 tokens of non-comment text (Phase 1 D-05). The two gate instructions must be concise — full detail lives in the agent definition files.

### Claude's Discretion

- Exact wording of the red-flag checklist items (as long as they cover the common rationalization patterns documented in research)
- Internal structure of the two-stage code review (section headers, checklist format)
- Which specific OWASP/quality items go in code quality vs spec compliance review
- verification-rules.md content (what to augment in GSD's verifier that isn't already there)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 2 Scope
- `.planning/REQUIREMENTS.md` §Engineering Discipline — ENG-01 through ENG-06 exact wording
- `.planning/ROADMAP.md` §Phase 2 — Success criteria (5 items) and dependency on Phase 1

### Phase 1 Locked Decisions
- `.planning/phases/01-router-context-infrastructure/01-CONTEXT.md` — D-01 through D-12 are locked; Phase 2 must not contradict them
- `.planning/phases/01-router-context-infrastructure/01-RESEARCH.md` — Pitfalls section (especially Pitfall 2: configs must stay in sync)

### GSD Integration Points
- `~/.claude/get-shit-done/bin/lib/init.cjs` lines 1432-1479 — `buildAgentSkillsBlock()` implementation; understand validatePath() and SKILL.md lookup before adding new agent_skills entries
- `~/.claude/get-shit-done/workflows/plan-phase.md` line 27-29 — agent-skills lookup keys for gsd-researcher, gsd-planner, gsd-checker (gsd-planner is confirmed stable)
- `~/.claude/get-shit-done/workflows/execute-phase.md` — how gsd-executor and gsd-debugger are dispatched, agent_skills injection pattern

### Existing Stubs to Populate
- `.claude/skills/harness/rules/tdd-enforcement.md` — stub, needs Iron Law + red flags + deletion penalty
- `.claude/skills/harness/rules/spec-driven.md` — NEW file (does not exist yet)
- `.claude/skills/harness/rules/systematic-debugging.md` — stub, needs 4-phase RCA + 3-failure cap
- `.claude/skills/harness/rules/code-review.md` — stub, becomes code-reviewer agent instructions
- `.claude/skills/harness/rules/verification-rules.md` — stub, needs verifier augmentations
- `.claude/skills/harness/tdd/SKILL.md` — stub, needs update to point to tdd-enforcement.md content

### Research Artifacts (superpowers patterns to absorb)
- `.planning/research/FEATURES.md` — lines 248-259: 7 TDD enforcement layers superpowers has; ENG-02 spec flow detail; ENG-04 4-phase debugging protocol
- `.planning/research/PITFALLS.md` — TDD bypass risks and anti-rationalization patterns documented here

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/config.json` agent_skills field — currently maps gsd-executor → tdd/ and gsd-verifier → rules/. Phase 2 adds gsd-planner → rules/ (spec-driven.md) and gsd-debugger → rules/ (systematic-debugging.md).
- `.planning/harness.json` tdd_exempt_plan_types — ["config", "docs", "scaffolding"]. tdd-enforcement.md must read this list to determine when Iron Law applies.
- `.claude/agents/harness-ceo-reviewer.md` and `harness-eng-reviewer.md` — Phase 1 agent stubs. harness-code-reviewer.md follows the same YAML frontmatter pattern.
- GSD's `node_repair_budget: 2` in config.json — works alongside ENG-04's 3-failure cap (different scopes: plan-level vs debugging-session-level).

### Established Patterns
- YAML frontmatter agent .md files — name, description, tools list. harness-code-reviewer.md follows this.
- Rules/ SKILL.md index — currently lists 4 files. Phase 2 updates it to list 5 files (adding spec-driven.md).
- agent_skills injection — project-relative paths (`.claude/skills/...`), validates SKILL.md existence at the path. spec-driven.md needs its own SKILL.md header or must be reachable via the rules/ SKILL.md.

### Integration Points
- `.planning/config.json` — add gsd-planner and gsd-debugger entries to agent_skills
- `CLAUDE.md` harness section — add two gate trigger instructions (spec gate + review gate), staying under 50-token budget
- `.claude/agents/` — create harness-code-reviewer.md agent stub (Phase 2 content, not Phase 3 stub)
- `.claude/skills/harness/rules/SKILL.md` — update index to list 5 files

</code_context>

<specifics>
## Specific Ideas

- User confirmed: GSD update risk for gsd-planner agent_skills injection is accepted — project-local config is safe, lookup key is stable API
- Iron Law must be framed imperatively, not as guidance — "You MUST" not "Consider doing"
- Two-stage code review must maintain independent perspective (separate context window via Task()) — self-review is explicitly rejected for ENG-06

</specifics>

<deferred>
## Deferred Ideas

- harness-code-reviewer could be split into two independent agents (spec-compliance-reviewer + code-quality-reviewer) for true isolation — deferred to Phase 3 or Phase 4 based on validation results
- gsd-debugger agent_skills could also receive systematic-debugging.md via the tdd/ path if the rules/ grouping becomes too broad — keep as-is for now
- verification-rules.md content could grow into a QA persona in Phase 3 — for now it augments gsd-verifier minimally

None — discussion stayed within Phase 2 scope.

</deferred>

---

*Phase: 02-engineering-discipline-rules*
*Context gathered: 2026-04-05*
