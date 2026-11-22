# FEAT-2229 code review — c4

**PASS. F3-I is closed by inspection at 46d0c4bce7cec18e0aabec56a490981496970cc0; no residual within the operator’s four-rule ruling and no actionable new-class finding identified.**

Reviewed `dfa52536..46d0c4bce7cec18e0aabec56a490981496970cc0` only. Read BRIEF, plan decisions, c3 review and operator ruling before the diff; completed spec compliance before quality assessment. Consulted PRODUCT/AGENTS.md and designated SPEC/DECISIONS/INDEX authorities; absent PRODUCT/docs contracts were not invented. Full history contains no human-tagged or foreign-feature commits. Only tracked dirt was feature.json bookkeeping; its live pin agrees with dispatch. Earlier c3 pin was evidence only, never executed. QA owns ef269da2/pin runtime-equivalence evidence.

## Stage 1 — specification compliance

- **T-01 / SC-02, F3-I closed:** `.claude/skills/harness/bin/plan_merge/check.py:207-208,276-310` caps fence/heading indentation at 0–3 literal spaces, rejects backticks in backtick-opener info, closes only on the opener’s character with sufficient run length and whitespace-only suffix, and excludes fenced headings. Four-space closer/openers remain content. The c3 counterexample cannot expose its spoof DEC-10. Unclosed fences remain open to EOF.
- **Regression binding:** `tests/integration/test-plan-decision-dispositions.py:281-323,337-383,649-661` invokes the actual CLI with spoof rejection and genuine-section acceptance controls. Coverage includes fenced/nested headings, suffix-bearing runs, over-indented openers/closers, heading lookup/section-end indentation, invalid backtick info and unclosed fences. Removing each new rule changes its corresponding expected result by inspection; no mutant executed here. Red-first receipts are historical evidence, not c4 execution claims.
- **SC-04 inspection met:** `.claude/skills/harness/teams/plan.yaml:59-66` requires the five fields and check; `.claude/skills/harness/teams/plan.yaml:103-108` requires independent omissions review and DEC-188 judgment; `.claude/skills/harness/templates/plan.yaml:75-86` and `.claude/skills/harness/references/patch-lane.md:20-22` preserve the empty-list claim and panel-free patch contract.
- **SC-05 inspection met:** `.omp/agents/harness-pm.md:58-82` requires individual pinned amend/strike outcomes and skips keep; `.claude/skills/harness/teams/validate.yaml:120-121` delegates to Mode 2; `.omp/agents/harness-validator-lead.md:104-105` preserves owning-task failures.
- **SC-06 inspection met:** `.harness/harness/docs/DECISIONS.md:5313-5336` rewrites DEC-188 without losing strike/amend distinctions; `.harness/harness/docs/DECISIONS.md:8253-8326` records DEC-254/D-01; `.harness/harness/docs/DECISIONS-INDEX.md:237` resolves DEC-254; `.harness/harness/docs/SPEC.md:2009-2043,2287-2302` retains the five-field and existing sc_status contract without a new validate script.
- SC-01/03 guards and SC-07 owner-scoped assertions remain intact. No scope creep, omission or mismatch identified against BRIEF/D-01.

## Stage 2 — quality and scanner locality

One decision-section scanner owns discovery and section bounds: `_real_headings` feeds `_Authority.section`; fence state is local. The package sweep found no second decision fence scanner. This is not literally zero other heading regexes: `_heading_level` repeats the same ATX prefix for DEC identity, and inherited `approval.py:356-357,378-385` separately slices BRIEF Approval. Neither introduces a conflicting decision-section convention; unrelated approval parsing was not silently folded into F3-I.

Required static grading ran once: canonical `code-grade.py --base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 --head 46d0c4bce7cec18e0aabec56a490981496970cc0`, exit 0, **PASSING: 97**, no high or grade-2 records. Its base is the measured origin/main merge-base, distinct from the feature diff base. No suites, builds, lint, formatting or runtime probes ran. QA should supply pinned acceptance-chain and rule/mutation evidence; this review does not substitute for it.

## Principles applied

- Model the Domain: judged the single fence-state transition and shared heading list rather than independent section scans.
- Delete First: accepted the localized scanner repair without a parallel parser or unrelated Approval rewrite.

Findings/must-fix: none. Open questions: none. No source/test edits.
