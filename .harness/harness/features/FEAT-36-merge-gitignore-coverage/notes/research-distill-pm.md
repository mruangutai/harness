# PM distillation — FEAT-36

## Conclusion

No Expertise operation is warranted. Both digest-skim candidates are already covered by stronger, reusable craft rules, and no current craft entry is stale enough to replace or drop.

## Sources and candidate counts

- Observation pass: 0 candidates inspected, 0 accepted. The exact expected log path, `.harness/harness/features/FEAT-36-merge-gitignore-coverage/observations/harness-pm.md`, does not exist.
- Digest-skim pass: 2 candidates inspected, 0 accepted.
- Digest sources: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-product/digest.md` and `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-c1-product/digest.md`.

## Candidate dispositions

- C1 rejected as already covered. P-04 requires a separate assertion for every item in quantified criteria, and P-05 requires every clause to be graded against its own subject. Together they already prohibit accepting the narrower, internally consistent fixture evidence that left SC-05's broader clause unproved. Adding C1 would duplicate those rules rather than sharpen them.
- C2 rejected as already covered. G-07 requires evidence to be rerun at the commit being graded, while G-09 explicitly warns that a corrective commit can stale previously met verdicts. Together they already require every affected success-criterion grade to be re-established at the moved pin. Adding C2 would duplicate them.

## Current-entry review

- Stale-entry disposition: retained P-01 through P-15, G-01 through G-15, and O-01 through O-09. None is contradicted, obsolete, incident-bound, or weaker than either rejected candidate; Open remains empty.
- Before counts: Patterns 15, Gotchas 15, Outcomes 9, Open 0.
- After counts: Patterns 15, Gotchas 15, Outcomes 9, Open 0.

## Operations and checks

- Exact applied ops: `[]`.
- `.harness/expertise/harness-pm.md` was not changed and `expertise-merge.py` was therefore not invoked.
- Per-file check: `check-expertise.sh` was correctly skipped because the Expertise file did not change.
- Touched file: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/research-distill-pm.md`.
