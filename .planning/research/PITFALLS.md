# Domain Pitfalls: Claude Code Framework Integration

**Domain:** Unified Claude Code workflow combining GSD + gstack + superpowers
**Researched:** 2026-04-04

## Critical Pitfalls

Mistakes that cause rewrites, abandonment, or fundamental architecture changes.

---

### Pitfall 1: Context Budget Death by a Thousand Tokens

**What goes wrong:** Three frameworks each contribute CLAUDE.md instructions, skill files, and agent definitions. The combined token cost loads on every single inference call -- not just when relevant. A 500-token CLAUDE.md is fine; a 12,000-token unified CLAUDE.md means 12,000 tokens consumed before Claude even reads the user's prompt. At scale, this creates the "dumb zone" where extraneous context competes for attention during reasoning, and critical instructions get lost in the middle of the context window (the well-documented "lost in the middle" effect).

**Why it happens:** Each framework was designed to be the only framework. GSD's CLAUDE.md assumes it owns the full budget. Superpowers' skills assume they are the primary methodology. gstack's 23 specialists each assume they might be needed. Combining them naively produces additive token costs that none of the individual frameworks anticipated.

**Consequences:**
- Claude ignores specific instructions because they are buried in noise
- Performance degrades as sessions extend -- the model spends tokens processing irrelevant framework rules
- Auto-compaction triggers earlier, losing actual work context to make room for framework overhead
- At 200K context window with ~33K buffer, you lose 16.5% to infrastructure before starting; a bloated harness could push that to 25-30%

**Prevention:**
- Budget the harness at under 1,000 tokens in CLAUDE.md (the always-loaded layer)
- Use skills for phase-specific guidance that loads on demand, not globally
- Apply the "would removing this cause mistakes?" test to every line
- Measure actual token consumption of the harness during development

**Detection:**
- Claude ignores documented conventions or rules
- Output drifts toward generic patterns instead of project-specific ones
- Auto-compaction triggers unusually early in sessions
- Token consumption exceeds expectations for simple tasks

**Confidence:** HIGH -- multiple independent sources document this mechanism (alexop.dev progressive disclosure article, MindStudio context rot analysis, Anthropic best practices)

**Sources:**
- [Stop Bloating Your CLAUDE.md](https://alexop.dev/posts/stop-bloating-your-claude-md-progressive-disclosure-ai-coding-tools/)
- [Context Rot in Claude Code Skills](https://www.mindstudio.ai/blog/context-rot-claude-code-skills-bloated-files)
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)

---

### Pitfall 2: The Outermost Frame Problem -- Three Frameworks Each Expecting to Be the Authority

**What goes wrong:** GSD expects to be the orchestrator that dispatches work. Superpowers expects to be the methodology that governs how work is done. gstack expects its role-based specialists to own decision-making at each stage. When combined, no framework yields authority gracefully. The result: contradictory instructions at the same precedence level, which Claude resolves inconsistently.

**Why it happens:** Each framework was built as a complete, self-contained workflow. GSD has its own phase model (research -> plan -> implement -> verify). Superpowers has its own (brainstorm -> spec -> implement with TDD -> review). gstack has its own (CEO defines -> Architect plans -> Engineer implements -> QA validates). They overlap on the same decisions (when to plan, how to implement, what "done" means) but disagree on process.

**Consequences:**
- Claude receives "always use TDD" from superpowers and "implement per the plan" from GSD -- which wins when the plan doesn't mention TDD?
- "Autonomous" from one skill and "confirm everything" from another produces erratic behavior
- The agent resolves conflicts by following whichever instruction is closest to the current prompt, creating inconsistent workflow execution
- Real-world case: a user reported Claude Code broke production services by inconsistently following contradictory CLAUDE.md directives during extended sessions

**Prevention:**
- The council research already identified this: **route, don't stack**. Each phase has exactly one framework authority. GSD orchestrates phases; within an implementation phase, superpowers' TDD owns methodology; gstack roles inform but don't override the active authority
- Never have two frameworks active simultaneously -- the routing gate must be explicit and exclusive
- Test conflict resolution explicitly: temporarily load only one framework's rules to verify behavior, then add the next layer and check for drift

**Detection:**
- Claude asks permission for something one skill says to do autonomously
- Workflow steps repeat (double-planning, double-review)
- Claude provides different answers to the same process question in different sessions

**Confidence:** HIGH -- the unified-workflow repo documents this exact failure mode (double-planning, nested execution, plan location collisions), and Claude Code's own docs confirm skill conflict resolution is unreliable at the same precedence level

**Sources:**
- [mattjaikaran/unified-workflow](https://github.com/mattjaikaran/unified-workflow) -- documents anti-patterns from GSD + superpowers integration
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) -- skill precedence rules
- [Claude Code ignoring directives issue #23032](https://github.com/anthropics/claude-code/issues/23032)

---

### Pitfall 3: Process Discipline Without Decision Discipline

**What goes wrong:** The harness enforces workflow gates (phases, TDD, reviews) but does not enforce the judgment calls between gates -- when to stop and decompose, when to ask a question, when to revert. The agent follows the process but makes bad scope decisions within it.

**Why it happens:** GSD provides process discipline (phases, verification, state on disk). Superpowers provides methodology discipline (TDD, spec-first). gstack provides role discipline (CEO/Architect/Engineer perspectives). None of them provide decision discipline -- the meta-skill of knowing when the current approach is wrong and needs human intervention.

**Consequences:**
- The agent sees a five-layer plan, starts implementing Layer 2, hits an edge case, and makes a judgment call without consulting the user -- then compounds the error through subsequent layers
- A flawed design document becomes "load-bearing even when wrong" -- five compensatory patches get applied before the fundamental error is recognized
- Scope cascades: what seems like a localized five-line change touches forty files across every architectural layer, but the agent doesn't flag this

**Prevention:**
- Add explicit "stop and ask" triggers to the harness: scope expansion beyond N files, test failures in unrelated areas, design assumptions contradicted by implementation reality
- Build in mandatory checkpoints that are not just process gates but decision gates -- "Is the current approach still correct?" not just "Did you follow TDD?"
- Superpowers' structured brainstorming (one question at a time with multiple-choice options) is specifically good at forcing genuine discussion rather than rapid implementation -- adopt this pattern at decision points

**Detection:**
- Agent produces patches-on-patches rather than questioning the design
- Agent makes assumptions about scope without asking
- Retroactive issue filing (work happened without pre-filed issues, indicating the agent jumped ahead)

**Confidence:** HIGH -- directly observed and documented in Avishek's experience report testing GSD v2 on a large refactoring, where switching to superpowers' structured brainstorming resolved the issue

**Sources:**
- [Testing Agentic Development Systems: GSD v2](https://avishek.net/2026/03/24/testing-agentic-development-systems-gsd-v2.html)
- [Superpowers blog post](https://blog.fsck.com/2025/10/09/superpowers/)

---

### Pitfall 4: TDD Enforcement Bypass Under Integration Pressure

**What goes wrong:** Superpowers enforces TDD by literally deleting code written before tests exist. This works when superpowers is the sole authority. But in a unified harness, the GSD orchestrator or a gstack role may dispatch implementation work with its own expectations, creating a seam where TDD enforcement gets weakened or bypassed entirely.

**Why it happens:** Superpowers explicitly allows a bypass: "If CLAUDE.md says 'don't use TDD,' follow the user's instructions." And subagents dispatched to execute specific tasks "skip the protocol as they are already executing within a structured workflow." In a unified harness, GSD's subagent-driven execution model dispatches workers that may not inherit superpowers' TDD mandate. The harness becomes a legitimate-seeming authority that inadvertently weakens the very discipline it is supposed to enforce.

**Consequences:**
- Implementation subagents produce code without tests, believing they are operating under the parent's workflow authority
- Weak test assertions mask bugs -- nine of fifteen integration tests in one real-world case used imprecise assertions like `assert "add" in result` instead of concrete value checks
- The "green" in RED-GREEN-REFACTOR becomes meaningless if tests are written to pass rather than to specify behavior

**Prevention:**
- TDD enforcement must be embedded in the implementation skill itself, not just in a global CLAUDE.md that subagents may not load
- Every subagent dispatched for implementation must receive the TDD mandate in its dispatch instructions, not rely on inheriting it from context
- Add a verification gate: after implementation, a separate agent checks that tests exist, are meaningful (not just `assert True`), and were written before the implementation code (check git history or timestamps)

**Detection:**
- Test files are committed in the same commit as implementation (may indicate tests written after)
- Tests use string containment or truthiness assertions instead of exact value checks
- Test count is suspiciously low relative to implementation complexity

**Confidence:** MEDIUM -- superpowers' bypass mechanism is documented, and the weak-assertion problem is documented in the agentic workflow experience report, but the specific interaction with GSD subagents is extrapolated

**Sources:**
- [Superpowers SKILL.md](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md) -- documents escape hatches
- [Testing Agentic Development Systems](https://avishek.net/2026/03/24/testing-agentic-development-systems-gsd-v2.html) -- weak assertion patterns

---

## Moderate Pitfalls

---

### Pitfall 5: Compaction Destroys Harness State

**What goes wrong:** When Claude's context window fills and auto-compaction triggers, the summarization process strips away design rationale, architectural decisions, and workflow state. Roughly 20-30% of original detail survives. The first task after compaction works fine, but references to earlier decisions fail silently.

**Prevention:**
- Critical harness state must live in files on disk (GSD's `.planning/` approach is correct here), not in conversation context
- Phase transitions should write state to disk before the context that motivated them is lost
- Aim to complete phase-scoped work within a single context window; use subagents to isolate verbose work
- Put constraints in CLAUDE.md (persists across compaction) rather than relying on conversation memory

**Detection:**
- Claude suggests code that contradicts earlier architectural decisions
- Claude asks about files it recently created
- Different implementation patterns appear within the same codebase after compaction

**Confidence:** HIGH -- multiple sources document the ~70-80% information loss during compaction

**Sources:**
- [Why Claude Loses Context After Compaction](https://docs.bswen.com/blog/2026-02-09-claude-context-loss-compaction/)
- [Context Buffer Management](https://claudefa.st/blog/guide/mechanics/context-buffer-management)

---

### Pitfall 6: Double-Planning and Artifact Collision

**What goes wrong:** GSD stores plans in `.planning/phases/`. Superpowers stores plans in `docs/plans/`. Both capture design decisions. With both active, the system produces two sets of planning artifacts that drift out of sync, destroying the single source of truth.

**Prevention:**
- The harness must own the artifact layout. One location for plans, one for specs, one for requirements. The unified-workflow's routing approach (check for `.planning/` existence) is the right pattern but needs to be enforced at the harness level, not left to individual skill files
- GSD's `.planning/` directory is the canonical location. Any superpowers-derived planning that produces artifacts must write to GSD's locations, not its own defaults

**Detection:**
- Plan files exist in multiple directories
- Decisions documented in one location contradict those in another
- Claude references a plan from the "wrong" framework's artifact location

**Confidence:** HIGH -- the unified-workflow repo explicitly documents plan location collision as a known anti-pattern

**Sources:**
- [mattjaikaran/unified-workflow](https://github.com/mattjaikaran/unified-workflow)

---

### Pitfall 7: Upstream Drift and Maintenance Burden

**What goes wrong:** GSD, gstack, and superpowers are all actively maintained by different authors with different priorities. Tracking changes across three repos, evaluating which updates matter, and integrating them into the harness becomes an ongoing tax. gstack is single-author personal tooling from Garry Tan; superpowers is obra's methodology; GSD targets multiple runtimes. None coordinate releases.

**Prevention:**
- Copy-and-own is the correct decision (already in PROJECT.md). Absorb the patterns, not the repos
- Version-stamp what was absorbed: "Derived from superpowers commit abc123, gstack v1.2, GSD v2.x"
- Establish a quarterly review cadence to check upstream for significant changes, not continuous tracking
- Design the harness so absorbed patterns are isolated -- replacing the TDD enforcement approach should not require rewriting the orchestrator

**Detection:**
- Upstream framework releases a feature that would improve the harness but integration is non-trivial
- Harness behavior diverges from documented upstream behavior, confusing users who know the source frameworks

**Confidence:** MEDIUM -- the copy-and-own decision mitigates this, but the maintenance review cadence is a discipline problem not a technical one

**Sources:**
- [Claude Code Plugin Dependencies issue #9444](https://github.com/anthropics/claude-code/issues/9444)
- [Avoid Dependency Hell for Claude Skills](https://medium.com/@michaelyuan_88928/avoid-dependency-hell-for-claude-skills-62658982ebb4)

---

### Pitfall 8: Role-Based Perspectives Becoming Performance Theater

**What goes wrong:** gstack's CEO/Architect/Engineer/QA roles are designed to provide different perspectives on the same work. But when the same LLM plays all roles, the "perspectives" can become superficially different rather than genuinely adversarial. The CEO role rubber-stamps what the Engineer role already decided. The QA role writes tests that confirm the implementation rather than challenging it.

**Prevention:**
- Roles need specific, concrete mandates -- not just persona descriptions. The CEO gate must have a checklist: "Does this solve a user problem? What is out of scope? What are the success metrics?" Not just "think like a CEO"
- Use structured outputs (checklists, required fields) rather than open-ended "review as [role]" prompts
- The QA role specifically should receive the spec/acceptance criteria independently and check the implementation against them, not review the implementation and generate tests from it

**Detection:**
- All role reviews produce positive assessments with minor suggestions
- QA tests mirror implementation structure rather than spec requirements
- CEO/product review never rejects or significantly reshapes a feature

**Confidence:** MEDIUM -- this is a known limitation of single-model role-playing (observed in council-style patterns), but gstack users report genuine value from the structure when prompts are specific enough

---

## Minor Pitfalls

---

### Pitfall 9: Subagent Context Isolation Surprise

**What goes wrong:** Subagents do not inherit the lead agent's conversation history. This is by design (each gets its own 200K window), but framework integrators often assume shared context. A subagent dispatched to implement a feature does not know about the architectural discussion that happened in the orchestrator's context.

**Prevention:**
- Every subagent dispatch must include explicit context: what to build, what constraints apply, what patterns to follow
- Never assume a subagent "knows" something discussed in the parent context
- Use file-based state (`.planning/` artifacts) as the shared context medium, not conversation history

**Detection:**
- Subagent produces code that contradicts patterns established in the parent session
- Subagent re-asks questions that were already resolved

**Confidence:** HIGH -- documented in Claude Code subagent docs and multiple community reports

**Sources:**
- [Context Management with Subagents](https://www.richsnapp.com/article/2025/10-05-context-management-with-subagents-in-claude-code)
- [Claude Code Sub-agents Guide](https://www.codewithseb.com/blog/claude-code-sub-agents-multi-agent-systems-guide)

---

### Pitfall 10: Accumulation Without Pruning (Context Rot)

**What goes wrong:** Every mistake Claude makes gets a new rule in CLAUDE.md. The file grows monotonically. Old workarounds for bugs that were fixed upstream remain. The harness becomes a sedimentary record of every past problem rather than a lean set of current constraints.

**Prevention:**
- Schedule periodic audits (monthly) of all harness files
- Mark rules with dates and reasons; remove rules whose reasons no longer apply
- Apply the "would removing this cause mistakes today?" test ruthlessly
- Separate permanent principles from temporary workarounds

**Detection:**
- CLAUDE.md or skill files only grow, never shrink
- Rules reference problems or patterns that no longer exist in the codebase
- New team members cannot explain what half the rules are for

**Confidence:** HIGH -- universally documented across all Claude Code best-practices sources

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Framework analysis (deep dive into GSD/gstack/superpowers) | Absorbing too much from each framework, creating bloat | Define a token budget per framework contribution before starting |
| Architecture design (route-not-stack) | Routing gates that are too coarse (whole phases) or too fine (every prompt) | Design 3-5 routing states maximum; test with real workflows |
| CLAUDE.md authoring | Context budget death (#1) and accumulation rot (#10) | Set a hard 1,000-token limit; use skills for everything else |
| TDD integration | Bypass via subagent dispatch (#4) | Embed TDD mandate in dispatch instructions, not just global config |
| Role integration (gstack perspectives) | Performance theater (#8) | Structured checklists per role, not open-ended persona prompts |
| Artifact layout unification | Double-planning (#6) | Decide canonical locations in Phase 1, enforce in skill files |
| Real-project validation | Process without decision discipline (#3) | Add explicit "stop and ask" triggers; test with a non-trivial feature |
| Global installation / distribution | Upstream drift (#7) | Version-stamp absorbed patterns; quarterly review cadence |

---

## Sources

- [mattjaikaran/unified-workflow](https://github.com/mattjaikaran/unified-workflow) -- prior art combining GSD + superpowers, documents anti-patterns
- [Stop Bloating Your CLAUDE.md](https://alexop.dev/posts/stop-bloating-your-claude-md-progressive-disclosure-ai-coding-tools/) -- progressive disclosure pattern
- [Context Rot in Claude Code Skills](https://www.mindstudio.ai/blog/context-rot-claude-code-skills-bloated-files) -- degradation mechanisms
- [Why Claude Loses Context After Compaction](https://docs.bswen.com/blog/2026-02-09-claude-context-loss-compaction/) -- compaction information loss
- [Testing Agentic Development Systems: GSD v2](https://avishek.net/2026/03/24/testing-agentic-development-systems-gsd-v2.html) -- real-world experience report
- [Superpowers](https://github.com/obra/superpowers) -- TDD enforcement and escape hatches
- [gstack](https://github.com/garrytan/gstack) -- role-based specialist approach
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) -- skill precedence and conflict resolution
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) -- official guidance on CLAUDE.md sizing
- [Claude Code ignoring directives #23032](https://github.com/anthropics/claude-code/issues/23032) -- real-world instruction conflict failures
