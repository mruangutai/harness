# Project Research Summary

**Project:** Harness — Unified Claude Code Workflow Framework
**Domain:** Claude Code framework integration (GSD + gstack + superpowers)
**Researched:** 2026-04-04
**Confidence:** HIGH

## Executive Summary

The harness is not a software application — it is a collection of markdown files, YAML frontmatter agent definitions, and a thin routing layer that unifies three independently-designed Claude Code workflow frameworks into a coherent development system. GSD provides the project backbone (orchestration, state tracking, artifact chain, parallel execution); superpowers provides engineering discipline (TDD enforcement with anti-rationalization guards, spec-driven planning, two-stage subagent review); gstack provides role-based perspective gates (CEO product challenge, Architect review, QA with real browser testing, security audit). Each framework was designed to be the sole authority, which is the central integration challenge.

The recommended approach is "route, don't stack." Each lifecycle phase has exactly one framework authority; the others are either inactive or injected as reference material into the active framework's subagents. GSD owns the orchestration backbone and never yields it. Superpowers TDD rules are injected into GSD's executor subagent prompts (not run as a competing orchestrator). gstack's role personas are absorbed as harness-owned skill files that load exclusively at defined trigger points. The harness deliverable is: a CLAUDE.md router under 1,000 tokens, a set of `.claude/skills/harness/rules/` files (~8 total), and configuration extensions to GSD's existing `.planning/config.json`. No new CLI, no new binary, no new planning artifact format.

The key risks are context budget death (loading all three frameworks simultaneously consumes 25-30% of the context window before any work begins), governance conflicts (three systems each expecting to be the outermost authority produce contradictory instructions that Claude resolves inconsistently), and TDD bypass (subagents dispatched by GSD's executor may not inherit superpowers' TDD mandate unless it is explicitly embedded in each dispatch). All three risks are well-understood and have clear preventions documented in prior art (the unified-workflow PoC already solved the routing problem; Pitfalls research identifies exact detection and mitigation strategies).

## Key Findings

### Recommended Stack

The harness stack is structured markdown and JSON, not code. GSD's gsd-tools.cjs (Node.js, already installed) is the only runtime component and should not be replaced or supplemented with a new binary. The integration surface is: SKILL.md files per harness rule (follows Claude Code's native skill discovery), YAML frontmatter agent definitions (follows GSD's existing agent pattern), `<files_to_read>` blocks for selective context loading, and config.json extensions in `.planning/`.

**Core technologies:**

- **GSD v1.30.0** (installed at `~/.claude/get-shit-done/`): Project backbone — orchestration, state, artifacts, parallel execution. Extend, never replace.
- **SKILL.md convention** (gstack + superpowers standard): Each harness rule is a self-contained SKILL.md that Claude loads on demand. Keeps CLAUDE.md lean.
- **`.planning/config.json` extension**: Harness gates (TDD enforcement, role review triggers, bypass protection) are configured here, extending GSD's existing config rather than introducing a separate file.
- **Copy-and-own pattern** (superpowers + gstack prompts): Absorb role personas and discipline rules as harness-owned files; no live dependency on upstream repos.
- **Node.js LTS** (existing GSD dependency): gsd-tools.cjs handles all CLI operations; no new runtime needed.

### Expected Features

The harness must deliver all table-stakes capabilities from each framework, or it is strictly worse than using any single framework alone.

**Must have (table stakes):**

- Thin orchestrator with subagent isolation — GSD's core innovation; without it, Claude degrades at 60%+ context
- Planning artifact chain (PROJECT > REQUIREMENTS > ROADMAP > STATE > PLAN) — persistent memory across sessions
- Wave-based parallel execution with fresh 200K-token contexts per subagent
- TDD Iron Law enforcement with deletion penalty and anti-rationalization guards — the single highest-impact quality gate
- Zero-placeholder plan tasks — "TBD" in a plan produces garbage subagent output
- CEO product challenge at project init and phase boundaries — "should we build this?" before "how do we build this?"
- Architect review at discuss-phase boundary — locks architecture with diagrams, edge cases, test matrices
- QA adversarial testing post-verification — real browser testing catches what unit tests miss
- Security audit pre-ship — OWASP + STRIDE, conditional on phase content

**Should have (competitive differentiators):**

- Route-not-stack architecture with exclusive per-phase ownership — prevents governance conflicts
- Spec review subagent before execution begins — fresh agent catches planning errors early
- Two-stage subagent review (spec compliance then code quality, in that order)
- Systematic debugging with evidence-before-fixes mandate — prevents random-change anti-pattern
- Scope drift detection — catches the most common Claude failure: silently dropping requirements
- `/gsd-quick` for ad-hoc tasks — not everything warrants full ceremony

**Defer to v2+:**

- Browser automation binary and visual testing (heavy installation burden)
- Cross-model review via Codex integration (adds dependency, secondary benefit)
- Post-deploy canary monitoring (valuable but milestone-level, not phase-level)
- Design system and variant generation (secondary to engineering discipline for v1)
- Team retrospectives and analytics

### Architecture Approach

The harness architecture is a router layer that sits above GSD's existing orchestration model without replacing it. A lightweight CLAUDE.md (under 1,000 tokens) contains routing rules and skill registration. A router SKILL.md maps lifecycle phases to their owning framework. Eight rule files in `.claude/skills/harness/rules/` contain the absorbed gstack personas and adapted superpowers disciplines. These rule files are injected selectively into GSD subagent prompts via the existing `<execution_context>` block mechanism — they never all load simultaneously.

**Major components:**

1. **Harness Router** (CLAUDE.md + SKILL.md) — Maps lifecycle phases to exclusive framework owners; determines which rule files load at each trigger point. Under 1,000 tokens in CLAUDE.md.
2. **GSD Core** (unmodified, `~/.claude/get-shit-done/`) — Project backbone: orchestration, artifact chain, wave execution, state tracking. The harness extends GSD's config.json but never modifies GSD's own files.
3. **Harness Gate Skills** (`.claude/skills/harness/rules/ceo-review.md`, `eng-review.md`, `qa-gate.md`, `cso-audit.md`) — Absorbed gstack personas, reformatted as harness-owned rule files (~2-5KB each) that reference GSD's artifact chain instead of gstack's independent storage.
4. **Harness Discipline Rules** (`.claude/skills/harness/rules/tdd-enforcement.md`, `verification-rules.md`, `code-review.md`, `systematic-debugging.md`) — Adapted superpowers disciplines, injected into GSD executor subagent prompts for implementation-type plans only.
5. **Config Extension** (`.planning/config.json` harness block) — Toggles TDD enforcement, gate trigger points, bypass protection, and TDD-exempt plan types (config, docs, scaffolding).

**Seven integration seams between components:**

- Seam 1: CEO review at project init (after requirements draft, before roadmap)
- Seam 2: Eng review at discuss-phase completion (before plan-phase)
- Seam 3: TDD injection into executor subagents for `type: tdd` plans
- Seam 4: Verification enhancement injected into verifier subagents
- Seam 5: Code review post-execution (fills GSD's missing review step)
- Seam 6: QA gate before ship
- Seam 7: Systematic debugging override for all implementation bugs

### Critical Pitfalls

1. **Context budget death** — Naively combining three frameworks' instruction files consumes 25-30% of context before any work. Prevention: hard 1,000-token limit on CLAUDE.md; phase-specific rules load via skills on demand, never globally.

2. **Governance conflicts (outermost frame problem)** — Each framework expects to be the authority. Loading all three simultaneously produces contradictory instructions Claude resolves inconsistently. Prevention: route to exclusive owner per phase; test conflict resolution explicitly by loading one framework at a time.

3. **TDD bypass under integration pressure** — GSD subagents dispatched for implementation may not inherit superpowers' TDD mandate. Prevention: embed TDD mandate in each implementation subagent's dispatch instructions; add verification gate checking test-before-code via git history.

4. **Process without decision discipline** — The harness enforces workflow gates but not judgment calls between them. Claude follows the process but makes bad scope decisions mid-plan without flagging. Prevention: add explicit "stop and ask" triggers (scope expansion beyond N files, test failures in unrelated areas); mandatory decision checkpoints, not just process checkpoints.

5. **Role-based perspectives as performance theater** — When one LLM plays CEO, Architect, and QA, perspectives can be superficially different rather than genuinely adversarial. Prevention: structured checklists per role with required fields (not open-ended persona prompts); QA role must receive spec independently and check implementation against it, not generate tests from the implementation.

## Implications for Roadmap

Based on research, the build order should follow the dependency structure identified in ARCHITECTURE.md. Each layer is a prerequisite for the next; validation with a real project should happen after Layer 2 before committing to the role gate complexity of Layer 3.

### Phase 1: Foundation — Router + TDD Enforcement

**Rationale:** These three files make the harness functional with immediate value and zero risk to existing GSD workflows. No gate complexity, no persona absorption needed. Proves the routing concept on a real project before adding role gates.
**Delivers:** CLAUDE.md router (under 1,000 tokens), harness SKILL.md (lifecycle-to-owner mapping), tdd-enforcement.md rule (injected into GSD executor for implementation plans). Config.json extension with harness block.
**Addresses:** Table stakes — thin orchestrator, TDD Iron Law, zero-placeholder plans, scope drift detection (all via GSD + TDD rule injection).
**Avoids:** Context budget death (token budget enforced from day one), TDD bypass (mandate embedded in executor dispatch, not just global config).

### Phase 2: Verification and Debug Enhancement

**Rationale:** Improves the quality of GSD's existing verify and debug phases without changing its orchestration model. Low complexity, high ROI. Fills the specific gaps GSD has: no systematic debugging methodology, no explicit evidence-before-completion mandate, no code review step between execute and ship.
**Delivers:** verification-rules.md (injected into GSD verifier), systematic-debugging.md (replaces GSD debugger for implementation bugs), code-review.md (merged superpowers + gstack review, fills GSD's missing step).
**Addresses:** Table stakes — systematic debugging, verification before completion, code review gate.
**Avoids:** Process-without-decision-discipline (decision gates added to verification), TDD bypass detection (verification checks test quality and ordering).

### Phase 3: Role-Based Gates

**Rationale:** Adds gstack's perspective value at specific trigger points. Deferred to Phase 3 because (a) GSD's discuss-phase already provides strategic alignment, so marginal value needs validation from Phase 1-2 experience; (b) absorbing gstack personas requires careful prompt surgery to reference GSD artifacts instead of gstack's independent storage.
**Delivers:** eng-review.md (triggered at discuss-phase boundary), ceo-review.md (triggered at project init and major scope changes).
**Addresses:** Table stakes — CEO product challenge, Architect review with locking.
**Avoids:** Role performance theater (structured checklists per role with required output fields, not open-ended "think like a CEO" prompts); redundant strategic gates (CEO review augments discuss-phase at defined moments, never duplicates it).

### Phase 4: QA and Security Gates

**Rationale:** Most infrastructure-dependent (QA requires browser automation) and most valuable after the core development loop is solid. Milestone-level gates, not phase-level. Requires Phase 1-3 to be validated on a real project first.
**Delivers:** qa-gate.md (absorbed from gstack `/qa`, real browser testing), cso-audit.md (absorbed from gstack `/cso`, OWASP + STRIDE pre-ship gate).
**Addresses:** Table stakes — adversarial QA testing, security audit.
**Avoids:** QA as a phase-level gate (should only trigger at milestone boundaries or pre-ship, not after every execution phase — avoids ceremony bloat).

### Phase 5: Real-Project Validation

**Rationale:** Framework metadata is not a product. The harness must be validated on a non-trivial real project (500+ LOC scope, multiple phases, at least one bug requiring debugging) before being considered shippable. Research identifies specific failure modes that only surface under real conditions.
**Delivers:** Validated harness with any rough edges smoothed, documented gaps, and a real-world evidence base for distribution.
**Addresses:** Process-without-decision-discipline (only observable at real scope), role-performance-theater (only falsifiable with real review scenarios), upstream drift (baseline version stamps established).
**Avoids:** Shipping a framework that works in theory but produces governance conflicts under real project pressure.

### Phase Ordering Rationale

- Foundation before gates: routing must exist before anything routes through it; TDD injection must work before verification of TDD quality is meaningful.
- Verification before roles: role gates (CEO, Architect) produce artifacts that feed into planning and verification; the verification layer must exist to receive them.
- Role gates before QA/security: QA and security are the outermost quality rings; they depend on solid execution and verification beneath them.
- Real-project validation last: it tests the full stack end-to-end; doing it after Phase 4 ensures all components are integrated before stress-testing.
- This order also mirrors the dependency graph in FEATURES.md: context engine first, engineering discipline second, role perspectives third, execution excellence fourth.

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 4 (QA Gate):** Browser automation approach is deferred from v1 scope but its integration seam needs design. Research how MCP-based browser access compares to bundled Chromium for the qa-gate.md rule file.
- **Phase 3 (Role Gates):** Prompt surgery required to make gstack CEO/Eng personas reference GSD artifacts (PROJECT.md, CONTEXT.md) instead of gstack's `~/.gstack/` storage. May need to run `/gsd:research-phase` to examine gstack SKILL.md files in detail before writing.
- **Phase 5 (Validation):** Needs selection of a real project with appropriate complexity. Should not be synthetic.

Phases with standard patterns (skip research-phase):

- **Phase 1 (Foundation):** All components are directly derived from local GSD installation (HIGH confidence). File formats and injection mechanisms are fully documented. No research needed.
- **Phase 2 (Verification/Debug):** Superpowers' verification and debugging skills are well-documented. Adaptation to GSD's `<execution_context>` injection is a straightforward pattern.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | GSD analyzed from local install (v1.30.0). gstack and superpowers analyzed from GitHub repos. File formats, injection patterns, and config structure fully understood. |
| Features | HIGH | All three frameworks' capabilities mapped exhaustively. Table stakes, differentiators, and anti-features clearly distinguished. Feature dependencies graphed. |
| Architecture | HIGH | Route-not-stack pattern validated by unified-workflow PoC (prior art). Seven integration seams are specific and actionable. Build order derived from dependency analysis. |
| Pitfalls | HIGH | All critical pitfalls have multiple independent sources. Detection signals are specific. Four of five critical pitfalls are HIGH confidence; one (TDD bypass via GSD subagent dispatch) is MEDIUM due to extrapolation. |

**Overall confidence:** HIGH

### Gaps to Address

- **TDD bypass via GSD subagent dispatch** (MEDIUM confidence): The specific interaction between GSD's Task() dispatch and superpowers' TDD mandate has not been tested end-to-end. Handle during Phase 1 by explicitly embedding the TDD mandate in the dispatch prompt template and verifying with a test plan.
- **gstack persona prompt surgery** (MEDIUM confidence): The exact reformatting needed to make CEO/Eng personas reference GSD's artifact chain (PROJECT.md, CONTEXT.md) rather than gstack's `~/.gstack/` storage is known conceptually but untested. Handle during Phase 3 research.
- **Token budget measurement**: The 1,000-token CLAUDE.md limit is the right target, but actual token consumption of the harness skill files has not been measured. Measure during Phase 1 construction and adjust.
- **Browser automation for QA gate**: Deferred from v1 scope. Document in qa-gate.md how to activate real browser testing when the user has MCP or bundled Chromium available. Leave as a configuration toggle.

## Sources

### Primary (HIGH confidence)

- GSD local installation (`~/.claude/get-shit-done/`, version 1.30.0) — workflows, agents, templates, CLI patterns
- GSD agents (`~/.claude/agents/gsd-*.md`, 19 definitions) — subagent dispatch, context injection patterns
- Council review (`/Users/molchairuangutai/GitHub/harness/council/unified-harness-gsd-gstack-superpowers/shared_reasoning.md`) — multi-perspective analysis of integration strategy

### Secondary (MEDIUM confidence)

- [garrytan/gstack GitHub repo](https://github.com/garrytan/gstack) — 31 skills, role personas, sprint workflow
- [obra/superpowers GitHub repo](https://github.com/obra/superpowers) — 14 skills, TDD enforcement, subagent-driven-development
- [mattjaikaran/unified-workflow](https://github.com/mattjaikaran/unified-workflow) — GSD + superpowers integration PoC, documents anti-patterns
- [gsd-build/get-shit-done GitHub repo](https://github.com/gsd-build/get-shit-done) — matches local install, confirms patterns
- [Testing Agentic Development Systems: GSD v2](https://avishek.net/2026/03/24/testing-agentic-development-systems-gsd-v2.html) — real-world experience report with failure modes
- [Stop Bloating Your CLAUDE.md](https://alexop.dev/posts/stop-bloating-your-claude-md-progressive-disclosure-ai-coding-tools/) — context budget guidance
- [Context Rot in Claude Code Skills](https://www.mindstudio.ai/blog/context-rot-claude-code-skills-bloated-files) — skill file degradation mechanisms
- [Why Claude Loses Context After Compaction](https://docs.bswen.com/blog/2026-02-09-claude-context-loss-compaction/) — compaction information loss (~70-80%)

### Tertiary (LOW confidence / needs validation)

- [Claude Code ignoring directives issue #23032](https://github.com/anthropics/claude-code/issues/23032) — instruction conflict failures in practice
- [Superpowers v5.0 blog](https://blog.fsck.com/2026/03/09/superpowers-5/) — spec review subagent feature (new, limited real-world usage data)

---
*Research completed: 2026-04-04*
*Ready for roadmap: yes*
