# BUG-2239 JSON fold intake — 2026-11-21

The bounded patch now includes the JSON crash: six criteria, one main-session-direct task, eight owned production/test paths. Both approval records remain pending. Existing route enforcement, exact injection note, refusal preservation and #2241 exclusion remain unchanged. No source/test implementation, commit, feature.json or STATE.md mutation was performed.

## Authority and assessment

- Settled authority: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-BUG-2239-route-gate-and-injection-note-2026-11-21.md, Settled. The reported NameError at immutable base 926383aef86ee505d2909c291ef4ab672b8ea09b is ground truth, not rerun during intake.
- Product guidance: .harness/harness/docs/SPEC.md sections 8.3 and 11.1; .harness/harness/docs/DECISIONS.md DEC-174, DEC-182 and DEC-225. Conventional docs/spec.md, docs/decisions.md and docs/architecture.md remain absent inputs.
- Existing check-skill-weight.py main calls json.dumps without importing json. Its existing integration suite provides _tree and scan/plain-mode assertions but no actual JSON CLI assertion. Extend that existing suite, not a new runner or test file.
- SC-06 is the sole added criterion. T-01 owns both JSON paths, traces all six criteria, executes the added integration file and retains the existing verification chain. Machine fields are well below the 50-line ceiling (eight file anchors and one verify command); the route gate below enforces that ceiling.
- Main must preserve authentic red from the same newly added subprocess regression against the exact immutable base, then green against the fixed subject, including commands, identities, exits and output. A copied baseline must retain sibling dependencies. Intake success is not regression evidence. Every state-producing verification execution, retry and copied fixture plan requires a freshly minted identity.

## Authorized intake gate evidence

Cwd for both: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note. Each gate executed once after intake edits.

1. Command: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.harness/harness/features/BUG-2239-route-gate-and-injection-note/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note
   Exit: 0. Output: OK T-01 8 anchor(s) resolved; CHECK reports 1 task(s), 8 anchor(s) resolved, 0 failure(s).
2. Command: python3 .claude/skills/harness/bin/check-plan-routes.py .harness/harness/features/BUG-2239-route-gate-and-injection-note/plan.yaml
   Exit: 0. Output: MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; OK T-01: declared main-session-direct (.omp/extensions/harness-hooks.ts ungranted); 0 violation(s) across 1 plan(s).

Controlled amendments emitted no APPROVAL-RESET receipt, so no remote status synchronization was invoked. Their automatic check-state hook reported the expected pending brief and missing Build-entry receipt; these are not claimed resolved by the two intake gates. No builds, linters, formatters, regression tests or production smoke runs were executed.

## Principles applied

- Redesign From First Principles: integrated JSON reporting into both perspectives, scope ownership, lanes, traces and execution verification, rather than adding an unowned exception.

## Open questions

None about scope or implementation. Required independent simplification readers are coordinated by the product lead; their findings must be settled before signature. No UAT criteria require personal operator execution.
