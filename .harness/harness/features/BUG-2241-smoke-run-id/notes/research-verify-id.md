# BUG-2241 — verify-id patch intake

BRIEF.md and plan.yaml are pending; both required intake gates exit 0. The requested change is one 44-word resident rule, but no configured squad persona can edit this skill: the resolver returns NOBODY. T-01 therefore declares the only existing legal route, main-session-direct, under the assignment's conditional fallback and DEC-179. This explicitly departs from the requested team packaging and needs routing acknowledgement before signature; no execution_agent or grant was fabricated. Implementation has not begun.

## Scope and guidance

- Mission and scope: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-BUG-2241-smoke-run-id-2026-11-21.md, Settled and Out of scope. Its verified BUG-2171 history was accepted without re-testing.
- PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id; baseline HEAD 594af2a8123771da1a5290942400f4f8a064656f. Control-plane HEAD 926383aef86ee505d2909c291ef4ab672b8ea09b.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent from this checkout's docs directory. Question: no product architecture document describes a new interface here; none is being introduced. AGENTS.md Project map instead identifies the product's .harness/harness/docs/SPEC.md and DECISIONS.md. SPEC section 6 explicitly reserves rule-skill edits to the human; section 11.2 supplies the task contract. No missing document was invented or edited.
- DEC-158 move 1 supplies rule + one-clause why + DEC pointer; DEC-182 supplies the existing verify contract; DEC-179 requires declared main-session-direct routing for an ungranted file; DEC-225 supplies the one-task patch lane but normally requires team. These last two requirements conflict for this exact target. The product routing regression test tests/integration/test-check-domain-grant.py, case (c), explicitly expects this skill to resolve to NOBODY (inspection only, not executed).
- Backlog read: gh issue list --repo mruangutai/harness --state open --limit 100, cwd /Users/molchairuangutai/GitHub/harness, exit 0; issue 2241 matches the grilling; issues 2239/2240 remain separate. Source: https://github.com/mruangutai/harness/issues/2241.
- change_type docs is configured with always: [] in .harness/harness.json. This is guidance text only, not runtime logic or an enforcement change; docs is appropriate despite the issue being a bug. The TDD production-code cycle is exempt, but SC-01 still requires a failing-before/passing-after content assertion. An unrelated green unit suite is not that evidence.

## Proposed resident text

Append one paragraph at the end of the existing verify literal-block section, before The panel result:

> A verify step creating durable state (a run, issue, branch or other named record) MUST derive a fresh id at execution (timestamp or run counter) or receive one as a parameter; a literal single-use id is a defect because validation cannot re-run it (DEC-182).

No mechanical detector, no BUG-2171 recipe rewrite, no new helper, no new interface, no extra task or decision. The eventual source diff owns only .agents/skills/harness-spec-driven/SKILL.md, whose tracked spelling for git show is .claude/skills/harness-spec-driven/SKILL.md.

## Domain evidence

Cwd: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id

Command:
```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-domain.py --resolve /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.claude/skills/harness-spec-driven/SKILL.md
```
Output (exit 0):
```text
NOBODY
```
The resolver enumerates all manifest roles, not a requested candidate. .harness/team-config.yaml grants documentor docs/** and .harness/*/docs/**, not skills; backend/dev-ops grants reach only .claude/skills/harness/bin/**. There is no execution_agent to select honestly. A route question was sent directly to the product lead; no grant, approval or feature.json was changed.

## Preload and word budget

Cwd for measurements: PRODUCT checkout above. Current skill: 1137 whitespace words from wc -w on its absolute .agents path. Proposed paragraph: 44 words from printf of the exact text piped to wc -w; projected skill 1181 (+44). Keep the eventual net delta at 44, with no history or procedure added.

Budget inspection command:
```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-skill-weight.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id
```
Exit 0. Report: pm 5001, universal 1476, total 57123 across 16 agents; no notes or violations. .harness/harness.json budgets.preload_warn_words is agent 5500 / universal 1900. Since only pm preloads this skill, projected pm 5045, universal unchanged 1476, total 57167. These are projections, not post-implementation measurements; warning thresholds are advisory, not hard errors.

The preceding --json invocation exited 1 with NameError: name 'json' is not defined at check-skill-weight.py main. The supported plain interface above supplied the measurements; no script was fixed. This unrelated reporting defect remains out of scope.

## Verification design

SC-01's supplementary unit-level assertion must read the actual paragraph inside the verify section via git show at an explicit pin, normalize whitespace, and compare the complete rule text. QA must capture red at baseline 594af2a8123771da1a5290942400f4f8a064656f and green at review_sha. No such check was run during intake. The docs matrix has no required suite; the inline assertion is supplemental evidence, not a claim that run-unit-tests.py discovers it. Inspection separately judges the rule's author-facing clarity, single-file scope, and brevity at the pin. No UAT or goal-check run is needed.

## Principles applied

- Experience First: describe the operator's rerun and the pm author's usable guidance, not a detector or a new interface.
- Redesign From First Principles: put the rule in the existing verify contract rather than a second procedure or exception for BUG-2171.

## Open questions

- Routing: the requested team task cannot name any granted execution_agent. A declared main-session-direct task is the only existing legal route; resolve this explicitly rather than fabricating a grant.
- Out-of-scope defect: check-skill-weight.py --json raises NameError; plain output works.

## Pending artifacts and intake gates

BRIEF.md is 47 lines (wc -l, exit 0), with three perspectives and three SCs, all traced by T-01. Both Approval records remain pending. plan.yaml was created only through plan-merge.py apply --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/plan.yaml --proposal - (exit 0); apply seeded approval.status pending. It printed APPLIED, with no APPROVAL-RESET receipt, so no remote status command was called.

Exactly one task, one source anchor, source_issues [2241], change_type docs, decisions []; literal verify block; 13 nonblank task lines before intent, below the 50-machine-line ceiling. The task has execution_reason instead of execution_agent because its file is ungranted. No panel was authored and no readers or goal-check ran.

Apply's automatic check-state --changed reported unsigned BRIEF and absent Build-entry receipt (INV-37), pending approval, unknown historical cycle attribution, and an untracked feature-directory note. These are not claimed green or repaired by this intake: signature, Build-entry and run metadata are outside the PM write scope.

Both following commands ran AFTER BRIEF.md and plan.yaml landed. Cwd for both: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id.

Plan anchor/trace gate command:
```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id
```
Output (exit 0):
```text
OK T-01 1 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id: 1 task(s), 1 anchor(s) resolved, 0 failure(s)
```

Scoped route gate command:
```text
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/plan.yaml
```
Output (exit 0):
```text
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01: declared main-session-direct (.agents/skills/harness-spec-driven/SKILL.md ungranted)
0 violation(s) across 1 plan(s)
```
The script's main(argv) accepts positional plan FILE paths; supplying this file avoids inspecting unrelated live plans. An exit-zero direct route is not evidence of a team grant. SC-01/02/03 remain not_met because their future source change, QA red/green receipts and pinned inspections do not exist yet. No build, lint, formatter, unit/integration suite, proposed task verify, skill edit, feature.json write or approval signature was performed.
