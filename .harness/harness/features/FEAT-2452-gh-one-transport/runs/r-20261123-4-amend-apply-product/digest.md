# FEAT-2452 · C1 amend apply — product-lead run report (r-20261123-4-amend-apply-product)

## Send-back criteria (written before dispatch)

Accept pm's return only if ALL hold; otherwise send back once, then escalate:

1. Receipt `notes/receipt-amend-apply-r-20261123-4.txt` exists and contains every writer's full stdout+stderr and the final `plan-merge.py check` output; no `APPROVAL-RESET:` line.
2. `plan.yaml` `decisions_affected`: exactly two DEC-138 rows — best-effort row still `keep`, byte-unchanged; runner-clause row now `amend` with a resolvable `successor` (D-NN of this plan or indexed DEC) and a one-line reason naming the C1-scoped amendment. DEC-146 row and all other rows byte-unchanged.
3. T-05 `files:` names `.harness/harness/docs/DECISIONS.md` (quote anchor) and `.harness/harness/docs/DECISIONS-INDEX.md`; T-05 intent no longer forbids DEC amendments and describes the amendment exactly as C1 scopes it; T-05's existing verify lines (incl. `len(owned) == 29`) preserved; T-05 `depends_on: [T-04]` unchanged.
4. BRIEF.md line-41 constraint block and the `DEC amendments` bullet state the ruled outcome (one DEC-138 amendment, scoped, delivered by T-05); `## Approval` unchanged.
5. `approval.status` pending; check exits 0 with 0 failures.
6. No other task/SC/decision/panel change.

## Result

**BLUF: C1 landed. Signature is now unblocked on C1.** The DEC-138 runner-clause row is `amend` with successor D-01, and T-05 owns DECISIONS.md and DECISIONS-INDEX.md and carries the scoped rewrite after T-04. The final `plan-merge.py check` exits 0: `5 task(s), 33 anchor(s) resolved, 0 failure(s)`. `approval.status` is still pending, and no writer printed `APPROVAL-RESET:`.

- Receipt (C6): `FD/notes/receipt-harness-pm-amend-apply-r-20261123-4.md`. check-domain refused the dispatched `.txt` path for harness-pm, so the receipt sits at a pm-permitted path. It is still under notes/, which satisfies C6. Naming that path was my dispatch error. pm's value files were staged in /tmp, and each one is reproduced in full in the receipt.
- The receipt honestly records one intermediate FAIL. The first verify amendment exceeded the DEC-182 50-line budget (53 lines). pm compressed the insertion to 3 lines, and the next check passed.
- pm's artifact: `FD/notes/research-FEAT-2452-gh-one-transport-amend-apply-plan.md`.

## Assessment against the criteria

1. **Met**, at the moved path above. The receipt has every writer's full output and the final check, and no APPROVAL-RESET.
2. **Met.** There are exactly two DEC-138 rows. The best-effort keep row is unchanged. The runner row is amend/D-01, and its one-line reason states the C1 scope. DEC-146 and every other row are unchanged; I read plan.yaml:108-135.
3. **Met.** T-05 files add DECISIONS.md (quote `Shared code, and migration scope.`) and DECISIONS-INDEX.md (`- DEC-138 @`). The intent is rescoped, and the original verify lines are preserved, including `len(owned) == 29`. pm appended 3 lines that assert the amendment: factory_gh is present, gh_bin and "keeps its own runner" are absent, and the guard sentence is intact. `depends_on: [T-04]` is unchanged.
4. **Met.** BRIEF lines 41 and 49 state the ruled outcome. `## Approval` still reads pending.
5. **Met.** approval.status is pending, and the check exits 0 with 0 failures.
6. **Met** per pm's diff check. I did not run git myself.

Advisory for T-05's builder: the new verify fails if the rewritten paragraph mentions `gh_bin` at all, even to say it was removed.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-4-amend-apply-product/digest.md
DIGEST:
  headline: 'C1 landed: the DEC-138 runner-clause row is now amend (successor D-01)
    and T-05 owns DECISIONS.md and its index and carries the scoped rewrite after
    T-04. plan-merge check exits 0 with ''5 task(s), 33 anchor(s) resolved, 0 failure(s)'';
    approval is still pending and no writer printed APPROVAL-RESET, so signature is
    unblocked on C1.'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/notes/receipt-harness-pm-amend-apply-r-20261123-4.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/notes/research-FEAT-2452-gh-one-transport-amend-apply-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-4-amend-apply-product/state.yaml
  expertise_update: []
  team: 'plan (apply-only: pm amend-apply; no readers, no goalcheck per signoff C1)'
  steps_run: 1
  cycles_used: 0
  members:
  - step: amend-apply
    persona: harness-pm
    verdict: PASS
    headline: 'Replaced the DEC-138 runner-clause keep row with amend/D-01 via set-key
      decisions_affected. Amended T-05 files, intent and verify via amend, appending
      3 verify lines that assert the rewrite. Updated BRIEF lines 41 and 49. Final
      check: 5 tasks, 33 anchors, 0 failures.'
    files_touched:
    - FD/plan.yaml
    - FD/BRIEF.md
    - FD/notes/receipt-harness-pm-amend-apply-r-20261123-4.md
    - FD/notes/research-FEAT-2452-gh-one-transport-amend-apply-plan.md
    - FD/observations/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Receipt path is FD/notes/receipt-harness-pm-amend-apply-r-20261123-4.md, not
    the dispatched notes/receipt-amend-apply-r-20261123-4.txt. check-domain refuses
    the .txt path for harness-pm. The receipt is still under notes/, so C6 holds.
    I resolved pm''s OQ-R4-1 as accepted: the dispatch path did not fit pm''s domain
    grant, and future dispatches should name a receipt-harness-pm-*.md path.'
  - pm staged the plan-merge value files in /tmp because pm cannot write other notes/
    names. Every value file is reproduced in full in the receipt beside its command,
    so C6, which governs stdout receipts, is satisfied.
  - 'The receipt records one intermediate check FAIL: T-05 reached 53 machine-field
    lines against the DEC-182 50-line budget. The verify insertion was then compressed
    to 3 lines, and the final check exits 0. This is an honest record, not a defect.'
  - 'Final check line: ''CHECK .../plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport:
    5 task(s), 33 anchor(s) resolved, 0 failure(s)'', exit=0. 33 anchors = 31 baseline
    + 2 new T-05 anchors (DECISIONS.md, DECISIONS-INDEX.md).'
  - 'I verified the results myself. plan.yaml:108-135 has exactly two DEC-138 rows:
    the best-effort row is keep and unchanged, and the runner row is amend/D-01. The
    DEC-146 row is unchanged and approval.status is pending. BRIEF lines 41 and 49
    state the ruled outcome, and the BRIEF Approval section is pending. T-05''s original
    verify lines are preserved, including len(owned) == 29.'
  - The 'no other change' claim rests on pm's yaml/diff comparison. I ran no git.
  - 'Advisory for the T-05 builder: the new verify asserts ''gh_bin'' is absent from
    the DEC-138 Shared-code paragraph. The rewrite must not name gh_bin at all, even
    to say it was removed.'
  - Every writer's check-state output shows VIOLATIONs (BRIEF not approved; INV-37
    no Build-entry receipt). Both are expected for a pending pre-signature plan, and
    all writers exited 0.
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
```
