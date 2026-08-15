# Observations — harness-orchestrator — FEAT-06-team-layer-inv6

- 2026-08-04: `cost-report.py --into <state.yaml>` fully prevents the INV-16 duplicate-`cost:`-key
  defect. product-lead raised it as Q13 with four FEAT-04 recurrences
  (`FEAT-04/runs/2026-08-01-03-product/digest.md:24`, `04-product/digest.md:25`,
  `13-product/digest.md:15`, `FEAT-04/feature.yaml:114`), all hand-repaired. Verified after this
  run: `grep -c '^cost:'` returns 1. The defect is not in the lead's seeding — it is in metering
  with `>>` instead of `--into`. Every FEAT-04 repair was fixing a symptom of the wrong flag.

- 2026-08-04: a lead returned an unprompted CORRECTION to its own member's artifact text
  (product-lead flagged `PLAN.md:687` saying the flip-delta touches three items "only" while
  `PLAN.md:173` names a fourth). I verified both line anchors before relaying and both held. The
  correction was worth more than the digest's headline: it was the one claim that would have
  under-priced a user decision. Spot-checking a lead's self-correction is cheaper than spot-checking
  its agreement.

- 2026-08-04: a user re-scope arrived as an answers file that SUPERSEDED the question it answered
  (EQ-1 was "accept or widen"; the answer was "neither, re-plan"). Both options the tier above had
  constructed were wrong. The tell was that the answers file spent its first section rejecting the
  question's framing rather than picking an option. When that happens the dispatch must carry the
  rejected options explicitly as LEAVE items, or pm re-derives them.

- 2026-08-04: pm's budget-fit estimate (Q9, "31-64 spent, the re-scope fits") was computed from
  feature.yaml BEFORE I metered pm's own run. Metering moved it to 57-90. A member's
  cost-feasibility answer is always one run stale by construction — it cannot see the run it is
  itself producing. Re-derive it after metering rather than relaying it.

- 2026-08-04: I declined to run the stale segment-2 eng review before the blocking decision it would
  have reviewed was signed. Reviewing a plan whose architecture question is unsigned means the
  review is stale on the flip. Sequencing a stale gate AFTER the signature, not before, is an
  execution-time adjustment and did not need the user.
