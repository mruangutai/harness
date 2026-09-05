# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-21-product/state.yaml
- squad: none
- status: awaiting-user

The operator's second signature-gate amendment is applied: the guard-covers-`unit.detect` invariant
is now a runtime-derived unit assertion (T-01 case 11, REQ-09, SC-19) and the audit note carries
exactly one fenced block by contract (T-03, T-04, SC-12). The cycle-5 goal-check found and pm closed
GAP-1, a `docs/**` substitution that kept the assertion green. The fresh cycle-6 panel then FAILED:
`severity_max: high`, seven findings, all dispositions `open`, no risk accepted anywhere. Both
readers independently defeated case 11's partition at the same root cause — it reasons lexically and
segment-wise, while the repository's only mechanical `unit.detect` consumer, `code_grade._is_test_path`
(`code_grade.py:466-471`), matches full relative paths with `fnmatch`, where `*` crosses `/`.
BRIEF carries 9 REQ and 19 SC over eleven acceptance criteria; plan.yaml carries 6 decisions and 5
tasks at station `plan`. Both approvals remain `pending`.

## Open Questions

- PF-c145e8377fc22dff2d33f76386c8bc6a (F-01, HIGH, scope). Case 11's excused test is an unnormalized
  lexical prefix compare, so a directory-only `detect` glob whose text begins `tests/` but escapes
  the tree is excused rather than rogue. The lead reproduced the mechanism but found the stated
  consequence non-reproducible today (`tests/../evil/**` matches no tracked path under `fnmatch`).
  A high finding reaches the operator; no agent may accept its risk. Remedy: normalize the literal
  prefix and reject any `..` component before the `tests/` comparison.
- PF-b3b6afcdbfce07dcf98d1e0fb29865e3 (F-02, med). Case 11's partition and final-segment-only
  synthesis assume wildcards do not cross `/`; the governing matcher does not. Remedy: state the
  matcher semantics in D-01/REQ-09/SC-19 and assert no `unit.detect` glob carries a wildcard in a
  non-final segment.
- Which matcher semantics does REQ-09's word "counts" denote? Under `fnmatch` over full relative
  paths, today's unmutated `**/test_*.py` already counts any file beneath a tracked `test_*`-named
  directory outside `tests/**` — basename innocent, so the guard structurally cannot refuse it —
  which falsifies REQ-09's absolute wording while SC-19 stays green. Narrowing a requirement is the
  operator's call, not pm's and not the panel's.
- Four lower findings (F-03..F-06, two med two low) and one info keep verdict entry are recorded in
  plan.yaml's `panel:` and enter the same signature review.
