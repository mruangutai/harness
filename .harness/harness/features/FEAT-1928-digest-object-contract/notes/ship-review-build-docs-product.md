# Ship review — FEAT-1928 digest object contract

## Conclusion

Shipping is blocked before SIMPLIFY and validation. T-01, T-02, and T-04 are built with passing unit, integration, parity, and live OpenAI evidence, but T-03 correctly stopped without edits because its signed reservation of DEC-236 collides with a fetched allocation. Across fetched heads, DEC-549 is the next free number. The recommended recovery is to amend T-03 from DEC-236 to DEC-549, re-sign that plan change, then resume T-03, SIMPLIFY, pin `review_sha`, and run the single validation team.

## Definition of done — current grade

The final validate goal-check has not run, so no implementation perspective can yet be certified met. The rows below distinguish delivered evidence from the remaining T-03 and validation gates.

| Perspective | Verdict | SCs | Evidence |
|---|---|---|---|
| operator | ungraded | SC-01, SC-04, SC-05 | T-01/T-02 are built; live OpenAI null-retry completion passes 18/18 at Harness `45292dee` (`notes/live-digest-object-probe.md`). Final validation is pending. |
| orchestrator | ungraded | SC-02 | Object-only persona contracts are built and the unit/integration suites passed in the main-session-direct build record, but the validate goal-check is pending. |
| code maintainer | blocked | SC-03, SC-08 | Canonical schemas and the hard cut are built; T-03's current-doctrine and replacement-decision work is unimplemented because DEC-236 is allocated (`runs/build-docs-product/digest.md`). |
| reader | blocked | SC-06, SC-07 | Validator parity is 291 cases with 0 unplanned mismatches (`notes/validator-parity.md`); T-03 doctrine and the final validation grade remain pending. |

The plan-phase goal-check passed all four perspectives as coverage, not implementation evidence (`notes/research-FEAT-1928-digest-object-contract-goalcheck-plan.md`).

## Blocking decision

The documentor confirmed that commit `4b6ed10918349c9a1cee3ba7941c92087bf33441` on fetched branch `feat/FEAT-1896-dashboard-from-prototype` already adds DEC-236 for grilling lifecycle front-matter. T-03 explicitly requires stopping for a plan amendment when that number is allocated. No T-03 documentation file or enforcement file was changed, and no T-03 commit was created. A scan of fetched local and remote heads found DEC-236 through DEC-548 allocated and DEC-549 as the next free number.

**Recommendation:** authorize PM to replace DEC-236 with DEC-549 throughout T-03, preserve every other signed T-03 requirement, and re-sign the amended plan before the documentor resumes.

## Phase summaries

- **Plan:** the initial and corrected plan panels resolved all findings; the reconciled and re-anchored four-task plan was re-signed on 2026-09-29 with the 2-round / 90-minute rework ruling unchanged.
- **Main-session build:** T-01, T-02, and T-04 landed in commits `6512eeda`, `b12dfcf2`, and `45292dee`, followed by the probe receipt and run close at `dbeb43c1`. Unit and integration runners passed; parity recorded 291 cases and zero unplanned mismatches; the OpenAI live probe passed 18/18. The Anthropic note records `data:"null"` as a string, hook refusal, and successful completion of the same job. The two T-04 `plan-merge.py check` anchor failures are expected because the approved task deleted those symbols; the canonical reader self-test retains the pre-existing main baseline finding set.
- **Documentation:** BLOCKED without edits. The exact T-03 generator/index command passes only as an untouched baseline; it does not verify the unimplemented documentation change.
- **SIMPLIFY and validate:** not started because T-03 has not completed. No `review_sha` has been pinned.

## Open question

1. Authorize the recommended T-03 plan amendment from DEC-236 to DEC-549 and re-sign it so the documentor can resume? This is blocking.

## Spend and ledger

- Runs: 8 of informational budget 20.
- Cycles used: 1 of hard budget 10; current rework rounds: 0.
- Recorded spend: 313 wall-clock minutes, 584,876 tokens; rework time: 0 minutes.
- Judgements: 3.
- Amendments: none; overrule rate: 0/0.

## Proposed backlog

None. The decision-number collision is a blocking signed-plan correction, not backlog work. Validation has not yet produced advisory findings.

## Sources and disclosure

No report round was spawned. This briefing was assembled from:

- `runs/plan-product/digest.md`
- `runs/plan-c1-product/digest.md`
- `runs/plan-reconcile-product/digest.md`
- `runs/plan-reanchor-product/digest.md`
- `runs/plan-reanchor-assess-product/digest.md`
- `runs/build-docs-product/digest.md`
- `notes/research-FEAT-1928-digest-object-contract-goalcheck-plan.md`
- `notes/validator-parity.md`
- `notes/live-digest-object-probe.md`
- `notes/receipt-harness-documentor-T-03-c0.md`
- `notes/approval-2026-09-29.md`

The feature ledger names two run records whose digest directories are absent in this worktree: `plan-product-c1` and `build-main-direct`. The build summary above uses the committed build/probe evidence and the main-session handoff; it does not claim a missing digest was read.
