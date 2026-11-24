# FEAT-2489 plan run r-20261124-1-plan-product — team digest

**BLUF:** BRIEF.md and plan.yaml are drafted, panelled and applied, and approval is `pending`. The goal-check grades all three perspectives (operator, code maintainer, reader) `pass` against the grilling ruling. Two **high** substance findings (PF-b25f…, PF-0e91…) were applied in the text but are still `open` in `panel.findings`, so `sign-approval` will refuse until a cycle-2 scope re-read resolves them or the operator overrules them. No finding has `scope: mission`, so there is no downgrade recommendation.

## Steps (all members ran, 0 send-backs)

| step | persona | verdict | artifact |
|---|---|---|---|
| draft | harness-pm | PASS | BRIEF.md, plan.yaml, notes/research-plan-routes-split.md |
| scope | harness-code-reviewer | FAIL (findings, valid return) | notes/review-harness-code-reviewer-plan-c1.md |
| should-not-exist | fable-advisor | PASS (3 findings) | carried in panel-c1.md (no write grant) |
| design | harness-ui-reviewer | PASS (self-scoped out, no UI) | notes/review-harness-ui-reviewer-plan-c1.md |
| apply | harness-pm | PASS | plan.yaml (panel c1 recorded), BRIEF.md |
| goalcheck | harness-pm | PASS | notes/research-FEAT-2489-plan-routes-split-goalcheck-plan.md |

The reader fan-in is in `panel-c1.md`. pm reported `record-panel --cycle 1` exit 0 (ADDED ×7) and `check` exit 0 (4 tasks, 17 anchors, 0 failures, OVERLAP test-check-plan-routes.py T-01/T-03, deliberate). The lead did not re-run either command. Send-back criteria were written before any return, in `sendback-criteria.md`. The draft met all nine except a soft spot on criterion 1, the SC-02 instance-shaped invariant; the scope reader raised that independently, and apply fixed it.

## Findings and dispositions

1. **High, substance (code-reviewer): SC-02 narrowed the invariant to six argv examples.** Applied. SC-02 is now one invariant for every audited tree state and argv, plus a closed list of the 4 sanctioned differences (Q3 items 1-4). The six argv runs plus one perturbed non-clean state are now evidence. **Open** pending re-gate.
2. **High, substance (code-reviewer): unequal input trees, last lines only.** Applied in T-02 and T-04. The comparison uses a matched base archive with HEAD's bin/tests overlaid, adds a `projection_confined` check, and keeps the full normalized stdout/stderr, unified diff, exit codes and tree ids. **Open** pending re-gate.
3. **Med, substance (code-reviewer): T-03 red breaks T-01 verify.** Applied. T-01's verify is now stage-aware, and its green receipt is bound to HEAD plus the blob hash. T-03's red and T-04's cumulative green are kept. **Open** pending re-gate (non-gating severity).
4. **Low, form (code-reviewer): receipt HEAD binding.** Resolved by T-04 (bound by tree id).
5. **Med, proportionality task (fable): T-02's AST checker half.** Trimmed. SC-01 and SC-05 are now graded by inspection (`git diff --color-moved`, the JSON diff), and Verification gaps says so. **Open** (non-gating).
6. **Low, proportionality task (fable): red-t02 pre-move receipt.** Dropped. **Open** (non-gating).
7. **Info, form (fable): SC-06/07 duplicated SC-04.** Resolved by T-04. They are folded into SC-04 as inspection-graded regression locks, which also answers the code-reviewer's non-blocking Q1.

**Lead assessment.** The two readers looked as if they pulled T-02 in opposite directions. They did not: the code-reviewer's objections were to the CLI half and the contract wording, and the fable-advisor's trim was to the AST half. The lead resolved it that way in the apply dispatch, and pm adopted it with evidence (a matched-tree probe at 261fdf72).

## For signature (operator)

- **Open highs.** Either run a cycle-2 scope re-read over T-01/T-02/T-04 in a new run dir, or overrule PF-b25f… and PF-0e91… at sign-approval.
- **SC-02 scope.** SC-02 covers a complete install only. A bin missing a new module now fails at import, a departure from Q3's "every tree state" that is disclosed in Verification gaps.
- **tests.yml comment.** The comment still names check-plan-routes.py as the home of the summary print. This is left alone under the tests.yml freeze, and a COUPLED pointer comment is added at the entry instead.
- **Rework.** The 2 rounds / 90 min ruling is not yet recorded anywhere. It is set at signature.
- **Prototype gate.** Not applicable. ui-reviewer self-scoped out and the plan has no end-user interaction, so no prototype is required. This is overridable.

## Team verdict

**FAIL**, by worst-wins: the scope reader returned FAIL, and its two high findings are applied but not yet re-confirmed. This is not a defect in the deliverable. The plan is complete, approval is pending, and the goal-check passes. The FAIL routes the orchestrator to one of two paths: a cycle-2 scope re-read limited to T-01, T-02 and T-04, or an operator overrule at signature.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'FEAT-2489 BRIEF and plan.yaml are drafted, panelled and applied, approval
    pending, and goal-check passes all 3 perspectives. Verdict is FAIL by worst-wins
    only: the scope reader''s two high substance findings are applied but still open,
    so sign-approval refuses until a cycle-2 scope re-read over T-01/T-02/T-04 or
    an operator overrule. No mission-scope finding, so no downgrade.'
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 4 tasks T-01..T-04, all main-session-direct, T-01 self-test fix first;
      plan-merge check exit 0
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-plan-routes-split.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Kept the all-direct two-module split. Asked to restore Q3's full invariant
      and fix the unequal-tree CLI proof (2 high, 1 med substance, 1 low form)
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/review-harness-code-reviewer-plan-c1.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: T-02's AST checker half and the red-t02 receipt over-build (proportionality,
      scope task); SC-06/07 duplicate SC-04 (form info)
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Self-scoped out: no user-facing surface'
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/review-harness-ui-reviewer-plan-c1.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: 'All 7 findings applied: SC-02 is now one invariant plus 4 closed deltas,
      T-02 is a matched-tree CLI comparison only, T-01 verify is stage-aware, SC-06/07
      are folded into SC-04. record-panel and check exit 0'
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-plan-routes-split.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator, code maintainer and reader perspectives all pass against the
      grilling ruling, as do the Q1-Q4/Q6 mandates; wording departures flagged for
      signature
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-FEAT-2489-plan-routes-split-goalcheck-plan.md
  must_fix:
  - "Resolve open high panel findings PF-b25f\u2026 (SC-02 invariant narrowed) and\
    \ PF-0e91\u2026 (unequal CLI input trees), both applied in BRIEF/T-02/T-04. Either\
    \ a cycle-2 scope (code-reviewer) re-read over T-01/T-02/T-04 in a new run dir,\
    \ or operator --overrule at sign-approval."
  files_touched:
  - .harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
  - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-plan-routes-split.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/notes/review-harness-code-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/notes/review-harness-ui-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-FEAT-2489-plan-routes-split-goalcheck-plan.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-1-plan-product/state.yaml
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-1-plan-product/panel-c1.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-1-plan-product/sendback-criteria.md
  branch: none
  open_questions:
  - id: OQ-1
    question: SC-02 holds the behaviour invariant only for a complete install. A bin
      missing either new module now fails at import (exit 1) where the base entry
      ran, a departure from grilling Q3's 'every tree state'. It is disclosed in BRIEF
      Verification gaps. Does the operator accept it at signature?
    blocking: false
  - id: OQ-2
    question: The .github/workflows/tests.yml comment will still name check-plan-routes.py
      as the home of the canonical summary print, which after the split lives in canonical_reader_audit.py.
      Ruling Q2 freezes tests.yml, so the plan keeps the runner names and adds a COUPLED
      pointer comment at the entry. Accept this, or relax the freeze for a one-line
      comment edit?
    blocking: false
  - id: OQ-3
    question: The rework ruling (2 rounds / 90 min) is recorded nowhere yet. The main
      session sets it at sign-approval --rework.
    blocking: false
  - id: OQ-4
    question: Harness-pm repository-tier expertise P-04/P-08 say plan-merge apply
      exits 7 CONFLICT on a changed value. The control-plane apply actually replaced
      fields (REPLACED, exit 0). Route this stale entry to curation at the next distill.
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'FAIL comes from worst-wins on the scope reader. The deliverable is complete:
    BRIEF and plan.yaml are drafted, panelled, applied and goal-checked, with approval
    pending. What remains is confirmation of the two applied high findings (must_fix).'
  - Code-reviewer's FAIL was a valid reader return carrying findings for apply, not
    an on_fail loop; 0 send-backs.
  - 'The readers looked contradictory on T-02 but were not: code-reviewer objected
    to the CLI half and the contract wording, fable-advisor to the AST half. The lead
    resolved this in the apply dispatch, and pm adopted it with a matched-tree probe
    at 261fdf72.'
  - record-panel and check exit codes are pm's reported output; the lead holds no
    shell and did not re-run them. The lead spot-checked that the trims landed (no
    AST checks and no red-t02 file in the tasks; approval.status pending).
  - 'Prototype gate: not required. ui-reviewer self-scoped out and the plan has no
    end-user interaction. The user may override either way.'
  - SC-06/SC-07 were added at draft and folded back into SC-04 at apply; the BRIEF
    carries SC-01..SC-05 per the ruling's seeds.
  sc_status:
  - id: operator
    verdict: pass
    method: inspection
    evidence: 'goal-check: SC-02 via T-02/T-03/T-04 matched-tree CLI comparison, notes/equivalence-final.txt'
  - id: code maintainer
    verdict: pass
    method: inspection
    evidence: 'goal-check: SC-01/SC-04/SC-05 via T-03 and T-04'
  - id: reader
    verdict: pass
    method: inspection
    evidence: 'goal-check: SC-03 via T-01 red/fix/default-register, T-03 red-t03,
      T-04 green'
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - SC-02 invariant scoped to a complete install; import failure of a missing module
    is new failure surface covered only by case 19b's copy list (OQ-1)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: SC-02 narrows the ruled behavior invariant to six argv examples.
    why: Applied at apply (one invariant + closed 4-item delta); open pending re-gate.
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: T-02/T-04 compare the audit singletons on unequal input trees and retain
      only last lines.
    why: Applied at apply (matched base archive + overlay, full normalized output
      retained); open pending re-gate.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: "T-03 breaks T-01\u2019s full-suite verify until T-04 restores the inventory."
    why: Applied at apply (stage-aware T-01 verify, receipt bound to HEAD+blob); open,
      non-gating.
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: The receipt's recorded HEAD cannot itself be the later commit that adds
      the receipt.
    why: 'Resolved by T-04: receipts bound by bin/tests tree ids.'
  - kind: proportionality
    scope: task
    severity: med
    reader: should-not-exist
    summary: T-02's eight structural/AST checks (body partitioning, per-statement
      dump equality, ordering, import shape, inventory_delta_confined) should not
      be built; only the CLI-equivalence half is the sanctioned evidence
    why: Trimmed at apply; SC-01/SC-05 graded by inspection; open, non-gating.
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: notes/red-t02-checker-premove.txt and T-02's verify assertions about
      the checker's exact FAIL set on the unsplit tree should not exist
    why: Dropped at apply; open, non-gating.
  - kind: form
    scope: none
    severity: info
    reader: should-not-exist
    summary: SC-06/SC-07 cause nothing new to be built and are acceptable; they duplicate
      seed SC-04's satellite-green clause as standalone SCs
    why: 'Resolved by T-04: folded into SC-04.'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: ran
    persona: fable-advisor
    reason: none
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-1-plan-product/digest.md
```
