# Goal-check — FEAT-2229 — validate c1

**FAIL: SC-07 is partial: the canonical strike-deletion obligation lacks its required deletion-sensitive regression. DEC-188's promised amendment is met. Q-01 is now resolved by terminal pinned QA PASS; the original assessment below predates that evidence.**

Review pin: `1ef1edbf4cd13eed110e5a187fe45b2ce0438d43`; range: `dfa52536..1ef1edbf4cd13eed110e5a187fe45b2ce0438d43`. Source citations below are repository-relative paths and pinned lines at that full SHA. Read-only inspection: no tests, builds, linters, formatters, fixes or replanning performed.

**Fan-in qualification (not another goal-check):** terminal QA `notes/review-harness-qa-c1.md:1-3,15-26` reports unit/integration PASS at the same full pin, named task verifies, and reproduced fail-first evidence for SC-01/02/03/07. Q-01 is closed. The original evidence-only partial grades and perspective grades below are retained as the submitted record, not a continuing missing-QA claim; validator synthesis can discharge that qualification from this receipt. F-01 and SC-07's substantive coverage gap remain unchanged: green execution does not test the omitted obligation. No further checks or regrading were performed.

## Done when — by perspective (original assessment before QA arrival)

- **operator — partial.** SC-01/SC-03 have named schema, provenance and historical-byte regressions plus build red/green receipts; QA's required outcome/fail-first digest is absent. SC-05 and the actual DEC-188 amend outcome are met: missing promised edits must fail with an owning-task route.
- **reader — partial.** SC-04's semantic/mechanical split and SC-05's pinned per-row landing contract are met. SC-02's six independent rejection cases and controls exist, with red/green receipts, but await QA acceptance evidence.
- **code maintainer — partial.** SC-06 is met: one record, existing drafting check and existing sc_status shape; SC-07 leaves the strike-deletion alternative undefended (F-01).

## Success criteria (original assessment before QA arrival)

| ID | Outcome / method | Specific evidence |
|---|---|---|
| SC-01 | partial / automated | tests/unit/test-decision-disposition-schema.py:71-180: block/field/value checks, set-key round-trip/refusal bytes, apply creation round-trip. notes/red-first-T-01.md:8-36,93-105 records 13/40 before and 40/40 after. QA DIGEST unavailable. T-01 traces this criterion. |
| SC-02 | partial / automated | tests/integration/test-plan-decision-dispositions.py:197-292: separate missing block, unindexed DEC, STRUCK keep/amend, own-section clause, successor and owner failures, plus controls and served authority. notes/red-first-T-01.md:38-52,93-105 records red cases and 91/91 green. QA DIGEST unavailable. T-01 traces this criterion. |
| SC-03 | partial / automated | tests/integration/test-plan-decision-dispositions.py:297-335,360-493: era before/exact/after, null/missing config, history, creation, refusal byte comparisons and legacy/stamp preservation. notes/red-first-T-01.md:53-87,93-105 records red/green. QA DIGEST unavailable. T-01 traces this criterion. |
| SC-04 | met / inspection | .claude/skills/harness/teams/plan.yaml:59-66,103-108; templates/plan.yaml:75-86 and references/patch-lane.md:16-25 under the same skill prefix: five-field drafting/check, independent omission/empty-list scrutiny, DEC-188 softer-strike authorization and panel-free patch. T-02/T-03 traces. |
| SC-05 | met / inspection | .omp/agents/harness-pm.md:58-82 requires every amend/strike, skip keep, pinned DEC/path/line, verdict/method/evidence, rewritten amend text or strike record/justified successor deletion, failure/owner routing. .claude/skills/harness/teams/validate.yaml:120-121 delegates to Mode 2; .omp/agents/harness-validator-lead.md:104-105 preserves must_fix despite clean QA. T-02/T-03 traces. |
| SC-06 | met / inspection | .harness/harness/docs/DECISIONS.md:5313-5336,8253-8326; DECISIONS-INDEX.md:188,237 resolves DEC-188 and DEC-254 @8253; SPEC.md:2009-2043,2287-2302 integrates declaration and outcome contracts. No added digest field or validate script in the full diff. T-03 traces. |
| SC-07 | partial / automated | tests/integration/test-plan-team.py:424-506 scopes 30 obligations to owners; notes/red-first-T-02.md:6-67 records pre-change failures, green 182/182 and mutation witnesses. F-01 below leaves a required obligation unasserted. QA DIGEST unavailable. T-02 traces. |

## Decision-disposition outcome

**DEC-188 — met / inspection.** Plan row `decisions_affected[0]`: amend; clause `The enforcement is a human reading a diff.`; successor D-01 (recorded as DEC-254); reason replaces human-only enforcement with bounded drafting and pinned pm landing checks. At `1ef1edbf4cd13eed110e5a187fe45b2ce0438d43:.harness/harness/docs/DECISIONS.md:5313-5327`, current text actually replaces that claim with the exact bounded gate and per-row validate grading; :5329-5336 retains softer amendments/operator authorization and successor deletion rules, while :5307-5311 and :5326-5327 retain rejection of general detection. DEC-254 :8253-8326 records D-01. Owning task: T-03 / harness-documentor; no landing remediation needed. Seven keep rows intentionally ungraded.

## Owned finding / must-fix

**F-01 — substance; original severity med; T-02; owner main-session-direct; SC-07.** `tests/integration/test-plan-team.py:481-483` tests only the strike-record prefix. Delete the alternate obligation from canonical `.omp/agents/harness-pm.md:78-79` — `or the deletion is justified by its named successor with citations repointed (DEC-188, DEC-205)` — and every matched pattern, including the in-script 10m witness, is unchanged. [INFERENCE from literal pattern inspection; no mutation executed.] Thus the test does not detect losing this changed validate obligation despite SC-07's explicit deletion-discrimination requirement. Add independent owner-scoped protection and a corresponding deletion witness; QA owns executing evidence afterward. This does not invalidate SC-05's currently present text or DEC-188's actual landing.

## Evidence limits / open questions

- **Q-01 — resolved:** terminal QA evidence is `notes/review-harness-qa-c1.md:1-3,15-26`, binding the named passing tests and reproduced fail-first outcomes to `1ef1edbf4cd13eed110e5a187fe45b2ce0438d43`. No open evidence question remains; preserve the separate SC-07 coverage finding.
- Settled evidence consulted: notes/receipt-main-session-T-01-T-02.md; runs/r-20261121-t03-product/digest.md; runs/r-20261121-simplify-build-eng/digest.md. Simplify leave notes, D-01/DEC-254 and known landed create:true behavior were not reopened.
- Full diff inspected, including changed source, instructions, config, docs, tests and feature bookkeeping. Exact classification fixture is `tests/integration/canonical-reader-classification.json`, not tests/fixtures/. `tests/integration/test-plan-merge.py` is unchanged in this range; pinned case_create_path_approval:717-777 was inspected.
- PRODUCT/docs/spec.md, docs/decisions.md and docs/architecture.md are absent as settled in the signed brief. No replacement authority invented; the assigned pinned product SPEC/DECISIONS/INDEX were graded directly.
