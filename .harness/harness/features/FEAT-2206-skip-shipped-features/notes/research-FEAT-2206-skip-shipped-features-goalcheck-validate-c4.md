# Goalcheck correction c4 — 4a351faea95ad3776f130d0f42f303a4eee3e4b9

Acceptance interpretation unresolved: literal SC-03 is not_met; its narrower preservation-only reading is supported, not approved by this assessment. The unconditional c3 SC-03/operator pass is superseded here; the original c3 note remains intact. No implementation task, waiver, authority precedence or finding severity is assigned.

## Perspectives

operator — partial: SC-01/02 are met and ordinary historical comparisons survive, but QA's malformed-shipped INV-52 counterexample defeats unqualified collision protection; SC-03 acceptance needs Q-02 (BRIEF.md:9,19; notes/review-harness-qa-c4.md:25-26,34).
code maintainer — pass: SC-04 retirement and unreadable/non-shipped protections retain fresh QA evidence; this does not certify every malformed historical branch claim (BRIEF.md:11,21; notes/review-harness-qa-c4.md:24,27).

## SC outcomes and trace coverage

All four SCs trace to signed T-01 (plan.yaml:23-25); operator maps to SC-01/02/03, code maintainer to SC-04. Coverage is complete; discharge is not.

- SC-01 met, automated: test-check-state-shipped-ctx.py classification/open-order assertions; QA c4 records fresh baseline 10 FAIL/5 PASS and pinned 15 PASS/0 FAIL; duplicate-status rework red remains retained rather than freshly reproduced (notes/review-harness-qa-c4.md:19,21,24).
- SC-02 met, automated: named full/changed/explicit/read-only CLI tests plus every-record corpus assertions; fresh baseline 21 corpus FAIL, pinned 7 shipped/21 PASS (notes/review-harness-qa-c4.md:19,21,25).
- SC-03 literal not_met, automated evidence: valid branch feat/dup on a shipped record with parent '²', 4,301 digits or 'x', plus another landed same-branch record (building or shipped), yields no INV-52; parent 5 control does report it. This falsifies unqualified shipped-branch collision detection, not the other clauses (notes/review-harness-qa-c4.md:26,34). Narrower preservation-only reading: met on supplied comparison tests and baseline behavior, conditional on an operator ruling; it does not discharge literal SC-03. The malformed-branch cell lacks a regression test.
- SC-04 met, automated: named retirement tests fail at baseline, pass at pin; adjacent missing-selector/unreadable-status controls remain green (notes/review-harness-qa-c4.md:19,21,27).

## Contract tension and retained dispositions

BRIEF.md:19,33 promises comparison-only shipped data and preserved INV-52 without an explicit strict-invalid exception. DEC-252 (DECISIONS.md:8159-8163) keeps all three comparisons but specifies usable factory claims expressly for INV-24. Signed T-01 (plan.yaml:71) confines its raw-record seam/usable issue rules to INV-24 and says preserve INV-52/29 “as they already operate”; its files list excludes check_state/corpus.py and feature_corpus.py (plan.yaml:31-52). Binding grilling:19,27-28 preserves INV-52 and delegates mechanism, without explicitly deciding malformed-record branch salvage. These support competing readings; neither baseline behavior nor a measured defect grants task ownership or resolves acceptance authority.

QA c4 F-1 remains low/substance/advisory, non-regression; code c3 F-1 remains med/substance/T-01 must-fix with its “no new operator decision” conclusion (notes/review-harness-qa-c4.md:34,42; notes/review-harness-code-reviewer-c3.md:3,13-17). This correction preserves, rather than adopts or re-rates, both dispositions. Baseline 'x' already skips; '²'/oversized previously crash, now refuse and skip. This establishes the failure, not an approved obligation to broaden the strict census.

Both c1 findings remain closed by fresh, independent QA reproductions: oversized shipped INV-24 retains the usable issue-11 collision; active Arabic-Indic '٣' retains the issue-3 collision. Baseline/c1/pin results and named tests are at notes/review-harness-qa-c4.md:8-13,28. No reversal of either closure.

## Evidence boundaries

QA c4 supplies exact-pin 60 unit + 86 integration files passing (146), not merely transferred b5b6fa70 evidence. Literal check-state exits 1 only on disclosed INV-26; no clean literal chained T-01 verify is asserted. b5b6fa70 differs only in feature.json and remains equivalent-code, not literal execution evidence (notes/review-harness-qa-c4.md:18-21,30-31). Product guidance absence is inherited from c3/QA reports, not newly probed. PM read artifacts only: no tests, probes, grading, builds, lint, formatting, source edits or commits; no replan or approval changes.

## Open questions

- Q-01 (nonblocking, T-01): YAML-mapping/invalid-YAML intent wording differs from DEC-252's text-line classifier. Recommendation: retain the adopted DEC-252 behavior and reconcile prose through its owner; no new implementation ruling or human decision is required for this assessment.
- Q-02 (blocking acceptance, operator ruling): Does SC-03 require branch salvage from strict-invalid shipped records, or preserve INV-52's existing strict-census population? Recommendation: accept the preservation-only reading for this bounded patch, explicitly acknowledging that strict-invalid shipped records can lose branch protection, because T-01 preserves existing INV-52 operation and does not own its census files. This is a proposed interpretation, not a waiver or sign-off. If the operator requires the literal broader guarantee, scope/approval ownership must be resolved before assigning a remedy; do not automatically adopt code c3's must-fix classification or expand files. Evidence collection is complete; repeated execution cannot settle this contract choice.

## Principles applied

Experience First: expose the operator's concrete lost collision protection and the maintainer's preserved active checks separately; do not let implementation convenience or green suites manufacture acceptance.
