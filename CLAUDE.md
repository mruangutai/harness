<!-- GSD:project-start source:PROJECT.md -->
## Project

**Harness**

A unified Claude Code workflow that combines the best of three frameworks — GSD (Get Shit Done), gstack, and superpowers — into a cohesive harness for AI-assisted software development. It uses GSD's context engine as the backbone, integrates gstack's role-based perspectives (CEO, Architect, Lead Engineer, QA) at key workflow gates, and enforces superpowers' engineering discipline (TDD, spec-driven development) during implementation. Built as portable files (CLAUDE.md, skills, agent definitions) first, with a path to global installation and distributable package.

**Core Value:** Enable a CTO to take a software idea from product validation through architecture, disciplined implementation, and QA — with Claude executing reliably at each stage without context drift, scope creep, quality shortcuts, or unchallenged assumptions.

### Constraints

- **Delivery format**: Files-only for v1 (CLAUDE.md, skills, agents) — no CLI, no build step, no dependencies
- **GSD compatibility**: Must work within GSD's existing subagent/orchestrator model, not fight against it
- **Context budget**: The harness itself must not bloat Claude's context — selective loading, not everything-at-once
- **Copy-and-own**: Absorb gstack/superpowers patterns into harness-owned files, not live external dependencies
- **TDD scope**: Mandatory for implementation code, exempt for config/scaffolding/one-off scripts
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## The "Stack" Is Not Code — It Is Structured Markdown
## Framework-by-Framework File Structure Analysis
### GSD (Get Shit Done) — The Backbone
#### Global Files (Installed to `~/.claude/`)
| Directory | Count | Purpose | Context Impact |
|-----------|-------|---------|----------------|
| `get-shit-done/workflows/` | 56 files | Orchestrator prompts (new-project, execute-phase, transition, etc.) | Loaded ONE at a time per command invocation |
| `get-shit-done/templates/` | 32 files | File templates for planning artifacts | Read on-demand during file creation |
| `get-shit-done/references/` | 15 files | Shared reference docs (TDD, git, verification patterns) | Loaded by agents as needed |
| `get-shit-done/bin/` | 18 .cjs files | Node.js CLI tooling (gsd-tools.cjs + lib/) | Not loaded into context — executed via Bash |
| `agents/` | 19 gsd-* agents | Subagent definitions (executor, verifier, planner, etc.) | Loaded ONE per subagent spawn |
| `commands/gsd/` | 59 .md files | Slash command definitions (`/gsd:*`) | Claude reads ONE per invocation |
#### Per-Project Files (Created in `.planning/`)
#### Context Management Pattern (CRITICAL)
- **Orchestrator** (the main Claude session) stays at 10-15% context usage
- Passes **file paths, not file contents** to subagents
- Each subagent spawns with a **fresh 200K token context**
- Subagents read only the files they need via `<files_to_read>` blocks
- `gsd-tools.cjs init` returns JSON metadata (phase info, config, file paths) — not file contents
#### Subagent Spawning
- Each agent type is defined in `~/.claude/agents/<name>.md`
- Agent definitions include: YAML frontmatter (name, tools, permissions) + role prompt + execution flow
- Agents are specialized: executor, verifier, planner, researcher, debugger, etc.
- **Wave-based parallel execution**: plans within a phase are grouped into dependency waves, executed in parallel within each wave
### gstack (Garry Tan) — Role-Based Perspective Gates
#### File Structure
#### Context Management Pattern
- Each skill directory contains a `SKILL.md` that Claude reads when the skill is invoked
- Skills are invoked via slash commands (`/office-hours`, `/plan-ceo-review`, etc.)
- **No orchestrator layer** — each skill runs in the main session context
- No subagent isolation between skills — the full session history carries forward
- `AGENTS.md` exists but is explicitly flagged as too large to load (100KB+)
- Skills use `AskUserQuestion` for interactive gates (one issue per question)
- Skills persist learnings to `~/.gstack/` for cross-session memory
#### Key Design Principles for Harness Integration
### Superpowers (Jesse Vincent / obra) — Engineering Discipline
#### File Structure
#### Context Management Pattern
- Each subagent receives **only precisely crafted context** — never session history
- The coordinator extracts task text from plans and provides it directly (subagents never read plan files)
- Subagent status protocol: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`
- Two-stage review: spec compliance first, then code quality (sequential, not parallel)
- Anti-rationalization prompts: explicit "Red Flags" sections listing common excuses for skipping TDD
#### Key Design Principles for Harness Integration
## Integration Surface Map
### Where the Harness Connects to Each Framework
| Integration Point | GSD Surface | gstack Surface | Superpowers Surface |
|-------------------|-------------|----------------|---------------------|
| **Project init** | `new-project` workflow + PROJECT.md | `/office-hours` SKILL.md | `brainstorming` SKILL.md |
| **Scope review** | `discuss-phase` workflow | `/plan-ceo-review` SKILL.md | (none — defers to coordinator) |
| **Architecture review** | (implicit in planning) | `/plan-eng-review` SKILL.md | `writing-plans` SKILL.md |
| **Implementation** | `gsd-executor` agent | (none — no execution layer) | `test-driven-development` + `subagent-driven-development` SKILL.md |
| **Verification** | `gsd-verifier` + `gsd-nyquist-auditor` agents | `/qa` + `/review` SKILL.md | `verification-before-completion` SKILL.md |
| **Code review** | (gap — no review step) | `/review` SKILL.md | `requesting-code-review` SKILL.md |
| **State management** | STATE.md + PROJECT.md + ROADMAP.md | (none) | (none) |
| **Subagent dispatch** | `execute-phase` orchestrator + `Task()` API | (none — interactive only) | `dispatching-parallel-agents` SKILL.md |
| **Context budget** | `gsd-tools.cjs init` returns metadata JSON | SKILL.md per invocation | Context isolation per subagent |
### Routing Architecture (from unified-workflow)
- `.planning/` exists -> GSD (macro layer: what + when)
- `.planning/` absent -> Superpowers (micro layer: how)
- **Always GSD** for project backbone (`.planning/` always exists)
- **Superpowers TDD injected** into GSD executor subagents for implementation plans
- **gstack role personas** invoked at specific GSD phase transitions (scope review, architecture review, QA)
## Recommended Harness Stack
### Delivery Format
| Component | Format | Location | Why |
|-----------|--------|----------|-----|
| Harness CLAUDE.md | Markdown with GSD markers | `./CLAUDE.md` | GSD's template system already manages project CLAUDE.md with marker-bounded sections |
| Phase router | Markdown workflow file | `~/.claude/get-shit-done/workflows/` or project `.claude/skills/harness/` | Follows GSD's existing workflow pattern |
| Role personas | Markdown skill files | `.claude/skills/harness/personas/` | Copy-and-own from gstack, loaded selectively |
| TDD enforcement | Markdown injected into executor prompt | `.claude/skills/harness/tdd/` | Derived from Superpowers, loaded only for implementation plans |
| Agent definitions | Markdown with YAML frontmatter | `.claude/agents/` | Follows GSD's existing agent pattern |
| Config | JSON | `.planning/config.json` (extended) | Extends GSD's existing config with harness-specific gates |
### File Conventions to Follow
| Convention | Source | Rationale |
|------------|--------|-----------|
| SKILL.md per skill directory | gstack + Superpowers | Both frameworks use this; Claude Code natively discovers skills via SKILL.md |
| YAML frontmatter in agent .md files | GSD | Agent metadata (name, tools, permissions, color) |
| `<purpose>`, `<process>`, `<step>` XML tags in workflows | GSD | Structured prompt sections that Claude parses reliably |
| `AskUserQuestion` for interactive gates | gstack | One issue per question, explicit user sovereignty |
| `<files_to_read>` blocks for subagent context | GSD | Declarative file loading, not inline content |
| Anti-rationalization "Red Flags" sections | Superpowers | Prevent agents from skipping discipline under pressure |
### Context Budget Strategy
| Layer | Budget Target | Mechanism |
|-------|---------------|-----------|
| Orchestrator (main session) | 10-15% of context | GSD's thin orchestrator — passes file paths, reads STATE.md only |
| Subagent (executor) | 40-50% of 200K | Loads: PLAN.md + relevant source files + TDD constraints (if implementation plan) |
| Role review gate | One SKILL.md per invocation | gstack persona loaded only at trigger points, not carried in session |
| Project state | <100 lines | STATE.md is a digest — full context lives in PROJECT.md, read on-demand |
### What NOT to Build
| Anti-Pattern | Why Avoid |
|--------------|-----------|
| Custom CLI or build system | GSD already has gsd-tools.cjs; adding another binary creates maintenance burden |
| Live dependency on gstack/superpowers repos | Single-author personal tooling with uncertain maintenance — copy and own the prompts |
| Simultaneous constraint activation | Three authority-claiming systems loaded at once produces governance conflicts and context bloat |
| New planning artifact format | GSD's PROJECT.md -> ROADMAP.md -> PLAN.md chain is battle-tested — extend, don't replace |
| Plugin marketplace distribution | v1 is files-first; plugin packaging is a future concern |
## Key Technical Patterns
### 1. GSD Init Pattern (Orchestrator Entry Point)
### 2. Selective Loading Pattern (Context Discipline)
- .planning/STATE.md
- .planning/phases/03-implementation/PLAN-01.md
- src/relevant-file.ts
### 3. Route-Not-Stack Pattern (Authority Resolution)
- Implementation plan -> GSD executor + Superpowers TDD rules
- Scope review gate -> gstack CEO persona (loaded, executed, unloaded)
- Architecture gate -> gstack Eng Manager persona (loaded, executed, unloaded)
- Code review step -> Superpowers review skill (fills GSD's gap)
- QA verification -> gstack QA persona (extends GSD's verifier)
### 4. Config Extension Pattern
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backbone | GSD | Superpowers | Superpowers has no project state management, no phase tracking, no session continuity |
| Backbone | GSD | gstack | gstack has no orchestrator, no subagent isolation, no state management — it is interactive-only |
| TDD approach | Superpowers TDD skill (copy-and-own) | GSD's built-in TDD reference | GSD's TDD is a reference doc, not enforcement — Superpowers has anti-skip guards and mandatory compliance framing |
| Role gates | gstack personas (copy-and-own) | Custom role prompts from scratch | gstack's CEO/Eng/QA review prompts are battle-tested at scale (600K LOC in 2 months) — no reason to reinvent |
| Delivery | Files-only (CLAUDE.md + skills + agents) | Claude Code plugin | Files-first is faster to validate; plugin packaging is a packaging concern, not an architecture concern |
| Config | Extend GSD's config.json | Separate harness config file | One config file is simpler; GSD already reads it at init time |
## Version Compatibility
| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| GSD | 1.30.0 | Installed locally | Fast-moving — update periodically |
| gstack | Latest (March 2026) | Not installed — will copy prompts | 28+ commands, MIT license |
| Superpowers | Latest (March 2026) | Not installed — will copy prompts | 135K stars, MIT license |
| Claude Code | Current | Required runtime | Task() API for subagent spawning |
| Node.js | Any LTS | Required for gsd-tools.cjs | Already a GSD dependency |
## Sources
- GSD local installation at `~/.claude/get-shit-done/` (analyzed directly) — HIGH confidence
- [garrytan/gstack GitHub repo](https://github.com/garrytan/gstack) — MEDIUM confidence (remote analysis)
- [obra/superpowers GitHub repo](https://github.com/obra/superpowers) — MEDIUM confidence (remote analysis)
- [mattjaikaran/unified-workflow GitHub repo](https://github.com/mattjaikaran/unified-workflow) — MEDIUM confidence (remote analysis)
- [gsd-build/get-shit-done GitHub repo](https://github.com/gsd-build/get-shit-done) — HIGH confidence (matches local install)
- [gstack skills documentation](https://github.com/garrytan/gstack/blob/main/docs/skills.md) — MEDIUM confidence
- [Superpowers blog post (October 2025)](https://blog.fsck.com/2025/10/09/superpowers/) — MEDIUM confidence
- Council research at `council/unified-harness-gsd-gstack-superpowers/shared_reasoning.md` — HIGH confidence (local analysis)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

| Skill | Description | Path |
|-------|-------------|------|
| harness |  | `.claude/skills/harness/SKILL.md` |
<!-- GSD:skills-end -->
<!-- GSD:harness-start -->
## Harness

Unified workflow harness active. Skills: `.claude/skills/harness/`
Config: `.planning/harness.json`

When dispatching subagents, include `.planning/harness.json` in the `<files_to_read>` block.
Before /gsd-plan-phase: verify CONTEXT.md has approaches-with-tradeoffs and user approval.
After /gsd-execute-phase on implementation plans: spawn harness-code-reviewer before /gsd-ship.
<!-- GSD:harness-end -->
