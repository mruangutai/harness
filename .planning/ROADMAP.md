# Roadmap: Harness

## Overview

The harness is built layer-by-layer, each layer a prerequisite for the next. Phase 1 establishes the routing infrastructure and GSD integration that everything else plugs into. Phase 2 adds engineering discipline rules (TDD, spec-driven dev, debugging, code review) that inject into GSD's executor and verifier subagents. Phase 3 adds role-based perspective gates (CEO, Architect, QA, Security) at defined trigger points. Phase 4 validates the complete harness on a real project to prove all four pain points are resolved before distribution.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Router & Context Infrastructure** - Harness CLAUDE.md, routing layer, config extension, and GSD context integration
- [ ] **Phase 2: Engineering Discipline Rules** - TDD enforcement, spec-driven development, systematic debugging, and code review gates
- [ ] **Phase 3: Role-Based Gates** - CEO product challenge, Architect review, QA adversarial testing, and Security audit
- [ ] **Phase 4: Real-Project Validation** - End-to-end validation on a non-trivial project with all harness components active

## Phase Details

### Phase 1: Router & Context Infrastructure
**Goal**: The harness routing layer exists, loads selectively, and integrates with GSD's orchestration without breaking existing workflows
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, CTX-01, CTX-02, CTX-03, CTX-04, CTX-05, CTX-06
**Success Criteria** (what must be TRUE):
  1. CLAUDE.md exists, is under 1,000 tokens, and maps lifecycle phases to exclusive framework owners
  2. Running a GSD workflow with the harness installed loads only phase-relevant skill files -- never all simultaneously
  3. `.planning/config.json` contains a harness block with gate toggles (TDD, role triggers, bypass protection) alongside existing GSD settings
  4. GSD's existing artifact chain (PROJECT > REQUIREMENTS > ROADMAP > STATE > PLAN), subagent isolation, wave execution, discussion phase, research gates, and scope drift detection all function unchanged
  5. All harness rule files are self-contained copies (no references to upstream gstack/superpowers repos)
**Plans**: TBD

### Phase 2: Engineering Discipline Rules
**Goal**: Claude follows strict engineering discipline during implementation -- tests before code, specs before implementation, evidence before fixes, review before ship
**Depends on**: Phase 1
**Requirements**: ENG-01, ENG-02, ENG-03, ENG-04, ENG-05, ENG-06
**Success Criteria** (what must be TRUE):
  1. When executing an implementation plan, Claude writes a failing test before writing production code -- and code written before tests triggers a deletion/rewrite guard
  2. Before implementation begins, a structured spec exists with clarifying questions answered, approaches evaluated, and user approval obtained
  3. Plan tasks contain exact file paths, complete code intent, and verification steps -- "TBD" or placeholder content is rejected
  4. When debugging, Claude gathers evidence and performs root cause analysis before attempting fixes -- and stops after 3 failed attempts
  5. After execution completes, a code review step checks spec compliance first, then code quality -- with two-stage subagent review (implementer self-review, then independent reviewers)
**Plans**: TBD

### Phase 3: Role-Based Gates
**Goal**: Domain-expert perspectives challenge assumptions and catch issues at defined workflow trigger points
**Depends on**: Phase 2
**Requirements**: ROLE-01, ROLE-02, ROLE-03, ROLE-04
**Success Criteria** (what must be TRUE):
  1. At project init and major phase boundaries, a CEO/Product review challenges scope, validates market fit, and asks forcing questions -- referencing PROJECT.md and REQUIREMENTS.md
  2. At the discuss-phase boundary, an Architect/Eng review locks architecture with data flow analysis, edge case enumeration, and test matrices -- referencing the existing codebase and PLAN.md
  3. Before shipping, QA receives the spec independently (not the implementation) and generates adversarial tests including regression tests
  4. When auth, data handling, or API code is touched, a Security audit runs OWASP Top 10 and STRIDE threat modeling before ship
**Plans**: TBD

### Phase 4: Real-Project Validation
**Goal**: The complete harness is proven to work under real project pressure -- all four pain points (context drift, quality shortcuts, scope creep, lack of pushback) are verifiably resolved
**Depends on**: Phase 3
**Requirements**: VAL-01, VAL-02, VAL-03
**Success Criteria** (what must be TRUE):
  1. A real project with 500+ LOC scope, multiple phases, and at least one debugging scenario has been completed using the harness end-to-end
  2. Token budgets are measured empirically -- CLAUDE.md under 1K tokens, skill files measured for actual context consumption when injected into subagents
  3. All four pain points are verified resolved with specific evidence: context drift (subagent isolation working), quality shortcuts (TDD enforced), scope creep (drift detection caught drops), pushback (role gates challenged decisions)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Router & Context Infrastructure | 0/TBD | Not started | - |
| 2. Engineering Discipline Rules | 0/TBD | Not started | - |
| 3. Role-Based Gates | 0/TBD | Not started | - |
| 4. Real-Project Validation | 0/TBD | Not started | - |
