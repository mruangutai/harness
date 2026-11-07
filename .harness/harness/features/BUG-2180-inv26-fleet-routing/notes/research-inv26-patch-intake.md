# BUG-2180 — patch intake ready for main signature

BRIEF.md and plan.yaml are pending approval: 46 brief lines, exactly T-01, two owned files, source_issues [2180], four automated integration SCs. T-01 declares both execution_mode and execution_agent main-session-direct, plus the DEC-174 reason. No implementation, product test, panel, goal-check or signature was performed. No blocking questions.

## Scope and research

- Settled input: .harness/notes/grilling-inv26-fleet-routing-2026-11-07.md in this feature checkout. Inv26RoutingAdvisor settled separate-patch ordering, loud GhError handling and direct execution; these were retained, not re-decided.
- At control-plane HEAD 4a05030d401593003209f525fd06e00802eccd36, the assigned product board.py symbols _inv26_declared_board, _inv26_numbers, _inv26_stations and inv_26 expose the owner-wide lookup. _inv37_feature already consumes feature_schema.resolve_binding. Resolver output is (repo, board, issue types); bound resolution can raise artifact_accessors.FleetError. Existing integration fixtures and fake-gh argv dispatch are the test seam.
- Reversible diagnostic choice: INV-26 CANNOT VERIFY <feature>: invalid authoritative repository binding: <error>. Feature plus original binding error is required; a separate repository field is unnecessary because invalid bindings need not supply a valid repository. No approval-worthy new D-NN trade-off.
- Explicit missing guidance: assigned PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md do not exist (docs directory listing contains PRINCIPLES.md and invalid-states-audit.html). No contents or precedence invented. AGENTS.md independently maps this repository's Harness authority to .harness/harness/docs/SPEC.md and DECISIONS.md; DEC-174, DEC-221 and DEC-225 were consulted as adopted constraints, not substitutes for missing product documents.
- Active unit/integration commands exist in control-plane harness.json; integration detect matches the named test. The runtime-code unit floor remains a validation obligation, not a waiver. Fake-gh acceptance needs no live availability proof. #2181, INV-30, gh-sync and Kaya corpus remain out of scope.

## Requested validator receipts

CWD for both commands: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2180-inv26-fleet-routing

Command (exit 0):
```text
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2180-inv26-fleet-routing/.harness/harness/features/BUG-2180-inv26-fleet-routing/plan.yaml
```
Output:
```text
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
DEVIATION T-01 .claude/skills/harness/bin/check_state/board.py, tests/integration/test-check-state-inv26.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
0 violation(s) across 1 plan(s)
```
The TASK deviation is the intended DEC-174 direct-execution carve-out, not a manifest deviation or violation.

Command (exit 0):
```text
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2180-inv26-fleet-routing/.harness/harness/features/BUG-2180-inv26-fleet-routing/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2180-inv26-fleet-routing
```
Output:
```text
OK T-01 2 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2180-inv26-fleet-routing/.harness/harness/features/BUG-2180-inv26-fleet-routing/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2180-inv26-fleet-routing: 1 task(s), 2 anchor(s) resolved, 0 failure(s)
```
Plan creation used the canonical control-plane plan-merge.py apply --proposal -; it emitted APPLIED and no APPROVAL-RESET receipt, so no gh-sync status call was made. Its automatic changed-state hook reported the unsigned BRIEF and absent INV-37 Build-entry receipt, plus pending/historical-attribution/untracked-feature notes. These are not passing production evidence or reasons to sign during intake. A discovery invocation of check-plan-routes.py --help exited 2 because this CLI treats every argument as a plan path; the actual plan-specific invocation above passed.

## Principles applied

- Redesign From First Principles — put repository identity into the operator perspective and every routing/error test instead of appending a Kaya-only exception; reuse the shared binding resolver and preserve owner controls.

## Open questions

None blocking. Main alone signs; red-first and green integration evidence plus configured validation remain to be exercised after signature. This receipt is intake evidence only, not SC delivery evidence.
