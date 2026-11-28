# BUG-2566 final pm pass — team digest (2026-11-27-03-plan-product)

**BLUF:** The plan is ready to sign. The operator's run-02 answers are applied exactly. All four T-01
remedies are in T-01.intent, and BRIEF SC-01, SC-02, SC-04 and SC-06 mirror them. All 16 panel findings
are `resolved_by: T-01`, so no finding is open at any severity, including high, critical and unrated.
record-panel (cycle 3), set-panel and check all exit 0. approval stays `pending`. The plan-exit goal-check
was re-run against the amended intent: SC-01 to SC-10 are all met in the plan, with three non-blocking
advisories. Team VERDICT: PASS.

## Steps
| step | persona | verdict | artifact |
|---|---|---|---|
| apply | harness-pm | PASS | notes/research-apply-c3.md |
| goalcheck | harness-pm | PASS | notes/research-BUG-2566-stale-hook-detection-goalcheck-plan.md |

Cycles (send-backs): 0. Fan-in: panel-c3.md. No reader ran (operator Q-01 (a)). Send-back criteria were
written before dispatch (sendback-criteria.md), and both returns met them.

## Assessment
- **Remedies, checked by distinctive token in plan.yaml:**
  - `data-less` finalize refusal and the held+JSON carve-out case (PF-1cf493dc).
  - `timeout: 5000, killSignal: "SIGKILL"` FIFO probe (PF-3eb8320f).
  - `O_NONBLOCK` open + `fstatSync` on the descriptor (PF-37c5f930).
  - "Controlled mtime offsets apply only to the three hook timestamp cases" (PF-292338b0).
- **Q-03 suffix:** verbatim in D-02 and in T-01's handler and P. BRIEF SC-02 now quotes it literally. Main
  has no suffix.
- **Unread clauses:** the folded T-01 text prescribes literal calls (`openSync(... O_NONBLOCK)`,
  `spawnSync` with a timeout, `utimesSync` offsets) that no reader has re-read. The operator accepted these
  unread (Q-01). The build's own tests and mutant step are their first witness.
- **Goal-check advisories (non-blocking):**
  - SC-02's "exactly as narrow as the held-run gate's" overclaims by the data-less finalize case.
  - T-01's export-grep omits `isBlockedYieldData`. SC-06 inspection still covers it.
  - `.omp/agents` exclusion is witnessed by inspection only.
- **Prototype gate:** unchanged. No prototype is needed, because the only user-facing surface is a refusal
  line that UAT SC-10 checks live. The operator can override this either way.
- **D-04 dependency on BUG-2565:** unchanged. The build fails safe (BLOCKED) if 2565 keeps digest-schema.ts.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection/.harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-03-plan-product/digest.md
DIGEST:
  headline: BUG-2566's plan is ready to sign. The four T-01 remedies are folded in,
    all 16 panel findings are resolved_by T-01 (none open at any severity, including
    high, critical and unrated), record-panel cycle 3 and check exit 0, and approval
    stays pending. The re-run goal-check finds SC-01 to SC-10 met against the amended
    intent.
  team: plan
  steps_run: 2
  cycles_used: 0
  members:
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Folded PF-1cf493dc, PF-3eb8320f, PF-37c5f930 and PF-292338b0 into T-01.intent
      through amend and mirrored them in BRIEF SC-01, SC-02, SC-04 and SC-06. The
      Q-03 suffix is verbatim. record-panel --cycle 3, set-panel and check all exit
      0, all 16 findings are resolved_by T-01, and approval is pending.
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
    - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
    - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-apply-c3.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Graded against the grilling as amended by the run-01 and run-02 answers.
      SC-01 to SC-10 are met in the plan, every amended-intent item maps to an SC
      and a task, and there are 3 non-blocking advisories.
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-BUG-2566-stale-hook-detection-goalcheck-plan.md
    - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-pm.md
  must_fix: []
  files_touched:
  - .harness/harness/features/BUG-2566-stale-hook-detection/plan.yaml
  - .harness/harness/features/BUG-2566-stale-hook-detection/BRIEF.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-apply-c3.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/notes/research-BUG-2566-stale-hook-detection-goalcheck-plan.md
  - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-pm.md
  branch: none
  open_questions:
  - id: Q-01
    question: 'Advisory from the goal-check: BRIEF SC-02 says the carve-out is ''exactly
      as narrow as the held-run gate''s'', but a stale process refuses a data-less
      finalize that a held run lets through (accepted at run-02 Q-01). Should the
      wording be tightened to data-bearing yields at signature, or left as is?'
    blocking: false
  - id: Q-02
    question: 'Advisory from the goal-check: the export-grep in T-01.verify could
      add isBlockedYieldData, so that SC-06''s module-private clause is machine-witnessed
      as well as inspected. Should it be added, or left to inspection?'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'No plan reader ran in cycle 3 (operator Q-01 option a). The folded T-01 text
    prescribes literal calls that no reader has re-read: openSync with O_NONBLOCK
    plus fstatSync, spawnSync with timeout 5000 and SIGKILL, and utimesSync offsets.
    The operator accepted these unread. The build''s tests and mutant step are their
    first witness.'
  - 'I verified the remedies by distinctive token in plan.yaml: data-less, killSignal,
    O_NONBLOCK/fstatSync, and ''only to the three hook timestamp cases''. The goal-check
    note has a cycle-3 section, and cycle 1 is marked superseded.'
  - 'Third goal-check advisory: exclusion of .omp/agents is witnessed by SC-06 inspection
    only, with no behavioural case. pm judges that sufficient.'
  - 'Prototype gate is unchanged from runs 01 and 02, decided by this host: no prototype
    is needed, because the only user-facing surface is a refusal line that UAT SC-10
    checks live. The operator can override this either way.'
  - D-04 still depends on BUG-2565 landing first. If 2565 keeps digest-schema.ts,
    T-01's precondition stops the build BLOCKED, which fails safe.
  - The goalcheck reader ran in cycle 3, after apply, against intent as amended by
    the run-01 and run-02 answers. Its panel-c3.md entry carries that reason text.
  sc_status:
  - id: SC-01
    verdict: met-in-plan
    method: plan inspection
    evidence: 'T-01.intent test (d) and items 2, 5 and 6: the FIFO probe is a killable
      spawnSync with a deadline, and the same-size case pins mtime M'
  - id: SC-02
    verdict: met-in-plan
    method: plan inspection
    evidence: 'T-01 handler and test (a): 13 refusals with reason P or the bare reason.
      Test (b): 4 carve-out cases, each with exactly one validate-digest.py --hook
      call'
  - id: SC-03
    verdict: met-in-plan
    method: plan inspection
    evidence: 'T-01 test (c): Main''s read, edit, write and bash git status'
  - id: SC-04
    verdict: met-in-plan
    method: plan inspection
    evidence: 'T-01 test (e) and the mutant paragraph: mtimes on the hook timestamp
      cases only, and the mutant must turn the same-size case red'
  - id: SC-05
    verdict: met-in-plan
    method: plan inspection
    evidence: 'T-01 test (f): 20 warm-up calls, then a median of 200 timed calls under
      5 ms'
  - id: SC-06
    verdict: met-in-plan
    method: plan inspection
    evidence: T-01 items 1-7, D-03 and D-04. The export-grep omits isBlockedYieldData
      (advisory)
  - id: SC-07
    verdict: met-in-plan
    method: plan inspection
    evidence: T-01.verify runs bun test tests/unit/omp-hooks.test.ts
  - id: SC-08
    verdict: met-in-plan
    method: plan inspection
    evidence: T-01.verify runs bun run typecheck
  - id: SC-09
    verdict: met-in-plan
    method: plan inspection
    evidence: T-02.intent paragraph; T-02.verify checks 9 phrases in SPEC 4.2
  - id: SC-10
    verdict: met-in-plan
    method: plan inspection
    evidence: T-01.traces includes SC-10. UAT stays not_met until the operator runs
      it
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps:
  - The four T-01 remedy clauses folded in cycle 3 have not been re-read by any plan
    reader; the operator accepted them unread (run-02 Q-01)
  findings: []
  readers:
  - reader: scope
    status: skipped
    persona: harness-code-reviewer
    reason: 'operator Q-01 option (a): final pm pass with no re-read; the remedies
      came from the cycle-2 scope read'
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'operator Q-01 option (a): no reader runs in cycle 3; ran in cycle 1'
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: 'operator Q-01 option (a): no reader runs in cycle 3; ran in cycle 1'
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
