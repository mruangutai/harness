# QA distill receipt — BUG-2003 (harness-qa)

**BLUF: no ops accepted; `expertise_update: []`.** Gate fields: suite n/a, matrix_ok n/a (distill).

## Sources
Self: notes/review-harness-qa-c0.md, review-harness-qa-c1.md, receipt-t01-fail-first.txt, receipt-t01-pass.txt. Relayed: cross-panel candidate (recall only), checked against runs/2026-10-03-validate-validator/digest.md and runs/2026-10-03-validate-c1-validator/digest.md.

## Candidate judged: "matrix PASS coexisted with code FAIL because promised preservation assertions were absent; green-before preservation controls need not be red-first"
Rejected as already covered:
- Phase 1 derivation + `coverage_gaps` (harness-verification-rules) already obligates listing every promised assertion before reading code; the c0 miss was applying that rule, not a missing rule.
- G-12 (per-item check, not aggregate) and P-04 (kind must exercise the changed behavior, not adjacent proof) cover "green suite masks missing items".
- O-03 (fail-first requires a retained pre-fix red bound to the named test) plus the receipt's own labelling already distinguishes controls from fail-first; the c1 digest confirms controls need no red.
- All four sections at cap (P 15/15, G 15/15, O 10/10); a new entry would need to displace a stronger one, and no weaker one exists.

Other observations (receipt equivalence, bash-write-guard refusing pin perturbation, run-unit-tests FAIL-token noise) duplicate existing entries (P-14, G-06 repo, G-09 repo, O-07).

## Counts (before = after)
Craft/project tier: Patterns 15, Gotchas 15, Outcomes 10, Open 1.
Repository tier: Patterns 0, Gotchas 11, Outcomes 0, Open 0.

## Ops
Applied: none. Unapplied: none proposed. expertise-merge.py not run.

## Checker
`check-expertise.py .harness/expertise/harness-qa.md` → OK (exit 0); `check-expertise.py .harness/harness/expertise/harness-qa.md` → OK (exit 0).
