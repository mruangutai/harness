# Goal-check validate c1 — FEAT-2340

**PASS — both signed perspectives are delivered; SC-01–SC-04 are met.** Review pin: `125a04f847db18bcc2ead0b9003a6b2826f9cd55`; signed comparison baseline: `e239d88156c508c948d49cd31238ea13b3b39865`. Source and decision evidence below comes from pinned git objects, not the control-plane gate. No tests, builds, lint, formatters or production edits performed by this reader.

## Perspectives
- **code maintainer — pass:** SC-01/SC-02; the existing angle questions and single-home naming bullets are present, the gate spells flags out and shares each targeted path grammar, and repair-independent respellings remain (`.claude/skills/harness-simplify/references/angle-reuse.md:13–19`, `angle-simplification.md:15–21`; `.claude/skills/harness-craft/references/model-the-domain.md:13–20`; gate anchors below).
- **operator — pass:** SC-03/SC-04; QA reports eight existing suites green at this pin with no FAIL output, corroborated by pre/post receipts; production scope is exactly the four approved files and prevention commit `df6ae1cc` precedes refactor `ffe320f5` (`notes/review-harness-qa-c1.md:11–20`; pinned baseline diff and task commit file lists).

## SC evidence and traceability
- **SC-01 — met, inspection; T-01.** The two angle questions land in their existing code-surface sections; cost/evidence and anchoring warnings remain. The three bullets and explicit bootstrap exception occur beside the naming paragraph in model-the-domain.md at the perspective anchors above. T-01 changes only these three guidance files; frontmatter and generated indexes are untouched.
- **SC-02 — met, inspection; T-02.** In `.claude/skills/harness/bin/check-domain.py`, `_PLAN_YAML_PATTERN` and its named feature_dir consumer are at `951–966`, case-insensitive shape compilation at `1501`; the legacy guard still runs at `1196` before shape rules (`2410–2432`). Mixed-case Plan.yaml therefore skips the case-sensitive legacy match but reaches the shape refusal, including beside PLAN.md. RE_HANDOFF at `1493–1494` retains the full path language with a non-greedy phase and optional final cycle; its consumer at `2317–2323` emits notes/handoff-x-c1.md for handoff-x-c1-c2.md and lowercases mixed-case diagnostics, matching baseline construction. No cycle gives no cycle problem. These are source-inspection conclusions, not executed edge-case claims. The baseline diff removes `_I`, its eight uses, the separate cycle matcher and live VERB; explicit flags, updated comments and SHAPE_DIAGNOSTIC_LABEL (`1473`, `1594`) replace them. State/digest declarations retain single-line literal spelling and aligned spacing (`1490`, `1500`), with only trailing flags substituted; the other protected symbols, bootstrap comments and identity fallback remain unchanged.
- **SC-03 — met, automated evidence collected; T-02.** QA PASS at the exact pin (`notes/review-harness-qa-c1.md:3,11–16`) reports eight suites, all exit 0, no FAIL/Traceback, 10.82 s. Specific carrying tests: `_handoff_cycle_suffix_cases` and `_record_cycle_refusal` (`tests/integration/test-check-domain-post.py:909–930`); `_t09_spelling` (`test-check-domain-approval.py:277`); `run_bug1106_shared_pattern_consistency` (`test-check-domain-artifact.py:575–613`). Committed `notes/verify-T02-post.out:49,267–269,567,594,600–602` records their relevant successful assertions; baseline/post receipts record rc=0, wall=11s/10s. No tests or fixtures differ from baseline. Fail-first is not claimed or required by signed SC-03's explicit regression-only wording; multi-cycle/order edges belong to SC-02 inspection.
- **SC-04 — met, inspection; T-01/T-02.** Baseline-to-pin production diff contains only the three guidance paths and check-domain.py; no new implementation file, test, fixture, mechanical lint or cross-file consolidation. History places T-01 `df6ae1cc` before dependent T-02 `ffe320f5`; remaining changes are feature-local plan, approval, handoff and evidence records.

## Decision dispositions at the pin
All eight decisions_affected rows are **keep**, not amend/strike. Canonical PM Mode 2 therefore requires no decision-disposition outcome rows in sc_status. Each retained clause was inspected in `125a04f847db18bcc2ead0b9003a6b2826f9cd55:.harness/harness/docs/DECISIONS.md`:

| Decision | Disposition assessment / pinned authority |
|---|---|
| DEC-174 | keep retained — enforcement carve-out, lines 4450–4461; both tasks declare main-session-direct. |
| DEC-179 | keep retained — existing resolver/no second route matcher, lines 4787–4802; no routing implementation changes. |
| DEC-195 | keep retained — four independent readers, lines 5774–5776; only existing angle questions extended. |
| DEC-234 | keep retained — prologue remains copied, lines 7853–7869; no prologue/import-seam changes. |
| DEC-235 | keep retained — leaf/index/citation contract, lines 7898–7915; leaf content extended without frontmatter/index changes. |
| DEC-159 | keep retained — phase note supersession, lines 3828–3831; canonicalization/refusal preserved. |
| DEC-180 | keep retained — pre prevention/post reporting, lines 4849–4855; diagnostic value bytes unchanged. |
| DEC-182 | keep retained — single-writer amendment, line 5105; legacy guard and shape write denial retained. |

No amend/strike rows, missing landings or remediation owners to route. Findings: none. Open questions: none. Product docs/spec.md, docs/decisions.md and docs/architecture.md remain absent as disclosed; pinned AGENTS.md maps the consulted authorities to SPEC.md §4.2 and DECISIONS.md. This goal-check does not claim ship approval or replace the validator lead's independent gate synthesis.
