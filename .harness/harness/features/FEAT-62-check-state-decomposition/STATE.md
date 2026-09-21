# STATE

## Current

- feature: FEAT-62-check-state-decomposition
- run: none
- squad: none
- status: built — T-01, T-02, T-03 done; awaiting review_sha pin and the validate run

## Build record (main session, DEC-174 carve-out)

- T-01 `ccb558b5` + `e38a8132`: table decomposition; eight suites byte-identical; table suite.
- T-02 `e7e4a3ce`: module-body, reads and authority locks; --changed posture scan.
- T-03: changed-state feedback loop in harness_boundary, called by plan-merge and
  feature_json_write; README clause. Evidence in notes/build-divergences.md.

## Open Questions

- Two record anomalies for the operator (notes/build-divergences.md, last section):
  the OMP-PORT numbering; the duplicate "INV-37" label.
