# Goal-check — FEAT-2229 — validate c5

**PASS: all seven SCs and the DEC-188 amendment are met at c163d5ea0fb17da27b3455559f317d67852981c7 (P).** Independent c5 QA now supplies the M6/M8 and identifier mutation evidence that the original assessment awaited; SC-02 and the reader perspective are met. This corrects that evidence hold, not the implementation or scope. Security's separate runtime acceptance remains undetermined because its read-only guard prevented every planned observation; this capability blocker is not an observed product failure or an unmet literal SC-02.

## Evidence and provenance

The original assessment read BRIEF, plan T-01, operator answers-2026-11-22-c4-ruling.md, c4 consolidated digest and c4 PM/code/security artifacts. It consulted PRODUCT/AGENTS.md and its designated SPEC decision-disposition/validate sections, decision index and DEC-188/254 authority. Absent docs/spec.md, docs/decisions.md and docs/architecture.md were not invented. It inspected only P's commit delta and current pinned source/test anchors. This same-run correction reads the signed BRIEF, this note and the completed c5 QA/security notes; it carries the explicit c4 delta judgments below without fresh historical review. No old pin re-read, tests, mutations, builds, lint, formatters or verification commands executed by PM; no pinned checkout created, hence none needs cleanup. This research note is the only write.

At P, tests/integration/test-plan-decision-dispositions.py:393-413 adds three cases, invoked at :685-686. The closer case tests both cross-character directions; the tilde-info case permits a backtick in tilde info; the full-identifier case rejects x, underscore, joined hyphen and decimal continuations and permits colon, parentheses and bare-id headings. Each spoof has a genuine-clause positive control. They use the existing _spoof_and_control → expect_fail/expect_pass → run_check → subprocess path (:97-99,165-191), executing .claude/skills/harness/bin/plan-merge.py with isolated fixture roots, not a helper-only imitation. This binds actual CLI regression behavior, stronger than merely observing the correct scanner or a green suite.

P:.claude/skills/harness/bin/plan_merge/check.py:209-212,280-288 replaces the digit-only negative lookahead with an explicit full-identifier delimiter. _Authority.section uses that predicate (:332-339). Fence behavior is unchanged: tilde info remains legal (:291-293), closer character equality remains mandatory (:305). New tests exercise those existing predicates rather than adding alternate parsing machinery.

P:notes/red-first-T-01.md, section “Validate c4 round (operator ruling 2026-11-22)” (feature-relative notes path), is **authored main-session evidence**: M6 produces the two expected closer reds (120/130 including eight then-unfixed identifier failures), M8 produces the expected tilde-info red (121/130 with those same eight failures), restored tilde assertions pass; identifier source-before-fix is 122/130 with eight spoof/control failures; final integration is 130/130, unit 40/40, team 184/184. These are reported receipt results, not my execution or independent QA reproduction. Their case-specific reds support discrimination; final suite green alone cannot close the stronger obligation.

**Independent acceptance evidence:** notes/review-harness-qa-c5.md:5-23 records actual-CLI cases at P, not a reproduction inferred from the authored receipt: M6 both directions 128/130, each direction separately 129/130; M8 129/130; identifier pre-fix-matcher mutant 122/130. Each semantic red retains its paired genuine-clause green control; the unmutated pin is 130/130 before and after. These are mutation-tier fail-first proofs, not natural pre-fix SHA execution. QA did not rely on notes/red-first-T-01.md. T-01 verify ran verbatim: unit 40/40, integration 130/130; configured runners exited 0 across 62 unit and 89 integration files. This closes the original independent-evidence hold.

**Separate security capability limit:** notes/review-harness-security-reviewer-c5.md:3-23 records static identifier closure but zero runtime observations: the read-only guard refused its temporary-fixture command. The 107 planned CLI observations are not executed evidence. QA's independent discrimination closes the literal SC-02 delta; it does not establish execution of that broader security-owned probe or turn the security BLOCKED receipt into PASS.

## Perspectives — one outcome each

- **operator — pass:** SC-01/03/05 and DEC-188 continue to carry declaration safety, forward-only compatibility and actual promised landing; T-01/T-02/T-03.
- **reader — pass:** SC-02's own-section rejection and valid controls retain c4 evidence, now supplemented by independent c5 actual-CLI M6/M8 and identifier mutation proofs; SC-04/05 remain met; T-01.
- **code maintainer — pass:** SC-06/07 preserve one record/check and owner-scoped instruction regressions; T-02/T-03. Static tests do not establish agent obedience.

## Individual outcomes and delta relevance

C4 evidence below is retained, not represented as fresh inspection or execution. C4 consolidated digest is runs/r-20261121-validate-c4-validator/digest.md; PM evidence is notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c4.md.

| ID | Outcome / method | Evidence and explicit delta judgment |
|---|---|---|
| SC-01 | met / automated | C4 QA notes/review-harness-qa-c4.md: unit 40/40; base red 13/40 reproduced. P changes neither schema nor writer/refusal paths; retained. |
| SC-02 | met / automated | C4 rejection/control evidence retained; P test :393-413,685-686 and check.py :209-212,280-288 directly address own-section selection. Independent notes/review-harness-qa-c5.md:5-23: M6 both 128/130, each 129/130; M8 129/130; identifier mutant 122/130; pin 130/130 with genuine controls green. Mutation-tier fail-first plus T-01 verify discharges the pending acceptance evidence; authored receipt remains separately attributed. Security's unexecuted broader probe is not a literal criterion failure. |
| SC-03 | met / automated | C4 QA notes/review-harness-qa-c4.md: era/provenance green and base red reproduced. P changes no era, eligibility, creation or provenance mutation logic; retained. |
| SC-04 | met / inspection | C4 PM: pinned teams/plan.yaml:59-66,103-108; templates/plan.yaml:75-86; references/patch-lane.md:16-25. P changes none of these instructions; retained. |
| SC-05 | met / inspection | C4 PM: pinned .omp/agents/harness-pm.md:58-82; teams/validate.yaml:115-121; harness-validator-lead.md:100-105. P changes no grading/delegation/failure-routing contract; retained. |
| SC-06 | met / inspection | 46d0c4bce7cec18e0aabec56a490981496970cc0:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326; PM note. P changes no authority text, index, SPEC or result schema; retained. |
| SC-07 | met / automated | C4 QA notes/review-harness-qa-c4.md: team tests green in full integration; base red reproduced. P changes no canonical prompt or test-plan-team.py obligation; retained. |
| DEC-188 | met / inspection | 46d0c4bce7cec18e0aabec56a490981496970cc0:.harness/harness/docs/DECISIONS.md:5313-5336; successor DEC-254:8253-8326; row decisions_affected[0], owner T-03. P changes no amendment text or row promise; retained without re-inspection of old pin. |

DEC-188 is the sole amend/strike row: clause “The enforcement is a human reading a diff.”, successor D-01 → DEC-254, replacement by bounded drafting/pinned landing enforcement while preserving strike/amend distinction. Keep rows remain skipped.

## Findings and routing

No new implementation must_fix; the original SC-02 evidence hold is discharged by completed independent QA. No production change or replanning requested. Product goal-check PASS is distinct from team security runtime acceptance, which remains BLOCKED/undetermined because no assigned security observations executed.

Retained backlog advisories, not new gates: substance / low / T-01 Unicode line-break/whitespace mismatch; substance / low / T-01 list-container phantom fences. QA c5 additionally records tilde-closer length and closer-info assertion gaps (X2/X5/X6 and X3), outside the operator-authorized M6/M8 set, as low-severity backlog only. SEC-C4-01's identifier fix has static closure and independent QA mutation discrimination; the broader security-owned runtime probe remains unexecuted. C4-QA-CONTRACT, SIMPLIFY B-1/B-2 and create:true already-exists remain operator-designated backlog, not reopened findings.

Open question **SEC-C5-EXEC (blocking for security acceptance only):** permit the security reviewer's temporary-fixture CLI execution or route its exact controls to an authorized executor (security note :23). No product acceptance evidence remains outstanding. This correction is not a fresh whole-feature review or a claim of execution equivalence between historical and current pins.
