# Technology Stack

**Project:** Harness — Unified Claude Code Workflow Framework
**Researched:** 2026-04-04

## The "Stack" Is Not Code — It Is Structured Markdown

This is not a traditional software project with npm dependencies and a runtime. The harness is a collection of **markdown files, JSON config, and a thin Node.js CLI** that together instruct Claude Code how to behave. The "stack" is the file conventions, prompt engineering patterns, and orchestration primitives that each framework uses.

The harness deliverable is: `CLAUDE.md` + `skills/` + `agents/` + `.planning/` templates that can be dropped into any project.

---

## Framework-by-Framework File Structure Analysis

### GSD (Get Shit Done) — The Backbone

**Location:** `~/.claude/get-shit-done/` (global install) + `.planning/` (per-project state)
**Version:** 1.30.0 (as of 2026-03-27)
**Author:** TACHES (gsd-build org)
**Confidence:** HIGH (local installation analyzed directly)

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

```
.planning/
  PROJECT.md          # Living requirements doc (updated at phase transitions)
  ROADMAP.md          # Phased execution plan
  STATE.md            # Current position, session continuity (<100 lines)
  REQUIREMENTS.md     # Detailed requirements (generated during init)
  config.json         # Project-specific GSD settings
  research/           # Research artifacts (per-milestone)
  phases/
    01-phase-name/
      PLAN-01.md      # Individual plan files (executed by subagents)
      PLAN-02.md
      SUMMARY-01.md   # Execution summaries (created by executor)
      SUMMARY-02.md
    02-phase-name/
      ...
  todos/
    pending/          # Captured ideas
    completed/        # Done items
```

#### Context Management Pattern (CRITICAL)

GSD's core architectural insight is the **thin orchestrator** pattern:
- **Orchestrator** (the main Claude session) stays at 10-15% context usage
- Passes **file paths, not file contents** to subagents
- Each subagent spawns with a **fresh 200K token context**
- Subagents read only the files they need via `<files_to_read>` blocks
- `gsd-tools.cjs init` returns JSON metadata (phase info, config, file paths) — not file contents

The `init` pattern is the key integration point:
```bash
INIT=$(node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" init <workflow> [args])
if [[ "$INIT" == @file:* ]]; then INIT=$(cat "${INIT#@file:}"); fi
```
This returns a JSON object with everything the orchestrator needs to route work without reading large files.

#### Subagent Spawning

GSD uses Claude Code's `Task()` API:
```
Task(subagent_type="gsd-executor", prompt="...", files_to_read=[...])
```
- Each agent type is defined in `~/.claude/agents/<name>.md`
- Agent definitions include: YAML frontmatter (name, tools, permissions) + role prompt + execution flow
- Agents are specialized: executor, verifier, planner, researcher, debugger, etc.
- **Wave-based parallel execution**: plans within a phase are grouped into dependency waves, executed in parallel within each wave

---

### gstack (Garry Tan) — Role-Based Perspective Gates

**Location:** Installed as skills in `~/.claude/skills/gstack/` or project-local `.claude/skills/gstack/`
**Version:** Active development (28+ commands as of March 2026)
**Author:** Garry Tan (Y Combinator president)
**Confidence:** MEDIUM (analyzed via GitHub repo structure and docs, not local install)

#### File Structure

```
gstack/
  CLAUDE.md             # Development guide for gstack contributors
  SKILL.md              # Top-level skill index
  SKILL.md.tmpl         # Template for generating SKILL.md files
  AGENTS.md             # Agent definitions (large — 100KB+, avoid loading)
  conductor.json        # {"scripts": {"setup": "bin/dev-setup", "archive": "bin/dev-teardown"}}
  setup                 # Installation script
  
  # Each skill is a directory with SKILL.md (+ optional .tmpl)
  office-hours/SKILL.md       # YC-style product interrogation
  plan-ceo-review/SKILL.md    # CEO scope review (4 modes: expand/selective/hold/reduce)
  plan-eng-review/SKILL.md    # Architecture review (4 sections + outside voice)
  plan-design-review/SKILL.md # Design planning
  plan-devex-review/SKILL.md  # Developer experience review
  
  review/SKILL.md             # Code review
  qa/SKILL.md                 # QA testing with browser (Playwright-based)
  qa-only/SKILL.md            # QA reporting without fixes
  design-review/SKILL.md      # 80-item visual audit
  
  ship/SKILL.md               # PR creation + test bootstrap
  land-and-deploy/SKILL.md    # Merge, deploy, verify
  canary/SKILL.md             # Post-deploy monitoring
  
  investigate/SKILL.md        # Systematic debugging
  benchmark/SKILL.md          # Core Web Vitals
  cso/SKILL.md                # OWASP/STRIDE security audit
  
  careful/SKILL.md            # Destructive command warnings
  freeze/SKILL.md             # Directory-scoped edit restrictions
  guard/SKILL.md              # careful + freeze combined
  
  browse/SKILL.md             # Headless Chromium (Playwright)
  codex/SKILL.md              # OpenAI second opinion
  learn/SKILL.md              # Memory management
  
  # Infrastructure
  bin/                        # Executables
  lib/                        # Shared TypeScript libraries
  hosts/                      # Multi-agent configs (Claude, Codex, Cursor, etc.)
  extension/                  # Browser extension
  docs/                       # Documentation
```

#### Context Management Pattern

gstack uses the **Claude Code skills system**:
- Each skill directory contains a `SKILL.md` that Claude reads when the skill is invoked
- Skills are invoked via slash commands (`/office-hours`, `/plan-ceo-review`, etc.)
- **No orchestrator layer** — each skill runs in the main session context
- No subagent isolation between skills — the full session history carries forward
- `AGENTS.md` exists but is explicitly flagged as too large to load (100KB+)
- Skills use `AskUserQuestion` for interactive gates (one issue per question)
- Skills persist learnings to `~/.gstack/` for cross-session memory

#### Key Design Principles for Harness Integration

1. **Skills are interactive** — designed for human-in-the-loop, not autonomous execution
2. **No project state backbone** — no equivalent of GSD's STATE.md or phase tracking
3. **Role-as-persona** — each skill embodies a professional role (CEO, Eng Manager, QA Lead)
4. **Opinionated review criteria** — each role has specific checklists and quality bars
5. **SKILL.md files are generated from .tmpl templates** — never edit generated files directly

---

### Superpowers (Jesse Vincent / obra) — Engineering Discipline

**Location:** Installed as Claude Code plugin or manually to `.claude/skills/`
**Version:** Active development (135K+ GitHub stars as of March 2026)
**Author:** Jesse Vincent (obra)
**Confidence:** MEDIUM (analyzed via GitHub repo structure and docs, not local install)

#### File Structure

```
superpowers/
  CLAUDE.md               # Contributor guidelines (94% PR rejection rate)
  AGENTS.md               # Agent definitions
  GEMINI.md               # Gemini-specific instructions
  
  skills/
    brainstorming/SKILL.md              # Structured ideation
    test-driven-development/SKILL.md    # RED-GREEN-REFACTOR (mandatory)
    systematic-debugging/SKILL.md       # Root-cause-first debugging
    writing-plans/SKILL.md              # Implementation plan creation
    executing-plans/SKILL.md            # Plan execution
    subagent-driven-development/SKILL.md # Fresh subagent per task + 2-stage review
    requesting-code-review/SKILL.md     # Outbound review
    receiving-code-review/SKILL.md      # Inbound review handling
    using-git-worktrees/SKILL.md        # Git worktree isolation
    finishing-a-development-branch/SKILL.md  # Branch completion
    dispatching-parallel-agents/SKILL.md     # Parallel execution
    verification-before-completion/SKILL.md  # Pre-commit verification
    writing-skills/SKILL.md             # Meta: how to write new skills
  
  agents/                 # Subagent definitions
  commands/               # CLI commands
  hooks/                  # Git/system hooks
  scripts/                # Utility scripts
  tests/                  # Test suite
  
  # Multi-runtime support
  .claude-plugin/         # Claude Code plugin config
  .codex/                 # Codex integration
  .cursor-plugin/         # Cursor plugin config
  .opencode/              # OpenCode integration
```

#### Context Management Pattern

Superpowers uses **context isolation as a first principle**:
- Each subagent receives **only precisely crafted context** — never session history
- The coordinator extracts task text from plans and provides it directly (subagents never read plan files)
- Subagent status protocol: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`
- Two-stage review: spec compliance first, then code quality (sequential, not parallel)
- Anti-rationalization prompts: explicit "Red Flags" sections listing common excuses for skipping TDD

#### Key Design Principles for Harness Integration

1. **Mandatory TDD** — "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST" (code written before tests gets deleted)
2. **Seven-phase workflow**: Brainstorm -> Spec -> Plan -> TDD -> Subagent Development -> Review -> Finalize
3. **Plans stored in `docs/plans/`** — NOT in `.planning/` (critical routing distinction)
4. **Skills are composable** — activated based on context, not invoked manually
5. **Psychological persuasion** — anti-skip guards use prewritten reality-check responses for common rationalizations

---

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

The proven routing pattern uses a single criterion:
- `.planning/` exists -> GSD (macro layer: what + when)
- `.planning/` absent -> Superpowers (micro layer: how)

**For the harness, the enhanced routing is:**
- **Always GSD** for project backbone (`.planning/` always exists)
- **Superpowers TDD injected** into GSD executor subagents for implementation plans
- **gstack role personas** invoked at specific GSD phase transitions (scope review, architecture review, QA)

---

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

---

## Key Technical Patterns

### 1. GSD Init Pattern (Orchestrator Entry Point)

Every GSD workflow starts with:
```bash
INIT=$(node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" init <workflow> [args])
if [[ "$INIT" == @file:* ]]; then INIT=$(cat "${INIT#@file:}"); fi
```
Returns JSON with: model preferences, file paths, phase info, config flags. The harness must hook into this — either by extending gsd-tools.cjs or by wrapping it.

### 2. Selective Loading Pattern (Context Discipline)

```markdown
<files_to_read>
- .planning/STATE.md
- .planning/phases/03-implementation/PLAN-01.md
- src/relevant-file.ts
</files_to_read>
```
Subagents receive explicit file lists. The harness adds TDD constraints or role-review criteria to this list conditionally based on plan type.

### 3. Route-Not-Stack Pattern (Authority Resolution)

From unified-workflow's proven design:
- Implementation plan -> GSD executor + Superpowers TDD rules
- Scope review gate -> gstack CEO persona (loaded, executed, unloaded)
- Architecture gate -> gstack Eng Manager persona (loaded, executed, unloaded)
- Code review step -> Superpowers review skill (fills GSD's gap)
- QA verification -> gstack QA persona (extends GSD's verifier)

Each persona/skill is loaded exclusively at its trigger point, never carried forward.

### 4. Config Extension Pattern

GSD's `.planning/config.json` is the single config file. Extend it:
```json
{
  "harness": {
    "tdd_enforcement": true,
    "tdd_exempt_types": ["research", "documentation", "config"],
    "role_gates": {
      "ceo_review": { "trigger": "before-scope-lock", "mode": "interactive" },
      "eng_review": { "trigger": "before-execution", "mode": "interactive" },
      "qa_review": { "trigger": "after-verification", "mode": "interactive" }
    },
    "bypass_protection": true
  }
}
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backbone | GSD | Superpowers | Superpowers has no project state management, no phase tracking, no session continuity |
| Backbone | GSD | gstack | gstack has no orchestrator, no subagent isolation, no state management — it is interactive-only |
| TDD approach | Superpowers TDD skill (copy-and-own) | GSD's built-in TDD reference | GSD's TDD is a reference doc, not enforcement — Superpowers has anti-skip guards and mandatory compliance framing |
| Role gates | gstack personas (copy-and-own) | Custom role prompts from scratch | gstack's CEO/Eng/QA review prompts are battle-tested at scale (600K LOC in 2 months) — no reason to reinvent |
| Delivery | Files-only (CLAUDE.md + skills + agents) | Claude Code plugin | Files-first is faster to validate; plugin packaging is a packaging concern, not an architecture concern |
| Config | Extend GSD's config.json | Separate harness config file | One config file is simpler; GSD already reads it at init time |

---

## Version Compatibility

| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| GSD | 1.30.0 | Installed locally | Fast-moving — update periodically |
| gstack | Latest (March 2026) | Not installed — will copy prompts | 28+ commands, MIT license |
| Superpowers | Latest (March 2026) | Not installed — will copy prompts | 135K stars, MIT license |
| Claude Code | Current | Required runtime | Task() API for subagent spawning |
| Node.js | Any LTS | Required for gsd-tools.cjs | Already a GSD dependency |

---

## Sources

- GSD local installation at `~/.claude/get-shit-done/` (analyzed directly) — HIGH confidence
- [garrytan/gstack GitHub repo](https://github.com/garrytan/gstack) — MEDIUM confidence (remote analysis)
- [obra/superpowers GitHub repo](https://github.com/obra/superpowers) — MEDIUM confidence (remote analysis)
- [mattjaikaran/unified-workflow GitHub repo](https://github.com/mattjaikaran/unified-workflow) — MEDIUM confidence (remote analysis)
- [gsd-build/get-shit-done GitHub repo](https://github.com/gsd-build/get-shit-done) — HIGH confidence (matches local install)
- [gstack skills documentation](https://github.com/garrytan/gstack/blob/main/docs/skills.md) — MEDIUM confidence
- [Superpowers blog post (October 2025)](https://blog.fsck.com/2025/10/09/superpowers/) — MEDIUM confidence
- Council research at `council/unified-harness-gsd-gstack-superpowers/shared_reasoning.md` — HIGH confidence (local analysis)
