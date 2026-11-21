# BUG-2171 — Task revision and five-row lane mapping ready

SC-04 adds real-handler string-data regression evidence; SC-01 now bounds the hook diff to one added refusal-text line and yield-branch parsing. One main-session-direct T-01 traces all four SCs. Both approvals remain pending and plan status remains plan. No implementation, reader, panel, goal-check, build, tests, lint, formatter or live smoke was executed. Intake cycles: 0.

## Authority and guidance

- Authoritative scope: control-plane .harness/notes/grilling-BUG-2171-task-structured-2026-11-08.md, Settled String data and Signature rulings. The patch remains bounded; dispatch, injection, lifecycle, validator and append are unchanged.
- PRODUCT root resolved with inflight_registry.py feature-root: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured. Immutable base b7af829c0207522b43f978b5275a2ebdc96b3210; assigned HEAD bf1fbb8b.
- Consulted PRODUCT AGENTS.md, mapped SPEC.md §8.3 and DECISIONS.md DEC-174/225/237. Conventional docs/spec.md, docs/decisions.md and docs/architecture.md remain absent (prior intake finding); T-01 preserves mapped guidance pointers. SPEC §8.3 and DEC-237 literally reject strings, conflicting with the newly settled operator JSON-object string ruling; the pending BRIEF and intent explicitly disclose this narrow authority change. No guidance or architecture substitute was authored.
- Hook registerHarnessHooks yield branch currently uses const digest = input.data and rejects strings before validation. Existing real-handler tests assert validation.payload.digest_object; digestText in the non-object loop is non-JSON and must remain refused. tests/unit/test-omp-hooks.py invokes bun test on omp-hooks.test.ts; the active unit matrix runs that wrapper. The unresolved/null typecheck runner covers the new branch and test; Bun behavior evidence is not a static typecheck.

## Proof and scope choices

- SC-04 requires exactly one validator call with deep-equal parsed PASS digest_object, invalid/non-object JSON refusals, retained object coverage and held-run BLOCKED-only semantics through the real tool_call handler. T-01 preserves unrelated verify requirements and adds the Bun wrapper, active unit matrix and isolated immutable-base-hook red/fixed-hook green assertion output. QA must retain both outputs, not merely current green. These commands are future execution instructions, not exercised intake evidence.
- OMP v19.1.0 --help explicitly documents --max-time=<value> with examples 600, 10m, 1h. T-01 now uses --max-time=10m and states timeout is failure; no live smoke ran. Rework baseline was untouched: operator rounds=1/minutes=45 belongs only at signature.
- Closing-comment correction remains selected: explain the missing native task.structured opt-in and bounded string-data handling, linking eventual fix and proof. Preserve original issue and BUG-2169 history; no issue mutation now.
- plan-merge apply printed APPLIED for task revisions, with no APPROVAL-RESET receipt, so no remote sync was invoked. Automatic state-hook output reported pending BRIEF, absent Build-entry receipt and unrelated terminal FEAT-2206 worktree; no bypass or unrelated edit was attempted.

## Intake check receipt

Required plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured exited 0, exact stdout:

    OK T-01 6 anchor(s) resolved
    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured: 1 task(s), 6 anchor(s) resolved, 0 failure(s)

Authorized set-lanes completed with five rows, preserving resolved_at b7af829c0207522b43f978b5275a2ebdc96b3210 and all four existing surfaces. The hook reason now covers refusal text and yield-branch string-data parse; tests/unit/omp-hooks.test.ts is main-session-direct with reason DEC-174 hook regression test. The replacement YAML value is notes/research-lanes.md: pm owns notes/research-*.md, while run-directory bookkeeping belongs to the lead, so the explicitly permitted staging fallback was used.

Set-lanes exited 0; exact mutation receipt:

    LANES 5 row(s) resolved at b7af829c0207522b43f978b5275a2ebdc96b3210 -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml
    APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml

The automatic state hook again reported pending BRIEF, absent Build-entry receipt and unrelated terminal FEAT-2206 worktree, plus historical cycle attribution and dirty-layout notes. These were not bypassed or edited. No APPROVAL-RESET receipt appeared and no remote sync ran.

The required post-set-lanes check exited 0; exact stdout:

    OK T-01 6 anchor(s) resolved
    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured: 1 task(s), 6 anchor(s) resolved, 0 failure(s)

## Adequacy notes

Full run change set: SC-04 added; SC-01 rewritten; smoke bounded to 10m; T-01 files/anchors added for the hook yield handler and unit regression; lanes updated to five rows. This completion changed lanes only, leaving the already-completed BRIEF and T-01 files/traces/verify/intent unchanged. Approval remains pending and plan status remains plan; rework baseline untouched. No implementation verification was executed.

## Principles applied

- Experience First — retain automatic durable return and unchanged actionable refusals, rather than accepting a green gate alone.
- Redesign From First Principles — integrate string-data equivalence into the maintainer perspective, bounded scope and real-handler proof, not a second validator path.

Open questions: none. Written paths in this completion: plan.yaml, notes/research-lanes.md and notes/research-intake.md, all inside this feature directory.
