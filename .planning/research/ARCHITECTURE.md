# Architecture Patterns

**Domain:** Claude Code workflow framework integration (GSD + gstack + superpowers)
**Researched:** 2026-04-04

## Framework Architectures (As-Is)

### GSD (Get Shit Done) — The Orchestration Backbone

**Architecture pattern:** Thin orchestrator + thick subagents with file-based shared memory.

**Core components:**
- **gsd-tools.cjs** — TypeScript CLI runtime. Handles `init`, `state`, `config`, `roadmap`, `phase-plan-index` commands. Every workflow's first action is `gsd-tools.cjs init <workflow-name>` which returns a JSON payload of paths, flags, and model selections. This is the harness's programmatic integration surface.
- **Workflows** (~56 files in `~/.claude/get-shit-done/workflows/`) — Markdown instruction files loaded as system prompts. Each workflow is a slash command (`/gsd:execute-phase`, `/gsd:plan-phase`, etc.). The orchestrator (main Claude session) reads these inline.
- **Agents** (~19 files in `~/.claude/agents/`) — Markdown agent definitions with YAML frontmatter. Spawned as subagents via `Task(subagent_type="gsd-executor", ...)`. Each gets a fresh context window.
- **Templates** (~32 files) — Structural templates for artifacts (STATE.md, PLAN.md, SUMMARY.md, etc.).
- **References** (~15 files) — Loaded selectively into subagent prompts via `<execution_context>` blocks.

**Orchestration model:**
1. User invokes `/gsd:<command>` (slash command)
2. Orchestrator workflow loads, calls `gsd-tools.cjs init` for context JSON
3. Orchestrator reads STATE.md, ROADMAP.md, config.json (paths only, not full content for lean models)
4. Orchestrator spawns subagents via `Task()`, passing:
   - `<objective>` block (what to do)
   - `<execution_context>` block (reference files to load as system prompt extensions)
   - `<files_to_read>` block (files the subagent must Read tool on startup)
   - `${AGENT_SKILLS}` variable (project-specific skills from `.claude/skills/`)
5. Subagent runs with full context budget (~200K or 1M tokens), reads files itself
6. Subagent produces artifacts (SUMMARY.md, commits, STATE.md updates)
7. Orchestrator spot-checks results (file existence, git log), reports to user

**Context isolation mechanism:** File-path passing. The orchestrator never reads plan contents into its own context — it passes paths. Subagents read files with their fresh context window. This keeps orchestrator at ~10-15% context usage.

**Shared memory artifacts:**
| Artifact | Purpose | Updated by |
|----------|---------|------------|
| PROJECT.md | Core value, requirements, constraints | Orchestrator at phase transitions |
| ROADMAP.md | Phase structure, progress tracking | Roadmapper subagent, executors |
| STATE.md | Current position, decisions, blockers | Executors, orchestrator |
| config.json | User preferences (models, parallelization, branching) | Setup, settings command |
| CONTEXT.md | User decisions from discuss-phase | discuss-phase workflow |
| PLAN.md files | Task-level execution instructions | Planner subagent |
| SUMMARY.md files | Execution results per plan | Executor subagent |
| VERIFICATION.md | Phase goal verification | Verifier subagent |

**Phase lifecycle:**
```
discuss-phase -> plan-phase -> execute-phase -> verify-phase -> transition
     |               |              |               |
  CONTEXT.md    PLAN.md files   SUMMARY.md    VERIFICATION.md
```

**Key architectural properties:**
- Wave-based parallel execution (plans grouped by dependency, parallel within waves)
- Deviation rules (auto-fix bugs/blockers, ask for architectural changes)
- Checkpoint system (subagents stop at defined points, fresh agent resumes)
- TDD support built into plan types (`type: tdd` triggers RED-GREEN-REFACTOR in executor)

---

### gstack — Role-Based Perspective Gates

**Architecture pattern:** Skill-per-role with slash-command dispatch. No orchestrator, no shared memory backbone.

**Core components:**
- **SKILL.md files** (~31 skills) — Each skill is a self-contained markdown file installed to `~/.claude/skills/gstack/`. Skills are loaded on-demand when the user invokes the corresponding slash command.
- **CLAUDE.md section** — Registers all available `/commands` so Claude knows they exist.
- **lib/** — Shared utilities (browser automation, analytics).
- **agents/** — AI agent implementations for multi-model reviews.
- **~/.gstack/** — Persistent project data (CEO plans, test plans, QA reports, analytics).

**Orchestration model:**
- No centralized orchestrator. Each skill is independently invoked.
- `/autoplan` is the only meta-orchestrator: chains CEO -> Design -> Eng -> DevEx reviews sequentially, passing artifact summaries between phases.
- Dual-voice pattern: Many skills run both Claude subagent AND Codex CLI in parallel, producing consensus tables (CONFIRMED/DISAGREE).
- All decisions logged to `~/.gstack/` for cross-session memory.

**Role personas and what they own:**

| Role | Skill | What it evaluates | Output artifacts |
|------|-------|-------------------|------------------|
| CEO/Founder | `/plan-ceo-review` | Premises, scope, failure modes, market fit | Failure Modes Registry, Error & Rescue Registry, CEO plan doc |
| Eng Manager | `/plan-eng-review` | Architecture, dependencies, test coverage, performance | Coverage diagram, test plan, parallelization strategy |
| Designer | `/plan-design-review` | UI/UX dimensions (7-dimension scoring) | Design litmus scorecard |
| DX Lead | `/plan-devex-review` | Developer experience, time-to-hello-world | Developer journey map, DX scorecard |
| Staff Engineer | `/review` | Code safety, injection, race conditions, completeness | Fix-first report with confidence scores |
| QA Lead | `/qa` | Browser-based testing, visual regression | Annotated screenshots, health score, regression baseline |
| Security Officer | `/cso` | OWASP Top 10, STRIDE threat model | Attack surface inventory |
| Release Engineer | `/ship` | Test coverage, PR readiness | PR with coverage audit |

**Key architectural properties:**
- Every finding has confidence calibration (1-10 scale)
- One decision = one AskUserQuestion (never batched)
- Auto-decision principles in `/autoplan` (completeness, DRY, explicit-over-clever, bias-toward-action)
- Browser integration via real headless Chromium (not MCP)
- `~/.gstack/projects/{slug}/` provides cross-session project memory

**What gstack lacks:**
- No phase/plan lifecycle management
- No context isolation for subagents (skills load in main session)
- No shared artifact chain (each skill produces independent outputs)
- No state tracking across sessions beyond `~/.gstack/` directory

---

### Superpowers — Engineering Discipline Framework

**Architecture pattern:** Composable mandatory skills with subagent-per-task execution.

**Core components:**
- **Skills** (14 skills in `skills/`) — Each is a SKILL.md with mandatory workflow triggers. Not suggestions — Claude checks for relevant skills before any task.
- **Agents** (in `agents/`) — Subagent definitions for parallel/review work.
- **Commands** (in `commands/`) — CLI entry points.
- **Hooks** (in `hooks/`) — Git and system hooks for enforcement.

**The 14 skills and their roles:**

| Skill | Phase | Purpose |
|-------|-------|---------|
| brainstorming | Design | Socratic refinement with stakeholder validation |
| writing-plans | Plan | Break work into 2-5 minute TDD-sized tasks |
| executing-plans | Execute | Run tasks in batches with checkpoints |
| subagent-driven-development | Execute | Fresh subagent per task + two-stage review |
| test-driven-development | Execute | RED-GREEN-REFACTOR enforcement with anti-rationalization |
| using-git-worktrees | Execute | Isolated branches per development unit |
| dispatching-parallel-agents | Execute | Multi-agent parallel task execution |
| requesting-code-review | Review | Pre-review checklist against plan |
| receiving-code-review | Review | Structured feedback response |
| systematic-debugging | Debug | Four-phase root cause investigation |
| verification-before-completion | Verify | Evidence-based completion gates |
| finishing-a-development-branch | Ship | Merge/PR decision workflow |
| writing-skills | Meta | Create new skills |
| using-superpowers | Meta | System introduction |

**Orchestration model:**
- No project-level orchestrator. Skills trigger automatically based on work type.
- `subagent-driven-development` is the execution orchestrator: spawns fresh subagent per task, runs two-stage review (spec compliance, then code quality), loops on fixes until both reviewers approve.
- Plans stored in `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`.

**Context isolation mechanism:**
- Fresh subagent per task (no session history inheritance)
- Git worktrees for branch-level isolation
- Controller extracts all tasks from plan upfront, provides each subagent exactly: task spec + relevant code context. Nothing more.
- Model selection by task complexity (mechanical -> cheap model, architectural -> capable model).

**TDD enforcement (the crown jewel):**
- Iron Law: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"
- 13-item anti-rationalization table addressing specific excuses ("Too simple to test", "TDD is dogmatic", etc.)
- Sunk cost reframing: unverified code = technical debt
- Verification checklist: binary accountability ("Can't check all boxes? You skipped TDD. Start over.")
- Code written before tests gets DELETED, not kept as reference.

**What superpowers lacks:**
- No project lifecycle management (milestones, phases, roadmaps)
- No role-based perspective (no CEO/Eng/QA personas)
- No persistent project memory across sessions
- No scope management or requirement tracking

---

## Route-Not-Stack: The Harness Architecture

### Core Principle

Each framework was designed to be the outermost authority. Stacking them (loading all three systems' rules simultaneously) produces governance conflicts, context bloat, and bypass pressure. The harness must **route** to the right framework per lifecycle phase, with exclusive ownership at each point.

### Ownership Map

```
PROJECT LIFECYCLE                    OWNER           WHAT LOADS
========================================================================

Idea -> Requirements                 GSD             new-project workflow
                                                     + CEO Review gate (gstack persona, absorbed)

Requirements -> Roadmap              GSD             roadmapper subagent
                                                     (no gstack/SP needed)

Phase Discussion                     GSD             discuss-phase workflow
                                                     + Eng Review gate (gstack persona, absorbed)
                                                     at phase boundary

Phase Research                       GSD             phase-researcher subagent
                                                     (no gstack/SP needed)

Phase Planning                       GSD             planner subagent
                                                     + plan-checker subagent
                                                     (no gstack/SP needed)

Plan Execution (implementation)      GSD + SP*       executor subagent
                                                     + SP TDD skill injected into executor prompt
                                                     + SP verification skill injected

Plan Execution (non-implementation)  GSD             executor subagent only
                                                     (config, docs, scaffolding)

Phase Verification                   GSD             verifier subagent
                                                     + SP verification-before-completion rules

Code Review                          SP              requesting-code-review
                                                     + receiving-code-review
                                                     (fills GSD's missing review step)

Bug Investigation                    SP              systematic-debugging
                                                     (always SP-first, per unified-workflow pattern)

QA Testing                           gstack          /qa skill (absorbed)
                                                     (real browser testing GSD/SP lack)

Security Audit                       gstack          /cso skill (absorbed)
                                                     (OWASP/STRIDE neither GSD nor SP provides)

Ship/PR                              GSD             ship workflow
                                                     + gstack /review for pre-PR code review
```

*"GSD + SP" means GSD owns orchestration (wave execution, state tracking) while SP rules are injected INTO the executor subagent's prompt. The executor sees one unified instruction set, not two competing authorities.

### Component Boundaries

| Component | Responsibility | Owns | Does NOT Own |
|-----------|---------------|------|--------------|
| **Harness Router** | Determines which framework owns current phase/action | Lifecycle routing decisions, gate sequencing | Execution details (delegated to owned framework) |
| **GSD Core** (unmodified) | Project lifecycle, orchestration, state, artifacts | PROJECT.md, ROADMAP.md, STATE.md, PLAN.md, SUMMARY.md, VERIFICATION.md, config.json | Role-based reviews, TDD enforcement, browser QA |
| **Harness Gate Skills** | Absorbed gstack personas as harness-owned skills | CEO review prompts, Eng review prompts, QA prompts, CSO prompts | GSD's artifact chain, execution model |
| **Harness TDD Injection** | SP's TDD + verification rules formatted for GSD executor | TDD reference file, anti-rationalization guards, verification checklist | GSD's plan structure, wave execution |
| **Harness Code Review** | SP's code review skills for post-execution review | Review request/response flow | GSD's verify-phase (complementary, not replacement) |
| **Harness Debug Override** | SP's systematic-debugging as first responder for all bugs | Debug methodology | GSD's debugger agent (replacement for implementation bugs) |

### Data Flow Between Components

```
                    +-----------------+
                    | Harness Router  |
                    | (CLAUDE.md +    |
                    |  routing skill) |
                    +--------+--------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v-------+  +--v----------+  +v-----------+
     | GSD Orchestrator|  | Gate Skills |  | SP Skills  |
     | (workflows/)    |  | (absorbed   |  | (absorbed  |
     |                 |  |  gstack)    |  |  superpow) |
     +--------+--------+  +------+------+  +-----+------+
              |                   |              |
              |    ARTIFACTS      |              |
              |    (file-based)   |              |
              v                   v              v
     +--------+--------+  +------+------+  +-----+------+
     | GSD Subagents    |  | Review      |  | TDD Rules  |
     | (executor,       |  | Artifacts   |  | (injected  |
     |  planner,        |  | (CEO plan,  |  |  into GSD  |
     |  verifier, etc.) |  |  test plan, |  |  executor  |
     |                  |  |  QA report) |  |  prompts)  |
     +------------------+  +-------------+  +------------+
```

**Artifact passing between components:**

1. **GSD -> Gate Skills:** PROJECT.md, ROADMAP.md, CONTEXT.md flow into CEO/Eng review as input context. The gate skill reads these files, produces a review artifact, and the review decisions feed back into GSD's discuss-phase CONTEXT.md or plan-phase inputs.

2. **GSD -> SP TDD:** When planner creates a `type: tdd` plan, the executor subagent prompt includes the harness's TDD reference file (adapted from SP's test-driven-development SKILL.md). The executor follows TDD rules as if they were GSD's own.

3. **Gate Skills -> GSD:** CEO review decisions become entries in PROJECT.md Key Decisions table. Eng review's test plan artifact feeds into plan-phase as a `--prd` input. QA report findings become gap-closure items for verify-phase.

4. **SP Debug -> GSD:** When systematic-debugging resolves a bug, results flow into a GSD SUMMARY.md for the deferred-items or gap-closure plan.

### Integration Seams (Specific Files)

**Seam 1: CEO Review at Project Initialization**
- **Trigger:** `/gsd:new-project` after requirements draft, before roadmap
- **What loads:** Harness CEO review skill (absorbed from gstack `/plan-ceo-review`)
- **Input:** Draft PROJECT.md requirements
- **Output:** Validated/challenged requirements, failure modes registry
- **Feeds into:** Final PROJECT.md requirements, informs roadmapper subagent

**Seam 2: Eng Review at Phase Discussion**
- **Trigger:** `/gsd:discuss-phase` completion, before plan-phase
- **What loads:** Harness Eng review skill (absorbed from gstack `/plan-eng-review`)
- **Input:** CONTEXT.md from discuss-phase + ROADMAP.md phase scope
- **Output:** Architecture review, test plan artifact, coverage diagram
- **Feeds into:** plan-phase `--prd` input, planner creates plans aligned with review

**Seam 3: TDD Injection at Plan Execution**
- **Trigger:** `execute-phase` spawns executor for `type: tdd` plan
- **What loads:** Harness TDD reference (adapted from SP `test-driven-development/SKILL.md`)
- **Injected via:** `<execution_context>` block in executor Task() prompt (replaces/extends GSD's existing `references/tdd.md`)
- **What it adds over GSD's built-in TDD:** Anti-rationalization guards, deletion of pre-test code, binary verification checklist

**Seam 4: Verification Enhancement**
- **Trigger:** `verify-phase` spawns verifier subagent
- **What loads:** Harness verification rules (adapted from SP `verification-before-completion/SKILL.md`)
- **Injected via:** Additional reference in verifier's `<execution_context>` block
- **What it adds:** Evidence-before-claims mandate, red flag detection for hedging language

**Seam 5: Code Review Post-Execution**
- **Trigger:** After execute-phase completes, before transition
- **What loads:** Harness code review skill (adapted from SP `requesting-code-review` + gstack `/review`)
- **Input:** Committed code from execution phase
- **Output:** Review findings, auto-fixes, ask items
- **Feeds into:** Gap-closure plans if issues found

**Seam 6: QA Gate Before Ship**
- **Trigger:** After all phases verified, before `/gsd:ship` or merge
- **What loads:** Harness QA skill (absorbed from gstack `/qa`)
- **Input:** Running application, git diff against base branch
- **Output:** QA report with health score, annotated screenshots
- **Feeds into:** Go/no-go decision, potential gap-closure

**Seam 7: Bug Investigation Override**
- **Trigger:** Any bug encountered during execution or reported post-ship
- **What loads:** Harness debug skill (absorbed from SP `systematic-debugging`)
- **Replaces:** GSD's default `gsd-debugger` agent for implementation bugs
- **Output:** Root cause analysis, fix proposal

### How the Router Works

The harness router lives in `CLAUDE.md` as routing rules plus a dedicated routing skill file. It does NOT replace GSD's slash commands — it augments them.

```
Harness files:
  CLAUDE.md                          -- Project-level: loads harness routing rules
  .claude/skills/harness/
    SKILL.md                         -- Router: maps lifecycle points to owners
    rules/
      ceo-review.md                  -- Absorbed gstack CEO persona
      eng-review.md                  -- Absorbed gstack Eng persona  
      qa-gate.md                     -- Absorbed gstack QA skill
      cso-audit.md                   -- Absorbed gstack CSO skill
      tdd-enforcement.md             -- Adapted SP TDD skill
      verification-rules.md          -- Adapted SP verification skill
      code-review.md                 -- Merged SP + gstack review
      systematic-debugging.md        -- Adapted SP debugging skill
```

The router skill's SKILL.md contains:
- Lifecycle phase -> owner mapping (the table above)
- Gate insertion points (when to invoke which absorbed skill)
- Conflict resolution rules (if two frameworks want the same phase, who wins)
- Selective loading rules (only load the rules relevant to current phase)

**Selective loading is critical.** The executor subagent for a TDD plan loads `tdd-enforcement.md` (~2-3KB absorbed) but NOT `ceo-review.md` (~15KB), `qa-gate.md` (~10KB), or any other unrelated skill. GSD's `<execution_context>` block mechanism already supports this — the harness just adds more reference files to the selection pool.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Simultaneous Constraint Activation
**What:** Loading all three frameworks' rules into every subagent prompt.
**Why bad:** Context bloat (combined ~1MB+ of instruction files), governance conflicts (three systems claiming authority over scope decisions), bypass pressure (developer skips all gates because overhead feels redundant).
**Instead:** Route to exclusive owner. One authority per phase. Gate skills load only at their trigger points.

### Anti-Pattern 2: gstack as Live Dependency
**What:** Importing gstack skills directly from `~/.claude/skills/gstack/` and calling them as `/plan-ceo-review`.
**Why bad:** Upstream breakage on any gstack update. gstack skills assume they own the session (no awareness of GSD's artifact chain). Template-generated SKILL.md files carry substantial context overhead designed for standalone use.
**Instead:** Copy-and-own: extract the persona prompts, review criteria, and output templates. Reformat as harness-owned rule files (~2-5KB each) that reference GSD's artifact chain.

### Anti-Pattern 3: Nesting Execution Frameworks
**What:** Running SP's `subagent-driven-development` inside GSD's `execute-phase`.
**Why bad:** Two orchestrators fighting over task dispatch, commit patterns, and completion signals. GSD's executor expects SUMMARY.md and STATE.md updates. SP's subagent-driven-dev expects its own review loop.
**Instead:** GSD owns execution orchestration (wave-based dispatch). SP's TDD rules and verification rules are INJECTED into GSD executor subagent prompts as reference material, not as a competing orchestrator.

### Anti-Pattern 4: Redundant Strategic Gates
**What:** Running CEO review, discuss-phase, AND brainstorming for the same scope.
**Why bad:** Three rounds of strategic questioning with no shared state between them. User bypasses all three by the second project.
**Instead:** GSD's discuss-phase IS the strategic alignment step. CEO review augments it at specific points (project init, major scope changes) — not replaces or duplicates it.

## Scalability Considerations

| Concern | Solo CTO (now) | Small Team (3-5) | Distributable |
|---------|----------------|-------------------|---------------|
| Gate overhead | CEO + Eng reviews at key milestones only, skip for small phases | Full gate pipeline per milestone | Configurable gates per project complexity |
| Context budget | Selective loading keeps each subagent under 40% context | Same — subagent isolation scales naturally | Same architecture |
| Maintenance | Single person tracks harness + GSD updates | Designate one person for harness maintenance | Versioned releases, changelog |
| Customization | Edit rule files directly | CLAUDE.md project overrides | Config-driven gate selection |

## Suggested Build Order

Based on dependency analysis between components:

### Layer 1: Foundation (no dependencies)
1. **Harness CLAUDE.md** — Routing rules, skill registration
2. **Harness SKILL.md** — Router logic with lifecycle->owner mapping
3. **tdd-enforcement.md** — Adapted from SP, most immediate value (addresses daily pain point of code quality shortcuts)

**Rationale:** These three files make the harness functional. GSD already works. Adding the router + enhanced TDD reference gives immediate value with zero risk to existing GSD workflow.

### Layer 2: Verification Enhancement (depends on Layer 1)
4. **verification-rules.md** — Adapted from SP, injected into GSD verifier
5. **systematic-debugging.md** — Adapted from SP, replaces GSD debugger for implementation bugs
6. **code-review.md** — Merged SP + gstack review, fills GSD's missing review step

**Rationale:** These improve the quality of GSD's existing verify and debug phases without changing GSD's orchestration model.

### Layer 3: Role-Based Gates (depends on Layer 1, benefits from Layer 2)
7. **eng-review.md** — Absorbed from gstack, triggered at discuss-phase boundary
8. **ceo-review.md** — Absorbed from gstack, triggered at project init and major scope changes

**Rationale:** These add gstack's perspective value. Deferred because: (a) GSD's discuss-phase already provides strategic alignment, so the marginal value needs validation; (b) absorbing gstack personas requires careful prompt surgery to reference GSD artifacts.

### Layer 4: QA and Security (depends on Layer 1-3)
9. **qa-gate.md** — Absorbed from gstack, requires browser infrastructure
10. **cso-audit.md** — Absorbed from gstack, pre-ship security gate

**Rationale:** These require the most infrastructure (browser automation) and are most valuable after the core development loop is solid. QA gate is a milestone-level gate, not a phase-level one.

## Sources

- GSD source code: `~/.claude/get-shit-done/` (local installation, version examined 2026-04-04)
- GSD agents: `~/.claude/agents/gsd-*.md` (19 agent definitions)
- [gstack GitHub repository](https://github.com/garrytan/gstack) — 31 skills, examined 2026-04-04
- [Superpowers GitHub repository](https://github.com/obra/superpowers) — 14 skills, examined 2026-04-04
- [mattjaikaran/unified-workflow](https://github.com/mattjaikaran/unified-workflow) — GSD+SP routing proof-of-concept
- Council review: `/Users/molchairuangutai/GitHub/harness/council/unified-harness-gsd-gstack-superpowers/shared_reasoning.md`
- gstack `/autoplan` SKILL.md — sequential review pipeline architecture
- gstack `/plan-ceo-review` SKILL.md — CEO persona evaluation criteria
- gstack `/plan-eng-review` SKILL.md — Eng Manager architecture review
- gstack `/qa` SKILL.md — Browser-based QA testing
- gstack `/review` SKILL.md — Staff engineer code review
- Superpowers `test-driven-development/SKILL.md` — TDD enforcement with anti-rationalization
- Superpowers `subagent-driven-development/SKILL.md` — Context isolation via fresh subagent per task
- Superpowers `executing-plans/SKILL.md` — Plan execution with checkpoints
- Superpowers `verification-before-completion/SKILL.md` — Evidence-based completion gates
- Superpowers `writing-plans/SKILL.md` — Task granularity rules
