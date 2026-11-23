# QA policy draft — amended after cycle-1 reader wave, unsigned

BRIEF.md and plan.yaml are pending at station plan, with source_issues [2398]. One cohesive main-session-direct task owns six files; three choices need the operator's signature. No product code or policy was changed. Reader-wave dispositions and command receipts are in notes/research-qa-policy-apply-c1.md; the revised choices below supersede the original draft wording.

## Evidence and choices

- Baseline: 9eb07b4f3cd235c234a10edddbfe5542c1e85fba. The supplied grilling Facts verified remain the investigation baseline, not a new measured reproduction. Issue #2398 and the open backlog were read through gh; #2400–#2404 remain excluded.
- D-01 resolves the open product-location/pin question: trusted feature.json factory.repo → validated fleet entry → factory_config.workspace_path object store; feature.json review_sha reconciled with existing trusted dispatch review_pin; git show full-commit:.harness/harness.json → load_harness_json(text, context). Both policy tables come from that document. One path also serves unbound Harness features; affected validator fixtures gain real commits and trusted bindings, and unpinned Harness QA reports now refuse. That proposed cost and compatibility break are explicit in the BRIEF and task before signature. No current-tree, remote-default-branch or Harness-policy fallback. Existing seams: factory_config.py#workspace_path, feature-worktree.py#resolve_repo/#targets, validate-digest.py#_review_binding/#_registered_review.
- D-02, narrowed at apply: policy-check every reported kind under every verdict; refuse omitted always-floor unresolved/active-null kinds under every verdict, but preserve the full satisfied-kind floor only at PASS/matrix_ok true. Other configured kinds may be omitted from otherwise valid early BLOCKED/FAIL reports without fabricating a not-yet-run state. Conditional applicability remains QA's judgment. Preserve _matrix_requires_no_kind's stricter all-excluded proof. SC-04 and T-01 require mixed-floor early-exit controls.
- D-03 records accepted Kaya BLOCKED behavior; runner/exclusion setup remains Kaya #7. INV-49 disclosure changes no outcome.
- Decision dispositions: DEC-256 is amend, replacing its actual universal default-branch sentence, with successor D-01 and T-01 owning DECISIONS.md plus index. DEC-187, DEC-212, DEC-174 and DEC-221 are keep with verbatim clause pointers. The latter's onboarding and remote board/mirror/fleet policy is not widened into QA policy.
- Product guidance is genuinely absent at PRODUCT/docs/spec.md, PRODUCT/docs/decisions.md and PRODUCT/docs/architecture.md. The listed docs directory contains PRINCIPLES.md and invalid-states-audit.html. AGENTS.md explicitly maps this repository's existing SPEC and decision authority; no missing guidance was authored.

## Routing and command receipts

- Feature-root resolver returned the assigned worktree. Control-plane HEAD was 9eb07b4f3cd235c234a10edddbfe5542c1e85fba.
- check-domain.py --resolve was executed for every planned file. Validator → backend/dev-ops; gate test → backend/dev-ops/qa; QA skill → NOBODY; each authority/spec/index file → documentor. DEC-174 and the settled execution ruling justify the declared all-direct carve-out instead of a team dispatch.
- plan-merge.py apply --file <feature>/plan.yaml --proposal -: exit 0, stdout printed APPLIED and the absolute feature plan path. It emitted no APPROVAL-RESET: receipt, so no gh-sync command ran. Its automatic changed-state output reports the deliberately unsigned BRIEF, absent pre-signature Build-entry receipt and pending plan; these are not draft-check failures and were not repaired by signing or remote writes.
- Required plan-merge.py check --file <feature>/plan.yaml --root <assigned worktree>: exit 0. Receipt: OK T-01 6 anchor(s) resolved; CHECK ... 1 task(s), 6 anchor(s) resolved, 0 failure(s).
- No builds, tests, lint, formatters or smoke runs were executed. The focused future verification is tests/integration/test-validate-digest.py --only run_feat2398_qa_policy_cases; it is specified, not claimed to exist or pass yet. Main owns scheduled RED/GREEN evidence and final unit/integration receipts; no TDD waiver is claimed.

## Principles applied

- Redesign From First Principles — one pinned policy source serves kind validation, matrix floor and no-kind exemption; the old grading-root assumption is not left beside the new product-policy path.
- Experience First — refusal text names both legitimate repairs; no UI/prototype work or Kaya runner work is added to an operator-facing QA contract fix.

## Open questions

No unresolved product question. The reader-wave application and panel recording are documented in notes/research-qa-policy-apply-c1.md; the host still owns its simplification pass and plan goal-check. All three decisions remain proposals for the operator's signature. Five SCs: four future integration checks with fail-first evidence, one pinned-content inspection; none requires personal UAT.
