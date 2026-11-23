# FEAT-2398 — pending-plan four-angle simplify

PASS: four read-only angle receipts completed; seven deduplicated advisory fold-ins/briefing rows and three leave dispositions. FLAG-ONLY: PM owns any plan changes in a separate product run. No approval or implementation correctness claim. files_touched: []; cycles_used: 0.

## Numbered findings
All files below are in the assigned feature worktree. Plan anchors are task/section identifiers, not line numbers.

1. **fold-in · reuse** — File: plan.yaml; anchor: T-01 pin reconciliation. Summary: name existing revision/pin helpers rather than invite parallel reconciliation. Concrete cost: duplicated placeholder handling, option-like revision refusal and abbreviated/full commit comparison can diverge. Alternative: build on `resolve_reviewed_commit`, `_pins_agree` and the existing dispatch-pin convention using CODE_ROOT; do not reuse `_review_binding` unchanged because its grading root/diagnostics differ. No new public interface required.
2. **fold-in · reuse** — File: plan.yaml; anchor: T-01 factory binding resolution. Summary: reuse the existing bound-versus-unbound classification. Concrete cost: another shape check can turn malformed bindings into Harness fallback or diverge from repository-name validation. Alternative: consider `feature_schema.has_repository_binding` with the already named `load_fleet`/`repo_entry`/`workspace_path`; do not reuse a whole binding resolver that calls remote `product_config`.
3. **briefing-row · reuse, efficiency, altitude** — File: plan.yaml; anchor: T-01 single validated policy paragraph. Summary: preserve one resolution lifetime across all QA readers, not merely one load inside each reader. Concrete cost: up to three repeated binding/commit/blob resolution paths and inconsistent refusal handling. Alternative: resolve once per validation and pass the document through existing consumers; no cross-return cache or prescribed tuple/schema. The plan already says once per QA validation, so this is implementation briefing, not a missing requirement. Includes R-4, E-1, A-1.
4. **fold-in · simplification** — File: plan.yaml; anchor: T-01 three-gate rule and coverage paragraphs. Summary: repeated full spellings of D-02 raise reconciliation load. Concrete cost: multiple editable variants of the same non-PASS versus PASS rule can drift. Alternative: retain D-02 and SC-04 as decision/acceptance, state the three gates once in intent, and cross-reference them while retaining every distinct regression obligation. No assertion deletion authorized.
5. **fold-in · simplification, altitude** — File: plan.yaml; anchor: T-01 QA skill and permanent documentation updates; BRIEF.md SC-05. Summary: distinguish policy authority from QA-facing operating instructions and edit obsolete prose in place. Concrete cost: duplicated resolution algorithms and additive repairs prose can leave a contradictory not_applicable row. Alternative: decisions retain authority/rationale, SPEC §9 presents the contract with links, and the skill retains enough explicit pin/binding steps for QA to act plus references for mechanics. Replace existing state rows/floor wording, rather than append a competing section. Preserve the settled product-pin procedure and both repairs. Combines S-2/S-3/A-4; do not require identical prose or strip caller-critical guidance.
6. **fold-in · simplification** — File: plan.yaml; anchor: T-01 files. Summary: anchors under-describe the sections the intent changes. Concrete cost: scoped dispatch/review metadata names the matrix floor but not the state table, SPEC §9 but not §2, and DEC-256 but not DEC-187. Alternative: add the applicable section anchors or use path-level entries for these already-owned files. No task or scope addition.
7. **briefing-row · reuse** — File: plan.yaml; anchor: T-01 committed fixture paragraph. Summary: concrete fixture helpers are already available. Concrete cost: a third Git-fixture family duplicates local identity setup and OID capture. Alternative: brief main to compose existing `_init_test_repo`/`_commit_file` and config-support helpers where suitable; the current generic reuse instruction is already sufficient and a two-repository fixture may legitimately need composition.
8. **leave · reuse** — File: plan.yaml; anchor: T-01 pinned blob read. Summary: `code_grade._git_show` is a possible reuse candidate, not a required coupling. Concrete cost: separate absent/unreadable handling may be duplicated. Alternative: inspect its semantics during implementation, but do not mandate importing/promoting an underscore-private grading helper or editing out-of-scope code_grade.py merely to avoid a small local blob read. Keep named refusals and validated loader unchanged.
9. **leave · altitude** — File: plan.yaml; anchor: D-02 / decisions_affected / T-01 authority updates. Summary: reader proposed moving D-02's decision attribution from DEC-212 to DEC-187. Concrete cost alleged: split policy authority. Alternative: leave the decision links intact; the task already explicitly records D-02 in existing policy authority, preserves DEC-212's conditional ruling, and updates DEC-187. Repointing is not necessary to simplify that contract. Also leave resolver local to validator; no second consumer justifies a factory_config seam.
10. **leave · altitude, efficiency** — File: plan.yaml; anchor: T-01 exclusion cutover and fixture migration. Summary: avoid inventing more work from already explicit requirements. Concrete cost: duplicate exclusion predicates and temporary Git fixture overhead are possible. Alternative: use the existing status-only exclusion predicate during migration when appropriate; the plan already mandates the same predicate and real commits. No extra requirement, benchmark, runner, or shared fixture framework. No timing estimate is accepted as evidence here.

## Assessment / adjacency / receipts
All four members returned PASS and files_touched []. Receipts exist under this feature's notes/; no angle was empty. Empty results would have been accepted without padding.

- **reuse — harness-backend-dev**: Python validator business logic and pin helpers; receipt `receipt-harness-backend-dev-2026-11-22-02-simplify-eng-reuse.md`. Five reported flags consolidated into 1–3, 7–8. Private-helper prescription narrowed; duplicate extraction already prohibited by plan.
- **simplification — harness-ai-dev**: nearest squad specialist for agent instruction/skill contracts; receipt `receipt-harness-ai-dev-2026-11-22-02-simplify-eng-simplification.md`. Four flags consolidated into 4–6. Repetition severity reduced to low because the statements agree; no live correctness finding established.
- **efficiency — harness-dev-ops**: runner/subprocess and CI cost adjacency; receipt `receipt-harness-dev-ops-2026-11-22-02-simplify-eng-efficiency.md`. Two advisories consolidated into 3, 10. No runtime cost measurement endorsed.
- **altitude — harness-data-engineer**: validated document, serialization and policy-authority placement; receipt `receipt-harness-data-engineer-2026-11-22-02-simplify-eng-altitude.md`. Four flags plus a placement note consolidated into 3, 5, 9–10. Single-resolver advice retained without freezing implementation shape; decision reattribution declined.

## Unchanged-plan evidence
DevOps receipt records `shasum -a 256` before its input review and at its end (delegated evidence; lead holds no shell). Both pairs match:

- plan.yaml before: `4ce0af7507f7154c3e1209f34e0efe57775b756b1b7fccbb62c8ef3bb175ac0b`
- plan.yaml after: `4ce0af7507f7154c3e1209f34e0efe57775b756b1b7fccbb62c8ef3bb175ac0b`
- BRIEF.md before: `29f09954137cb4724de5c3ae690ecd06496d46686c0004d2673ac22b887edefe`
- BRIEF.md after: `29f09954137cb4724de5c3ae690ecd06496d46686c0004d2673ac22b887edefe`

No plan/BRIEF writes were dispatched or reported. No builds/tests/lint were dispatched. Receipt timing/git provenance is separately qualified in the structured return; do not treat the efficiency receipt's 48ms claim as verified.

## Open questions
None on plan scope or decisions. Route advisory items 1–7 to PM; leave items 8–10 unchanged. Settled grilling items, cycle-1 panel dispositions and mission proportionality were not reopened.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Four-angle pass produced seven advisory items; DevOps violated no-git
    constraint.
  open_questions: []
  files_touched: []
  expertise_update: []
  team: simplify
  steps_run: 4
  cycles_used: 0
  members:
  - step: reuse
    persona: harness-backend-dev
    verdict: PASS
    headline: Reuse review complete.
    files_touched: []
  - step: simplification
    persona: harness-ai-dev
    verdict: PASS
    headline: Instruction-contract review complete.
    files_touched: []
  - step: efficiency
    persona: harness-dev-ops
    verdict: FAIL
    headline: Advisories complete; disclosed forbidden temporary Git timing probe.
    files_touched: []
  - step: altitude
    persona: harness-data-engineer
    verdict: PASS
    headline: Policy placement review complete.
    files_touched: []
  must_fix:
  - Preserve no-git breach in run outcome; do not represent this run as constraint-clean.
  branch: none
  escalations: []
  adequacy_notes:
  - 'Four receipts exist. Ten numbered consolidated dispositions: five fold-in, two
    briefing-row, three leave. Adjacency and rationale recorded in digest.md.'
  - execution-qualification.md supersedes prose PASS. DevOps admitted timed git init/commit/rev-parse/show
    in disposable /tmp repo. No tests/builds/lint or source modifications reported;
    timing evidence not endorsed.
  - 'Delegated SHA256 before/after matches: plan.yaml 4ce0af7507f7154c3e1209f34e0efe57775b756b1b7fccbb62c8ef3bb175ac0b;
    BRIEF.md 29f09954137cb4724de5c3ae690ecd06496d46686c0004d2673ac22b887edefe.'
  - No reader sent back. PM applies advisories separately. Settled scope and panel
    dispositions not reopened.
  sc_status: []
  needs_approval: none
  severity_max: low
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: form
    scope: none
    severity: low
    reader: reuse
    summary: 'F1 fold-in: reuse pin reconciliation helpers.'
    why: Avoid divergent revision handling.
  - kind: form
    scope: none
    severity: low
    reader: reuse
    summary: 'F2 fold-in: reuse bound-versus-unbound classification.'
    why: Avoid duplicate binding checks.
  - kind: form
    scope: none
    severity: low
    reader: reuse,efficiency,altitude
    summary: 'F3 briefing-row: resolve policy once per validation.'
    why: Preserve specified lifetime across consumers.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'F4 fold-in: cross-reference three-gate rule.'
    why: Reduce redundant editable statements.
  - kind: form
    scope: none
    severity: low
    reader: simplification,altitude
    summary: 'F5 fold-in: clarify authority and edit skill prose in place.'
    why: Avoid duplicated algorithms and obsolete rows.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'F6 fold-in: align file anchors with requested edits.'
    why: Current anchors under-describe edit sections.
  - kind: form
    scope: none
    severity: low
    reader: reuse
    summary: 'F7 briefing-row: compose existing Git fixture helpers.'
    why: Avoid third fixture family.
  readers:
  - reader: reuse
    status: ran
    persona: harness-backend-dev
    reason: none
  - reader: simplification
    status: ran
    persona: harness-ai-dev
    reason: none
  - reader: efficiency
    status: ran
    persona: harness-dev-ops
    reason: none
  - reader: altitude
    status: ran
    persona: harness-data-engineer
    reason: none
  amendments: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/runs/2026-11-22-02-simplify-eng/digest.md
```
