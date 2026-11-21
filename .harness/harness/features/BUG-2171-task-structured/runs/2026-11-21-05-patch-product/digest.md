# T-01 budget amendment requires Main-owned prerequisites

BLOCKED: plan remains unchanged and approved. Before count is 75 (supplied CI failure); no after count or successful gate is claimed. No suites, smoke, checks or commits ran.

PM's durable handoff is notes/research-BUG-2171-task-structured-budget-trim.md: it records all preserved checks, exact extracted-body fingerprints, invariant fingerprints and the scoped justification to relocate.

Two prerequisites require Main:
1. Create/own the feature-local notes/verify-task-structured.py helper; PM's manifest grants plan.yaml and research notes, not arbitrary helper scripts. Main could not answer while its blocking lead dispatch was live.
2. Use plan-merge.py revoke-approval as the approval owner. Actual control-plane plan_merge/amend.py#_amended_text explicitly keeps the signature for existing-field replacements (BUG-1716 D-04); plan_merge/union.py#_carry_base_items resets only task-set changes. Thus the CLI header's broader reset description is stale. No unauthorized temporary task-set change or manual approval edit was attempted.

Once supplied, PM can amend only T-01 intent/verify, retain every suite and historical red/green/append assertion, keep the smoke command referenced, and run the requested route check plus required plan check. This is not a plan-panel or prototype feature; no interaction surface is changed. Member: harness-pm BLOCKED, zero send-backs.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: 'T-01 remains unchanged: Main must own the helper and revoke approval;
    existing-field plan amendments do not reset signatures.'
  open_questions:
  - id: Q-01
    question: Main must create/own notes/verify-task-structured.py outside PM's manifest
      domain, then redispatch the contract amendment.
    blocking: true
  - id: Q-02
    question: 'Main must invoke plan-merge.py revoke-approval: current apply/amend
      retain approval for existing-field replacements, contrary to their stale header
      description; changing the task set solely to force reset would violate scope.'
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/notes/research-BUG-2171-task-structured-budget-trim.md
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: trim
    persona: harness-pm
    verdict: BLOCKED
    headline: Helper ownership and actual approval-reset policy prevent the requested
      amendment; plan unchanged.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/notes/research-BUG-2171-task-structured-budget-trim.md
  must_fix:
  - Supply Main-owned verification helper.
  - Reset approval through Main-only revoke-approval, amend T-01 without semantic
    changes, and record passing route check and final machine-field count.
  branch: none
  escalations: []
  adequacy_notes:
  - 'Before count: 75, from supplied CI failure; no failing baseline was rerun. No
    after count is claimed because plan was not changed.'
  - PM preserved exact verification-body and invariant fingerprints in its research
    artifact; no product source, tests, config, BRIEF, SCs or plan fields changed.
  - 'Source-confirmed blocker: control-plane plan_merge/amend.py#_amended_text sets
    reset=False; union.py#_carry_base_items resets only task-set changes.'
  - 'No checks, suites, live smoke or commits ran. No prototype is required: this
    amendment changes no end-user interaction.'
  sc_status: []
  needs_approval: true
  severity_max: med
  matrix_ok: none
  coverage_gaps:
  - Requested final route check and machine-field count remain pending Main-owned
    prerequisites.
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/runs/2026-11-21-05-patch-product/digest.md
```
