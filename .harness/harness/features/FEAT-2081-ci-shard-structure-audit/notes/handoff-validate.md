# Handoff — FEAT-2081-ci-shard-structure-audit, validate → ship — written at 3ee8bd06, seq-0

## Next

Ship: `gh-sync.py ship` with `--pr 2100` from a clean clone of main (the main checkout carries the operator's uncommitted files), commit and push the station, then remove the feature worktree and branch.

## Trust

- VALIDATE cycle 2 at f2791446 passed: all six cycle-1 blockers closed, must_fix empty, matrix green (unit 49, integration 76 files). The YAML record was transcribed by the main session because the lead's return was refused (#2110) — runs/2026-10-05-03-validator/digest.md — VERIFIED
- Review pin moved to 7e03ba2c for main merges, the weight re-measure and the brief/plan text amendment only; the feature code and workflow are unchanged since b886dbcf, and the weights since 6ccff7f1 — notes/evidence-T-04.md — VERIFIED
- UAT passed, signed by the operator 2026-10-07: SC-09 U-01/U-02/U-04/U-05 as expected; SC-10 median 83s under amended OQ-01; L-01 medians lower — notes/uat.md — VERIFIED
- PR #2100 squash-merged as 3ee8bd06 after the required `integration` check passed (run 37565720110) — VERIFIED

## Dead ends

- Do not run ship from the feature worktree; its copy of the feature directory is deleted with it — gh-sync ship refusal, 2026-10-07 — VERIFIED
- Do not re-run the validation panel for this feature: #2110 refuses the lead's return, and the panel's result is already on disk — runs/2026-10-05-03-validator/digest.md — VERIFIED

## Working set

- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md
- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/plan.yaml
- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/feature.json
- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/notes/uat.md
- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/notes/evidence-T-04.md

## Done when

Scope: FEAT-2081 shipped — station done on every recorded card, milestone #98 closed
Authority: brief-perspective:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md#code maintainer
Authority: approval:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/plan.yaml#approval
