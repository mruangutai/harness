# BRIEF — FEAT-495-repo-write-grants Repository-scoped factory write grants

## Problem

Factory agents receive role-wide wildcard grants, while the OMP pre-write adapter and worktree claims identify them only by role. Concurrent agents of the same role can therefore reach another declared product's matching control-plane segment or checkout. The factory cannot be treated as safe for concurrent multi-product operation.

## Done when — by perspective

**operator** — I can run factory work concurrently for different declared products knowing that an agent cannot write across the repository boundary. If Harness cannot establish that boundary, the write stops loudly; Harness self-development and the main session keep their current behavior.

**orchestrator** — I can dispatch same-role factory work to distinct declared products without serializing independent product features, because each child is bound to its repository before its first governed write.

**code maintainer** — Write/Edit and detectable Bash writes use one repository-binding decision while the existing target-side two-base classification, worktree claims, and plan-time resolver contract remain intact and protected from drift.

## Success criteria

- SC-01 (operator): Two live same-role factory agents assigned to different declared products can concurrently write only their own permitted control-plane and product-workspace targets; either agent's cross-repository Write, extractable Edit, or detectable Bash write exits 2.
  verify: automated
  evidence: integration
- SC-02 (operator): A product target with missing, reused by another active dispatch, mismatched, stale, released, unreadable, or ambiguous runtime-lineage and repository-claim state exits 2 through both enforcement routes, names the collision/mismatch category, and never falls through to a wildcard role grant.
  verify: automated
  evidence: integration
- SC-03 (orchestrator): Every governed factory-product dispatch validates the repository header, creates a repository-bound claim before spawn, and binds that claim to OMP's host-provided child and immediate-parent runtime identities; missing lineage or an unbound/foreign claim refuses before a governed mutation.
  verify: automated
  evidence: integration
- SC-04 (orchestrator): A live OMP session proves governed children inherit the project extension, every child policy callback receives the host's child and immediate-parent ids (`ctx.agent.id`, `ctx.agent.parentId`), and concurrent same-persona children receive distinct child identities under the correct immediate parent, without putting authority in prompt text, tool arguments, or session artifacts.
  verify: automated
  evidence: inflight_claim_lifecycle_live
- SC-05 (code maintainer): `check-domain.py --resolve --feature FEAT-495-repo-write-grants` preserves its current plan-time ownership result without runtime-lineage or repository-binding lookup.
  verify: automated
  evidence: integration
- SC-06 (operator): The main session, Harness self-development, two independent Kaya feature worktrees, and two same-role children on one product feature retain their current permitted behavior.
  verify: automated
  evidence: integration
- SC-07 (code maintainer): Both guard routes delegate repository and exact runtime-lineage matching to one shared `harness_boundary.py` decision while retaining two-base classification and worktree protections.
  verify: inspection
  evidence: `.claude/skills/harness/bin/harness_boundary.py`
- SC-08 (code maintainer): Caller-authored prompt text, payload fields, environment variables, task names, and task results cannot override the host-provided runtime lineage or repository claim; each refusal names only the actionable mismatch category.
  verify: automated
  evidence: integration

## Verification gaps

- `inflight_claim_lifecycle_live` is locally run: CI cannot prove a credentialed live OMP child receives the project extension and host-provided runtime lineage. Upstream OMP now supplies that lineage natively (#2000 dropped Harness's own runtime pin and lineage probe), so SC-04 reuses BUG-1898's live merge-gate probe, `tests/manual/probe-inflight-claim-lifecycle.py`, whose S3 scenario observes distinct child ids and lineage under a real parent. Its receipt is recorded before ship; deterministic hook and guard integration tests cover repository binding, concurrency, refusal categories, and both write routes.

## Constraints

- Factory-dispatched work for fleet-declared product repositories only; this supplies the boundary and leaves Harness self-development and main-session policy unchanged.
- DEC-174 blocks delegated execution of Harness hook, validator, and gate-script changes and their tests; those tasks are main-session-direct.
- DEC-179 supplies the lineage-free plan-time `check-domain.py --resolve` contract.
- DEC-189 supplies target-side two-base classification; DEC-193 supplies its location protections.
- DEC-204 and DEC-218 supply OMP child/immediate-parent runtime lineage and fail-closed claim authorization; repository authority narrows that claim to one fleet member.
- #495 may proceed alongside #496, but #495 is required before concurrent multi-product factory operation is called safe.

## Out of scope

- Changing Harness self-development into factory-dispatched work.
- Delaying or folding #496's first Kaya proof into this feature.
- Replacing role domains beyond the repository-binding enforcement necessary for factory work.

## Approval

status: approved
approved-by: molchairuangutai
date: 2026-09-24
