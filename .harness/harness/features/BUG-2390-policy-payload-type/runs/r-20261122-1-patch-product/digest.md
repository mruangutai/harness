# BUG-2390 patch intake

One-task draft is ready; signature must wait for Main's fresh hook-suite baseline receipt and actual pass count. The historical 186 figure was not adopted. See notes/research-patch-intake.md and plan.yaml: T-01 refuses verification without MAIN_BASELINE_PASS_COUNT.

PM authored the <=120-line, by-perspective BRIEF and pending plan. T-01 covers SC-01–03, names only the hook and its test, routes execution directly to Main under DEC-174, and requires test-only compiler-red evidence before production widening. PM reports plan-merge apply/check success; no implementation or tests ran in this product run.

No prototype is required: this internal typing correction adds no end-user interaction. No patch panel/readers/goal-check ran. Approval remains pending for the delegated advisor. Main must obtain and record the baseline count/receipt before signature; this product lead has no shell to capture it.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: One-task patch draft ready; fresh Main baseline receipt required before
    signature
  open_questions:
  - id: Q-01
    question: Main must capture and record the fresh omp-hooks baseline pass count,
      pin and raw-output receipt before signature, then bind MAIN_BASELINE_PASS_COUNT;
      historical 186 was not adopted.
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2390-policy-payload-type/.harness/harness/features/BUG-2390-policy-payload-type/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2390-policy-payload-type/.harness/harness/features/BUG-2390-policy-payload-type/plan.yaml
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: intake
    persona: harness-pm
    verdict: ESCALATE
    headline: Patch draft checks clean; fresh Main baseline count still required before
      signature
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2390-policy-payload-type/.harness/harness/features/BUG-2390-policy-payload-type/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2390-policy-payload-type/.harness/harness/features/BUG-2390-policy-payload-type/plan.yaml
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Approval remains pending for delegated advisor signature.
  - 'No prototype needed: internal typing correction adds no end-user interaction;
    operator may override.'
  - T-01 is main-session-direct under DEC-174, traces every SC, and requires test-only
    static compiler red before production widening.
  - No implementation tests ran; PM reports plan-merge apply/check success.
  - No patch readers, panel, goal-check or plan-flow simplify ran.
  sc_status:
  - id: SC-01
    verdict: planned
    method: inspection
    evidence: T-01 covers honest payload contracts and checked narrowing.
  - id: SC-02
    verdict: planned
    method: automated
    evidence: T-01 requires pinned test-only typecheck failure then green.
  - id: SC-03
    verdict: planned
    method: automated
    evidence: T-01 preserves fresh Main baseline pass count; receipt remains outstanding.
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps:
  - Fresh Main baseline count and receipt not available during intake.
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2390-policy-payload-type/.harness/harness/features/BUG-2390-policy-payload-type/runs/r-20261122-1-patch-product/digest.md
```
