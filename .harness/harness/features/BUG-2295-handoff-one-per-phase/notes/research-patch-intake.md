# Patch intake — BUG-2295

Ready for operator signature: BRIEF.md is 48 lines; plan.yaml is 64 lines with exactly T-01, bugfix, main-session-direct, all four SC traces, three assigned files and four five-field keep dispositions. Both approvals remain pending. No production implementation or tests ran.

## Scope and evidence

- Operator-settled grilling: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-handoff-one-per-phase-2026-11-22.md. Issue 2295 and the open backlog were read; the issue's INV-17-at-done claim is stale, not adopted scope. Issue 2219 concerns the separate ship prerequisite policy; it is not included.
- Baseline dd04e52a898109fdbe09cf5fa14e1148161734d0. Supplied main-session measurement is retained in Problem without re-derivation: only team-built FEAT-2229 lacked the canonical note; the remaining omissions were all-main-session-direct exemptions.
- Product anchors: check-domain.py _rule_handoff and RE_HANDOFF including Edit reconstruction; gh-sync.py cmd_ship comment and unchanged handoff predicate; tests/integration/test-check-domain-post.py _handoff_grammar_cases and _handoff_pointer_cases. The grilling's unit-test path is stale; the plan uses the existing integration file.
- Missing product guidance: PRODUCT /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/docs contains neither spec.md, decisions.md nor architecture.md. Thus those files supply no requirements, adopted rationale or component guidance for this patch. No contents or precedence were invented; the settled filename correction and existing code suffice for the bounded draft.
- DEC-174 governs direct execution; BUG-2305 main-corpus plan confirms omission of execution_agent for direct tasks. DEC-225 retains one-task/no-panel/no-goal-check intake; DEC-252 explains the stale comment; DEC-254 supplies exact five-field keep rows. No hard-to-reverse new choice warrants a D-NN.

## Authorized validation receipts

Both commands used the control-plane scripts and completed successfully:

1. python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase
   Exit 0: 1 task, 3 anchors resolved, 0 failures.
2. python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/plan.yaml
   Exit 0: 0 violations across 1 plan. TASK DEVIATION is the intentional DEC-174 direct carve-out, not a manifest violation.

CLI discovery found check-plan-routes.py treats --help as a path (ERROR: --help does not exist); source inspection established its positional plan-file CLI. The actual scoped route check above passed. plan-merge.py apply emitted APPLIED, without APPROVAL-RESET. Its automatic post-write check-state messages report the expected pending brief and missing pre-signature Build-entry receipt; no signature, gh-sync, standalone state audit, panel, readers or goal-check was run.

## Principles applied

- Experience First: refusal must name the canonical note and tell the operator to supersede it, not merely reject a filename.
- Redesign From First Principles: enforce the single convention in the existing handoff rule while retaining routing for invalid names; do not add a second ship convention.

## Open questions

None blocking this bounded draft. Main owns signature and subsequent test-first implementation, literal integration verify, qa and pinned inspection for SC-03/SC-04. No UAT or prototype is needed for this internal filename rule.
