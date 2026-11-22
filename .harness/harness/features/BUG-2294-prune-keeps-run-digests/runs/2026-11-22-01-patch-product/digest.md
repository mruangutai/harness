# BUG-2294 — patch intake

Acceptance before dispatch: PM must produce pending BRIEF.md (all patch sections, ≤120 lines) and pending plan.yaml (one T-01, bugfix, five-field decisions_affected, every SC traced). Preserve the operator's UI-only deletion scope, all three run metadata files, unchanged keep rules and ship invocation, and the BLOCKED/no-UI check-state regression. No implementation or unit-test execution. Record exact successful plan-merge check and check-plan-routes commands in notes/research-*.md, including justification for the execution route around the unowned ship-command path. No readers, panel, goal-check or signature; zero send-back cycles expected.

Prototype decision: not required; this patch changes evidence retention, not end-user interaction. The operator may override.

## Assessment

Pending BRIEF.md and the single-task plan pass both planning gates; approval and implementation remain outstanding.

- PM PASS: BRIEF.md has 45 lines, all patch sections, SC-01–03 and pending approval. plan.yaml has pending approval and one bugfix T-01 tracing all three SCs. Research receipt: notes/research-patch-intake.md.
- Both planning gates exit 0, with exact commands and outcomes in that receipt. Gates were run by PM, not rerun by the lead. Implementation and fail-first evidence are explicitly unverified.
- Whole patch is main-session-direct: the unowned .omp/commands/harness-ship.md cannot enter a team task, and the operator permitted this route. No engineering-lead dispatch is needed for build.
- Main authorized adding DECISIONS.md and its regenerated DECISIONS-INDEX.md to the same T-01 because DEC-238's whole-run ship-deletion wording contradicts the settled UI-only behavior. The PM history confirms Main's ruling; no extra behavior or second task was introduced. DEC-238's keep rules and Abandon policy stay untouched.
- SC-01 plans UI-only deletion and byte-preserved records; SC-02 plans the ten-run final-BLOCKED/no-UI regression with real feature-scoped check-state before/after; SC-03 plans unchanged selectors/invocations and corrected retention prose/decision text.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned checkout; PM recorded this without inventing substitutes. The supplied grilling defines this patch.
- No readers, panel, goal-check, unit tests or implementation; zero send-back cycles. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: Pending patch brief and one-task direct plan pass both planning gates;
    approval required.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/runs/2026-11-22-01-patch-product/state.yaml
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: patch-intake
    persona: harness-pm
    verdict: PASS
    headline: Pending brief and single-task direct plan pass both planning gates;
      implementation unverified.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/plan.yaml
  must_fix: []
  branch: feat/BUG-2294-prune-keeps-run-digests
  escalations: []
  adequacy_notes:
  - BRIEF has 45 lines and all required patch sections; both approvals remain pending.
    Exact successful planning commands and outcomes are recorded in notes/research-patch-intake.md.
  - Whole T-01 is main-session-direct because the ship command is unowned; operator
    expressly authorized this route. Do not dispatch build to an engineering lead.
  - Main authorized DEC-238 amendment and regenerated decision index in the same T-01,
    resolving contradictory whole-run ship-deletion prose without changing keep rules
    or Abandon policy.
  - 'No prototype required: no end-user interaction changes; operator may override.
    No readers, panel, goal-check, implementation or unit tests ran.'
  - Assigned checkout lacks docs/spec.md, docs/decisions.md and docs/architecture.md;
    PM recorded the gap without inventing guidance. Implementation and fail-first
    evidence remain unverified.
  sc_status:
  - id: SC-01
    verdict: planned
    method: planning
    evidence: BRIEF SC-01 and T-01 trace UI-only pruning, byte-preserved run metadata,
      kept UI, dry-run and repeat safety; implementation/fail-first unverified.
  - id: SC-02
    verdict: planned
    method: planning
    evidence: BRIEF SC-02 and T-01 trace ten-run final-BLOCKED/no-UI empty-keep regression,
      surviving digest hashes and real check-state before/after; implementation/fail-first
      unverified.
  - id: SC-03
    verdict: planned
    method: planning
    evidence: BRIEF SC-03 and T-01 trace unchanged keep rules and ship invocations,
      corrected retention prose, DEC-238 amendment and index regeneration; pinned
      implementation inspection unverified.
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.harness/harness/features/BUG-2294-prune-keeps-run-digests/runs/2026-11-22-01-patch-product/digest.md
```
