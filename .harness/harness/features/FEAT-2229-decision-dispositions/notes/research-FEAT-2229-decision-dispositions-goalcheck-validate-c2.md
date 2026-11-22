# Goal-check — FEAT-2229 — validate c2

**FAIL (evidence gate): inspection outcomes and all three prior repairs are substantiated, but terminal c2 QA evidence is not available to discharge automated outcomes. DEC-188 landing is met.**

Pin P = a8b8df6196c6107b76cbd941bf2266b3e71476d6; range dfa52536..a8b8df61. Every source/test line below was read with git show P:path. No tests, builds, lint, formatting, mutations, fixes or plan edits were run by this reader. Grades stand until the next validate; later green execution must not silently rewrite this record.

## Perspectives

- **operator — partial:** SC-01/03 have discriminating schema, creation/provenance and historical-byte assertions, but lack terminal c2 QA acceptance. SC-05 and DEC-188 prove the pinned promise/landing route (T-01/T-02/T-03).
- **reader — partial:** SC-02 has separate mandatory rejection/control cases, including repaired fenced-section selection; terminal QA remains outstanding. SC-04/05 are met by canonical scope and landing instructions (T-01/T-02/T-03).
- **code maintainer — partial:** SC-06 is met: one five-field record, existing drafting check and existing sc_status contract. SC-07's formerly missing successor-deletion assertion now exists at its canonical owner with a discriminating witness; automated QA acceptance remains outstanding (T-02/T-03).

## SC outcomes

| ID | Grade / method | Pinned evidence and ownership |
|---|---|---|
| SC-01 | partial / automated | P:tests/unit/test-decision-disposition-schema.py:71-180 checks shape, exact fields, values, lossless set-key/apply round trips and refused-write bytes. P:tests/integration/test-plan-decision-dispositions.py:436-449 checks malformed creation refusal/no file and valid creation. P:.claude/skills/harness/bin/plan_merge/union.py:340-341,381-391 calls the shared shape validator before creation; harness_yaml.py:421-433,460 supplies that same rule. P:feature notes/red-first-T-01.md:8-36,107-128 records red/green. T-01; QA acceptance pending. |
| SC-02 | partial / automated | P:tests/integration/test-plan-decision-dispositions.py:197-246,281-340 separately covers empty/keep/amend/strike controls, absent block, unindexed DEC, STRUCK keep/amend, own-section/normalization checks, successors, ownership and served authority. :281-292 adds plain/nested fenced-heading rejection plus real-section/end-scan controls. P:.claude/skills/harness/bin/plan_merge/check.py:279-321 excludes fenced headings before selecting exact DEC sections; :350-372 retains row-index/DEC diagnostics. Red receipt notes/red-first-T-01.md:38-52,107-128. T-01; QA acceptance pending. |
| SC-03 | partial / automated | P:tests/integration/test-plan-decision-dispositions.py:343-378 covers before/exact/after era, null/missing era, invalid instants and approved/landed history; :406-434,493-554 covers writer stamp, refusal routes, byte preservation and ordinary legacy edits. Red receipt notes/red-first-T-01.md:53-105. T-01; no fresh c2 QA digest, so prior met outcome is not promoted solely from a former suite result. |
| SC-04 | met / inspection | P:.claude/skills/harness/teams/plan.yaml:59-66,103-108 requires the five fields/check and independent omission/empty-list scrutiny, DEC-188 flat-versus-soft distinction and operator authorization; templates/plan.yaml:75-86 gives explicit empty list; references/patch-lane.md:16-25 preserves one task/no panel. T-02/T-03. |
| SC-05 | met / inspection | P:.omp/agents/harness-pm.md:58-82 requires individual amend/strike grades, keep skipping, pinned DEC/path/line and verdict/method/evidence, current amended text or strike record/justified successor deletion, and failure/owning-task routing. P:.claude/skills/harness/teams/validate.yaml:115-121 delegates at supplied pin; P:.omp/agents/harness-validator-lead.md:100-105 preserves failures despite clean QA. T-02/T-03. |
| SC-06 | met / inspection | P:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326 records bounded enforcement and schema authority while retaining exclusions; DECISIONS-INDEX.md DEC-188 @5290 and DEC-254 @8253 resolve; SPEC.md:2009-2043,2287-2302 integrates existing declaration/goal-check machinery. Full range file list contains no new validate-time script or digest schema field. T-03. |
| SC-07 | partial / automated | P:tests/integration/test-plan-team.py:424-435 selects each canonical owner (pm specifically Mode 2 through Mode 3); :436-499 defines independent obligations; :484-486 now explicitly requires successor-justified deletion with repointed citations. :500-506 checks presence and deletion sensitivity in that same owner slice. P:notes/red-first-T-02.md:74-90 records old-test mutant green, new-test mutant exit 1 with the exact alternative assertion failing, and real-source 184/184 green. T-02; terminal QA acceptance pending. |

## Prior findings — independently regraded, not erased by suites

- **F1 — substance / high / reader code-reviewer / T-01:** implementation repair substantiated. Creation calls the shared validator before rendering/writing (union.py:340-341,381-391); regression :436-449 demands nonzero diagnostic, absent output file and valid control. Pinned red receipt records the formerly accepted malformed row and now-green refusal. Closure of the execution gate still belongs to QA.
- **F2 — substance / med / reader code-reviewer / T-01:** implementation repair substantiated. check.py:279-321 tracks fence character/length from file start, selects real exact DEC headings and ignores fenced impostors/end boundaries. Regression :249-292 covers ordinary and nested fences plus real-clause and post-example controls. Pinned red receipt names the three discriminating failures.
- **F-01 — substance / med / reader harness-pm / T-02:** assertion repair substantiated. The new obligation is scoped to canonical pm Mode 2, not another document or file-global match. Removing its matched clause makes _missing nonempty in :500-506; the file-level mutation receipt :80-90 reports exactly that assertion red while the old suite stayed green. This is static instruction coverage, not proof of agent obedience.

## Decision-disposition landing (third unit)

**DEC-188 — met / inspection; owning task T-03.** Plan row decisions_affected[0] is amend, clause `The enforcement is a human reading a diff.`, successor D-01/DEC-254, reason replacing human-only enforcement with bounded drafting and pinned pm landing checks. At P:.harness/harness/docs/DECISIONS.md:5313-5327 the current text actually replaces that assertion with the five-field shape/index/section/successor/ownership gate and individual pm grades; :5307-5311,5326-5327 retain rejection of general stale-decision detection; :5329-5336 retains softer amendment/operator authorization and named-successor deletion rules. D-01 resolves to DEC-254 :8253. This is direct current-text evidence, not a mention or a suite result. Seven keep rows are intentionally not graded. No landing remediation is due.

## Evidence gate and limits

**E-01 — substance / med / reader harness-pm / owning tasks T-01 and T-02; evidence collection owner QA.** Automated SC-01/02/03/07 remain partial because no terminal c2 QA DIGEST or notes/review-harness-qa-c2.md was available at collection. Required action: QA supply named pinned execution and fail-first acceptance; do not ask the user to test or infer it from build receipts. This is an evidence gap, not a newly alleged production defect. Inspection criteria were directly re-read at P; no c1 grade was blindly carried forward.

Verified git diff c8a8e174..P changes only this feature's feature.json and plan.yaml (two lines); source/tests/fixtures/config and committed red receipts are identical between those commits. This establishes subject equivalence, not re-execution. No tests were run against the c1 pin. Build receipts are committed at P but are explicitly secondary to QA acceptance.

Pinned AGENTS.md identifies SPEC/DECISIONS/INDEX as product authorities; SPEC's declaration and validate contracts and DEC-73/188/205 were consulted. The known absent PRODUCT/docs/{spec,decisions,architecture}.md were not invented. Settled LEAVE boundaries (D-01/DEC-254 content, FINISHED_STATIONS draft classification, pm placeholder, gate placement, simplify/briefing leaves and landed create:true reporting) were not reopened. No scope expansion or new implementation finding. Open question: E-01 only; no UAT is required.

## Terminal correction — same validate c2, 2026-11-21

**FAIL: E-01 is closed by terminal QA PASS, but SC-02 is not_met because the remaining fence-suffix case violates its literal own-section promise.** This appended assessment supersedes the provisional grades above, not their historical bytes. The earlier “next validate” restriction, F2 generalization, “no implementation finding” and E-01-only open-question statements are superseded here within the same run; no c3 assessment or new review pin is introduced.

Pin remains P = a8b8df6196c6107b76cbd941bf2266b3e71476d6, range dfa52536..a8b8df61. Terminal evidence: notes/review-harness-qa-c2.md:14-40 reports fresh execution at P, matrix_ok true, full unit/integration green, signed T-01/T-02/T-03 green and natural semantic RED for SC-01/02/03/07 at immutable base dfa52536. F1/F2 use pre-fix 98305097; F-01 uses the pinned owner-scoped deletion witness. These are QA's executions, not mine; no tests or other executable verification were run by PM.

### Terminal perspectives and SC outcomes

| Perspective | Terminal outcome |
|---|---|
| operator | met — SC-01/03 automated evidence is now accepted; SC-05 and DEC-188 landing remain met (T-01/T-02/T-03). |
| reader | partial — SC-04 remains met, but SC-02's section-identity protection fails in the specific static case below (T-01). |
| code maintainer | met — SC-06 remains met and SC-07 now has terminal owner-scoped, deletion-sensitive QA acceptance (T-02/T-03); static prompt coverage does not claim agent obedience. |

| ID | Terminal grade / method | Evidence |
|---|---|---|
| SC-01 | met / automated | QA c2:17,26-27,33,37; P:tests/unit/test-decision-disposition-schema.py:71-180 and tests/integration/test-plan-decision-dispositions.py:436-449. Shape/writer checks green; natural RED and creation-refusal repair accepted. T-01. |
| SC-02 | not_met / automated | QA c2:17,28,33,38 proves existing rejection/control cases and original fence examples green, not the suffix variant. Static counterexample at P:check.py:203,279-320,350-363 below contradicts the explicit “text in another section cannot satisfy” clause. T-01. |
| SC-03 | met / automated | QA c2:17,28,39; P:tests/integration/test-plan-decision-dispositions.py:343-378,406-434,493-554. Boundary/provenance/legacy assertions green with natural RED. T-01. |
| SC-04 | met / inspection | P:teams/plan.yaml:59-66,103-108; templates/plan.yaml:75-86; references/patch-lane.md:16-25, under .claude/skills/harness. Prior direct pinned inspection stands, corroborated by code review c2:19. T-02/T-03. |
| SC-05 | met / inspection | P:.omp/agents/harness-pm.md:58-82; .claude/skills/harness/teams/validate.yaml:115-121; .omp/agents/harness-validator-lead.md:100-105. Individual landing grades and preserved failure routing remain present; code review c2:20. T-02/T-03. |
| SC-06 | met / inspection | P:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326; DECISIONS-INDEX.md DEC-188/254; SPEC.md:2009-2043,2287-2302. Prior pinned bounded-authority/schema inspection stands; code review c2:21. T-03. |
| SC-07 | met / automated | QA c2:18,29,34,40; P:tests/integration/test-plan-team.py:424-509. Canonical per-owner obligations, successor-deletion alternative and independent deletion witness accepted; natural RED at base and F-01 old-green/new-red demonstrated. T-02. |

### Remaining acceptance failure — same medium T-01 substance

F3 (code reviewer c2:15) and SEC-C2-01 (security reviewer c2:11,16) describe the same residual, not two defects. Retain substance / med / owner T-01; neither reader's advisory PASS or lack of must_fix is changed. Product acceptance is independently **not_met**, not a severity escalation.

At P:.claude/skills/harness/bin/plan_merge/check.py:203, FENCE_RE matches only the initial fence run. At :279-287, an open three-backtick text fence is closed by a three-backtick python content line because only character and run length are compared; the non-whitespace suffix is never checked. Markdown leaves that line inside the original fence. Put a spoof DEC-10 heading and clause after that content line inside DEC-11's example, close the actual fence, then put genuine DEC-10 without the clause later. _real_headings (:290-298) records the spoof before the genuine heading. _Authority.section (:313-320) returns the first matching DEC-10 section, and _row_faults (:359-363) accepts its spoof clause. With an indexed non-struck DEC-10, a valid in-era pending draft and otherwise valid row/ownership/successor controls, the required own-section rejection is absent. This is a static control-flow counterexample, **reasoned, not executed**; existing green tests do not exercise the suffix-bearing closing candidate.

Original F2 plain/nested-fence and end-scan examples are closed by QA's targeted red/green evidence; the suffix case is explicitly not covered by that closure. F1 and F-01 are closed by both structural evidence and QA's discriminating execution. E-01 was solely same-run evidence timing and is closed without a user question.

Required acceptance work is bound to **T-01**: preserve actual Markdown fence boundaries for suffix-bearing content lines, with a real-check regression rejecting the spoof clause and accepting the genuine section, plus discriminating red/green evidence from QA. No source/plan edits or new task are authored here. DEC-188 remains **met / inspection / T-03** on the exact pinned current text and successor resolution cited above; seven keep rows remain intentionally ungraded. All settled LEAVE boundaries remain untouched. Open questions: none; no UAT required.
