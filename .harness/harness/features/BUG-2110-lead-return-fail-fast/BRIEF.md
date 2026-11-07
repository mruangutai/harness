# BRIEF — BUG-2110-lead-return-fail-fast Lead return failures stop at start

## Problem

Harness leads can complete their work and then have every return refused because a prerequisite was already unsatisfied at start. In [#2110](https://github.com/mruangutai/harness/issues/2110#issuecomment-6030231316), no open registered lead run existed, `digest_destination.py bind` failed, and `harness-hooks.ts` silently continued without `digestBinding`; claim release was not the cause. In [#2097](https://github.com/mruangutai/harness/issues/2097#issuecomment-6030231445), a plan panel ran after signature even though its return requires pending approval. Operators inherit wasted panel work and repeated unexplained refusals. These causes were verified by the main session at origin/main `63cac11a`.

## Done when — by perspective

**orchestrator** — I cannot spend a lead run or its readers' work on either known startup condition that makes its return impossible. The run stops before substantive work, not when it tries to return.

**operator** — I receive the exact failed prerequisite and an actionable remedy at start, so I can correct the dispatch without guessing, relabelling the review, or weakening a gate.

**code maintainer** — I can rely on the existing return authorization and pending-only plan-review contracts remaining enforced, while correctly prepared runs still complete normally.

## Success criteria

- SC-01 (orchestrator): For each of `harness-eng-lead`, `harness-product-lead`, and `harness-validator-lead`, a start with no matching open registered lead run, or more than one, is refused before substantive lead work or reader dispatch; it cannot silently continue without a trusted digest binding. QA must demonstrate the startup assertions failing against `63cac11a` before the fix.
  verify: automated        evidence: unit
- SC-02 (orchestrator): A plan-panel start targeting a plan whose `approval.status` is not `pending` is refused before lead assessment or reader work, rather than first refusing at yield. Exercise an approved plan and missing approval status; QA must demonstrate these startup assertions failing against `63cac11a` before the fix.
  verify: automated        evidence: integration
- SC-03 (operator): The startup refusal for a missing or ambiguous registered run names the actual binding failure and the affected feature/lead, and explains how to establish exactly one matching open run, including `feature-record.py run-start` for a missing run. The plan-panel refusal identifies the target and observed approval status, states that plan panels run before signature, and directs the caller to the pending-plan phase rather than recommending an approval toggle or review relabelling. QA must demonstrate both diagnostic assertions failing against `63cac11a` before the fix.
  verify: automated        evidence: unit
- SC-04 (code maintainer): Correctly prepared lead runs with exactly one matching open registered run still start and return through their authorized digest destination, and a pending-plan panel still returns normally. Missing trusted binding and non-pending plan reviews remain refused by return-time validation, including when approval changes after a valid start. QA must first demonstrate failing states for the new startup-to-return regression assertions and use gate-loosening mutants to prove the retained refusal assertions discriminate.
  verify: automated        evidence: integration

## Verification gaps

- `unit` and `integration` have active runners in `.harness/harness.json`; hook behavior is runnable through `tests/unit/test-omp-hooks.py` and `omp-hooks.test.ts`, and gate integration through `tests/integration/test-dispatch-guard.py` and `test-validate-digest.py`. No SC relies on a null or excluded runner.
- `typecheck` is unresolved with `cmd: null` and detects `.omp/extensions/harness-hooks.ts`. SC-01 and SC-03 use executable unit assertions, not proof of static TypeScript correctness; SC-02 and SC-04 use integration assertions. Static type checking remains unproven. If required by the resulting diff, this kind is BLOCKED, never skipped; recommend a dev-ops runner task/backlog item during planning.
- Automated hook/gate coverage does not claim execution in a fresh credentialled OMP session. No UAT criterion is required: the promised timing, diagnostics, and gate outcomes are deterministic assertions, not personal judgement.

## Constraints

- Mission: `plan`, as settled by the operator. This intake authors only the pending brief; the exact refusal location (before spawn, at run start, or both) remains a plan decision, not a prescribed implementation.
- DEC-174 (BLOCKS team execution; SUPPLIES main-session-direct routing): enforcement-layer changes and their tests must be built directly in this feature worktree. The settled gate surfaces are `.claude/skills/harness/bin/validate-digest.py`, `digest_destination.py`, `dispatch-guard.py`, `.omp/extensions/harness-hooks.ts`, and their tests.
- DEC-237 (BLOCKS authorization bypass; SUPPLIES the hook-owned digest binding): preserve the runtime identity, feature, checkout, and sole open registered squad-run binding. A matching `feature.json` `runs[]` entry has the lead's agent/squad, verdict `PENDING`, and no `ended_at`; the normal registration mechanism is `feature-record.py run-start`.
- DEC-228 (BLOCKS retrospective plan-panel acceptance; SUPPLIES pre-signature plan-target review): `plan:<path>` reviews require pending plan approval. The #2095 signature gate against open gating findings remains intact; no gate is loosened.
- DEC-229 (SUPPLIES legitimate return to pending after task-set change): use the existing approval-reset lifecycle, not an ad hoc status toggle, when a signed plan actually needs revision and another panel.

## Out of scope

- Loosening the pending-only plan-review rule or accepting retrospective plan panels — the operator confirmed that panels run before signature and the rule is intended.
- Docs-only closure — the operator requires runtime fail-fast behavior, not instructions that leave the late refusal reachable.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-10-07
