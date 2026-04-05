# Feature Landscape

**Domain:** Unified Claude Code workflow framework (GSD + gstack + superpowers)
**Researched:** 2026-04-04
**Overall confidence:** HIGH

## Framework-by-Framework Capability Map

### GSD (Get Shit Done) — The Context Engine & Project Backbone

**What it does:** Project lifecycle management with context-engineered multi-agent orchestration. Manages the *what* and *when* of building software.

| Capability | Description | Role Served |
|------------|-------------|-------------|
| `/gsd-new-project` | Vision capture, parallel domain research (4 agents), requirements extraction, roadmap generation | CEO/Product |
| `/gsd-discuss-phase N` | Surfaces design gray areas; two modes: questions (interactive) and assumptions (codebase-inferred, you correct) | Architect |
| `/gsd-plan-phase N` | Research + atomic XML task plans + verification loop against requirements | Lead Engineer |
| `/gsd-execute-phase N` | Wave-based parallel execution; fresh 200k-token context per task; dependency-aware ordering | Lead Engineer |
| `/gsd-verify-work N` | UAT + automated gap diagnosis; creates fix plans for failures | QA |
| `/gsd-ship N` | PR creation from verified work | Release |
| `/gsd-next` | Auto-detects and runs next workflow step | Orchestration |
| `/gsd-quick` | Lightweight ad-hoc tasks with optional `--discuss`, `--research`, `--validate`, `--full` flags | All |
| `/gsd-map-codebase` | Parallel agents analyze existing project: stack, architecture, conventions | Architect |
| `/gsd-new-milestone` / `/gsd-complete-milestone` | Version cycle management, archival, tagging | Project Mgmt |
| Planning artifacts | PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, CONTEXT.md, PLAN.md, SUMMARY.md, UAT.md | All |
| State consistency gates | `state validate` / `state sync` detect drift between STATE.md and filesystem | Orchestration |
| Research gates | Block planning if RESEARCH.md has unresolved questions | Quality |
| Scope drift detection | Flags when planner silently drops requirements | Quality |
| Schema drift detection | Flags ORM changes missing migrations | Quality |
| Discussion modes | `questions` (interactive Q&A) vs `assumptions` (system infers, you correct) | Architect |

### gstack — The Role-Based Perspective Engine

**What it does:** 31 specialized skills organized as a sprint workflow (Think > Plan > Build > Review > Test > Ship > Reflect). Each skill embodies a specific professional role. Created by Garry Tan (YC CEO).

| Capability | Description | Role Served |
|------------|-------------|-------------|
| `/office-hours` | YC-style discovery: 6 forcing questions, reframes product, generates alternatives | CEO/Product |
| `/plan-ceo-review` | Founder mode: 4 scope modes (Expansion, Selective Expansion, Hold Scope, Reduction), finds "10-star product" | CEO/Product |
| `/plan-eng-review` | Engineering manager: locks architecture, data flow diagrams, edge cases, test matrices | Architect |
| `/plan-design-review` | Senior designer: rates 7 dimensions (IA, interaction states, user journey, AI slop risk, design system, responsive, unresolved decisions) | Designer |
| `/plan-devex-review` | DX Lead: personas, competitor benchmarks, magical moments | Product |
| `/autoplan` | Runs CEO > design > eng > DX review automatically with encoded decision principles | All Planning |
| `/design-consultation` | Research-backed design system from scratch | Designer |
| `/design-shotgun` | 3 AI-generated visual variants with comparison board | Designer |
| `/design-html` | Production HTML with Pretext layout, framework detection | Designer/Eng |
| `/design-review` | 80-item live-site visual audit, CSS-only atomic fixes, before/after screenshots | Designer/QA |
| `/review` | Staff engineer: finds production bugs that pass CI, auto-fixes obvious ones, flags gaps | Lead Engineer |
| `/investigate` | Root-cause debugger: hypothesis testing, stops after 3 failed fixes ("Iron Law: no fixes without investigation") | Lead Engineer |
| `/qa` | QA lead: tests in real browser, fixes bugs atomically, auto-generates regression tests | QA |
| `/qa-only` | QA reporter: finds bugs without code changes | QA |
| `/cso` | OWASP Top 10 + STRIDE threat modeling security audit | Security |
| `/ship` | Release engineer: sync main, run tests, audit coverage, open PR, bootstrap test frameworks | Release |
| `/land-and-deploy` | Merge PR, wait for CI/deploy, verify production health | Release |
| `/canary` | Post-deploy monitoring: console errors, performance regressions | SRE |
| `/benchmark` | Performance baselines: page load, Core Web Vitals, resource sizes | SRE |
| `/document-release` | Auto-update all docs to match shipped features | Docs |
| `/retro` | Team retrospective with per-person breakdowns and growth opportunities | Team Lead |
| `/learn` | Cross-session memory: patterns, pitfalls, preferences | All |
| `/browse` | Real Chromium browser with ~100ms response time | QA/Testing |
| `/careful` / `/freeze` / `/guard` | Safety guardrails: destructive command warnings, edit locks, combined mode | Safety |
| `/codex` | Independent OpenAI Codex review (3 modes: review, adversarial, consultation) | Lead Engineer |

### superpowers — The Engineering Discipline Engine

**What it does:** 14 composable skills enforcing TDD, spec-driven development, and systematic execution. Created by Jesse Vincent (obra). The *how* of building software correctly.

| Capability | Description | Role Served |
|------------|-------------|-------------|
| `brainstorming` | 9-step structured ideation: context review, clarifying questions (one at a time), 2-3 approaches with tradeoffs, sectional design approval, written spec with self-review, user approval gate | Architect/Product |
| `writing-plans` | Breaks approved design into 2-5 min tasks with exact file paths, complete code, verification steps, git commits. Zero placeholders allowed. Self-review for spec coverage, placeholder scan, type consistency | Lead Engineer |
| `test-driven-development` | **RED-GREEN-REFACTOR enforcement.** Iron Law: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST." Code written before tests must be deleted. 13-item red flag checklist. 8-item verification checklist. No exceptions without human permission. | Lead Engineer |
| `subagent-driven-development` | Fresh agent per task. Three-gate review: (1) implementer self-review, (2) spec compliance reviewer, (3) code quality reviewer. Loops until all pass. | Lead Engineer |
| `executing-plans` | Batch execution with human checkpoints between task groups | Lead Engineer |
| `dispatching-parallel-agents` | Concurrent subagent workflows for independent tasks | Lead Engineer |
| `systematic-debugging` | 4-phase root cause analysis. Evidence-gathering before any fix attempts. | Lead Engineer |
| `verification-before-completion` | Confirms fixes actually work before marking done | QA |
| `requesting-code-review` | Pre-review checklist before submitting for review | Lead Engineer |
| `receiving-code-review` | Systematic response to review feedback | Lead Engineer |
| `using-git-worktrees` | Isolated parallel development branches | Lead Engineer |
| `finishing-a-development-branch` | Merge/PR decision workflow | Release |
| `writing-skills` | Meta-skill: create new skills following framework guidelines | Meta |
| `using-superpowers` | Framework introduction and orientation | Meta |

---

## Table Stakes (Must-Have for Unified Harness)

Features the harness cannot ship without. Missing any of these means the harness is less capable than using the individual frameworks.

### From GSD (Context & Orchestration)

| Feature | Why Table Stakes | Complexity |
|---------|-----------------|------------|
| Thin orchestrator / subagent isolation | Prevents context bloat — the core architectural innovation. Without this, Claude degrades at 60%+ context. | High (backbone) |
| Planning artifact chain (PROJECT > REQUIREMENTS > ROADMAP > STATE > PLAN) | Provides traceable state across sessions. Every framework needs persistent memory; GSD's is the most structured. | Medium |
| Wave-based parallel execution with dependency tracking | Dramatically speeds up multi-file changes. Fresh context per executor prevents accumulated degradation. | High |
| Discussion phase (questions + assumptions modes) | Surfaces design decisions before implementation. Catches ambiguity that causes rework. | Medium |
| Research gates (block planning on unresolved questions) | Prevents building on shaky foundations. Simple but high-impact quality gate. | Low |
| Scope drift detection | Catches the #1 Claude failure mode: silently dropping requirements during planning. | Low |
| `/gsd-quick` for ad-hoc tasks | Not everything is a phase. Must support lightweight work without full ceremony. | Low |
| State consistency validation | SESSION.md can drift from filesystem reality. Detection + repair is essential for long-running projects. | Low |

### From superpowers (Engineering Discipline)

| Feature | Why Table Stakes | Complexity |
|---------|-----------------|------------|
| TDD enforcement (RED-GREEN-REFACTOR with Iron Law) | The single most impactful quality gate. Without it, Claude writes plausible-looking code that fails at edges. Delete-and-restart enforcement is what makes it work. | Medium |
| Brainstorming with sectional approval | Forces design thinking before coding. Two approval gates (design sections + written spec) prevent premature implementation. | Low |
| Writing-plans with zero-placeholder constraint | Plans with "TBD" or "implement later" produce garbage subagent output. Complete, executable task specs are non-negotiable. | Low |
| Subagent two-stage review (spec compliance then code quality) | Spec review catches scope drift; code review catches quality issues. Order matters: don't polish wrong code. | Medium |
| Systematic debugging (evidence before fixes) | Prevents the "try random changes" anti-pattern that wastes context and creates new bugs. | Low |

### From gstack (Role Perspectives)

| Feature | Why Table Stakes | Complexity |
|---------|-----------------|------------|
| CEO/Product challenge (`/office-hours` pattern) | Forces product-level questioning before committing to build. "Should we build this?" before "how do we build this?" | Low |
| Engineering architecture review (`/plan-eng-review` pattern) | Locks architecture decisions with diagrams, edge cases, and test matrices before implementation begins. | Low |
| QA with real browser testing (`/qa` pattern) | Visual and interaction testing catches what unit tests miss. Real Chromium, not simulated. | Medium |
| Security audit (`/cso` pattern) | OWASP + STRIDE is a structured, repeatable security review. Not optional for production code. | Low |

---

## Differentiators (Unique Capabilities Worth Integrating)

Features that set the harness apart from using any single framework.

### High-Value Differentiators

| Feature | Source | Value Proposition | Complexity |
|---------|--------|-------------------|------------|
| Route-not-stack architecture | unified-workflow PoC | Exclusive ownership per phase prevents governance conflicts. GSD owns *what*, superpowers owns *how*. | Medium |
| `/autoplan` pipeline (CEO > design > eng > DX auto-review) | gstack | Automated multi-perspective review with only taste decisions surfaced to human. Compresses 4 review cycles into one command. | Medium |
| Cross-model review (`/codex` independent analysis) | gstack | Second LLM opinion catches blind spots in Claude's reasoning. Adversarial mode is particularly valuable. | Low |
| Post-deploy verification (`/canary` + `/benchmark`) | gstack | Closes the loop from "code merged" to "verified in production." Most frameworks stop at PR. | Medium |
| Spec review subagent (v5.0) | superpowers | After planning, a fresh agent reviews plan docs for sanity/completeness before execution begins. Catches planning errors early. | Low |
| Permission model for TDD exceptions | superpowers | Human must explicitly approve skipping TDD. Prevents Claude from rationalizing shortcuts. | Low |
| Design system creation (`/design-consultation`) | gstack | Full design system from scratch with typography, color, spacing, motion. Valuable for greenfield projects. | Low |

### Medium-Value Differentiators

| Feature | Source | Value Proposition | Complexity |
|---------|--------|-------------------|------------|
| `/investigate` with 3-failure cap | gstack | Prevents infinite debugging loops. If 3 hypotheses fail, stop and reassess. | Low |
| `/retro` team retrospective | gstack | Structured reflection on what shipped, what struggled, growth opportunities. | Low |
| `/learn` cross-session memory | gstack | Accumulates project-specific patterns and preferences across sessions. | Low |
| `writing-skills` meta-skill | superpowers | Users can extend the framework with new skills following consistent guidelines. | Low |
| Seeds / todos capture | GSD | Forward-looking ideas captured at milestone boundaries for future consideration. | Low |

---

## Anti-Features (Do NOT Bring Into Harness)

Features to deliberately exclude or defer.

| Anti-Feature | Source | Why Avoid | What to Do Instead |
|--------------|--------|-----------|-------------------|
| Browser automation binary (gstack-browser, Chromium bundling) | gstack | Adds binary dependency, conflicts with files-first constraint. Heavy installation burden. | Defer to v2. For v1, document how users can add browser testing via MCP or external tools. |
| Telemetry (even opt-in) | gstack | Adds infrastructure dependency (Supabase). Unnecessary for personal CTO tool. | Skip entirely. |
| Design variant generation (`/design-shotgun`) | gstack | Requires image generation APIs. Over-scoped for engineering-focused harness. | Defer. Design is secondary to engineering discipline for v1. |
| Parallel sprint conductor (10-15 simultaneous sessions) | gstack | Requires external tooling (conductor). Over-complex for v1. | GSD's wave execution covers parallel needs within a phase. |
| Cookie import / authenticated browser sessions | gstack | Security risk, browser-specific, complex setup. | Defer to v2 with browser integration. |
| Voice-friendly trigger phrases | gstack | Nice-to-have, not core. Adds prompt bloat for marginal benefit. | Users can add voice aliases outside the harness. |
| GSD v2 CLI/TypeScript application layer | GSD | V1 must be files-only (CLAUDE.md, skills, agents). CLI adds build step and dependency. | Use v1 file-based approach. CLI is the upgrade path for v2 of the harness. |
| Multi-agent runtime support (8 agents in gstack, 12 in GSD) | Both | Spreading across runtimes dilutes testing. Focus on Claude Code. | Support Claude Code only for v1. |
| `/plan-design-review` and `/plan-devex-review` | gstack | Design and DX review are secondary to core engineering workflow. Adds prompt weight. | Defer to v2. CEO + Architect + QA is the minimum viable perspective set. |
| TodoWrite-based task tracking | superpowers | GSD uses planning artifacts for tracking. Two tracking systems create conflicts. | Use GSD's artifact chain exclusively. |

---

## Role-Based Feature Mapping

Which framework provides which role, and what the harness should use.

### CEO / Product Owner

**Primary source:** gstack (`/office-hours`, `/plan-ceo-review`)
**Secondary:** GSD (`/gsd-new-project` vision capture, `/gsd-discuss-phase`)
**superpowers:** `brainstorming` (but scoped to technical design, not product strategy)

**Harness approach:** Use gstack's product-challenge patterns during GSD's project initialization and discuss phases. The CEO role activates at:
- Project inception (should we build this?)
- Phase boundaries (is this still the right thing to build?)
- Scope decisions (expand, hold, or reduce?)

### Architect

**Primary source:** gstack (`/plan-eng-review`), superpowers (`brainstorming` spec flow)
**Secondary:** GSD (`/gsd-discuss-phase`, `/gsd-map-codebase`)

**Harness approach:** Merge gstack's architecture locking (diagrams, edge cases, test matrices) with superpowers' spec approval flow (sectional design, written spec, self-review). Activate during:
- GSD discuss phase (architecture decisions)
- Plan phase (implementation approach)
- When codebase mapping is needed

### Lead Engineer

**Primary source:** superpowers (TDD, writing-plans, subagent-driven-development, systematic-debugging)
**Secondary:** gstack (`/review`, `/investigate`)
**Tertiary:** GSD (execution orchestration, wave-based parallelism)

**Harness approach:** superpowers owns implementation discipline entirely. GSD provides the execution infrastructure (wave orchestration, fresh contexts). gstack's review patterns supplement post-execution. Activate during:
- Plan creation (writing-plans with zero-placeholder constraint)
- Execution (TDD enforcement per task, subagent review gates)
- Bug fixing (systematic-debugging before any fix attempts)

### QA

**Primary source:** gstack (`/qa`, `/qa-only`, real browser testing)
**Secondary:** GSD (`/gsd-verify-work`)
**Tertiary:** superpowers (`verification-before-completion`)

**Harness approach:** GSD's verify-work provides the structural UAT gate. gstack's adversarial QA mindset and browser testing supplement it. superpowers' verification-before-completion applies at task level. Activate during:
- Post-execution verification (GSD verify-work + gstack QA perspective)
- Per-task completion (superpowers verification)
- Pre-ship (regression testing)

### Security

**Primary source:** gstack (`/cso`)
**No equivalent in GSD or superpowers.**

**Harness approach:** Integrate OWASP + STRIDE review as a gate before shipping. Not every phase needs it, but any phase touching auth, data handling, or external APIs should trigger it.

### Release

**Primary source:** GSD (`/gsd-ship`), gstack (`/ship`, `/land-and-deploy`, `/canary`)
**Secondary:** superpowers (`finishing-a-development-branch`)

**Harness approach:** GSD handles PR creation. gstack patterns add post-merge verification (deploy health, canary monitoring). Activate during:
- Ship phase (GSD creates PR)
- Post-merge (deploy verification, canary monitoring)

---

## TDD Enforcement Mechanism (Detail)

This is the single most important engineering discipline feature. Documented in full because the harness must replicate it precisely.

### The Iron Law
> "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"

### Enforcement Layers

1. **Ordering constraint:** Test must exist and fail before any production code is written
2. **Deletion penalty:** Code written before its test must be deleted entirely — no "keep as reference," no "adapt it"
3. **Mandatory verification:** Each RED/GREEN/REFACTOR step requires running `npm test` (or equivalent) and observing the expected result
4. **13-item red flag checklist:** Signs that TDD was abandoned, each requiring delete-and-restart:
   - Writing production code "just to see if it works"
   - Writing test after implementation
   - Writing multiple tests before any implementation
   - Refactoring while tests are red
   - Adding features during GREEN phase
   - Skipping the RED verification step
   - (and 7 more)
5. **8-item completion verification:** Checkboxes that must all be true; inability to verify any = skipped TDD
6. **Permission model:** No exceptions without explicit human approval — the agent cannot self-authorize TDD skips
7. **Scope exemption:** Config, scaffolding, and one-off scripts are exempt (per PROJECT.md constraint)

### Why Delete-and-Restart Works
Tests written after implementation pass immediately, proving nothing about correctness. They test that code exists, not that it behaves correctly. The deletion penalty makes the cost of skipping TDD higher than the cost of doing it right.

---

## PRD / Spec Approach (Detail)

The second critical discipline feature. How requirements become implementation specs.

### superpowers' Approach (brainstorming > writing-plans)

**Phase 1: Brainstorming (design spec)**
1. Review project context (files, docs, commits)
2. Ask clarifying questions one at a time
3. Propose 2-3 approaches with tradeoffs and recommendation
4. Present design in sections, seeking approval after each
5. Write spec to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
6. Self-review spec for placeholders, consistency, scope, ambiguity
7. User approves written spec
8. Hard gate: NO implementation skills invoked until spec is approved

**Phase 2: Writing Plans (implementation spec)**
1. Break approved design into 2-5 minute tasks
2. Each task has: exact file paths, complete code (no pseudocode), test commands with expected output, git commit message
3. Zero placeholder tolerance: no "TBD", "TODO", "implement later", "add appropriate error handling", "similar to Task N"
4. Self-review: spec coverage mapping, placeholder scan, type consistency check
5. (v5.0) Spec review subagent: fresh agent reviews plan docs for sanity/completeness

### GSD's Existing Approach (discuss > plan)

**Phase 1: Discuss** — Surfaces gray areas, locks decisions in CONTEXT.md
**Phase 2: Plan** — Research + atomic XML task plans + verification against REQUIREMENTS.md

### Integration Recommendation

Enhance GSD's discuss phase with superpowers' brainstorming rigor:
- Add sectional approval (not just Q&A, but presenting approaches with tradeoffs)
- Add written spec output (CONTEXT.md already serves this role but lacks the self-review and zero-placeholder discipline)
- Keep GSD's REQUIREMENTS.md as the source of truth; spec is phase-scoped

Enhance GSD's plan phase with superpowers' writing-plans discipline:
- Zero-placeholder constraint on all PLAN.md files
- Complete code in tasks, not instructions about code
- Self-review for spec coverage and type consistency
- Add spec review subagent before execution begins

---

## Feature Dependencies

```
Context Engine (GSD orchestrator) ──> Everything else depends on this
    |
    ├── Planning Artifacts ──> Discussion Phase ──> Plan Phase ──> Execution
    |                              |                    |
    |                    CEO Challenge Gate    Spec Zero-Placeholder Gate
    |                    Architect Review      Spec Review Subagent
    |                                               |
    |                                    TDD Enforcement (per task)
    |                                    Subagent Two-Stage Review
    |                                               |
    |                                    Verify Phase (UAT + QA)
    |                                    Security Audit (conditional)
    |                                               |
    |                                    Ship + Post-Deploy Verify
    |
    └── Quick Mode (bypasses full pipeline for ad-hoc work)
```

Key dependency chain:
- TDD enforcement requires plan tasks to have complete test code (writing-plans dependency)
- Spec review subagent requires written plans to exist (writing-plans dependency)
- Two-stage review requires spec document to review against (brainstorming/discuss dependency)
- CEO challenge is most valuable at project init and phase boundaries (no dependency on implementation stack)
- Security audit is independent but most valuable pre-ship

---

## MVP Feature Prioritization

### Phase 1: Core Backbone
1. GSD orchestrator with subagent isolation (table stakes infrastructure)
2. Planning artifact chain (PROJECT > REQUIREMENTS > ROADMAP > STATE)
3. Discussion phase with assumptions + questions modes
4. Research gates blocking planning on unresolved questions

### Phase 2: Engineering Discipline
5. TDD enforcement (Iron Law, deletion penalty, permission model)
6. Writing-plans with zero-placeholder constraint
7. Brainstorming with sectional approval and written spec
8. Spec review subagent before execution

### Phase 3: Role Perspectives
9. CEO product challenge at project init and phase boundaries
10. Architect review with architecture locking
11. QA adversarial testing post-verification
12. Security audit pre-ship (conditional trigger)

### Phase 4: Execution Excellence
13. Wave-based parallel execution with fresh contexts
14. Subagent two-stage review (spec then quality)
15. Systematic debugging (evidence before fixes)
16. Scope drift detection

### Defer to v2
- Browser automation and visual testing
- Cross-model review (Codex integration)
- Post-deploy canary monitoring
- Design system and variant generation
- Team retrospectives
- CLI/TypeScript application layer

---

## Sources

- [garrytan/gstack](https://github.com/garrytan/gstack) — Complete skill set and role architecture
- [gstack skills documentation](https://github.com/garrytan/gstack/blob/main/docs/skills.md) — Detailed skill descriptions
- [obra/superpowers](https://github.com/obra/superpowers) — TDD enforcement, spec-driven development
- [superpowers TDD skill](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md) — Iron Law and enforcement details
- [superpowers writing-plans skill](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) — Zero-placeholder task specs
- [superpowers brainstorming skill](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md) — Sectional approval and spec flow
- [superpowers subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md) — Two-stage review
- [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) — Context engine, orchestrator, planning artifacts
- [mattjaikaran/unified-workflow](https://github.com/mattjaikaran/unified-workflow) — Route-not-stack integration PoC
- [GStack SitePoint tutorial](https://www.sitepoint.com/gstack-garry-tan-claude-code/) — Sprint workflow details
- [Superpowers v5.0 blog](https://blog.fsck.com/2026/03/09/superpowers-5/) — Spec review subagent feature
- [Superpowers rave review](https://emschwartz.me/a-rave-review-of-superpowers-for-claude-code/) — Real-world usage patterns
