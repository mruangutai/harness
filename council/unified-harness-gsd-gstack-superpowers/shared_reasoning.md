# Council Review

**Date:** 2026-04-04
**Idea:** Create a unified harness that combines GSD (Get Shit Done), gstack, and superpowers GitHub workflows into one cohesive workflow. GSD provides project management that breaks work into digestible units. gstack constrains roles allowing role-specific strengths (CEO to QA engineer). superpowers provides technical process constraints as a lead engineer using best practices. The unified harness would enable validating a software idea from CEO-level vision down to QA testing, using best architecture and coding practices, with a project workflow that doesn't bloat LLM context and enables Claude to execute reliably without hallucination.
**Council:** optimist-council-member, pessimist-council-member, realist-council-member

---

## Optimist Council Member

### Reasoning

**What each system actually does, and where each stops short.**

GSD (Get Shit Done) is a meta-prompting, context engineering, and spec-driven development system built on a thin orchestrator pattern. Its core architectural insight is that orchestrators should maintain 10-15% context usage by passing file paths rather than content, while subagents receive full 200k token budgets for deep work. The result: an entire phase — research, planning, parallel code execution, verification — runs in fresh subagent contexts while the main session stays responsive. GSD's structured artifacts (PROJECT.md, ROADMAP.md, STATE.md, PLAN.md) create a shared external memory that survives context resets. What GSD does not provide is role-specific perspective constraints — it knows *how* to build but does not enforce *who* is evaluating or *what criteria* govern each phase. It is a scaffolding engine without opinionated gatekeeping.

Gstack (Garry Tan's setup) is a role-based constraint system with 23 slash commands that transform Claude into a virtual engineering organization: CEO reviews market fit, Eng Manager locks architecture, Designer audits visual quality, Security Officer runs OWASP/STRIDE, QA opens a real Chromium browser. Its key value is precisely what GSD lacks — opinionated *perspective enforcement* at each lifecycle stage. The CEO review checks user value before implementation begins; the engineering review gates on architecture; QA validates via real browser interaction. The result: Garry Tan's team shipped 600,000 lines of production code in two months of 2026 using this approach. Gstack's limitation is that it provides role gates without a project memory backbone — it does not track phase state, manage context across sessions, or break work into dependency-ordered waves.

Superpowers (Jesse Vincent / obra) is a composable skills framework enforcing rigid Brainstorm → Spec → Plan → TDD → Subagent Execution → Review → Finalize phases. Its distinguishing mechanism is context isolation as a first principle: subagents receive only precisely crafted context they need, never inheriting the parent session's history. It enforces true RED-GREEN-REFACTOR TDD and uses psychological persuasion principles to prevent agents from rationalizing shortcuts (explicit "Red Flags" sections listing the exact rationalizations agents use to skip steps, with prewritten reality-check responses). Superpowers grew to 121,000+ GitHub stars in months, which is itself evidence of a market that was underserved. Its limitation: it enforces *how to build correctly* but does not provide multi-phase project memory or organizational role-based review gates.

**The core value kernel: each system solves one leg of the same three-legged problem.**

The unified harness idea is based on a structurally sound observation about the problem space. Context bloat and hallucination in LLM-driven development arise from three distinct failure modes: (1) the agent loses project-level continuity across long sessions — GSD's domain; (2) the agent evaluates work from a single undifferentiated perspective without role-specific constraints — gstack's domain; (3) the agent rationalizes skipping engineering discipline (tests, specs, planning) in favor of premature implementation — Superpowers' domain. No single system addresses all three. GSD has no CEO review. Gstack has no context isolation architecture. Superpowers has no multi-session project memory. A harness that integrates all three addresses each failure mode at the layer most suited to it, which is the definition of composable design.

**Plausible integration vectors and the mechanisms that make them non-trivial.**

The most important integration point is the *handoff protocol*: GSD's phase structure naturally maps to gstack's role-gate sequence. A GSD phase transition (plan-phase complete → execute-phase begins) can trigger gstack's /plan-eng-review before execution begins, and /plan-ceo-review before scope is locked. The ROADMAP.md and PROJECT.md artifacts that GSD maintains give gstack's CEO persona the persistent context it needs to evaluate market fit with continuity across sessions — something gstack alone lacks because it has no project memory backbone. This is not a forced combination; it is filling a gap each system already has. The second integration vector is at the execution layer: when GSD's gsd-executor subagent is spawned, Superpowers' TDD constraint and context isolation principle can be injected directly into that subagent's system prompt, ensuring that every plan execution follows RED-GREEN-REFACTOR and that the subagent receives only the files relevant to its plan — not the full session history. GSD already passes file paths rather than content to subagents; Superpowers' isolation principle reinforces the same mechanism from a different angle. The third vector is verification: GSD's gsd-verifier agent and gsd-nyquist-auditor can be extended to include gstack's /qa and /review criteria as verification gates, creating a single artifact (VERIFICATION.md) that tracks both GSD's stub-detection checks and gstack's browser-validated QA results.

**Historical analogies and compounding dynamics.**

The closest analogy is the emergence of CI/CD pipelines: Jenkins, GitHub Actions, and similar tools did not invent linting, testing, or deployment — they integrated pre-existing tools into a sequenced, gated pipeline where each stage's output became the next stage's input. The individual tools (eslint, jest, docker) predated CI/CD. The value was not in the tools themselves but in the enforced sequencing and shared artifact passing. The unified harness proposed here is precisely this: a CI/CD-style pipeline for LLM-driven development where GSD provides the pipeline engine, gstack provides the review gates, and Superpowers provides the engineering process constraints enforced within each stage. The parallel is strong because CI/CD adoption followed a similar trajectory — early adopters built bespoke integrations, then a consolidating abstraction emerged that made the integrated workflow the default. The open-source momentum is already present: GSD at 32,000 stars, gstack at 39,000 stars in 11 days, Superpowers at 121,000+ stars. The user base that has adopted all three independently is the natural early adopter population for a harness that unifies them. Importantly, GSD v2 is already a TypeScript application (not just a prompt framework) with runtime-level control over context, cost tracking, and git integration — giving the unified harness a programmatic integration surface that would not have existed 12 months ago.

**Key uncertainties worth flagging before the conclusion.**

The main uncertainty is integration friction at the *seam points* — specifically, whether gstack's role-gate timing (designed for interactive use) can be made non-blocking in GSD's autonomous wave execution. If the harness requires human confirmation at every gstack role gate, it degrades GSD's autonomous execution model. This is solvable (gstack gates can be configured as advisory-only for autonomous runs and mandatory for interactive runs), but it requires explicit design. The second uncertainty is Superpowers' TDD enforcement in GSD's executor subagent: if the executor's prompt is already large, adding Superpowers' RED-GREEN-REFACTOR constraint overhead may push subagent prompts toward their effective limits. This can be mitigated by loading TDD constraints selectively (only for implementation plans, not for research or documentation plans), but the harness must be built with this selectivity in mind from the start.

### Conclusion

The best realistic trajectory for this unified harness is that it becomes the canonical workflow for seed-stage and early-growth engineering teams using Claude Code to build at high velocity without accumulating technical debt. The enabling conditions are: (1) GSD's phase transitions are wired as trigger points for gstack role reviews, making gstack gates part of the GSD workflow rather than a parallel system; (2) Superpowers' TDD and context isolation principles are injected selectively into GSD executor subagents based on plan type (implementation vs. research vs. documentation); (3) a shared artifact schema — extending GSD's existing PROJECT.md / ROADMAP.md / PLAN.md structure — carries gstack's CEO and Eng review decisions forward as context that subsequent phases can reference without re-litigating scope. Given that all three projects have already demonstrated strong independent adoption, and given that the problem of fragmented workflows is clearly felt (evidenced by the mattjaikaran/unified-workflow project already attempting a GSD-Superpowers bridge), the demand is real and the integration surface is technically tractable. The council should treat this not as an experimental combination but as a logical consolidation of three complementary systems into a workflow that is more than the sum of its parts, specifically because each system's weakness is another system's strength.

---

## Pessimist Council Member

### Reasoning

**The integration surface is real, but the primary assumption that needs auditing is whether "complementary gaps" actually compose cleanly — or whether they just add overhead at every seam.**

The optimist framing treats GSD, gstack, and Superpowers as three puzzle pieces that slot together: GSD provides the scaffolding engine, gstack provides perspective gates, Superpowers provides TDD enforcement. This is structurally elegant, but it papers over a critical operational problem: each system was designed to be the outermost frame, not a component inside something else. GSD's executor agent (gsd-executor.md, ~21KB) already reads a CLAUDE.md, loads skills, checks `.claude/skills/`, and follows project-specific conventions as hard constraints — before any plan execution begins. Superpowers is itself a collection of mandatory skills meant to govern that same executor context. gstack's role commands (/plan-ceo-review, /plan-eng-review) are also slash commands, not subroutines — they're designed to be invoked interactively by a human, not wired as automatic gates inside GSD's wave execution. The integration is not impossible, but it requires rebuilding the entry-point logic for each framework so that none of them is the authority — a meta-harness now owns that role. That meta-harness is an entirely new system, not an "integration" of three existing ones.

**The context overhead problem is concrete, not theoretical, and it points to a specific failure mode that is the opposite of what the unified harness promises.**

GSD's architecture is explicitly designed around keeping the orchestrator's context lean while spawning fresh subagents with full 200k budgets. The workflow files alone total ~620KB across 50+ files, with the largest (discuss-phase.md: 43KB, new-project.md: 39KB, execute-phase.md: 35KB) loaded in full at command invocation. The agent definitions add another ~375KB across 19 files. Now add gstack: 23+ slash commands, each a substantial markdown skill file, plus the role-specific instruction sets for CEO/Eng/QA reviewers. Now add Superpowers: 10+ skills covering brainstorm, plan, TDD cycle, code review, parallel agents, git worktrees, branch completion — each with mandatory-compliance framing and anti-rationalization "Red Flags" sections. The harness's central promise is "doesn't bloat LLM context" — but the unified system's cold-start load will be substantially larger than any individual framework, not smaller. The subagent context problem is worse: a GSD executor subagent that also carries Superpowers TDD constraints and gstack review criteria will receive a far larger prompt than either system generates independently. The optimist correctly flags this risk; the question is whether it is "solvable with selective loading" or whether selective loading requires a configuration system of sufficient complexity that it becomes its own failure source.

**The governance and maintenance risk is the crux — not the technical integration, but the social one.**

GSD is actively maintained and fast-moving (the README warns explicitly: "GSD evolves fast. Update periodically."). gstack is Garry Tan's personal tooling, open-sourced with 39,000 stars in 11 days — a signal of intense demand, but also a project whose long-term maintenance depends on a single VC's continued personal interest. Superpowers (obra/Jesse Vincent) is similarly personal, with a growing star count but minimal explicit maintenance documentation. Three independently-authored systems that each define the workflow — and the unified harness sits on top of all three. Any breaking change in GSD's tooling contract (gsd-tools.cjs init API, agent JSON schema), any gstack command rename, or any Superpowers skill restructuring propagates as a harness breakage. The unified harness's maintenance burden is not additive; it is multiplicative, because a change in any one system requires testing against the combined integration surface. Research on multi-tool AI stacks explicitly names this problem: "tool proliferation without integration creates command conflicts, contradictory process guidance, and AI confusion about which framework's rules to follow." A seed-stage CTO who builds this harness is also implicitly committing to tracking three external release cadences — in addition to building the actual product.

**The "decision authority" conflict is not fully addressed by the optimist and deserves explicit treatment.**

gstack's CEO review (/plan-ceo-review) is designed to evaluate market fit and scope before implementation begins. GSD's discuss-phase step already includes adaptive questioning, grey-area resolution, and user approval of scope. Superpowers' brainstorming phase also front-loads clarifying questions and design agreement. In the unified harness, all three systems want to own the "strategic alignment" gate. In practice, what happens is not clean composition — the user gets three rounds of strategic questioning at different abstraction levels, with no shared state between them unless the harness explicitly shuttles PROJECT.md content into gstack's CEO context. The optimist notes this can be solved by using GSD's artifacts as the input to gstack reviews — that's correct as a design decision, but it means the harness must define explicit artifact-passing contracts at every seam, and those contracts must be maintained as all three systems evolve independently. More practically: for a solo founder or small team, three sequential strategic reviews per phase is not rigorous process discipline — it is friction that will cause the developer to bypass one or more framework layers after the second or third time it feels redundant. There is strong empirical evidence for this: Superpowers itself uses explicit psychological anti-rationalization prompts because skipping steps under time pressure is the modal failure mode for AI-assisted workflows.

### Conclusion

The idea can work, but the conditions for success are harder than the framing suggests, and the failure mode is specific: the unified harness becomes a high-maintenance meta-framework that the builder abandons under time pressure, reverting to whichever single tool they find most intuitive — likely GSD, since it already has the most complete architecture.

**Key failure modes:**

1. **Cold-start context bloat** — The combined skill/workflow load undermines the very context discipline each system independently tries to enforce. The harness must implement selective loading from day one, or it defeats its own premise.

2. **Dual-authority conflicts** — Three frameworks each designed to own the "what gets built and how" decision create ambiguity about which system's output is authoritative when they diverge. Without an explicit conflict-resolution protocol, the developer resolves conflicts manually every time — which is exactly the overhead the harness was meant to eliminate.

3. **Maintenance multiplication** — Tracking three independently-evolving external systems while building a product is a second job. gstack in particular has uncertain long-term maintenance trajectory (single-author personal tooling, viral launch, no organizational backing).

4. **Bypass pressure** — The more complete the workflow structure, the more pressure a time-constrained operator feels to skip phases. Three frameworks layered together means three sets of gates to rationalize skipping. Superpowers explicitly guards against this with anti-rationalization prompts — but those guards are written for Superpowers in isolation, not for a harness where two other frameworks have already asked similar questions.

**Conditions required for success:** The builder must treat this as a new software project with an explicit architecture (not just three config files layered together), define ownership boundaries for each workflow phase in a machine-readable format, implement selective context loading for subagents, and accept ongoing maintenance overhead as a product cost. If the target is personal use, this is achievable but requires substantially more upfront design work than the framing implies. If the target is something distributable — a harness others can adopt — the surface area is much larger and the maintenance burden grows with every upstream change in any of the three component systems.

**Council recommendation:** Pursue a staged integration rather than a unified harness from the start. The GSD + Superpowers pairing (TDD discipline injected into GSD's executor subagents) is the tightest integration with the fewest authority conflicts and the least new glue code. Validate that combination first, measure where gstack's role-based reviews add concrete value over GSD's existing discuss-phase questioning, and only add gstack gates at the specific phase transition points where the gap is demonstrably felt. This produces a harness that earns its complexity rather than assuming it.

---

## Realist Council Member

### Reasoning

**Adjudicating the core dispute: the pessimist wins on mechanism, the optimist wins on demand.**

The optimist's central claim — that GSD, gstack, and Superpowers each solve one leg of a three-legged problem — is structurally sound and I accept it. The failure modes they address (context drift, single-perspective evaluation, undisciplined implementation) are genuinely distinct, and the evidence that each system independently achieved strong adoption validates that each gap is real and felt. However, the optimist's integration narrative overstates the engineering work implied by "composable design." The pessimist is correct that each system was built to be the outermost authority — gstack's role commands are interactive slash commands, GSD's executor already governs plan execution from the inside, and Superpowers' mandatory-compliance framing assumes it controls the agent context. Wiring three authority-claiming systems together does not produce composition; it produces a governance conflict that the meta-harness must actively resolve. The optimist treats the seam-point problem as "solvable with explicit design" without reckoning with the fact that this design is non-trivial and must be maintained as three upstream systems evolve independently.

The pessimist's strongest contribution is the decision-authority analysis: GSD's discuss-phase, gstack's /plan-ceo-review, and Superpowers' brainstorming phase all front-load strategic alignment questions. In the unified harness, without explicit artifact-passing contracts, a user running all three will experience redundant strategic interrogation before a single line of code is written. This is not a theoretical concern — Superpowers itself encodes the empirical observation that skipping steps is the modal failure mode under time pressure, and layering three gate systems multiplies the pressure to bypass. The pessimist slightly overreaches on the context overhead framing: GSD's selective loading model is a genuine architectural answer to this problem, and a well-built harness that passes file paths rather than file contents can keep individual subagent context loads within acceptable limits. The problem is real but it is an implementation constraint, not an architectural ceiling.

**The dimension both agents underweight: the mattjaikaran unified-workflow already exists and its design choices are instructive evidence.**

Neither agent adequately reckons with the fact that the GSD + Superpowers bridge has already been built by a third party (mattjaikaran/unified-workflow). Its design is telling: it routes between the two systems rather than nesting them — "GSD executors OR SP subagent-driven-dev. Never nested." This routing-not-nesting approach is the critical insight. It avoids the authority conflict by establishing explicit phase-ownership boundaries: GSD owns the what and when, Superpowers owns the implementation loop. The harness does not make the systems peers inside a shared context; it makes them exclusive executors per task type. This is a meaningful constraint on the unified harness concept — it implies the right architecture is a router with clear ownership handoffs, not a pipeline where all three systems' rules are simultaneously active. The optimist's CI/CD analogy is apt in one direction (each system's output becomes the next's input) but breaks down if interpreted to mean all three systems' constraints are stacked on every agent invocation. What the search evidence also surfaces: gstack now has 28 commands (not 23 as cited by both agents), including an /autoplan command that collapses the sequential CEO + Eng review into a single invocation — suggesting even Garry Tan has already identified the redundant-gate problem the pessimist flags and partially solved it upstream.

**Load-bearing variables that determine success or failure.**

The single most important variable is whether the harness establishes exclusive ownership per phase or attempts shared authority. A router that assigns GSD to project management, gstack personas to review gates, and Superpowers to implementation discipline — with clean handoffs and no simultaneous rule activation — is achievable by one person in a week and has a working partial proof-of-concept to build from. A harness that stacks all three systems' instructions on every agent invocation will fail at cold-start context load before the first task executes. The second variable is gstack's maintenance trajectory: Garry Tan has 45 open PRs and an active community (the project has grown to 28 commands), which partially addresses the single-author risk. The strategic mitigation is to treat gstack as a source of role personas and prompt patterns to absorb into the harness's own artifacts, not as a live dependency to wire against. Copy the CEO/Eng/QA review prompts into harness-owned files; don't import from a live external repo that can break the harness on any upstream rename.

### Trade-off Map

| Gain | Sacrifice |
|------|-----------|
| Role-specific perspective gates (CEO, Eng, QA) that GSD alone lacks | Ongoing maintenance overhead tracking three external release cadences |
| Context isolation discipline (Superpowers TDD) applied inside GSD executor subagents | Increased cold-start context load if selective loading is not implemented from day one |
| Persistent project memory (GSD artifacts) feeding gstack role reviews across sessions | Design and maintenance cost of explicit artifact-passing contracts at every framework seam |
| Full lifecycle coverage from vision validation to QA browser testing | Multiplied bypass pressure — three gate systems means three times the rationalization friction under time pressure |
| Community-validated proof of concept (mattjaikaran unified-workflow) to build from | Authority conflict at every phase boundary unless routing-not-nesting architecture is enforced |
| Absorbing gstack role personas into harness-owned prompts decouples from upstream breakage | Loss of upstream gstack improvements if harness forks the prompts rather than importing them live |

### Uncertainty Register

| Type | Unknown | Resolution / Why irreducible |
|------|---------|------------------------------|
| don't know | Whether routing-not-nesting eliminates the authority conflict in practice | Build the mattjaikaran approach first and run 3-5 full project cycles; the conflict either surfaces or doesn't |
| don't know | Whether selective context loading keeps combined prompt size within effective limits when Superpowers TDD is injected into GSD executor subagents | Measure empirically: run one GSD executor with Superpowers constraints injected and log actual token usage |
| don't know | How much concrete value gstack's /plan-ceo-review adds over GSD's discuss-phase for a solo CTO | Run a parallel project — one with gstack CEO review, one without — and assess which caught real scope errors the other missed |
| can't know | Whether gstack will remain actively maintained as Garry Tan's priorities shift | structurally irreducible because: single-author personal tooling; maintenance depends on one person's discretionary time and is not contractually bound |
| can't know | Whether the unified harness produces measurably better software outcomes than GSD alone | structurally irreducible because: outcome quality in LLM-assisted development depends on problem type, team skill, and prompt hygiene in ways that cannot be cleanly isolated in a controlled comparison |

### Conclusion

The most likely outcome is a staged, partial integration that converges on the routing-not-nesting architecture: GSD as the project backbone, gstack's role-review personas absorbed as harness-owned prompt artifacts rather than live dependencies, and Superpowers' TDD discipline injected selectively into GSD executor subagents for implementation-type plans. This is achievable, has an existing proof-of-concept to build from, and avoids the maintenance multiplication risk the pessimist correctly identifies. The full three-system simultaneous authority model — which the optimist implies but does not fully specify — is unlikely to survive contact with real usage because bypass pressure will cause one or two layers to be dropped under time pressure, and the pessimist's failure mode prediction (reverting to GSD alone) is the probabilistically correct endpoint for the undifferentiated version.

The key variable is architecture choice: routing vs. stacking. A harness that routes to the right tool per phase has a high probability of succeeding for personal use by a technical CTO, and a plausible path to a distributable tool if the artifact-passing contracts are documented. A harness that stacks all three systems' constraints simultaneously will fail at context load before it proves value. Build the router. Treat gstack role personas as prompts to copy-and-own, not live external dependencies. Validate GSD + Superpowers TDD injection across three real build cycles before adding gstack review gates. Add individual gstack gates only at the specific phase transitions where GSD's discuss-phase demonstrably misses scope decisions — measure the gap before filling it.

---

## Synthesis

**Situation (neutral framing):** Three independently successful Claude Code workflow systems — GSD (project management/context engineering, 32K stars), gstack (role-based perspective gates, 39K stars), and Superpowers (TDD/engineering discipline, 121K stars) — each solve a distinct failure mode in LLM-assisted development. The proposal is to combine them into a unified harness that covers the full software lifecycle from CEO-level idea validation to QA testing, with context discipline that prevents hallucination. A partial proof-of-concept (mattjaikaran/unified-workflow) already exists.

**Key facts:**
- Each system was designed to be the outermost authority, not a composable module
- GSD's thin-orchestrator pattern (10-15% context, file-path-not-content passing) is the only one architecturally designed for context management at scale
- The mattjaikaran/unified-workflow project already made the critical design decision: routing-not-nesting ("GSD executors OR SP subagent-driven-dev. Never nested.")
- gstack now has 28 commands including /autoplan, which collapses redundant sequential reviews — Garry Tan already identified the gate-redundancy problem
- Superpowers embeds anti-rationalization prompts because skipping steps under time pressure is the empirically observed modal failure mode
- GSD v2 is a TypeScript application with programmatic runtime control, providing a real integration surface
- Combined cold-start context load of all three systems exceeds any individual system's load significantly (~1MB+ of instruction files)

**Trade-off analysis:**

| Gain | Sacrifice |
|------|-----------|
| Full lifecycle coverage: vision validation → architecture → TDD implementation → QA | Maintenance burden tracking three independently evolving external systems |
| Role-specific perspective enforcement that GSD alone lacks | Increased bypass pressure — three gate layers means triple the rationalization friction |
| Context isolation + project memory + engineering discipline in one workflow | Upfront architecture work to define routing boundaries and artifact-passing contracts |
| Existing proof-of-concept to build from (mattjaikaran/unified-workflow) | Forking gstack prompts into harness-owned files means losing upstream improvements |
| Persistent project memory feeding role reviews across sessions | Selective loading system required from day one or context bloat defeats the premise |

**Feasibility assessment:** Highly feasible for a technical CTO as a personal tool using the staged approach. GSD as backbone + Superpowers TDD injection into executor subagents is achievable in roughly a week, with an existing partial implementation to reference. Adding gstack role gates selectively at measured gap points extends this incrementally. A full three-system simultaneous-authority harness is not feasible without significant architecture work and would likely collapse under bypass pressure. A distributable tool is plausible but multiplies the maintenance surface.

**Where agents converge:**
- The three systems genuinely address distinct failure modes (context drift, single-perspective evaluation, undisciplined implementation)
- The right architecture is routing-not-nesting — exclusive ownership per phase, not stacked constraints on every invocation
- GSD should be the backbone/orchestration layer
- Superpowers TDD injection into GSD executor subagents is the tightest, lowest-friction integration point
- gstack role gates should be added selectively and empirically, not wholesale
- Selective context loading is non-negotiable from day one

**Realist's ruling on the core dispute:** The optimist is right that the demand is real and the complementary-gaps thesis is structurally sound. The pessimist is right that the implementation path matters enormously — stacking produces governance conflicts, routing produces composition. The resolution: build a router, not a stack. The CI/CD analogy holds for sequenced handoffs but breaks down if interpreted as simultaneous constraint activation.

**Remaining open question:** Does gstack's role-based review (particularly CEO and Eng Manager perspectives) add concrete value over GSD's existing discuss-phase for a solo CTO? This is resolvable by running parallel projects — one with gstack review gates, one without — and measuring which catches real scope errors the other misses.

**Recommended next step:** Fork the mattjaikaran/unified-workflow as a starting point. Implement GSD + Superpowers TDD injection into executor subagents first. Run three real build cycles on Implentio features. Measure where you feel the gap in strategic/role-based review, then add specific gstack personas at those exact phase transitions — copy the prompts into harness-owned files rather than wiring against the live repo.
