# BRIEF — FEAT-2229 Decision dispositions

## Problem

A mechanism change can leave earlier decisions contradicted without anybody recording what must change in them. FEAT-30's Expertise cutover named its new choice but not the dispositions of the earlier write grants; the plan panel missed the stranded personas. An operator therefore cannot tell from a plan what decision edits it promises, or from validate whether those edits landed. Issue #2229 describes the symptom; the operator-confirmed grilling corrects its historical attribution and settles the scope.

## Done when — by perspective

**operator** — I can see what a proposed change does to existing decisions before I sign it. Validate cannot call that change delivered while a promised decision edit is missing, and older work is not retroactively invalidated.

**reader** — I can distinguish a mechanically malformed declaration from an incomplete or unjustified one. I can judge a proposed strike against the actual decision and route an unlanded promise to the task responsible for it.

**code maintainer** — I have one disposition record and one drafting check, integrated with the existing plan writer and goal-check rather than a parallel decision-audit system. The boundaries and regressions are explicit enough to change safely.

## Success criteria

- SC-01 (operator): A newly drafted plan, including a one-task patch, carries decisions_affected as a list. Each row has exactly dec, disposition, clause, successor and reason; an explicit empty list is valid. The shared plan loader and writer retain valid rows and reject malformed rows without partially changing the plan. QA demonstrates the new assertions failing before the change.
  verify: automated evidence: unit
- SC-02 (reader): For an in-era pending draft, plan-merge.py check fails separately for an absent block, an unindexed dec, keep/amend of an already STRUCK decision, a clause absent from that decision's section, an unresolved amend/strike successor, or an amend/strike lacking a DECISIONS.md-owning task. Valid keep/amend/strike and empty-list controls pass; text in another section cannot satisfy the clause check. QA demonstrates fail-first evidence for each new rejection.
  verify: automated evidence: integration
- SC-03 (operator): decision_dispositions_era_start makes the requirement forward-only by draft creation, not signature or feature station: new drafts after activation are checked, while previously drafted in-flight and landed plans are neither refused nor backfilled by this addition. Tests compare legacy plan bytes before/after mutation and exercise both sides of the era boundary. QA demonstrates fail-first evidence for the new boundary behavior.
  verify: automated evidence: integration
- SC-04 (reader): At the pinned review_sha, git show <review_sha>:.claude/skills/harness/teams/plan.yaml instructs scope to compare affected decisions against the work, challenge omissions including an empty list, and apply DEC-188's flat-contradiction versus operator-authorized softer-strike rule. The drafting and patch instructions require the same five-field block and the same check; a patch gains no pre-build panel.
  verify: inspection
- SC-05 (operator): At the pinned review_sha, git show <review_sha>:.omp/agents/harness-pm.md requires Mode 2 to grade every amend/strike individually, skip keep, and report met/not_met/partial, method and evidence from DECISIONS.md at review_sha; git show <review_sha>:.claude/skills/harness/teams/validate.yaml delegates that grading to canonical Mode 2 at the supplied pin rather than duplicating its contract. Strike evidence is a strike record or a justified deletion with the named successor; amend evidence is the rewritten current text. Missing/partial landing fails validate like an unmet SC and identifies the owning DECISIONS.md task; a green test suite cannot substitute. The validator synthesis instructions preserve those failures.
  verify: inspection
- SC-06 (code maintainer): At the pinned review_sha, git show <review_sha>:.harness/harness/docs/DECISIONS.md records the new D-01 schema/enforcement decision and rewrites DEC-188's human-only enforcement claim to describe the bounded drafting gate plus pm landing check, retaining its strike/amend distinction and rejection of general stale-decision detection. The generated index resolves the new entry. Existing sc_status rows carry disposition grades without a new digest field or validate-time script; shipped guidance retains one five-field record and the stated exclusions.
  verify: inspection
- SC-07 (code maintainer): Targeted integration regressions assert each changed drafting, scope and validate obligation at its canonical owner, including patch coverage, pm's row-level pinned evidence, keep skipping and failure routing, and the validate prompt's delegation to Mode 2; deleting any one obligation from its owning section reddens that assertion rather than being masked by another document. QA records the failing pre-change assertions.
  verify: automated evidence: integration

## Verification gaps

No applicable null-runner gap: unit and integration are active runnable kinds covering the new Python regressions. Functional and eval are excluded under DEC-187; component, ui and typecheck are unresolved but this feature adds no browser, component or TypeScript surface. SC-04 through SC-06 are pinned-artifact inspections, not claims that static prompt tests prove an agent will obey; the actual validate goal-check must also grade this feature's promised DEC-188 amendment. No UAT or visual prototype is required for this non-UI schema/prompt/gate change.

## Constraints

- SUPPLIES DEC-188: strike flat contradictions, amend softer changes, and require the operator's word before a softer strike. Its human-only enforcement assertion is amended, not the decision struck.
- BLOCKS DEC-174 and SUPPLIES DEC-179: enforcement and gate tests execute main-session-direct; unowned role/skill/template surfaces are also declared main-session-direct, never routed to a squad by topic.
- SUPPLIES DEC-182 and DEC-229: real YAML; plan edits only through plan-merge.py, literal verify commands, explicit task ownership/dependencies, pending signature and unchanged panel-recording authority.
- SUPPLIES DEC-73 and DEC-205: evidence rather than re-testing; amend means rewrite current truth, not append dated amendment history. Disposition outcomes reuse sc_status's existing id/verdict/method/evidence shape.
- BLOCKS DEC-227's no-retroactive-grading principle and DEC-252's shipped-history boundary: no backfill or new refusal of previously drafted/landed plans. Record decision_dispositions_era_start in per-project harness.json, with a new-install template value.
- SUPPLIES DEC-228: the existing scope reader judges completeness and strike/amend appropriateness; patch remains panel-free.
- PRODUCT is /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions. Its docs/spec.md, docs/decisions.md and docs/architecture.md are absent. AGENTS.md identifies .harness/harness/docs/SPEC.md and DECISIONS.md as the existing Harness authorities; no separate architecture contract was found or invented.

## Out of scope

- Reciprocal-link checks — the operator excluded them; per-feature goal-check proves landing, with reconsideration only if forgotten strikes recur.
- Mechanical detection of stale decisions generally — struck by DEC-188 and not reopened.
- A prose blast-radius line in DECISIONS.md and a relied_on_by field — the plan block is the single record; unconsumed prose would drift and no evidence justified the extra field.

## Approval

status: pending
approved-by:
date:
