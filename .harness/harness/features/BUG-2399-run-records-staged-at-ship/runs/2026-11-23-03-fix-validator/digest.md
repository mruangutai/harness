# BUG-2399 validation c2

**74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd is ship-ready: PASS.** All five readers pass; no new findings, must-fix items or open questions. Reviewed base 9eb07b4f3cd235c234a10edddbfe5542c1e85fba through this pin, not mutable HEAD.

## C1 disposition

- **MF-1 resolved / substance / T-01:** code c2 identifies pruner:186–200 error aggregation and :238–243 refusal before prune/stage, including dry-run. QA c2 ran the permission-sensitive regression as uid 501: all 40 pruner checks passed, no skips. Hash-bound c1-fix evidence records three real assertion failures on the old pruner. No regression reported.
- **MF-2 resolved / form / T-01:** notes/answers-2026-11-23-c1-ruling.md explicitly accepts the historical removal clause as vacuously satisfied. PM c2 grades the remaining SC-03 clauses met; no amendment or reapproval required. No regression reported.

## Adequacy assessment

QA's production unit receipt (`qa/manifest-unit.json`) binds the exact pin, 65 selected/completed files and exit 0; only unit is required. Both T-01 verify commands also passed at the pin, including the decision-index comparison. SC-01 and SC-02 have genuine retained assertion-red evidence audited by hash, not rerun. This closes the previous panel's specific missing failure mode rather than relying on aggregate green.

Code and security independently inspected refusal and publication boundaries; security performed no attack execution. UI measured 21 changed files before declining visual/interactive scope. PM's note predates the available c2 QA return and explicitly bounds its evidence; this consolidated assessment adds the current-pin QA receipt without claiming PM reran anything. Both perspectives, SC-01–03 and the DEC-238 amendment are met.

QA's dedicated-regression gaps remain advisory: git-add failure, unsafe run ids, nested ui inclusion, linked files, hash-mismatched and escaped evidence paths. They are coverage limits, not demonstrated new defects. No findings silently dropped or reclassified. Integration is not required and was not run. Lead ran no checks.

Reader artifacts: notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c2.md and notes/research-BUG-2399-run-records-staged-at-ship-goalcheck-validate-c2.md. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: 74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd is ship-ready; both c1 must-fix
    items resolved.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/notes/research-BUG-2399-run-records-staged-at-ship-goalcheck-validate-c2.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 65 unit files green at pin; fail-first hash-bound; unreadable regression
      executed without skips.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Traversal refusal precedes mutation; both c1 items resolved; no new
      findings.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Pinned retention and publication boundaries pass inspection.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured 21-file diff has no visual or interactive UI; scoped out.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: "Both perspectives and SC-01\u201303 met; DEC-238 amendment landed."
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/notes/research-BUG-2399-run-records-staged-at-ship-goalcheck-validate-c2.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - "MF-1 resolved / substance / T-01: code c2 pruner:186\u2013200 and :238\u2013\
    243 confirms traversal errors aggregated and refused before pruning/staging in\
    \ both modes. QA ran unreadable regression as uid 501; 40 pruner checks passed\
    \ without skips. Hash-bound c1 fix receipt records three assertion failures against\
    \ old pruner. No regression."
  - 'MF-2 resolved / form / T-01: notes/answers-2026-11-23-c1-ruling.md disposes historical
    removal clause as vacuously satisfied; PM grades remaining SC-03 clauses met.
    No amendment or reapproval. No regression.'
  - 'QA production receipt in this run qa/manifest-unit.json: exact pin, 65 selected/completed
    unit files, exit 0. Unit is the only required kind. Both T-01 verify commands
    passed at pin, including decision-index generation comparison.'
  - SC-01 and SC-02 genuine assertion-red evidence audited by hash in notes/red-first-T-01.md;
    historical failures not rerun.
  - PM explicitly used historical/pinned evidence before c2 QA note was available;
    lead adds current-pin QA assurance. Security inspection-only, no attack probes.
    UI scope decline supported by measured diff census.
  - No new findings or silent dismissals. Advisory regression gaps bound assurance,
    not demonstrated defects. Integration not required/not run; lead ran no checks.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: "Pinned tests/unit/test-prune-run-evidence.py staging assertions and\
      \ unreadable cases:271\u2013296; QA c2 40 PASS/0 SKIP and production receipt;\
      \ notes/red-first-T-01.md hash-binds original and c1-fix assertion failures."
  - id: SC-02
    verdict: met
    method: automated
    evidence: "Pinned tests/unit/test-prune-run-evidence.py:239\u2013268 covers all\
      \ missing paths, exit 2 and refusal immutability; QA c2 green receipt plus audited\
      \ base assertion-red evidence."
  - id: SC-03
    verdict: met
    method: inspection
    evidence: "PM/code c2 inspect pinned .omp/commands/harness-ship.md:43\u201359\
      \ and preserved pruner selection/refusal/dry-run semantics; operator ruling\
      \ accepts historical removal clause. QA decision-index comparison passed at\
      \ pin."
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: "PM c2 pinned DECISIONS.md:8058\u20138070 implements plan decisions_affected[0],\
      \ successor D-01, owner T-01. Other bullets unchanged; keep rows skipped."
  needs_approval: false
  severity_max: none
  matrix_ok: true
  coverage_gaps:
  - 'Advisory: git-add failure, unsafe run ids, nested ui inclusion, linked files,
    evidence hash mismatch and escaped evidence paths lack dedicated regressions.'
  - Security assurance is inspection-only; no attack execution.
  - Integration not required and not run.
  findings: []
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/runs/2026-11-23-03-fix-validator/digest.md
```
