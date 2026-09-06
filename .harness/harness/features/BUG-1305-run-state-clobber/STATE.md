# STATE

## Current

- feature: BUG-1305-run-state-clobber
- run: .harness/harness/features/BUG-1305-run-state-clobber/runs/plan-fix-c2-product/state.yaml
- squad: validator
- status: in-flight

## Open Questions

- Operator ruling at signature: accept the residual foreign write whose marker and checkpoint already match its seed fields (on-disk identical to a resumed owner), or reject the plan.
- Operator ruling at signature: T-07 supersedes part of signed DEC-145 (run-directory slug grammar); confirm or strike REQ-08.
- Operator ruling at signature: DEC-208 ruling 3 carries a clause this feature measured false; amend it separately or leave it standing knowingly.
- Operator ruling at signature: T-10 backfills marker-less run directories, one task beyond the original brief scope; confirm or strike.
