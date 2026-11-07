# PLAN scope recovery — FEAT-2081

**BLOCKED — the native contract cannot represent this authorized signed retrospective PLAN review. PM F1 is endorsed and materially qualifies c1's clean assessment.** Target remains the signed plan at `7ea60c88325d54630bd12465766889707125afa3`; c1 is preserved, not rewritten. This is the single on_fail recovery, not a fresh review or implementation assessment.

## F1 cross-review

**PM-origin F1: kind substance; severity high (PM's rating, endorsed); tasks T-03/T-04; criteria SC-06/SC-08, downstream SC-09/SC-10.** `plan.yaml:107,110` requires extraction of checker baseline `8e0b9e900986d4e0e07414ffedb1c09a2a6a7554` from git in the new discovered integration regression. T-04 preserves existing checkout setup (`plan.yaml:127`) but supplies no historical-object prerequisite. Current checkout is bare `actions/checkout@v4` (`.github/workflows/tests.yml:52`); its [v4 documentation](https://raw.githubusercontent.com/actions/checkout/v4/README.md) specifies one fetched commit by default.

**Concrete scenario [INFERENCE]:** on a fresh runner at a later tested commit, the baseline object is absent. The shard executing `test-structure-audit-single-pass.py` cannot extract its required comparison subject. Honest failure prevents required integration success and passing UAT controls; skipping or substituting current code violates the SC-06 differential contract. Local full-history fixtures do not provision the actual Actions runner. This is a missing environmental dependency, not proof that the indexing design or task graph is wrong. No implementation or CI failure was executed or observed.

**Fix:** PM should amend T-04 to provision the exact baseline before shard execution (explicit fetch or sufficient history), bind T-03 extraction to that provision with explicit failure when unavailable, and include its setup cost in T-06's existing timing ledger. Do not skip differential evidence or weaken acceptance. **Operator re-signature is required** for changed signed T-03/T-04 intent/verification prerequisites; no BRIEF criterion or threshold change is requested. PM's original high finding remains theirs; this endorsement is not a second independent defect.

SC-04/SC-05 inspection remains planned at `plan.yaml:126,128–129`, not a claim that the unimplemented workflow already satisfies those criteria. Read-only `git diff 7ea60c88325d54630bd12465766889707125afa3 --` for BRIEF.md, plan.yaml and tests.yml returned no differences, grounding these citations in the existing pin.

## Exact return-contract blocker

`validate-digest.py:978–988` accepts `plan:<path>` only with `approval.status: pending`; this plan records `approved` (`plan.yaml:3–6`). `_code_grade_errors` invokes the binding without a verdict exemption (`validate-digest.py:1626–1637`), so native BLOCKED also cannot escape it. The expected refusal is: `plan review mode is only valid while approval.status is pending; '<absolute feature plan path>' records 'approved'.` The supplied six earlier refusals are ground truth; none were rerun. The pending-only protocol is also explicit in `references/plan-phase-review.md`.

The JSON schema permits BLOCKED, so one honest native BLOCKED object will be attempted with `reviewed: plan:<actual absolute path>` and `code_grade: n_a`. If the semantic guard rejects it, this note is the durable impossibility evidence; do not loop, alter approval, fabricate a different pin, or label this a code diff. A supported signed-retrospective reader contract or explicit operator disposition is required from the owner.

**Open questions:** contract owner must resolve the pending-only guard for authorized signed retrospective reviews; PM/operator must amend and re-sign F1 or explicitly dispose of it. Only this recovery note was written. No approval, source, c1, plan, or peer record was edited; no builds, tests, linters, formatters, validator execution, or UAT ran.
