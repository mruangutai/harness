# Patch intake — BUG-2390

Honest runner typing is a bounded two-file patch; T-01 must execute directly in Main under DEC-174. Approval remains pending. No implementation or test execution was performed by PM.

## Authority and scope

- Settled input: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-policy-payload-type-2026-11-22.md, Destination and Settled. Adopt Dict | unknown[] and asserted test narrowing, retaining existing behavior and existing as any reads.
- Source issue: https://github.com/mruangutai/harness/issues/2390. Its historical wontfix option is superseded by settled intake; no adjacent backlog issue is absorbed.
- Product checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2390-policy-payload-type, observed HEAD 9eb07b4f3cd235c234a10edddbfe5542c1e85fba.
- docs/spec.md, docs/decisions.md and docs/architecture.md are absent from this checkout's docs directory. AGENTS.md Project map explicitly identifies .harness/harness/docs/SPEC.md and DECISIONS.md as this product's actual guidance. SPEC section 4.2 defines refusal/unavailable/allow preservation; section 5.3 records the strict TypeScript check and real-host API coverage gap. No standalone architecture document was found or invented.
- Control-plane DECISIONS-INDEX.md consulted; DEC-174 ruling requires direct execution; DEC-225 bounds the patch; DEC-182 governs plan writes; DEC-231 governs perspectives; DEC-254 governs dispositions. These decisions remain intact; no decision-text amendment is needed.
- check-domain --resolve returns NOBODY for .omp/extensions/harness-hooks.ts and backend/dev-ops/qa grants for tests/unit/omp-hooks.test.ts. DEC-174 overrides team execution for both hook and its tests.

## Exact implementation anchors

- .omp/extensions/harness-hooks.ts: PolicyRunner, classifyPolicyRun, runPolicy, applyExpertise. Widen payload signatures; guard arrays before object access; remove the member-ops double cast. reportingRunner already forwards untouched payloads.
- tests/unit/omp-hooks.test.ts: lifecycle fixture runner, gate option, recorded calls, postPaths and real-registry runner/Call type. Widen all affected runner-facing types, route object reads through one asserted-narrowing helper, and remove the stale member-ops comment. Do not move the false object assertion into another cast.

## Traceability and execution evidence

- T-01 traces SC-01 (honest contract and narrowing; pinned inspection), SC-02 (test-first compiler mismatch then green; typecheck), SC-03 (behavior preservation and main baseline count; unit).
- Main must capture a test-only pin and raw compiler mismatch output before production widening, then record completed-pin green evidence. Runtime tests are regression evidence, not a manufactured runtime red.
- Active unit and typecheck kinds cover this surface; no applicable null runner. Existing pi/ctx any typing does not establish live-host API validity.

## Open questions

None about scope or approach. Main's fresh baseline receipt is required to pin the exact regression pass count in T-01 before signature.

## Draft check and signature prerequisite

plan-merge.py apply returned APPLIED; plan-merge.py check resolved T-01's two anchors with zero failures. Its post-write state report says BRIEF is unsigned and Build-entry receipt absent; neither is intake approval authority.

The fresh baseline receipt cannot arrive while Main is blocked on this child: the host reported that Main and the product lead are waiting on this run. The historical Main transcript mentions 186 passes for FEAT-2257 but is not a fresh BUG-2390 baseline and was not adopted. The plan requires MAIN_BASELINE_PASS_COUNT from a pinned fresh Main receipt and refuses execution without it. Before signature, Main must supply that receipt and record the actual count here; this remains unresolved, not a completed measurement.

## Main baseline receipt (main session, 2026-11-22)
In the owner main checkout at `9a818b46071dadd58d2c59b4dd29d398fc4701e7` under Bun 1.3.14, `bun test tests/unit/omp-hooks.test.ts` exits 0 with **214 pass**, 0 fail and 1553 `expect()` calls. The raw output is in `notes/receipts/main-baseline-hooks.txt`. `MAIN_BASELINE_PASS_COUNT=214`. Q-01 is resolved.
