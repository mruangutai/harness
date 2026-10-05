# BRIEF — FEAT-2037-product-document-guidance

## Problem

Issue #2037 identifies missing product-document paths and consultation guidance in preloaded Harness playbooks. Planning, implementation, delegation and review can therefore assume requirements or lose reference pointers across fresh-context dispatch, or resolve them in the Harness checkout rather than the assigned product checkout.

## Done when — by perspective

**operator** — I can rely on agents answering product questions from the assigned product's relevant guidance before assuming or escalating, and identifying concrete gaps rather than inventing answers.

**orchestrator** — I can rely on product identity and relevant document pointers reaching the actual implementer through task intent and nested delegation without changing file ownership.

**reader** — I can assess conformance against product guidance without confusing it with Harness governance or expanding this patch into a new enforcement system.

## Success criteria

- SC-01 (operator): In the focused scenario in notes/uat-product-document-guidance-c0.md, actual planning and implementation reads resolve docs/spec.md, docs/decisions.md and docs/architecture.md in the assigned PRODUCT checkout, despite same-named conflicting control-plane decoys; requirements, decision and architecture answers use their corresponding relevant sections before assumptions or escalation.
  verify: uat
- SC-02 (orchestrator): The scenario's real task intent and real lead-to-member dispatch both retain assigned PRODUCT checkout identity and all three applicable document pointers; the three documents remain read inputs, absent from task-owned files when unchanged.
  verify: uat
- SC-03 (reader): The actual reviewer consults the relevant product sections and reports the scenario's planted implementation nonconformance; missing, unresolved and conflicting guidance each produces a concrete path/question/gap report rather than fabricated contents or silent precedence.
  verify: uat
- SC-04 (reader): Inspect git show <review_sha>:<path> for each of T-01's four paths: compact shared guidance reaches planning, implementation and review through harness-principles, task-intent preservation is in harness-spec-driven, nested preservation is in harness-zero-micro-management, and SPEC.md supports it. Existing Harness governance and ownership remain intact; no full-read mandate, mandatory citation ceremony, embedded product contents, injection, registry, schema or runtime mechanism is added.
  verify: inspection

## Verification gaps

- SC-01–SC-03 are NOT RUN YET. DEC-70 requires conduct observed through real agent reads and dispatches, not source greps or a new dataset eval. Operator/main executes the draft scenario only after edits and green QA/review inspection, then records their judgment; PM does not mark it passed.
- docs has no required kinds in this worktree's test_matrix. Unit/integration runners exist; static checks are supplemental structural/regression evidence, not conduct proof. eval is excluded with cmd: null and is not relied upon. functional/component/ui/typecheck null runners do not cover these four Markdown edits.
- Live OMP credentials, updated-skill delivery, raw transcript visibility and the disposable fixture roots are not exercised at intake. Inability to observe real reads or actual nested dispatch leaves the affected SC unmet; no runtime instrumentation is added to work around it. Backlog #1865 notes UAT is not automatically dispatched: main must execute this explicit script.

## Constraints

- DEC-225 SUPPLIES the confirmed patch mission: <=120-line BRIEF, exactly one T-01, no panel or goal-check. Escalate if the four-file guidance diff becomes unbounded or needs a public interface; do not silently trim scope.
- DEC-21 BLOCKS delegated skill-policy edits. Settled check-domain resolution is NOBODY for the three skill files; DEC-179 SUPPLIES declared main-session-direct routing. SPEC.md already grants harness-documentor, but stays with the skill files in the single main-session layer-0 task; no specialist grant is revoked or widened.
- DEC-70 SUPPLIES conduct verification for preloaded Markdown playbooks. change_type docs matches guidance-only edits; bugfix would invoke runtime/contract-doc predicates, while ai_behavior forces eval for prompt/model/tool integration, none of which changes here. No new dataset eval.
- DEC-158 SUPPLIES compact shared resident rules; DEC-202 SUPPLIES the single authored .claude/skills tree and OMP delivery. Do not edit agent definitions or duplicate the rule across personas.
- DEC-214 SUPPLIES separate control-plane and feature-artifact anchors. Lowercase docs/spec.md, docs/decisions.md and docs/architecture.md resolve in the assigned PRODUCT checkout, not either Harness anchor by default.
- Harness governance remains distinct: harness-brief still consults the control-plane .harness/harness/docs/DECISIONS-INDEX.md and relevant .harness/harness/docs/DECISIONS.md entries; Harness .harness/harness/docs/SPEC.md is supporting governance documentation, not product docs/spec.md.
- DEC-231 SUPPLIES perspective-tagged criteria; DEC-232 SUPPLIES stable file anchors. Only main records approval on explicit operator signature; all substantive work remains pending.

## Out of scope

- Product document authoring or repair; editing model integrations, hooks, validators, gate scripts, agent definitions or their tests; automatic context loading; documentation registries; new configuration or schema; unrelated state cleanup — excluded by settled guidance-only intake.

## Approval

status: approved
approved-by: operator
date: 2026-10-05
