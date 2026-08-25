# STATE

## Current

- feature: FEAT-40-harness-writes-done
- run: PLAN PHASE COMPLETE at its exit predicate — BRIEF.md, plan.yaml and DESIGN.md on disk, all
  reviews adopted, nothing in flight. Handoff at `notes/handoff-plan.md`. Base cc84b29.
  cycles_used 2/10, 3 runs vs informational bound 20. NOT committed by me, NOT signed.
- squad: none
- status: Plan

<!-- Run 3 (2026-08-25-03-product) died on an API connection error, NOT on its work. Disk shows its
     work LANDED before the drop, verified by me: DESIGN.md Q1 closed (09:05), and plan.yaml (09:19)
     carries the new T-11, the github-mirror read-back sentence at :886, and T-09's part-C verify
     clause at :949. What is missing is only the lead's digest.

     ONE BLOCKING PLAN DEFECT REMAINS — T-11 pins the accepted red-suite set to FIVE scripts
     (plan.yaml:1044 `want=`, restated :1006); the true set is SEVEN. T-04/T-05/T-06/T-07/T-08 all
     depend on T-11 and compare the runner's FAIL lines to that literal by string equality, so as
     written T-11 and its five dependents can never pass. Add test-hooks-install.py and
     test-post-merge-sweep.py to the literal wherever it appears. -->

## Open Questions

- BLOCKING, PM — T-11's pinned red-suite set names five scripts; I measured eight failing at base and
  reproduced all eight in the main clone. After T-11 repairs test-validate-feature-json.py, seven
  remain. The literal omits test-hooks-install.py and test-post-merge-sweep.py — the two that guard
  the sweep machinery T-02 exists to prove.
- BLOCKING, OPERATOR — constraint 5's environment marker is impossible; the gate cannot see abandon's
  close at all. The plan refuses every `gh issue close` unconditionally: your outcome, not your
  stated mechanism. Confirm or overrule.
- BLOCKING, OPERATOR — DEC-203's prose register. "Less concise, less wordy, but clear" is read as
  plain readable prose. No DEC-203 text is written yet; T-03 is blocked on this.
- BLOCKING, MAIN SESSION — plan.yaml has no `approval:` block. check-state.sh makes an absent key a
  violation, not the "pending" note other live plans carry. No agent may write it.
- CORRECTION — #728 has thirteen children, not none. All closed, all at `Review`, so all OPEN under
  the new rule. The acceptance test is the hard case, not the trivial one.
- NON-BLOCKING, five more in the product lead's digest (Q4 sweep FAILED literal, Q5 prototype gate,
  Q6 REQ-06 narrowed, Q7 DEC-200, Q8 close-task's survival). Carried up unchanged.
