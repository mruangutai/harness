# BUG-2328 — patch ready for signature

BRIEF.md and plan.yaml are pending. The bounded plan has exactly T-01, main-session-direct under DEC-174, exactly the two supplied implementation files, a lanes table at dd04e52a898109fdbe09cf5fa14e1148161734d0, and traces to all three SCs. No new D-NN is needed: removal and rejected cache alternatives were operator-settled. No source files changed and no implementation tests ran.

## Authority and scope

- Operator-confirmed input: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-digest-schema-cache-2026-11-22.md, Destination, Settled, Out of scope and Facts I verified; accepted without re-derivation. Source: https://github.com/mruangutai/harness/issues/2328.
- Retain aliases/projection and per-call BundleLoader.#documents; remove only process-lifetime BUNDLES and update existing comments. Require temporary-common.json behavioral red at dd04e52a and green after; both content-equivalence updates and distinct-copy preservation are explicit in T-01.
- PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2328-digest-schema-cache. docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no guidance invented or substituted. CLAUDE.md/AGENTS.md confirm the direct-execution boundary.
- Backlog vote read with gh issue list --repo mruangutai/harness --state open --limit 100 (exit 0). #2329 records generic unit runner missing Bun files; direct bun test is mandatory. #2257 owns unresolved null typecheck. Both gaps are disclosed at signature, neither silently fixed or claimed passing.
- All grilling exclusions retained, including host restart for TypeScript edits, unchanged Python subprocess validation and no broader #2195 work (operator says closed through #2230). No reader/panel/goal-check or prototype: assigned patch intake adds no end-user interaction.

## Required gate evidence — 2026-11-22

All commands used control-plane scripts under /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/ and ran from the assigned PRODUCT worktree. Let PLAN mean the absolute assigned feature path ending .harness/harness/features/BUG-2328-digest-schema-cache/plan.yaml; ROOT means the PRODUCT checkout above.

- python3 <control-plane-bin>/plan-merge.py check --file PLAN --root ROOT: exit 0; 1 task, 2 anchors resolved, 0 failures.
- python3 <control-plane-bin>/check-plan-routes.py PLAN: exit 0; owner MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; T-01 declared main-session-direct for ungranted digest-schema.ts; 0 violations across 1 plan.
- python3 <control-plane-bin>/check-plan-routes.py --canonical-reader-audit: exit 0; 0 unresolved reader sites across 100 Python files. The actual interface accepts audit standalone only (main, lines 2620–2628); adding PLAN would treat the flag as a filename, not scope the audit. Ordinary route gate alone takes the absolute plan selector.
- Interface discovery via --help exited 2 because this script has no help option; its source established the valid selectors before the required gates. No implementation test, build, linter or formatter ran.
- plan-merge apply succeeded; its automatic changed-state advisory reported pending BRIEF approval and absent Build-entry receipt. These remain main-session signature/open duties, not an intake approval or a failed plan gate. No APPROVAL-RESET receipt was emitted; no remote status update was invoked.

## Open questions

None. Main owns approval/signature and subsequent direct build. SC outcomes are not yet graded; automated red/green and pinned inspection evidence are required during validate, not manufactured at intake.
