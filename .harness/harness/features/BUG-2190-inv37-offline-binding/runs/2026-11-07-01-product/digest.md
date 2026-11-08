Pending patch intake is ready for main's signature; no implementation or signature was performed. Zero send-back cycles.

PM: PASS — BRIEF.md remains below 120 lines; plan.yaml contains one pending-approval T-01, three required file anchors, matching main-session-direct lane rows and literal verification commands. Six criteria cover offline local authority and receipt/provenance failures, invalid local bindings, unchanged authenticated verification and owner/unbound controls, plus the DEC-217 unit floor. Small independent tests are required to avoid the sibling patch's complexity failure.

Evidence: notes/research-offline-binding.md preserves the authorized route check (0 violations across this plan) and plan-merge check (0 failures). These are intake gates, not production verification. The research receipt discloses pending repository-state findings from automatic hooks; it does not claim a green repository gate.

The pending BRIEF explicitly exposes DEC-221's unconditional remote-verification wording versus the assigned operator-authorized narrow offline exception; approval adopts only that scoped behavior. Shared resolve_binding remains unchanged. Optional offline note omitted. Prototype not required: noninteractive checker correction, no new user interaction; main may override. No panel or goal-check, as required for this patch lane.

Member artifact: notes/research-offline-binding.md. Approval remains with main.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'Patch intake ready: pending approval, route and plan checks pass.'
  open_questions: []
  files_touched:
  - .harness/harness/features/BUG-2190-inv37-offline-binding/BRIEF.md
  - .harness/harness/features/BUG-2190-inv37-offline-binding/plan.yaml
  - .harness/harness/features/BUG-2190-inv37-offline-binding/notes/research-offline-binding.md
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: intake
    persona: harness-pm
    verdict: PASS
    headline: Pending BRIEF and single-task plan satisfy intake gates.
    files_touched:
    - .harness/harness/features/BUG-2190-inv37-offline-binding/BRIEF.md
    - .harness/harness/features/BUG-2190-inv37-offline-binding/plan.yaml
    - .harness/harness/features/BUG-2190-inv37-offline-binding/notes/research-offline-binding.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Route check: 0 violations; plan-merge check: 0 failures.'
  - Production verification not run; approval remains pending.
  - DEC-221 wording conflict and authorized narrow offline exception are explicit
    in the pending artifacts.
  - Prototype unnecessary for this noninteractive gate correction; main may override.
  - No panel or goal-check, per patch lane.
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding/.harness/harness/features/BUG-2190-inv37-offline-binding/runs/2026-11-07-01-product/digest.md
```
