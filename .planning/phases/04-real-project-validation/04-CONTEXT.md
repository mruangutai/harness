---
phase: 04-real-project-validation
status: ready-for-planning
discussed: 2026-04-08
requirements: [VAL-01, VAL-02, VAL-03]
---

# Phase 4 Context: Real-Project Validation

## Phase Goal

Prove the harness works under real project pressure. Run the harness end-to-end on a non-trivial Implentio feature, then measure token budgets and collect evidence that all four pain points are resolved.

## Canonical Refs

- `.planning/REQUIREMENTS.md` §VAL-01, VAL-02, VAL-03 — exact wording
- `.planning/ROADMAP.md` §Phase 4 — success criteria
- `.planning/phases/03-role-based-gates/03-CONTEXT.md` — locked decisions about role gate agents

---

<decisions>

## D-01: Validation Project

**Decision:** Implentio PDF editor — invoice annotation tool for 3PL invoices.

**What it does:** Ingests 3PL invoice PDFs, uses OCR + AI to extract key fields (invoice date, billing period, charge description, charge amount, biller/3PL name, customer name). Routes by confidence score:
- **≥90% confidence** → auto-ingest, parse, and store. No human intervention.
- **<90% confidence** → block data from entering the system, notify support team, present PDF + parsing issue summary for human annotation. After annotation, re-parse and re-score until ≥90% reached.

**Existing code:** Partial extraction pipeline exists in Implentio codebase. No confidence scoring, no routing logic, no annotation UI yet. Backend specifics TBD — codebase exploration required before planning.

**Tech stack:** TanStack + TypeScript (full-stack). Backend TBD via codebase exploration during discuss-phase for each sub-phase.

**UI:** Split-screen — PDF document viewer (left) + annotation form (right). Screenshots available at UI phase.

## D-02: Confidence Threshold

**Decision:** <90% = human review queue. No separate 70–90% tier. The threshold is binary: either data is trusted (≥90%) or it isn't and a human must review it. Simplifies routing logic and protects data quality.

## D-03: Validation Sub-Phase Breakdown

The PDF editor feature breaks into 3 phases, executed using the harness end-to-end:

- **Sub-Phase A:** Confidence scoring + data blocking logic — add confidence scoring to existing extraction pipeline, implement <90% routing to human review queue, block low-confidence data from system
- **Sub-Phase B:** Annotation UI — split-screen PDF viewer + annotation form, support team workflow for correcting extraction errors
- **Sub-Phase C:** Re-parse flow + unblock — post-annotation re-parse, re-score, unblock data when ≥90% achieved

Each sub-phase runs the full harness: discuss → plan → execute → code review → verify → QA/security gate.

## D-04: Pain Point Evidence Criteria (VAL-03)

Evidence must be observable and verifiable from git history and planning artifacts.

| Pain Point | Required Evidence |
|---|---|
| Context drift | At least one executor subagent SUMMARY.md shows only files listed in the plan — no off-plan edits |
| Quality shortcuts | At least one plan has a test file committed before its implementation file (verifiable via `git log`) |
| Scope creep | At least one discuss-phase session produces a `<deferred>` section showing a scope item caught and redirected |
| Lack of pushback | At least one role-gate agent (CEO or Eng reviewer) fires and produces a report with ≥1 finding or forcing question |

Evidence collected after all 3 sub-phases complete and written to `VALIDATION-REPORT.md`.

## D-05: Token Budget Measurement (VAL-02)

**Decision:** Post-phase dedicated measurement task, after all 3 sub-phases complete.

**What to measure:**
- CLAUDE.md token count (must be <1,000 tokens)
- Each skill file in `.claude/skills/harness/` — individual token counts
- Each agent definition in `.claude/agents/harness-*.md` — individual token counts
- Actual agent_skills injection paths from `harness.json` — confirm correct files are loaded

**Output:** `MEASUREMENTS.md` artifact in the phase directory. Includes pass/fail for each threshold.

## D-06: Harness Improvement — Eng Reviewer Pre-Discuss Mode

**Decision:** Implement as part of Phase 4 (not deferred to v2).

**Problem:** `discuss-phase` explicitly avoids architectural questions (architecture is listed as "Claude handles this"). For phases where the deliverable IS architecture (agents, APIs, data models), discuss-phase produces behavioral decisions but no architectural ones — the eng reviewer then has nothing to review against.

**Solution:** `harness-eng-reviewer` gets a second operational mode:

- **Pre-discuss mode (new):** Spawned BEFORE discuss-phase begins on architectural phases. Reads the phase goal from ROADMAP.md and generates a set of architectural questions for the user to consider during the discuss session. Output: a list of questions, not a review report.
- **Post-discuss mode (existing):** Spawned after discuss-phase to review CONTEXT.md decisions for edge cases, trust boundaries, and test matrix gaps. Unchanged.

**CLAUDE.md trigger to add:** "Before /gsd-discuss-phase on architectural phases (agents, APIs, data models, schemas): spawn harness-eng-reviewer in pre-discuss mode."

**Detection heuristic for "architectural phase":** Phase goal contains keywords: `agent`, `API`, `schema`, `data model`, `interface`, `contract`, or the phase deliverable is a set of files that define system behavior rather than implement it.

</decisions>

<specifics>

## Specific Notes

- Backend codebase exploration happens inside each sub-phase's discuss session — not pre-Phase 4
- Screenshots of the annotation UI will be provided at Sub-Phase B discuss session
- The harness validation run happens in the Implentio repo, not the harness repo
- The eng reviewer pre-discuss mode implementation happens IN the harness repo as Plan 01

</specifics>

<deferred>

## Deferred Ideas

- VIS-01/VIS-02/VIS-03: Browser automation + visual regression testing — v2 requirements, not Phase 4
- ADV-01: Cross-model review — v2
- DIST-01: Global ~/.claude/ installation — v2, after validation proves the files are distribution-ready

</deferred>
