# Plan scope and architecture review — BUG-1699-lifecycle-cards — c1

**BLUF: FAIL.** The mission is proportionate and the five-task architecture concentrates lifecycle policy at the right seam, but the specification does not preserve the operator's separately measurable lifecycle checkpoints and does not provide executable proof that the orchestration callers consume the new receipts in the required order.

## Findings

### F-01 — Separately requested lifecycle checkpoints are collapsed into untagged compound criteria

- kind: substance
- severity: high
- consequence: A goal check cannot independently report the operator, orchestrator, and maintainer perspectives or each requested checkpoint. In particular, SC-02 combines Plan, Building, Review, Done, per-card failure continuation, open-child behavior, and abandonment in one result (`BRIEF.md:28-30`), while SC-03 combines atomic reset and all three resume outcomes (`BRIEF.md:31-33`). None of SC-01 through SC-08 carries a perspective tag (`BRIEF.md:25-48`). A partial implementation can therefore be discussed as one compound pass/fail rather than exposing, for example, that must-fix returned cards to Building but the next validation did not return them to Review. Split the operator-requested Plan, initial Ready, ordinary Building, ordinary Review, must-fix Building, post-fix Review, Done, approval-resume outcomes, and reconciliation checkpoints into separately measurable, perspective-tagged criteria; preserve explicit orchestrator and maintainer criteria rather than relying on section proximity.
- refs: operator intake `grilling-bug-1699-lifecycle-cards-2026-09-15.md` Settled bullets 2-5; issue #1699 Confirmed destination; `BRIEF.md:8-21,25-48`

### F-02 — T-03 has no focused verification of the lifecycle caller chain it changes

- kind: substance
- severity: high
- consequence: If a plan/patch command ignores the emitted RESUME station, invokes status before open, fails to react to APPROVAL-RESET, or starts a reader before the post-fix Review transition, T-01's status tests and T-02's plan-merge tests can still pass. T-03's verify block runs only the plan-team structural script, generated-adapter parity scripts, and adapter `--check` commands (`plan.yaml:126-129`); the current versions of those three integration scripts contain no RESUME, APPROVAL-RESET, gh-sync, or lifecycle-station assertion. SC-01 and SC-03 nevertheless promise focused integration scenarios spanning signature/reset through the resulting board phase (`BRIEF.md:25-33`). Add focused executable scenarios that bind the emitted receipts to the canonical callers and assert open→resume ordering, reset→Plan, Build-entry→Building, validation-entry→Review, and fix→phase-review→reader ordering. Adapter parity remains useful but cannot prove the canonical behavior it copies.
- refs: `plan.yaml:91-131`; current callers at `.omp/commands/harness-plan.md:36-45`, `.omp/commands/harness-patch.md:31-38`, `.claude/skills/harness/SKILL.md:121-127`, `.claude/skills/harness/references/build-phase.md:9-12,31-34`

## Spec-compliance audit

- Every SC is traced by at least one task; every task traces a live SC. No orphan or nonexistent SC trace was found.
- The declared task dependency graph is acyclic and topological: T-01 precedes its policy consumers, T-03 follows receipt production, T-04 follows projection, and T-05 follows executable truth.
- Sampled symbol and quoted anchors resolve in the current tree, including `gh_board.py#project`, `gh-sync.py#cmd_status`, `plan-merge.py#_maybe_reset_approval`, `board_lifecycle.py#_status_findings`, INV-26 `case_v`, the approval-reset case, and both adapter `main` symbols. No stale-anchor finding.
- Change types, routes, agents/reasons, literal verify blocks, task status, pending approval, and explicit decisions are present. No task mixes team and main-session-direct execution.
- Preserved contracts are explicit: best-effort outbound writes, six stations, ship-only Done/open-child behavior, abandonment, no inbound authority, no hidden plan-writer network call, and the existing receipt schema (`BRIEF.md:50-75`; `plan.yaml:28-50`).
- Rework remains under the signed ruling and one fix-team run; the planned mechanical phase-review step does not introduce a second approval (`BRIEF.md:15-17`; `plan.yaml:40-43,130-131`). No pending-ruling-field defect: the plan is correctly pending before the main session records the ruling at signature.

## Architecture and proportionality

**Mission proportionality: proportionate; no proportionality finding.** The issue changes visible truth at signature, amendment, Build, validation, rework, ship preservation, and fleet reconciliation, so a plan mission and the five-task graph match the real cross-cutting work. T-03 is broad because the same orchestration contract has canonical and generated carriers; splitting those carriers would create ordering drift rather than useful independence.

`gh_board.project` is a deep-module seam: one small projection interface supplies status mutation, INV-26 drift detection, and reconciliation, giving leverage and locality. `gh-sync.py` and `board_lifecycle.py` remain adapters at distinct live seams (event mutation versus fleet repair), so this is not a hypothetical abstraction. Approval resume metadata stays local; explicit orchestrator callers retain best-effort network ownership. Done and abandonment remain outside the active-phase projection. No new pass-through module or competing policy is planned.

## Open questions

None.

```yaml
VERDICT: FAIL
DIGEST:
  headline: The mission and architecture are proportionate, but compound untagged criteria and missing caller-chain verification leave lifecycle checkpoints independently unprovable.
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "Separately requested lifecycle checkpoints are collapsed into untagged compound SCs.", why: "Goal-check cannot independently expose a missed perspective or lifecycle transition." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-03 does not execute the receipt-to-lifecycle caller chain it changes.", why: "Component and adapter-parity checks can stay green while canonical orchestration uses the wrong station or ordering." }
  must_fix:
    - Split and perspective-tag the separately requested lifecycle checkpoints, then update task traces.
    - Add focused executable verification for the canonical lifecycle caller/receipt ordering changed by T-03.
  spec_violations:
    - { kind: mismatch, path: ".harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md", ref: "operator intake lifecycle checkpoints" }
    - { kind: omission, path: ".harness/harness/features/BUG-1699-lifecycle-cards/plan.yaml", ref: "SC-01/SC-03 executable orchestration proof" }
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1699-lifecycle-cards/.harness/harness/features/BUG-1699-lifecycle-cards/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1699-lifecycle-cards/.harness/harness/features/BUG-1699-lifecycle-cards/notes/review-harness-code-reviewer-plan-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1699-lifecycle-cards/.harness/harness/features/BUG-1699-lifecycle-cards/notes/review-harness-code-reviewer-plan-c1.md
```
