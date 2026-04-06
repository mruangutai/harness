# Phase 3: Role-Based Gates - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Populate 4 role-reviewer agent stubs with actual enforcement content and trigger logic so domain-expert perspectives run at defined workflow points: CEO/Product at project init and scope-change boundaries, Architect/Eng at the discuss-phase boundary, QA and Security as pre-ship gates. Phase 3 delivers working reviewers — Phase 4 validates them on a real project.

</domain>

<decisions>
## Implementation Decisions

### Gate Behavior

- **D-01:** All 4 reviewers are **advisory with summary** — they output a structured report (findings, severity, recommendations) and the workflow continues. No hard block on findings. The user reads the report and decides to proceed or fix. Rationale: personal CTO tool, user is always present; hard blocks add friction and false positives would be bypassed anyway.

### Agent Architecture

- **D-02:** All 4 reviewer agents are **self-contained** — the agent `.md` file contains the full role prompt (YAML frontmatter + complete role content). No dependency on the `personas/` stub files. Follows the same pattern as `harness-code-reviewer.md` from Phase 2. Single source of truth.
- **D-03:** Two new agent stubs must be created in Phase 3: `harness-qa-reviewer.md` and `harness-security-reviewer.md`. The existing stubs for `harness-ceo-reviewer.md` and `harness-eng-reviewer.md` are populated with content.
- **D-04:** `personas/ceo-review.md`, `personas/eng-review.md`, `personas/qa-gate.md`, and `personas/cso-audit.md` are vestigial stubs (agents are self-contained). Leave them as empty stubs or delete — Claude's discretion. They have no functional role.

### Persona Content Approach

- **D-05:** **Gstack structure + GSD-native references.** Use gstack's proven question/evaluation structure (from `.planning/research/FEATURES.md` — `/office-hours` forcing questions, `/plan-eng-review` architecture patterns, `/qa` adversarial approach, `/cso` STRIDE model) but replace ALL gstack storage references with GSD artifacts: `PROJECT.md`, `REQUIREMENTS.md`, `CONTEXT.md`, `PLAN.md`. No gstack-specific references remain in the final agent files.

### CEO Reviewer (ROLE-01)

- **D-06:** Trigger: spawned by CLAUDE.md instruction at new-project init and scope-change boundaries. Reads: `PROJECT.md`, `REQUIREMENTS.md`, current `ROADMAP.md`.
- **D-07:** Content pattern from gstack's `/office-hours` (6 forcing questions) + `/plan-ceo-review` (4 scope modes: Expansion, Selective Expansion, Hold Scope, Reduction). Adapted: replace "10-star product" framing with harness's Core Value framing; replace gstack storage with GSD artifacts.
- **D-08:** Output format: structured advisory report — scope mode recommendation, 3–6 forcing questions the user should answer, any requirements that appear underspecified or contradicted.

### Architect/Eng Reviewer (ROLE-02)

- **D-09:** Trigger: spawned by CLAUDE.md instruction at the discuss-phase boundary (before planning begins). Reads: the current phase's `CONTEXT.md`, `ROADMAP.md` phase section, relevant source files (Glob/Grep permitted).
- **D-10:** Content pattern from gstack's `/plan-eng-review` — locks architecture with data flow analysis, edge case enumeration, test matrices. Adapted: references CONTEXT.md decisions instead of gstack plan artifacts.
- **D-11:** Output format: architecture verdict (proceed / concerns noted), data flow assessment, edge cases not captured in CONTEXT.md, test matrix gaps.

### QA Reviewer (ROLE-03)

- **D-12:** **Spec-then-verify sequence** (single agent, two phases): Phase 1 reads CONTEXT.md + phase success criteria ONLY and produces test cases with expected behaviors. Phase 2 reads the implementation (source files) and verifies each test case against what was actually built. Agent is explicitly instructed to complete Phase 1 before reading any source files.
- **D-13:** Trigger: pre-ship gate, runs before `/gsd-ship`. Reads: phase CONTEXT.md (spec), then source files (implementation).
- **D-14:** Output format: test case list with pass/fail status, spec gaps (requirements in CONTEXT.md not covered by implementation), regression test suggestions.

### Security Reviewer (ROLE-04)

- **D-15:** **Always-on pre-ship** — Security audit runs on every `/gsd-ship` invocation. The auditor reads the plan/phase summary and self-declares scope: either runs OWASP Top 10 + STRIDE analysis or outputs "No security-sensitive changes found — audit skipped." No manual trigger required.
- **D-16:** Content pattern from gstack's `/cso` skill — OWASP Top 10 + STRIDE threat modeling. Adapted: reads PLAN.md / phase summary to self-scope, outputs findings against GSD artifact paths.
- **D-17:** Trigger: pre-ship gate (same trigger point as QA). Reads: PLAN.md (or phase summary), relevant source files for security-sensitive patterns (auth, session, API keys, data handling).
- **D-18:** Output format: scope declaration ("in scope / not in scope"), threat findings with severity (Critical/High/Medium/Low), OWASP categories triggered, recommended mitigations.

### CLAUDE.md Gate Triggers

- **D-19:** CLAUDE.md harness section gains two new trigger instructions (within GSD:harness-start/end markers, staying under 50-token budget for non-comment text):
  - `At new-project init or scope-change: spawn harness-ceo-reviewer.`
  - `Before /gsd-ship: spawn harness-qa-reviewer and harness-security-reviewer.`
  (Eng reviewer trigger already exists from Phase 2: "Before /gsd-plan-phase: verify CONTEXT.md has approaches-with-tradeoffs and user approval.")

### Claude's Discretion

- Exact wording of the CEO forcing questions (must cover: scope creep risk, unvalidated assumptions, competing priorities, market fit, user need)
- Whether to delete or leave the `personas/` stub files
- Internal structure of the Architect review output (section headers, checklist format)
- Which OWASP categories the Security auditor always checks vs. conditionally checks
- Exact framing of QA's Phase 1 / Phase 2 boundary instruction

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 3 Requirements
- `.planning/REQUIREMENTS.md` §Role-Based Perspectives — ROLE-01 through ROLE-04 exact wording and success criteria
- `.planning/ROADMAP.md` §Phase 3 — Goal, success criteria (4 items), dependency on Phase 2

### Phase 1 & 2 Locked Decisions
- `.planning/phases/01-router-context-infrastructure/01-CONTEXT.md` — D-04: agent dispatch pattern (Task() with fresh 200K context, scoped inputs); D-05: CLAUDE.md token budget (50 tokens for non-comment harness section)
- `.planning/phases/02-engineering-discipline-rules/02-CONTEXT.md` — D-22/D-23: CLAUDE.md harness section structure (existing triggers, token budget constraint)

### Gstack Patterns to Adapt
- `.planning/research/FEATURES.md` — gstack capability table (rows: /office-hours, /plan-ceo-review, /plan-eng-review, /qa, /cso) — primary source for agent content patterns

### Existing Agent Pattern to Follow
- `.claude/agents/harness-code-reviewer.md` — the self-contained agent file pattern (YAML frontmatter + role prompt) that all Phase 3 agents must follow

### Harness Config
- `.planning/harness.json` — role_triggers field (current trigger points: ceo_review, eng_review, qa_gate, security_audit)
- `CLAUDE.md` §Harness — existing gate trigger instructions added in Phase 2 (spec gate + review gate); Phase 3 adds two more

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.claude/agents/harness-ceo-reviewer.md` — existing stub with correct YAML frontmatter (name, description, tools). Needs role prompt populated.
- `.claude/agents/harness-eng-reviewer.md` — same pattern. Needs role prompt populated.
- `.claude/agents/harness-code-reviewer.md` — Phase 2 completed agent. The structural template for all Phase 3 agents (two-stage structure, spec-first framing, advisory output).
- `CLAUDE.md` §Harness — already has two gate instructions from Phase 2. Phase 3 appends two more within the same marker block.

### Established Patterns
- YAML frontmatter agent files: `name`, `description`, `tools` list. All role reviewers use: Read, Glob, Grep, Bash (for codebase access).
- Advisory report format: established by harness-code-reviewer (Stage 1 findings, Stage 2 findings, severity labels). Phase 3 reviewers follow same formatting convention.
- `Task()` dispatch with `subagent_type` = agent name — how gate agents are spawned from CLAUDE.md trigger instructions.

### Integration Points
- `CLAUDE.md` §Harness — add CEO and QA/Security trigger instructions (within existing marker block)
- `.claude/agents/` — populate 2 existing stubs + create 2 new agent files
- `.claude/skills/harness/personas/` — vestigial stub files, no functional role in Phase 3

</code_context>

<specifics>
## Specific Ideas

- User confirmed all recommended defaults — advisory behavior, gstack structure adapted to GSD, spec-then-verify for QA, always-on for Security.
- gstack's `/office-hours` "6 forcing questions" framing is the right structure for CEO reviewer forcing questions.
- Security auditor self-scoping ("audit skipped" output is valid) prevents overhead on non-security phases.

</specifics>

<deferred>
## Deferred Ideas

- **Designer role gate** (from Phase 1 deferred) — Visual/UX quality audit after UI implementation. Not in Phase 3 scope (REQUIREMENTS.md only specifies ROLE-01 through ROLE-04).
- **DevEx Lead role gate** (from Phase 1 deferred) — Developer experience review for API/SDK projects. Same deferral as Designer.
- **Hard block mode** — If future validation (Phase 4) reveals advisory reports are being ignored, revisit gate behavior. Deferred to Phase 4 feedback.
- **harness-code-reviewer split** (from Phase 2 deferred) — Split into spec-compliance-reviewer + code-quality-reviewer for true isolation. Still deferred.

</deferred>

---

*Phase: 03-role-based-gates*
*Context gathered: 2026-04-06*
