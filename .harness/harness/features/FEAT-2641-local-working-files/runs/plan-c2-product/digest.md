# plan-c2-product — FEAT-2641-local-working-files — team digest (plan cycle 2)

**BLUF: ESCALATE, for signature only.** Every operator ruling is now in the plan. BRIEF.md and
plan.yaml are both still `pending`. pm reports `record-panel --cycle 2` and `plan-merge.py check`
both exited 0.

- **GC-01.** Cleanup is now automatic and runs only after the station write succeeds:
  - `plan-merge.py set-feature-station` cleans after writing `rejected` (T-10).
  - The new `gh-sync.py skip-distill` records a declined distill, then cleans (D-11, T-05, T-04).
- **The five undistilled features** are declined post-merge through skip-distill (D-12, T-09
  step 5), with no snapshot step.
- **The one authorized scope re-read ran** and raised 3 high and 2 med substance findings, plus 1
  low form finding. pm applied all five substance findings after checking each premise at source.
  No reader has read that applied text, and the operator authorized only one re-read.

In-run send-backs: 0.

## Answer traceability (from notes/research-FEAT-2641-apply-answers-c2.md)
|Answer|Carried by|
|---|---|
|GC-01|T-10 (new), T-03, T-04, T-05, T-07, T-08, T-09; D-05, D-11 (new); SC-06, SC-16, SC-17, SC-18 (new); decisions_affected rows for DEC-230 and DEC-238|
|OQ-02|D-12 (new), D-10, T-09 step 5, T-08. BRIEF Constraints, Out of scope and Verification gaps. No preservation or snapshot step|
|OQ-01|D-07 kept. Its `because` and BRIEF Constraints ("Departure from the grilling") record the departure|
|OQ-03|T-07 (checkout-upgrade.md repair, verify greps `rm -r --cached --sparse`), SC-16|
|OQ-04|No plan step claims this feature's notes. BRIEF Out of scope names them unclaimed, and T-09 step 5 forbids claiming them|
|LEAD-01|Discharged by this run's scope step (notes/review-harness-code-reviewer-plan-c2.md)|
|OQ-05, ORCH-01|Nothing to apply|

I checked plan.yaml and BRIEF.md by grep for leftover caller-run text. "Follow-up" and "caller" now
appear only in D-05 and D-11 `because`, where they name the rejected alternative.

## Per member
|step|persona|verdict|headline|artifact|
|---|---|---|---|---|
|apply-answers|harness-pm|PASS|All rulings applied. T-10, D-11, D-12 and SC-18 added. check exit 0|notes/research-FEAT-2641-apply-answers-c2.md|
|scope|harness-code-reviewer|FAIL (pre-apply text)|Reject cleanup is ordered correctly. skip-distill could silently skip, clean after a failed commit, or miss a short-id worktree|notes/review-harness-code-reviewer-plan-c2.md|
|apply|harness-pm|PASS|5 substance findings resolved; the form finding on task order is open (no reorder verb). record-panel c2 and check exit 0. Operator perspective re-graded met|notes/research-FEAT-2641-apply-panel-c2.md|

## Cycle-2 findings and dispositions
- **PF-171c, high, substance.** skip-distill silently skips behind gh-sync preflight. Resolved_by
  T-05: it now dispatches before `load_config`. T-09 step 5 confirms each decline from git and the
  ledger.
- **PF-294f, high, substance.** A failed decline commit still permits cleanup. Resolved_by T-05:
  `feature.json` is committed alone, a failed commit exits 1 with nothing removed, and a retry is
  idempotent.
- **PF-05ce, high, substance.** clean resolves the wrong checkout or a short-id worktree. Resolved_by
  T-03: the owner comes from `feature_corpus.owner_root`, a linked worktree matches by short or full
  id, and two matches exit 5.
- **PF-85f4, med, substance.** A post-merge lookup failure is reported as a refusal. Resolved_by
  T-06: lookup errors are caught, the result reports exit 4, and the message says "do not re-run
  merge-distill".
- **PF-cdd3, med, substance.** Two amendment reasons still direct obsolete behaviour. Resolved_by
  T-08: the DEC-253 and DEC-238 reasons and D-05 `because` are corrected.
- **PF-527a, low, form.** The task list is not in topological order. **Open, not remedied.**
  plan-merge has no reorder verb. The build team schedules from `depends_on`
  (`from_task_depends_on`), and the reader confirmed the graph is acyclic. I accept this as
  non-gating.

## Lead assessment
- **The reader's FAIL graded pre-apply text.** It was a valid return, so on_fail did not fire and
  the findings went to apply. The reader confirmed that reject cleanup is ordered correctly
  (GC-01's safety condition) and that the cycle-1 highs it did not re-raise stayed resolved.
- **Changed after the reader saw it, and unread:**
  - tasks T-03, T-05, T-06, T-08 and T-09;
  - decisions D-05, D-11 and D-12;
  - the DEC-253 and DEC-238 rows in decisions_affected;
  - BRIEF SC-08, SC-17 and SC-18.

  This includes new literal behaviour: T-05 changes the signature of `_commit_terminal_station`, and
  T-03 changes linked-worktree matching. These remedies follow the reader's own must_fix closely and
  each premise was verified at source. Recommendation: accept them unread at signature.
- **Prototype gate: not applicable.** This is a CLI-only surface, and no visual-designer step ran.
  The operator can override.
- **Proportionality.** The cycle-2 reader raised no `scope: mission` finding, so there is no
  downgrade recommendation.

Reader fan-in: runs/plan-c2-product/panel-c2.md. Send-back criteria were written before the first
return: runs/plan-c2-product/criteria.md.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files/.harness/harness/features/FEAT-2641-local-working-files/runs/plan-c2-product/digest.md
DIGEST:
  headline: 'FEAT-2641 is ready for signature and still pending; check and record-panel
    c2 exit 0. Every operator ruling is applied: reject and declined-distill cleanup
    is automatic and runs only after the station write (T-10, D-11), and the five
    declines are D-12. The one scope re-read''s 5 substance findings were applied
    but no reader has seen that text.'
  team: plan
  steps_run: 3
  cycles_used: 0
  members:
  - step: apply-answers
    persona: harness-pm
    verdict: PASS
    headline: All operator rulings applied. T-10, D-11, D-12 and SC-18 added. check
      exit 0. Approval pending
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/plan.yaml
    - .harness/harness/features/FEAT-2641-local-working-files/BRIEF.md
    - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-apply-answers-c2.md
    - .harness/harness/features/FEAT-2641-local-working-files/observations/harness-pm.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Pre-apply text: reject cleanup is ordered correctly, but skip-distill
      could silently skip, clean after a failed commit, or miss a short-id worktree'
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/notes/review-harness-code-reviewer-plan-c2.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: 5 substance findings resolved after their premises were verified at
      source. The task-order form finding is open (no reorder verb). record-panel
      c2 and check exit 0. Operator perspective met
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/plan.yaml
    - .harness/harness/features/FEAT-2641-local-working-files/BRIEF.md
    - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-local-working-files-goalcheck-plan.md
    - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-apply-panel-c2.md
    - .harness/harness/features/FEAT-2641-local-working-files/observations/harness-pm.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2641-local-working-files/plan.yaml
  - .harness/harness/features/FEAT-2641-local-working-files/BRIEF.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-apply-answers-c2.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-apply-panel-c2.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/review-harness-code-reviewer-plan-c2.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-local-working-files-goalcheck-plan.md
  - .harness/harness/features/FEAT-2641-local-working-files/observations/harness-pm.md
  - .harness/harness/features/FEAT-2641-local-working-files/runs/plan-c2-product/state.yaml
  - .harness/harness/features/FEAT-2641-local-working-files/runs/plan-c2-product/criteria.md
  - .harness/harness/features/FEAT-2641-local-working-files/runs/plan-c2-product/panel-c2.md
  branch: feat/FEAT-2641-local-working-files
  open_questions:
  - id: LEAD-02
    question: 'The operator authorized one re-read, and it has run. pm then applied
      its 3 high and 2 med substance findings. The following changed after the reader
      saw them, and no reader has read them: T-03, T-05, T-06, T-08 and T-09; D-05,
      D-11 and D-12; the DEC-253 and DEC-238 rows in decisions_affected; BRIEF SC-08,
      SC-17 and SC-18. This includes new literal behaviour: T-05 changes the signature
      and return of _commit_terminal_station, skip-distill dispatches before load_config,
      and T-03 matches linked worktrees by short or full id. Recommendation: accept
      them unread at signature. The remedies follow the reader''s own must_fix, and
      pm checked each premise at source.'
    blocking: true
  - id: PM-C2-01
    question: 'The five distill declines (BUG-2451, FEAT-2557, BUG-2565, BUG-2566
      and FEAT-2581) are recorded after the merge, in the owner checkout, with gh-sync.py
      skip-distill (D-12, T-09 step 5). The feature worktree is sparse, and FEAT-1559
      forbids writing other features from it. No SC grades the declines at the pin;
      T-09 confirms each one from git and the ledger. Accept the post-merge route?
      Recommendation: accept.'
    blocking: false
  - id: PM-C2-02
    question: 'GC-01 covered reject and declined distill only. A distill that applied
      no Expertise op therefore still ends with a feature-worktree.py clean step after
      its ordinary merge. Should that route also become automatic? Recommendation:
      leave it as planned unless you intended GC-01 to cover every distill outcome.'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'Changed after the cycle-2 reader saw them, and so applied and unread: T-03, T-05,
    T-06, T-08 and T-09 (intent); D-05, D-11 and D-12; the DEC-253 and DEC-238 rows
    in decisions_affected; BRIEF SC-08, SC-17 and SC-18. T-04, T-07 and T-10 have
    not changed since the reader saw them.'
  - 'Every answer is traceable to an id (table in digest.md). GC-01: T-10, T-03, T-04,
    T-05, T-07, T-08, T-09, D-05, D-11, SC-06, SC-16, SC-17, SC-18. OQ-02: D-12, D-10,
    T-09 step 5, T-08. OQ-01: D-07 `because` plus BRIEF Constraints. OQ-03: T-07,
    SC-16. OQ-04: BRIEF Out of scope, T-09 step 5. LEAD-01: this run''s scope step.
    OQ-05 and ORCH-01: nothing to apply.'
  - I grepped plan.yaml and BRIEF.md for 'follow-up' and 'caller'. They now appear
    only in D-05 and D-11 `because`, where they name the rejected alternative. No
    text describes reject or declined-distill cleanup as a caller-run follow-up.
  - 'I confirmed by grep that plan.yaml approval.status and BRIEF ## Approval both
    read pending. pm reports that record-panel --cycle 2 and check exited 0. I did
    not run them.'
  - The scope FAIL was a valid return that graded the pre-apply text, so on_fail did
    not fire and its findings went to apply. The ESCALATE is for the LEAD-02 signature
    acknowledgement only; no further planning is needed.
  - The cycle-2 panel records should-not-exist and design as `status skipped`, outside
    the operator's one-reader authorization; both ran in cycle 1. goalcheck is listed
    as ran, but it was a refresh of GC-01 and GC-02/OQ-01 only, not a new goal-check.
  - PF-527a (low, form, task list order) stays open because plan-merge has no reorder
    verb. depends_on is acyclic and the build team schedules from depends_on, so it
    does not gate.
  - 'Process note: my seq-3 state.yaml checkpoint was refused because it lacked the
    minted run_uid. The scope dispatch went out in the same turn, and the checkpoint
    landed after the reader returned.'
  - 'Prototype gate: not applicable. The surface is CLI only and no visual-designer
    step ran. The operator can override.'
  sc_status:
  - id: operator
    verdict: met
    method: inspection
    evidence: 'Refreshed goalcheck note, departures A and B: GC-01 is automatic (T-10,
      D-11/T-05) and the D-07 departure is on record (D-07 because, BRIEF Constraints).
      Residual: PM-C2-02.'
  - id: code maintainer
    verdict: met
    method: inspection
    evidence: cycle-1 goalcheck grade, not re-graded this run
  - id: orchestrator
    verdict: met
    method: inspection
    evidence: cycle-1 goalcheck grade, not re-graded this run
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-05/T-09 (D-11/D-12, SC-18): the local decline can silently skip.'
    why: gh-sync preflight exits 0 before the handler. Resolved_by T-05 (dispatch
      before load_config) and T-09 step 5 (confirm each decline); applied and unread.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-05 (D-11, SC-18): a failed decline commit still permits cleanup.'
    why: 'The commit helper is nonfatal. Resolved_by T-05: feature.json is committed
      alone, a failed commit exits 1 with nothing removed, and a retry is idempotent;
      applied and unread.'
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-03/T-05/T-07 (D-05/D-11, SC-08/09/18): clean can resolve the wrong
      checkout or fail before deletion.'
    why: A short-id worktree is missed and the owner is resolved without bin_dir.
      Resolved_by T-03 (owner_root, short or full id match); applied and unread.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-06 (SC-17): post-merge lookup failure can report a merge refusal.'
    why: 'Resolved_by T-06: lookup errors are caught, the result is exit 4, and the
      message says do not re-run merge-distill; applied and unread.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-08 (D-04/D-05, SC-10/15): two amendment reasons still direct obsolete
      behavior.'
    why: 'Resolved_by T-08: the DEC-253 and DEC-238 reasons and D-05 because are corrected;
      applied and unread.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-05/T-07/T-08/T-09/T-10: the task list is not topological.'
    why: 'Open: plan-merge has no reorder verb. depends_on is acyclic and the build
      team schedules from it.'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'status skipped: outside the operator''s one-reader cycle-2 authorization;
      ran in cycle 1'
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: 'status skipped: outside the operator''s one-reader cycle-2 authorization;
      ran in cycle 1'
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
