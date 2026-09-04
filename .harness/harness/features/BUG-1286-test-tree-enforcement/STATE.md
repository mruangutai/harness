# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-15-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase at its terminus for the second time, after the operator's signature-gate amendment.
Fix 1 (T-03's `--against` output contract is unconditional and additive) and Fix 2 (D-01's
repository-wide vocabulary split into an extension-restricted group `test-*`, `test_*`, `probe-*`
and an extension-agnostic group `*_test.*`, `*.test.*` mirroring `unit.detect`) are applied and
carried through D-01, T-01, T-03, T-05 and BRIEF; the `harness.json` residual is closed from the
guard's side with `harness.json` untouched, measured inert on the present tree. BRIEF carries 18 SC
over all eleven ticket acceptance criteria; plan.yaml carries 6 decisions and 5 tasks at station
`plan`. The cycle-4 goal-check returned PASS with no surviving gap, and a fresh cycle-4 panel
returned PASS at severity_max `med` with nothing high, critical or unrated. Both approvals remain
`pending`: only the main session signs. check-state reports one violation for this feature, the
expected unsigned BRIEF.

## Open Questions

- Two cycle-4 panel findings carry `remedy_window: closes at signature` and are the operator's to
  rule on. PF-8de8d64458a4a30d8c7ba0b111546ccd (med): the guard-covers-`unit.detect` invariant that
  justifies the whole widening is asserted by no test, so a future `detect` widening re-creates the
  defect silently; remedy is one assertion in `tests/unit/test-suite-layout.py`, which T-01 already
  owns. PF-8da87ee5041dd05ed45864fd98318883 (low): T-03's note parser finds every fenced block while
  T-04 never caps the note at one, so a correct audit note carrying a second bare fence can fail the
  comparison; one sentence in either task closes it.
