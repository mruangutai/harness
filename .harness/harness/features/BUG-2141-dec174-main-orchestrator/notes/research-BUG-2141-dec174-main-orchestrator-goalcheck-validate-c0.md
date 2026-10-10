# BUG-2141 — validation outcome assessment

FAIL: the approved integration coverage in SC-04 is incomplete. Documentation and unit outcomes are met, including QA's independent pinned final and fail-first evidence. This is the explicitly requested validation assessment, not patch-lane replanning.

Review pin: `423049fe49c122ee2ec790c53cdc6ce19f1ec791`; actual origin/main merge-base: `0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f`, matching the fail-first receipt. Source/test claims refer to git show/git grep at that pin; executed evidence is collected from notes/review-harness-qa-c0.md. I executed no checks.

## Perspective coverage

- **operator — pass:** SC-01/SC-02 discharge lifecycle ownership, allowed leads, ledger/header pointers and no-handoff preservation. DECISIONS.md:2359–2362 reconciles DEC-120; DEC-174:4509–4520 names every required duty and permission. AGENTS.md:39 and .omp/commands/harness.md:8–15 provide matching bounded exceptions. DECISIONS-INDEX.md:126,175–176 has corresponding updated references/heading locations; QA notes/review-harness-qa-c0.md:29 confirms empty regeneration diff at the pin.
- **code maintainer — partial:** T-01 traces both SC-03 and SC-04. Named unit assertions and historical red evidence support SC-03, but SC-04's required integration controls are absent. Unit controls cannot substitute for an explicitly integration-graded clause.

## SC outcomes

| SC | Status | Exact evidence |
|---|---|---|
| SC-01 | met | DECISIONS.md:2359–2362,4380,4509–4520; DECISIONS-INDEX.md:126,175–176. All duties, allowed plan team/panel/patch and validate/fix routes, engineering prohibition, shared-policy exemption and header authority are present. QA notes/review-harness-qa-c0.md:29 records index regeneration exit 0, empty diff. |
| SC-02 | met | AGENTS.md:39; .omp/commands/harness.md:8–15. Opening no-work/no-lead defaults are qualified by the adjacent DEC-174 exception; ledger and header authority are pointers, not copied procedures. |
| SC-03 | met | tests/unit/test-lead-start-preflight.py:344–386: dec174_main_eng_lead_refused, dec174_nonqualifying_unchanged and dec174_controls execute the real guard and check refusal/diagnostic/registry plus prior origin/plan outcomes. QA notes/review-harness-qa-c0.md:23–31 binds final 50/50 and configured unit success to the pin; :44–56 independently reproduces four historical assertion failures caused by acceptance/claim, not setup errors. |
| SC-04 | partial | tests/integration/test-dispatch-guard.py:679–716 case_15c tests only all-direct and mixed plans. QA notes/review-harness-qa-c0.md:28,31,51–57 records pinned integration success and three discriminating historical failures. dispatch-guard.py:690–715 consumes handoff_policy.exempt_reason before preflight/claim, without changing handoff_policy.py. Required integration assertions for valid main product/validator dispatches, team plans and shared-policy nonqualifying shapes are missing (QA F-1:61–69). |

## Finding bound to T-01

**GC-01 — medium / coverage / must-fix (same gap as QA F-1, whose original major / spec-gap classification is preserved):** SC-04 explicitly requires integration assertions for main→product/validator and team/nonqualifying plans. The complete pinned integration file contains no such BUG-2141 controls: case_15c enumerates only all-direct/mixed. These controls exist only in the unit file (:356–386). Add the missing integration assertions within T-01's already owned test file and have QA supply their final execution evidence; do not weaken the signed criterion or create new scope.

## Origin and fallback assessment

The new refusal uses the unchanged omp_main conjunction (dispatch-guard.py:127–133), matching harness-hooks.ts's top-level Main task route and runtime-authored lineage payload (basePayload:167–174). Child-origin dispatches are not reclassified as main. The new function returns on feature-resolution failure and then still invokes existing BUG-2110 _start_preflight (:715); absent/invalid/empty/non-direct plans do not acquire the new refusal. Missing feature identity still reaches registered-run refusal, not an unconditional claim bypass. This is inspected preservation, not an executed new origin/fallback probe. No additional production defect established.

## Open evidence questions

- None outstanding for evidence collection: QA's terminal artifact resolves the original E-01 final-run question. SC-04 remains partial because execution of the existing green suite cannot prove absent assertions.
- No user-only UAT, approval change, new task or plan rewrite requested.
