# BUG-2171 — Bounded patch intake ready for signature

One main-session-direct task covers all three SCs; both approvals remain pending. No implementation, panel, reader, goal-check, tests, build, lint, formatter or live smoke was run by this intake.

## Scope and authority

- Settled scope and cause: control-plane .harness/notes/grilling-BUG-2171-task-structured-2026-11-08.md, Destination/Settled/Facts I verified; [source issue #2171](https://github.com/mruangutai/harness/issues/2171). No cause re-derivation.
- Product checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured; base and lane resolution SHA b7af829c0207522b43f978b5275a2ebdc96b3210. Registry feature-root resolved to this checkout.
- Product AGENTS.md maps requirements to .harness/harness/docs/SPEC.md §8.3 and decisions to .harness/harness/docs/DECISIONS.md. DEC-174 reserves execution, including the gate test, to main; DEC-225 supplies one-task patch intake; DEC-237 preserves strict hook injection and validator-owned append.
- Conventional product docs/spec.md, docs/decisions.md and docs/architecture.md are absent. The mapped specification and decisions answer the return-contract question. No standalone architecture document answers component-relationship guidance; this patch introduces no new boundary and invents none.

## Choices and proof contract

- D-01 records the settled native opt-in rather than schema duplication, text parsing or downgrade. Closing-comment versus issue-body correction is cheap/reversible: choose a closing comment at ship, preserving the investigation record. No issue mutation now.
- Proposed closing correction: OMP 18.10.2 introduced native task.structured, default off; Harness never set it. With it off, argument revalidation strips hook-injected outputSchema/schemaMode, children receive no yield, and the existing yield hook never runs. This fix enables task.structured, guards it and clarifies that earlier schema fields were hook-injected. Link the fix SHA and red/green plus live-append evidence when available; do not claim those proofs already exist.
- SC-01: pinned config and exactly one added refusal-text source line; no other hook byte changes. SC-02: new named integration assertions run against the immutable base gate and fixed gate. SC-03: fresh credentialled OMP process, actual child and lead yield calls, human-only before.md, hook-triggered fenced append, canonical digest reader and retained session pointers. plan.yaml T-01.verify supplies runnable commands from the worktree root, including the live smoke; T-01.intent binds runtime/source provenance and forbids manual append or direct validator calls.
- Verification disclosure: integration is active and detects the named test. Typecheck has unresolved/null runner coverage for the .ts text line; pinned diff inspection and live smoke carry the bounded change, not a fabricated typecheck. No exact structured-return smoke runner is registered; durable evidence is inspected. No personal UAT, UI or prototype work is required. No standing runner repair is added to this patch.

## Intake check receipt

Controlled plan creation printed APPLIED with no APPROVAL-RESET receipt; no remote sync was invoked. Its automatic state-hook report named unsigned BRIEF and absent Build-entry receipt, expected before the operator signature; neither was bypassed.

Authorized plan-merge.py check exited 0:

    OK T-01 4 anchor(s) resolved
    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured: 1 task(s), 4 anchor(s) resolved, 0 failure(s)

Artifacts: BRIEF.md and plan.yaml beside this notes/ directory; this file is the pm-owned durable artifact. Only intake metadata was authored. Main signs or amends; implementation and all planned verification remain unexercised. No open scope question.

## Principles applied

- Experience First — operator success is automatic durable return, not merely a green gate; no extra UI or workflow.
- Redesign From First Principles — the native structured-return requirement is folded into the existing return contract and perspectives, not a parallel fallback path.
