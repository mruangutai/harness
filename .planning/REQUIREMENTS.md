# Requirements: Harness

**Defined:** 2026-04-04
**Core Value:** Enable a CTO to take a software idea from product validation through architecture, disciplined implementation, and QA — with Claude executing reliably at each stage without context drift, scope creep, quality shortcuts, or unchallenged assumptions.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Harness Infrastructure

- [ ] **INFRA-01**: Harness CLAUDE.md router stays under 1,000 tokens and maps lifecycle phases to exclusive framework owners
- [ ] **INFRA-02**: Route-not-stack architecture — each phase has exactly one framework authority; others load only as reference material via skills
- [ ] **INFRA-03**: Selective context loading — skill files load on demand at trigger points, never all simultaneously
- [ ] **INFRA-04**: Config extension in `.planning/config.json` — harness gates (TDD enforcement, role triggers, bypass protection) configured alongside GSD settings
- [ ] **INFRA-05**: Copy-and-own pattern — gstack/superpowers patterns absorbed as harness-owned files, no live upstream dependencies

### Context & Orchestration (GSD backbone)

- [ ] **CTX-01**: Thin orchestrator with subagent isolation — main session stays at 10-15% context, subagents get fresh 200K-token windows
- [ ] **CTX-02**: Planning artifact chain — PROJECT.md > REQUIREMENTS.md > ROADMAP.md > STATE.md > PLAN.md with traceable state across sessions
- [ ] **CTX-03**: Wave-based parallel execution — independent plans run simultaneously with dependency-aware ordering
- [ ] **CTX-04**: Discussion phase — questions mode (interactive Q&A) and assumptions mode (system infers, user corrects) before planning
- [ ] **CTX-05**: Research gates — block planning if research has unresolved questions
- [ ] **CTX-06**: Scope drift detection — flag when planner silently drops requirements during planning

### Engineering Discipline (superpowers)

- [ ] **ENG-01**: TDD Iron Law enforcement — no production code without a failing test first; code written before tests must be deleted; anti-rationalization guards with explicit red-flag checklist
- [ ] **ENG-02**: Spec-driven development — structured brainstorming (context review, clarifying questions, approaches with tradeoffs) → written spec with self-review → user approval gate → implementation
- [ ] **ENG-03**: Zero-placeholder plan tasks — "TBD" and placeholder code in plans is rejected; every task has exact file paths, complete code intent, and verification steps
- [ ] **ENG-04**: Systematic debugging — evidence-gathering before any fix attempts; 4-phase root cause analysis; stops after 3 failed fixes
- [ ] **ENG-05**: Code review gate — review step between execute and ship; checks spec compliance first, then code quality; fills GSD's missing review step
- [ ] **ENG-06**: Two-stage subagent review — implementer self-review, then spec compliance reviewer, then code quality reviewer; loops until all pass

### Role-Based Perspectives (gstack)

- [x] **ROLE-01**: CEO product challenge — at project init and major phase boundaries; validates scope, checks market fit, challenges assumptions with forcing questions; references PROJECT.md and REQUIREMENTS.md
- [x] **ROLE-02**: Architect/Eng review — at discuss-phase boundary; locks architecture with data flow diagrams, edge cases, test matrices; references existing codebase and PLAN.md
- [x] **ROLE-03**: QA adversarial testing — pre-ship gate; tests against spec independently (receives spec, not implementation); generates regression tests; v1 without browser automation
- [x] **ROLE-04**: Security audit — OWASP Top 10 + STRIDE threat modeling pre-ship; conditional on phase content (triggers when auth, data handling, or API code is touched)

### Validation

- [x] **VAL-01**: Harness validated on a real project (500+ LOC scope, multiple phases, at least one bug requiring debugging) before distribution
- [x] **VAL-02**: Token budget measured empirically — CLAUDE.md under 1K tokens, skill files measured for actual consumption when injected into subagents
- [x] **VAL-03**: All four pain points verified resolved: context drift, code quality shortcuts, scope creep, lack of pushback

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Browser & Visual Testing

- **VIS-01**: QA gate with real browser automation (Chromium or MCP-based)
- **VIS-02**: Visual regression testing with before/after screenshots
- **VIS-03**: Design review with 80-item visual audit

### Cross-Model & Advanced

- **ADV-01**: Cross-model review via external AI (Codex, competing model)
- **ADV-02**: Post-deploy canary monitoring (console errors, performance regression)
- **ADV-03**: Design system generation and variant comparison

### Distribution

- **DIST-01**: Global installation to `~/.claude/` for multi-project use
- **DIST-02**: Distributable package with install script and version management
- **DIST-03**: Team onboarding documentation and configuration guide

## Out of Scope

| Feature | Reason |
|---------|--------|
| New CLI or binary | Files-only for v1; GSD's gsd-tools.cjs handles all runtime needs |
| Live upstream dependencies | Copy-and-own; wiring against gstack/superpowers repos creates maintenance burden and breakage risk |
| Replacing GSD's core infrastructure | Extend, not rebuild; GSD's orchestration is proven and installed |
| Simultaneous framework loading | Route-not-stack; loading all three simultaneously causes governance conflicts and context bloat |
| Team retrospectives and analytics | Valuable but not core to the solo-CTO-to-small-team use case |
| Design consultation/generation | Secondary to engineering discipline for v1 |
| Post-deploy monitoring | Valuable but milestone-level concern, not harness-level |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Pending |
| INFRA-02 | Phase 1 | Pending |
| INFRA-03 | Phase 1 | Pending |
| INFRA-04 | Phase 1 | Pending |
| INFRA-05 | Phase 1 | Pending |
| CTX-01 | Phase 1 | Pending |
| CTX-02 | Phase 1 | Pending |
| CTX-03 | Phase 1 | Pending |
| CTX-04 | Phase 1 | Pending |
| CTX-05 | Phase 1 | Pending |
| CTX-06 | Phase 1 | Pending |
| ENG-01 | Phase 2 | Pending |
| ENG-02 | Phase 2 | Pending |
| ENG-03 | Phase 2 | Pending |
| ENG-04 | Phase 2 | Pending |
| ENG-05 | Phase 2 | Pending |
| ENG-06 | Phase 2 | Pending |
| ROLE-01 | Phase 3 | Complete |
| ROLE-02 | Phase 3 | Complete |
| ROLE-03 | Phase 3 | Complete |
| ROLE-04 | Phase 3 | Complete |
| VAL-01 | Phase 4 | Complete |
| VAL-02 | Phase 4 | Complete |
| VAL-03 | Phase 4 | Complete |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0

---
*Requirements defined: 2026-04-04*
*Last updated: 2026-04-04 after roadmap creation*
