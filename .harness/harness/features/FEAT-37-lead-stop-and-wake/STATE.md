# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: amendment DRAFTED and UNSIGNED; awaiting the operator's signature. No build started.
- squad: product (last), validation and eng before it
- status: Building — cycles 1/10, runs 14/20, HEAD 899e4a6

**THE AMENDMENT IS ON DISK AND IS NOT SIGNED.** One pm run, zero send-backs, per the operator's
ruling in `notes/answers-2026-08-27-02.md`: AUTHOR THE EVAL, do not sign an exclusion. Added to
plan.yaml: **T-07** (`change_type: scaffolding`, authors the eval under `evals/lead-never-wait/`),
**T-08** (`change_type: config`, `harness-dev-ops` sets `test_kinds.eval.cmd` and flips `status`),
and decisions **D-14** and **D-15**. `approval:` was correctly LEFT UNTOUCHED at
`approved`/2026-08-27 — it signs the FIVE-task plan and the task set has changed since. Only the
main session writes that block (DEC-120). **No build starts until it is re-signed.**

**BRIEF.md:275-278 IS CORRECTED** and the correction is verified in the diff: the bullet no longer
says the eval requirement "resolves to a soft skip and proves nothing". It now states that
`unresolved` is not `excluded`, that the requirement BLOCKS, and cites DEC-36, DEC-187 and DEC-70.
Both decisions were re-derived at disk this run: DEC-36's own heading (@448) reads "An unresolvable
test command is a LOUD third state, not a soft skip", and DEC-187 (@5861) requires
`excluded_because` + `signed` for the excluded shape, which only `functional` carries.

**THE BLOCKING QUESTION IS T-07's AUTHOR, AND IT IS STRUCTURAL, NOT A DEFECT.** DEC-70 (@852) names
`harness-ai-dev` as the eval's author. `check-domain.sh --resolve` returns **NOBODY** for
`evals/**` in this checkout. I re-derived it rather than taking the report: the cause is NOT that
`evals/` is absent from disk — a nonexistent path under a harness-base glob
(`observations/harness-ai-dev.md`) resolves cleanly to `harness-ai-dev`. The cause is that
`evals/**` is a **product-base** glob. `resolve_fleet` reports this checkout's product bases as
`harness-factories/kaya-ai` and `harness-factories/harness-factory-smoke` — other repositories
entirely — so the two-sided filter at `check-domain.sh:273-278` drops every product-code glob when
the target sits in the harness base. `src/**` returns NOBODY for `harness-backend-dev` for exactly
the same reason. **In this self-hosted checkout the product-code personas own nothing but their own
receipts, expertise and observations.** I did not isolate which half of the two-sided rule rejects
it and do not claim to; the operational conclusion is measured and is what matters.

**COSTS OF THE THREE ROUTES, ALL MEASURED THIS RUN:** main-session-direct for T-07, the lane T-02
already took, deviating from DEC-70's named author. Or widen ai-dev's domain first — but
`.harness/team-config.yaml` itself resolves to **NOBODY**, so that is a main-session step too, plus
a run. Or relocate the eval to a path ai-dev already owns here, which is only its receipt/expertise/
observations paths — none of which an eval belongs in.

**`.harness/harness.json` RESOLVES CLEANLY to `harness-dev-ops`**, so T-08's lane is sound and needs
no widening. DEC-174 does NOT cover it: amendment 4 (@4983) rules the parenthetical list is examples
and the CATEGORY governs, and no enforcement script reads `test_kinds.eval.cmd`. pm reached the same
conclusion by the stronger route; the dispatch's own "not in the named list" argument was void.

**TWO GAPS TO FOLD INTO SIGNATURE RATHER THAN SPEND A RUN ON:** the `lanes:` block (plan.yaml:42-68)
still reads `resolved_at: 8fc87f8` with eight rows and NO row for either new surface — verified. And
neither new task carries a matrix-required test: `scaffolding` and `config` both map to `always: []`.

**BUDGET IS THE BINDING CONSTRAINT.** 14 of 20 runs; six remain for eval authoring, the qa re-run,
the panel, the goal-check and the docs sweep. pm excluded T-07 from its count as main-session-direct;
if main-session steps do count, slack is zero.

**UNCHANGED AND STILL BINDING:** SC-08 stays `not_met` (four corroborations; the operator runs it
after merge from the main checkout, D-13). The gap in the task numbering is deliberate and the
struck id is deliberately NOT named here — check-state.sh raises a violation when a live STATE.md
names a task its plan no longer holds, and this run re-introduced that defect once and corrected it.
D-12 is the strike record and #903 the regression. Six INV-26 violations are known, expected and the operator's under
DEC-174 — not edited, not worked around. `review_sha` is still `none` and must NOT be pinned until
the gate resolves and simplify has run.

## Open Questions

- Q1 (was: D-02 and D-11 spell the ruling AMEND) — RESOLVED at re-plan. Both now read "corrected IN
  PLACE". The only `AMEND` strings left in `plan.yaml` are T-05's and T-06's own DO NOT ADD AN
  AMENDMENT instructions.
- Q2 (was: DEC-199 amend or STRIKE) — RESOLVED. Corrected in place. D-11 and T-06 carry the reasoning.
- Q3 (was: the #811 split ruling) — RESOLVED by operator ruling of 2026-08-24. D-07 is the strike
  record. Issue #811 stays OPEN and returns to the backlog.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files;
  the lead reconstructs it by hand. Schema gap or intended?
- Q6 (the #866 deadlock) — HALF CLOSED BY FEAT-42, and the note that said otherwise is now corrected.
  The dispatch end is fixed: `release_cmd` prints an absolute single-agent command, so a refusal no
  longer tells an agent to wipe every feature's live claims. The RETURN end is what T-04 still
  corrects. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry
  when they run from one cwd.
