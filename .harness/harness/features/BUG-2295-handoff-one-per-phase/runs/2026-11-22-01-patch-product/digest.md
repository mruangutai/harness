# Patch intake acceptance

Accept the PM draft only when BRIEF.md is at most 120 lines with every patch section and pending Approval; plan.yaml has pending approval and exactly T-01, main-session-direct, bugfix, all SC traces, five-field decisions_affected, the three assigned code/test paths, and a literal verify block running tests/integration/test-check-domain-post.py. PM's research receipt must preserve successful plan-merge check and route-check commands and exit codes.

SCs must cover cycle-suffixed handoff refusal and canonical supersede guidance, correction of the stale INV-17 comment, unchanged ship predicate, and preservation of shipped historical suffixed notes. No reader, panel, goal-check, implementation, or signature belongs to this run. Escalate an unbounded change or new public interface rather than widening the patch.

# Patch intake PASS — pending main signature

BRIEF.md has 48 lines and every patch section; its Approval remains pending. plan.yaml has exactly T-01, pending approval, bugfix, main-session-direct, all four SC traces, five-field decision dispositions, the three requested source/test paths, and a literal verify block running tests/integration/test-check-domain-post.py. No execution_agent is needed for the direct-task convention.

## Member assessment

- draft · harness-pm · PASS: bounded intake meets the pre-dispatch acceptance criteria. Artifact: ../../notes/research-patch-intake.md. That receipt records exact plan-merge.py check and check-plan-routes.py commands, each exit 0. Lead inspected BRIEF.md, plan.yaml and receipt on disk; no shell checks repeated.
- SC-01/02 specify test-first refusal and canonical acceptance across Write/Edit; SC-03 corrects the comment; SC-04 preserves the ship predicate and historical suffixed notes. Their implementation verification remains pending, not claimed by intake PASS.

## Qualifications

No panel, readers, goal-check or production checks ran (DEC-225); no send-back cycles were used. No prototype/UAT is needed because this changes internal filename enforcement, not an interactive surface; main may override that assessment. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent, recorded by PM rather than invented. The operator-settled constraints and existing enforcement code sufficiently bound this patch.

## Open questions

None. Main alone signs both artifacts and performs subsequent direct implementation and verification.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'Patch intake ready: 48-line BRIEF and one direct T-01, both pending;
    draft gates exit 0.'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/notes/research-patch-intake.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/runs/2026-11-22-01-patch-product/state.yaml
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: Bounded patch artifacts pending signature; plan shape and route checks
      exit 0.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/plan.yaml
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/notes/research-patch-intake.md
  must_fix: []
  branch: feat/BUG-2295-handoff-one-per-phase
  escalations: []
  adequacy_notes:
  - Lead confirmed both artifacts and PM validation receipt on disk; no shell checks
    repeated.
  - No readers, panel or goal-check ran under DEC-225.
  - No prototype or UAT needed for this internal enforcement change; main may override.
  - Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent; settled
    operator constraints and existing code bound this patch.
  - Production SC verification remains pending; PASS applies only to intake. Main
    alone signs and implements.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: Draft specifies fail-first filename regression; implementation and execution
      remain pending.
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: Draft covers Write/Edit and existing shape checks; implementation and
      execution remain pending.
  - id: SC-03
    verdict: not_met
    method: inspection
    evidence: Stale comment correction awaits implementation and pinned review.
  - id: SC-04
    verdict: not_met
    method: inspection
    evidence: Predicate and historical-note preservation await pinned implementation
      diff.
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2295-handoff-one-per-phase/.harness/harness/features/BUG-2295-handoff-one-per-phase/runs/2026-11-22-01-patch-product/digest.md
```
