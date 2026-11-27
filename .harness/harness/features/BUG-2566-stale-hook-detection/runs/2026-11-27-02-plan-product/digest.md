# BUG-2566 bounded re-panel — team digest (2026-11-27-02-plan-product)

**BLUF:** The operator's rulings are applied, and Q-01 is answered. The scope reader re-read T-01 and
T-02 and graded both cycle-1 highs: merge order is resolved by D-04/T-01, and per-file naming is moot under
Q-02/Q-03. All ten cycle-1 findings are now `resolved_by: T-01`. The re-read raised six new findings, all
med or low, so none gates signature. The two form findings are fixed in text. The four substance findings
(three med in T-01's tests and FIFO handling) are left open for the operator, as dispatched. BRIEF and
plan.yaml are `pending`. record-panel (cycle 2) and check both exit 0. The team VERDICT is FAIL only
because the scope reader's FAIL rolls up worst-wins (run-01 Q-05).

## Steps
| step | persona | verdict | artifact |
|---|---|---|---|
| answers | harness-pm | PASS | notes/research-rulings-q02-q04.md |
| scope | harness-code-reviewer | FAIL (findings) | notes/review-harness-code-reviewer-plan-c2.md |
| apply | harness-pm | PASS | notes/research-apply-c2.md |

Cycles (send-backs): 0. Fan-in: panel-c2.md. should-not-exist, design and goalcheck were skipped by the
regate's bound.

## Assessment
- What the rulings changed: the fingerprint is now the loaded hook module only (D-03). A stale process
  admits a persona's BLOCKED yield only (D-02). DEC-204 and DEC-100 are back to `keep`, which the reader
  confirmed under DEC-188. T-02 is SPEC 4.2 only.
- The open substance findings are real, and they sit in T-01's spec:
  - SC-02 lacks the held+JSON BLOCKED witness and the data-less-finalize denial.
  - The FIFO test probe is unbounded.
  - A stat→read race can still block on a substituted FIFO. That is the Main-recovery hang D-01 exists
    to prevent.
  - The sidecar mtime recipe is wrong (low).
  The reader gave concrete remedies for each. Recommendation: fold them into T-01 before build.
- Host error: the apply dispatch told pm to leave all six cycle-2 findings open, including the two form
  findings that were fixed in text. They are low, so neither gates signature, but the record shows them
  open. They should be `resolved_by: T-01`.
- pm's Q-06 (a sibling editing T-01 concurrently) is dismissed. EquivalentBoa is BUG-2565's product lead
  and edits BUG-2565's own plan.yaml, not this one.
- D-04 still rests on BUG-2565's plan, which is being re-planned concurrently. If 2565 keeps
  digest-schema.ts, T-01's precondition stops the build BLOCKED, which fails safe.
- Prototype gate: unchanged from run 01. No prototype is needed, because the only user-facing surface is
  refusal text. The operator can override this.
- No proportionality finding, so no downgrade.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection/.harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-02-plan-product/digest.md
DIGEST:
  headline: 'The operator''s rulings are applied, and the bounded re-read closes Q-01:
    both cycle-1 highs are resolved or moot, and all 10 cycle-1 findings are now resolved_by
    T-01. Six new findings are med or low, so none gates signature. The 2 form findings
    are fixed in text; 4 substance findings in T-01 stay open for the operator. The
    plan is pending and check exits 0. The team verdict is FAIL only because the reader''s
    FAIL rolls up worst-wins.'
  team: plan
  steps_run: 3
  cycles_used: 0
  members:
  - step: answers
    persona: harness-pm
    verdict: PASS
    headline: Applied Q-02..Q-04. Only harness-hooks.ts is fingerprinted, and a persona's
      yield stays allowed only when it is VERDICT BLOCKED. DEC-204 and DEC-100 are
      back to keep, T-02 now touches SPEC 4.2 only, and check exits 0.
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
    - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
    - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-pm.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Both Q-01 highs are closed: merge order is resolved by D-04, and per-file
      naming is moot. T-01 still needs the held+JSON BLOCKED and data-less-finalize
      witnesses, a bounded FIFO probe, and a fix for the stat/read race. No OVERLAP.'
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Fixed both form findings and adopted the Q-07 refusal wording. Recorded
      the panel as cycle 2 with 10 cycle-1 findings resolved_by T-01 and 6 cycle-2
      findings open. record-panel, set-panel and check all exit 0; approval is pending.
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
    - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
  must_fix: []
  files_touched:
  - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
  - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-pm.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-rulings-q02-q04.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/notes/review-harness-code-reviewer-plan-c2.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-apply-c2.md
  branch: none
  open_questions:
  - id: Q-01
    question: 'Four cycle-2 substance findings on T-01 are open and non-gating, but
      they are real. Med: SC-02 lacks the held+JSON BLOCKED witness and the stale
      data-less-finalize denial (PF-1cf493dc). Med: the FIFO test probe can hang the
      suite (PF-3eb8320f). Med: a stat-then-read race can still block on a FIFO swapped
      in, which is the Main-recovery hang D-01 exists to prevent (PF-37c5f930). Low:
      the sidecar mtime recipe is wrong (PF-292338b0). Options: (a) one more pm apply
      folds the reader''s specific remedies into T-01 before signature; (b) sign and
      carry them as build amendments; (c) overrule and accept the risk. Recommendation:
      (a).'
    blocking: true
  - id: Q-02
    question: PF-7f19ccf3 and PF-298aabb8 are low form findings. Their text is fixed
      in plan.yaml and BRIEF.md, but the record shows them open, because the host's
      apply dispatch said to leave every cycle-2 finding open. They do not gate signature.
      Should the orchestrator run set-panel to mark them resolved_by T-01?
    blocking: false
  - id: Q-03
    question: 'A persona''s stale refusal now ends with the reader''s wording: ''While
      this process is stale, you may yield only a BLOCKED digest that names this cause.''
      Main''s refusal has no suffix. Confirm or strike at signature.'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'Team FAIL is the worst-wins roll-up of the scope reader''s FAIL, which carries
    its findings. The deliverable is ready to sign: no open finding is high or above,
    record-panel --cycle 2 and check both exit 0, and approval.status is pending.'
  - 'Goalcheck did not run this cycle: the regate''s bound allowed only the scope
    reader. The cycle-1 goalcheck graded the plan from before the rulings, so no reader
    re-graded intent after the operator re-decided the fingerprint set. That set is
    the operator''s own ruling, which overrides the grilling.'
  - pm's Q-06 (a sibling editing T-01 at the same time) is dismissed. EquivalentBoa
    is BUG-2565's product lead and edits BUG-2565's own plan.yaml, not this plan.
  - D-04 still depends on BUG-2565's plan, which is being re-planned at the same time.
    If 2565 keeps digest-schema.ts, T-01's precondition stops the build BLOCKED. That
    fails safe, but this plan would then need re-planning.
  - 'Prototype gate is unchanged from run 01 and was decided by this host. No prototype
    is needed: the only user-facing surface is a refusal text line, which UAT SC-10
    checks live. The operator can override this either way.'
  - 'In panel-c2.md and plan.yaml panel.readers, the skip reasons say: the orchestrator
    regate bounded cycle 2 to the scope reader re-reading T-01 and T-02, and the cycle-1
    goal-check stands.'
  sc_status: []
  needs_approval: true
  severity_max: med
  matrix_ok: none
  coverage_gaps:
  - The plan-exit goal-check was not re-run on the plan after the rulings (cycle 2)
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: T-01 omits the held JSON BLOCKED witness and stale data-less finalize
      denial.
    why: plan.yaml T-01 tests can pass with a held-only object transport check or
      an exception admitting data-less finalize. Left open for the operator.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: SC-01's direct synchronous FIFO probe can hang the test process.
    why: Neither the detector call nor the test process is bounded, so a regression
      wedges the suite instead of failing. Left open.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: T-01's separate stat and read can still block on a concurrently substituted
      FIFO.
    why: The stat and the read resolve the path separately, so a FIFO swapped in between
      can freeze Main recovery. Left open.
  - kind: substance
    scope: none
    severity: low
    reader: code-reviewer
    summary: T-01 applies a load-time mtime instruction to a sidecar absent at load.
    why: The controlled mtime offsets belong on the hook timestamp cases only. Left
      open.
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: D-04 overstates its grep's precision.
    why: 'Fixed at apply: the text now calls it a legacy-spelling check. The record
      still shows it open (host dispatch error).'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: D-02 and T-02 overstate what passing the stale check guarantees.
    why: 'Fixed at apply: completion is now qualified as subject to validation, and
      rediscovery as applying to new spawns. The record still shows it open (host
      dispatch error).'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: orchestrator regate bounded cycle 2 to the scope reader; ran in cycle
      1
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: orchestrator regate bounded cycle 2 to the scope reader; ran in cycle
      1
  - reader: goalcheck
    status: skipped
    persona: harness-pm
    reason: plan-exit goal-check ran in cycle 1; regate ran no other reader in cycle
      2
```
