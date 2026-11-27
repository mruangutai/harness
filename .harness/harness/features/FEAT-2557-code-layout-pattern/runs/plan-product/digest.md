# FEAT-2557 · patch intake · product-lead digest

**BLUF:** Patch intake ready for signature. `BRIEF.md` (6 SCs, all `inspection`) and `plan.yaml`
(3 tasks), both `approval: pending`; pm reports `plan-merge.py check` at 0 failures. One
non-blocking operator question: accept the three-route split of a patch-lane plan.

## Member: pm (step `draft`) — PASS
- Artifacts: `../../BRIEF.md`, `../../plan.yaml`.
- Tasks, in dependency order:
  - T-02 `.claude/skills/harness/bin/LAYOUT.md` → team, harness-backend-dev (team-config.yaml:187).
  - T-01 `harness-codebase-design/SKILL.md` + `AGENTS.md` → main-session-direct (no squad grant;
    DEC-179 declared step), after T-02.
  - T-03 `DECISIONS.md` + `DECISIONS-INDEX.md` (new DEC-259) → team, harness-documentor; terminal
    task, its verify asserts the whole diff is exactly the five files.
- Not-yet-specified item settled: `delete-first.md` gains **no** pointer (T-01 intent, BRIEF
  Constraints); T-01 verify asserts the file unchanged.

## Lead assessment (against send-back criteria written in state.yaml before the return)
- Approval pending in both files — yes.
- Out of scope absent from every task (feature.json refactor, feature-json-merge.py, test layout,
  lint/cap, splitting long files) — yes.
- LAYOUT.md: no size column, no "A split" section — enforced by T-02 verify (refuses
  `lines|size|grade`, `## A split`, `FEAT-`, `DEC-174`).
- Conventions bullet pathless, verbatim from Settled; LAYOUT.md path occurs once in AGENTS.md —
  enforced by T-01 verify.
- No hook/gate/validator/schema/test file in any task's `files:`; T-03 verify runs existing
  checks only.
- I did not run `plan-merge.py check` (no shell); the 0-failure result is pm's report.

## Deviation from patch-lane.md
patch-lane.md specifies exactly one `team` task. The dispatch ruled "a task needing two routes is
two tasks"; the paths resolve to three routes, so three tasks, one main-session-direct between two
team tasks. Raised as Q-01 for the operator (alternative: all three main-session-direct).

## Open questions
- Q-01 (non-blocking): accept the 3-task mixed-mode split, or run all three main-session-direct?
- Q-02 (non-blocking): DEC-259 is free at cf7b422b; T-03 stops on a collision rather than renumber.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2557 patch intake ready for signature: BRIEF.md (6 inspection SCs)
    and 3-task plan.yaml both pending, plan-merge check 0 failures per pm; patch lane
    split into three routes (Q-01, non-blocking)'
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 111-line BRIEF with 6 SCs; plan.yaml T-02 LAYOUT.md (backend-dev) ->
      T-01 skill + AGENTS.md (main-session-direct) -> T-03 DEC-259 (documentor); delete-first
      gains no pointer
    files_touched:
    - .harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md
    - .harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml
    - .harness/harness/features/FEAT-2557-code-layout-pattern/observations/harness-pm.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md
  - .harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml
  - .harness/harness/features/FEAT-2557-code-layout-pattern/observations/harness-pm.md
  - .harness/harness/features/FEAT-2557-code-layout-pattern/runs/plan-product/state.yaml
  branch: none
  open_questions:
  - id: Q-01
    question: 'patch-lane.md specifies one team task, but check-domain resolves three
      routes (LAYOUT.md -> harness-backend-dev; harness-codebase-design SKILL.md +
      AGENTS.md -> no grant, main-session-direct; DECISIONS*.md -> harness-documentor),
      so the plan has three tasks: T-02 team, then T-01 main-session step (DEC-179),
      then T-03 team. Accept this mixed-mode split, or run all three main-session-direct
      (which prints non-gating TASK DEVIATION lines)? Recommendation: accept the split.'
    blocking: false
  - id: Q-02
    question: DEC-259 is free at cf7b422b and in live worktrees/plans per pm; T-03
      is told to stop and report on a collision rather than renumber. Confirm no other
      in-flight feature will land a DEC-259 first.
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - plan-merge.py check result (0 failures) is pm's report; this lead holds no shell
    and did not rerun it.
  - 'Not-yet-specified item settled by pm: harness-craft/references/delete-first.md
    gains no pointer; recorded in T-01 intent and BRIEF Constraints, and T-01 verify
    asserts the file unchanged.'
  - 'Operator constraints checked against plan text: no Out-of-scope item in any task;
    LAYOUT.md size column and ''A split'' section refused by T-02 verify; Conventions
    bullet verbatim and pathless, path once in Project map, enforced by T-01 verify;
    no hook/gate/validator/schema/test file in any task''s files.'
  - Patch lane, so no readers, panel or goal-check ran by design (DEC-225).
  sc_status:
  - id: SC-01
    verdict: not_met
    method: inspection
    evidence: pre-build; T-01 owns the Layout section
  - id: SC-02
    verdict: not_met
    method: inspection
    evidence: pre-build; T-01 owns the Applying it bullet
  - id: SC-03
    verdict: not_met
    method: inspection
    evidence: pre-build; T-02 owns bin/LAYOUT.md
  - id: SC-04
    verdict: not_met
    method: inspection
    evidence: pre-build; T-01 owns the AGENTS.md map row and Conventions bullet
  - id: SC-05
    verdict: not_met
    method: inspection
    evidence: pre-build; T-03 owns DEC-259 and its index row
  - id: SC-06
    verdict: not_met
    method: inspection
    evidence: pre-build; whole-diff scope check in T-03 verify
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern/.harness/harness/features/FEAT-2557-code-layout-pattern/runs/plan-product/digest.md
```
