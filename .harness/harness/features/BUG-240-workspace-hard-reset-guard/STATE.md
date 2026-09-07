# STATE

## Current

- feature: BUG-240-workspace-hard-reset-guard
- run: .harness/harness/features/BUG-240-workspace-hard-reset-guard/runs/2026-09-07-06-product/digest.md
- squad: none
- status: awaiting-user
- phase: plan COMPLETE — BRIEF.md and plan.yaml drafted, panel run at cycle 0 (3 readers ran,
  10 findings, 8 resolved, 2 open at low). Both approvals read pending; only the main session signs.
  Next: operator signature, then the build phase (T-01 then T-02).

## Open Questions

- Q1 (non-blocking, harness defect): runs/2026-09-07-01-product/digest.md fails the lead digest
  contract and CANNOT be repaired — corrections may only append, and validate-digest.py parses the
  FIRST `DIGEST:` block. check-state.sh reports it as a VIOLATION against this feature until the
  directory is removed by someone whose domain covers it.
- Q2 (non-blocking, harness defect): INV-32 grades the panel record only on an APPROVED plan, so a
  malformed readers index is undetectable until the moment of signature. This feature's record was
  mis-keyed (`step:` for `reader:`) and passed every check until the orchestrator simulated INV-32
  by hand.
- Q3 (non-blocking, for the operator at signature): two panel findings are recorded `open` at
  severity low — PF-d795aab03bf4a49e7ef3ef6614024cdf (case 7's source-text scan forbids the module
  documenting why no bypass exists) and PF-ff733189ddbdfca901c0d587800cb8c4 (D-01's containment
  premise ships with no fixture). Neither gates; both are strike-or-keep at signature.
