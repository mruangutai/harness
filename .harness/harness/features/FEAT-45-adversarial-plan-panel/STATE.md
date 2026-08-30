# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-30-1-product/state.yaml
- squad: none
- status: awaiting-user

The operator's rulings in notes/answers-2026-08-30-plan.md are applied in one product run.
REQ-02 and REQ-05 are restored to the independent-MODEL claim; REQ-14 and SC-17 define and grade
absent-persona behaviour; the reader persona is repinned general-purpose -> fable-advisor, which is
what makes the model claim deliverable. Plan parses, 11 tasks, ids unchanged, check-plan-routes.py
exit 0 with 0 violations and the two expected DEC-174 deviations (T-07, T-08).

Both approval fragments remain `pending`. The plan is ready to be presented for signature; only the
main session signs. review_sha stays 1d3e5db. The five questions that previously blocked the
signature are closed by the rulings.

## Open Questions

- Accept the absent-persona trade as REQ-14 and SC-17 define it: where fable-advisor does not
  resolve, the panel records a skip that WARNS rather than fails, so the gate stays usable in a
  project lacking the operator's HOME definition. The alternative is a hard failure there. Not
  blocking the signature; the operator should confirm the trade. — harness-pm
- SC-16 remains the only thing that can settle whether the host RESOLVES fable-advisor to a runnable
  agent once the allowlist admits it. The stakes moved: the persona now carries REQ-02's model
  claim, not merely the spawn. Not blocking; confirm the signature is acceptable with that
  live-observation gap outstanding. — harness-pm
