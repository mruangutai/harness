# Goal-check — BUG-2295 — validate c2

PASS: both approved perspectives land; SC-01–04 are met and the consolidated c1 mixed-case bypass is closed at pin 7d76c1cea576822760e8bc42432f8c01fc3c8031 (base dd04e52a898109fdbe09cf5fa14e1148161734d0). No replan or decision amendment is required.

## Perspective landing

- **operator — pass:** SC-01 supplies actionable cycle-name refusal and canonical acceptance; SC-04 preserves the ship prerequisite/exemption and shipped history. Evidence: notes/review-harness-qa-c2.md:17–21 and notes/review-harness-code-reviewer-c2.md:11–14.
- **code maintainer — pass:** SC-02 supplies Write/Edit regression coverage with retained shape checks; SC-03 corrects the explanation without changing ship behavior. Evidence: notes/review-harness-qa-c2.md:18–21 and notes/review-harness-code-reviewer-c2.md:12–14.

## Criterion outcomes

All four SCs trace through pinned plan.yaml T-01.traces to its three owned files; no perspective or SC is orphaned. Source citations below are committed bytes read with git show at the full pin above, not working-tree claims.

| Criterion | Verdict / method | Discriminating evidence |
|---|---|---|
| SC-01 | met / automated | QA c2:17–21: current integration gate exits 0, 117 ok, zero FAIL; canonical build/validate/plan accepted, cycles 1/12/305 and mixed-case names refused with supersede guidance and exact lowercase canonical paths. QA c1:15–22 records original lowercase Write refusals red against dd04e52a; QA c2 independently reproduces mixed-case red against 253cdf2a production (12 assertion failures across Write/Edit and exact-path assertions), then green at this pin. Test: tests/integration/test-check-domain-post.py:909–950, _handoff_cycle_suffix_cases and helpers. |
| SC-02 | met / automated | Same QA receipts, c1:18–23 and c2:18–21: existing suffixed-file Edit reconstruction is exercised, canonical acceptance and cap/required-section/Done when cases remain green. Pinned test file:970–978 invokes the retained checks and new cycle cases. Unchanged-file controls are supplemental baseline-green checks, not refusal proof. |
| SC-03 | met / inspection | Reviewer c2:13 cites pinned .claude/skills/harness/bin/gh-sync.py:2586–2590: comment distinguishes DEC-252's shipped-feature exemption, preventive ship prerequisite and shared DEC-174 predicate; obsolete INV-17-at-done assertion removed. |
| SC-04 | met / inspection | Reviewer c2:14 and direct base-to-pin diff: gh-sync.py changes comments only; executable predicate/exemption/diagnostics at :2594–2602 are unchanged. Complete name-status diff contains no FEAT-2225 or FEAT-2229 paths, preserving the specified shipped c2/c3/c5 and c3/c4/c5 handoffs. |

QA c1/c2 above mean notes/review-harness-qa-c1.md and notes/review-harness-qa-c2.md; reviewer c2 means notes/review-harness-code-reviewer-c2.md. Current raw QA receipts: runs/2026-11-22-03-validate-c2-validator/qa-c2-{red,green,unit,integration}.out. Original red is inherited explicitly, not claimed re-executed in c2.

## C1 closure at the pin

The failed premise is repaired, not waived: pinned check-domain.py:2296 now compiles _RE_HANDOFF_CYCLE with _I, matching RE_HANDOFF:1486; :2315 lowercases the canonical path. Tests:918–950 exercise Build-c1, build-C1 and VALIDATE-C12 through both Write and Edit, including case-sensitive diagnostic assertions. QA's independently executed red/green establishes the formerly bypassing cases now refuse. Fix c4c93ef1 and the review pin have no difference in check-domain.py or this test file. Existing content checks remain at :2301–2305. Reviewer c2:11–12 concurs. This closes the one consolidated c1 finding; it does not erase the c1 failure record.

## Decision dispositions — canonical Mode 2

Every pinned decisions_affected row is keep, successor none; there are no amend/strike rows to score or DEC outcome rows to manufacture. Pinned .harness/harness/docs/DECISIONS.md is unchanged from the base. Each requested disposition is preserved, with its exact retained clause located at the pin:

| Plan row | Disposition assessment | Pinned decision anchor |
|---|---|---|
| 1 / DEC-174 | keep — preserved; landing grade skipped | :4553, “it builds directly.” T-01 remains main-session-direct, including enforcement tests. |
| 2 / DEC-225 | keep — preserved; landing grade skipped | :7408, “with no panel and no goal-check run”; bounded one-task patch retained. This is the requested validate perspective read, not a replan or added plan-stage gate. |
| 3 / DEC-252 | keep — preserved; landing grade skipped | :8193, “A shipped feature is checked for nothing”; only the ship comment changes, not the prerequisite or history. |
| 4 / DEC-254 | keep — preserved; landing grade skipped | :8299, “Each row has exactly five fields:”; all four plan rows retain five fields. :8349–8353 explicitly skips keep rows in landing grades. |

## Boundaries and open questions

Open questions: none. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent per intake; no substitute guidance was used. The pre-existing DEC-252 commentary discrepancy is outside T-01 and is not a finding. C1 artifacts are preserved. PM ran no tests, builds, lint, formatters, mutations or source edits; automated evidence is QA's, pinned inspection evidence is the reviewer's and direct read-only git comparisons. The only PM write is this c2 note.
