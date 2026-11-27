# revise-product — FEAT-2557 INV-32 one-task revision

**PASS.** The plan now has one task, T-01. It is main-session-direct, covers the five files the ruling names, traces SC-01..SC-06, and has `depends_on: []`. `approval.status` is `pending`, so it is ready for re-signature. BRIEF.md changed only in its routing bullet; its Approval block is pending.

## Lead assessment (against the send-back criteria seeded before the return)
- plan.yaml: `tasks:` holds only T-01. It has no `execution_agent`. Its `execution_reason` names `notes/answers-2026-11-27-inv32.md` and DEC-179. Its `files:` are the five ruling files and it carries `change_type: docs`. I compared the merged verify against the three signed verifies: every assertion is present, ordered T-02, then T-01, then T-03. The only duplicate, `test -f LAYOUT.md`, is folded. The merged intent orders the steps LAYOUT.md → skill+AGENTS.md → DEC-259+index and keeps every settled requirement.
- D-01 is unchanged. Of the decisions_affected rows, only the DEC-179 reason was reworded. The `lanes:` rows for `bin/**` and `.harness/harness/docs/**` now read main-session-direct, and their reasons cite the ruling.
- `approval:` was reset by `delete-items` (receipt below). The tool kept `approved_by`/`date` next to `status: pending` (pm Q-03). That is the tool's behaviour, and `sign-approval` overwrites both.
- BRIEF.md: HEAD already held a pending Approval block, so the diff against HEAD is the routing bullet only. That is within the acceptance. The file is 112 lines.

## Receipts (pm, verbatim)
```
APPROVAL-RESET: the plan was approved and its task set or a task field changed; approval.status is pending until the main session signs again
```
plan-merge.py check printed:
```
OK T-01 5 anchor(s) resolved
CHECK .../plan.yaml against .../FEAT-2557-code-layout-pattern: 1 task(s), 5 anchor(s) resolved, 0 failure(s)
```
check-plan-routes printed:
```
OK T-01: declared main-session-direct (.claude/skills/harness-codebase-design/SKILL.md, AGENTS.md ungranted)
0 violation(s) across 1 plan(s)
```
No DEVIATION lines appeared. The ruling accepted those findings in advance; once the lanes were declared main-session-direct, they no longer fire.

## Open (non-blocking, the orchestrator's)
- INV-26 board drift: #2560, #2558 and #2557 read `ready`, but the plan projects `plan`. #2559 (T-02) and #2561 (T-03) have no placement. These are for `gh-sync.py`, which pm did not run.
- DEC-159: check-state reported a missing `notes/handoff-plan.md` on the first amend.
- pm listed `feature.json` in files_touched. This was outside the dispatched target, and pm's return does not say whether plan-merge wrote it or pm did.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/runs/revise-product/digest.md
DIGEST:
  headline: FEAT-2557 plan is now one main-session-direct task, T-01, covering the
    five files the INV-32 ruling names and tracing SC-01..06. All prior verify assertions
    are kept. Approval is pending and the plan is ready for re-signature.
  open_questions:
  - id: Q-01
    question: 'Existing INV-26 board drift: #2560, #2558 and #2557 read ready, but
      the plan projects plan. Dropped-task cards #2559 (T-02) and #2561 (T-03) have
      no placement. The orchestrator should reconcile through gh-sync.py, which pm
      did not run.'
    blocking: false
  - id: Q-02
    question: On the first amend, check-state reported that notes/handoff-plan.md
      is missing (DEC-159, plan seam crossed without a handoff). pm has no grant for
      that file. Should the orchestrator write it before re-signature?
    blocking: false
  - id: Q-03
    question: pm listed feature.json in files_touched, although the dispatch named
      only plan.yaml and BRIEF.md. Its return does not say whether plan-merge.py's
      status sync wrote it or pm did. The orchestrator should check the feature.json
      diff before re-signature.
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/feature.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/runs/revise-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/runs/revise-product/digest.md
  expertise_update: []
  team: product
  steps_run: 1
  cycles_used: 0
  members:
  - step: revise
    persona: harness-pm
    verdict: PASS
    headline: Cut the plan to T-01 using amend, delete-items --task T-02 --task T-03,
      set-lanes and set-key, all through plan-merge.py. The merged intent runs LAYOUT.md,
      then skill+AGENTS.md, then DEC-259+index. The merged verify keeps every T-01/T-02/T-03
      assertion. Only the BRIEF routing bullet changed.
    files_touched:
    - plan.yaml
    - BRIEF.md
    - feature.json
    - observations/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'APPROVAL-RESET receipt, verbatim, printed by delete-items only; the later amends
    ran on an already-pending plan: ''APPROVAL-RESET: the plan was approved and its
    task set or a task field changed; approval.status is pending until the main session
    signs again'''
  - 'plan-merge.py check: ''OK T-01 5 anchor(s) resolved'' / ''1 task(s), 5 anchor(s)
    resolved, 0 failure(s)'', exit 0. check-plan-routes: ''OK T-01: declared main-session-direct
    (.claude/skills/harness-codebase-design/SKILL.md, AGENTS.md ungranted)'' / ''0
    violation(s) across 1 plan(s)'', exit 0. No DEVIATION lines fired, because the
    lanes rows for bin/** and .harness/harness/docs/** now declare main-session-direct
    and cite the ruling.'
  - 'I compared the merged verify against the three signed verifies myself: no assertion
    was dropped. The duplicate ''test -f LAYOUT.md'' is folded, and the closing echo
    is now LAYOUT-SKILL-AGENTS-DEC-OK.'
  - 'plan.yaml approval: the tool kept approved_by/date next to status: pending plus
    reset_at/reset_reason. Nothing was written by hand, and sign-approval overwrites
    these fields. Top-level plan status is now ''plan''.'
  - 'BRIEF.md: HEAD already held a pending Approval block, so the diff against HEAD
    is the routing bullet alone. The file is 112 lines. No SC or decision was added
    or dropped, and the mission is unchanged (patch).'
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
```
