# Decision dispositions — pending draft receipt

BRIEF.md and plan.yaml are drafted pending, with three file-disjoint tasks, seven SCs, one new D-01 → DEC-254 decision, and eight honest decisions_affected rows. The assigned existing plan check passes. This is a draft handoff to the plan readers, not implementation or signature readiness.

## Inputs and findings

- Operator-confirmed scope: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-decision-dispositions-2026-11-21.md, especially Settled; [issue #2229](https://github.com/mruangutai/harness/issues/2229) is intake, not overriding authority. Open backlog consulted; unrelated tickets were not incorporated.
- Baseline observed at e839075e7b6445bb519984b2351a8eb05d49fbfd. Existing creation seam is plan_merge/union.py#_seed_new_plan; checker seam is plan_merge/check.py#cmd_check; shared shape seam is harness_yaml.py#validate_plan_doc. The current checker does not yet enforce this feature's new dispositions.
- PRODUCT/docs/spec.md, docs/decisions.md and docs/architecture.md are absent. PRODUCT/AGENTS.md points to .harness/harness/docs/SPEC.md, DECISIONS.md and DECISIONS-INDEX.md; their applicable planning, evidence and decision sections were consulted. No missing document was invented.
- DEC-188 is amended, not struck: replace its human-only enforcement assertion while retaining flat-contradiction and softer-strike rules. DEC-205 is kept: amendment means rewrite current truth, not restore dated amendment subsections. Other keep rows preserve DEC-73/174/179/182/227/228.
- D-01 makes the compatibility tradeoff visible: writer-stamped drafted_at on future creations, decision_dispositions_era_start in configuration, legacy undated drafts untouched. Existing sc_status can carry DEC-identified verdict/method/evidence rows; no new digest schema or validate script is needed.

## Routing and experience

T-01 is main-session-direct for schema/writer/check/era changes and gate regressions. T-02 is main-session-direct for unowned canonical .omp roles and shipped skill/template/team contracts plus coupled prompt regressions. T-03 is harness-documentor for owned DECISIONS.md, generated index and SPEC changes; depends_on orders both prior tasks first. The check resolves all 19 anchors/routes with no overlap advisory. No squad is assigned an unowned path by subject matter.

No prototype is needed: this is a non-UI schema/prompt/gate change, with no new interactive surface. SC-01 uses unit; SC-02/03/07 integration; SC-04/05/06 pinned artifact inspection. No UAT criterion is assigned. Static prompt tests are explicitly not proof of agent conduct; the eventual validate run must grade this feature's DEC-188 amendment.

## Exact check receipt

Invocation after the final controlled amendments:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions

Observed exit 0, 1.94 seconds: OK T-01 (8 anchors), OK T-02 (8), OK T-03 (3); CHECK: 3 tasks, 19 anchors, 0 failures. An initial check also exited 0 before verify blocks were hardened with fail-fast shell preambles.

All plan mutations used plan-merge.py: apply; amend T-01.verify; amend T-03.verify; set-key decisions_affected. Each exited 0 and printed its stdout. None emitted APPROVAL-RESET:, so no gh-sync call was made. Writer-triggered advisory check-state output reported the deliberately unsigned BRIEF and absent future Build-entry receipt; those were not converted to approvals or remote state. No builds, test suites, linters, formatters or production changes were run/made.

Created: BRIEF.md, plan.yaml and this notes/research-decision-dispositions.md under the assigned feature directory. The task verification commands are future implementation instructions, not executed evidence.

## Principles applied

- Experience First — one disposition record, no redundant blast-radius prose or reciprocal-link mechanism; no visual prototype for a non-UI change.
- Redesign From First Principles — integrate the record into the existing writer, draft check, scope prompt and Mode 2 instead of adding a parallel validate subsystem.
- No more specific than necessary (PRINCIPLES §6) — constrain observable checks and evidence while leaving helper decomposition to implementation.

## Open questions and remaining gates

No unresolved product question. The independent plan readers, panel recording/apply and one final perspective goal-check belong to subsequent plan-team steps. The required four separate harness-simplify angle dispatches must occur before signature; the product lead was asked to orchestrate them because pm has no spawn tool. No simplify result, panel record or approval is claimed here. DEC-254 was unused at the baseline; T-03 must report a later allocation collision rather than overwrite another decision.
