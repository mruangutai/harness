# Goal-check c1 — FAIL

Landed QA evidence discharges SC-02 and the tested SC-03 policy-selection behavior, but does not cure GC-01's omission gaps, GC-02's inaccurate QA instruction, or the separate reasoned SC-03 CLI bypass. Required integration remains red. This same-pin reconciliation supersedes c0's evidence-availability qualifications; it does not reopen signed D-01–D-03.

Pin: `685e861a667efd13e3c9720dffe9dbb847d4207b`; baseline: `9eb07b4f3cd235c234a10edddbfe5542c1e85fba`. All paths below are feature-local unless repository-relative; product line citations inherit c0's pinned-object inspection. QA = `notes/review-harness-qa-c0.md`; code = `notes/review-harness-code-reviewer-c0.md`; prior = `notes/research-FEAT-2398-qa-test-kind-status-goalcheck-validate-c0.md`.

## Criteria and perspective coverage

T-01 traces to SC-01–05 (`plan.yaml:132`, prior:13); operator has SC-01/02, reader SC-03/04, code maintainer SC-05. None is orphaned; every perspective remains partial because at least one assigned promise is not discharged.

| Criterion | Verdict | Evidence and remaining limit |
|---|---|---|
| SC-01 | partial | QA:34–46 independently reproduces 52/52 at the pin and 39/52 failures against the baseline validator; `_kp_sc01_cases`, `tests/integration/test-validate-digest.py:7067–7087`, exercises the status/refusal/repair behavior. QA:48–50 confirms missing ESCALATE omission and independent matrix_ok controls (GC-01). |
| SC-02 | met | QA:34–46: `_kp_sc02_cases` / `_kp_sc02_disclosure_case`, test file:7090–7117, pass at the pin; baseline mismatched locally_run and with/without Verification gaps disclosure cases fail semantically. Excluded/local/active controls intentionally pass at baseline. No longer partial for unavailable QA evidence. |
| SC-03 | partial | QA:34–46 independently confirms `_kp_sc03_harness_cases` / `_kp_product_cases`, test file:7120–7133,7156–7213, green at the pin and identifies semantic source-selection reds as well as absent-machinery reds. That proves the exercised pin/binding/authority cases, not every CLI path. Code:3–6 separately identifies an empty-kinds/no-started-tasks CLI early return before `_qa_policy`, at validator:1795–1800,3206; this is explicitly REASONED, not executed. Unconditional missing-policy refusal therefore remains unclosed for that concrete path, not because QA was unavailable or integration was red. |
| SC-04 | partial | QA:34–50: `_kp_sc04_cases`, test file:7136–7153, proves early-report latitude, PASS floor, conditional and no-kind controls with discriminating baseline reds where behavior changes. GC-01 leaves the universal omission/matrix-independence clause unproven. |
| SC-05 | partial | Prior:23,30 and code:12 supply pinned instruction/authority inspection. QA:55 explicitly does not replace prose review. The INV-49 instruction defect remains GC-02 despite passing documentation-dependent sweeps. |

SC-03's lack of a matrix-only pair is **nonblocking**: the existing P1 omission refusal depends jointly on pinned unresolved status and pinned integration-floor membership while the competing sources contradict P1 (prior:21; QA:51–54). Reading either table from the wrong source would lose that refusal: this discrimination is an inspection inference, not an executed mutation claim. A pair changing only matrix membership would isolate the dimensions further but is not an additional signed behavior requirement. No extra matrix-only test is required by this goal-check; the distinct CLI bypass is not that coverage suggestion.

## Canonical findings and ownership

- **GC-01 — kind: substance; severity: med; must_fix: T-01, main-session-direct (DEC-174).** Missing ESCALATE omission and schema-valid independent verdict/matrix_ok controls leave the signed SC-01/04 behavior without its required automated proof (prior:29; QA:48–50). This is evidence correctness, not formatting. Add the missing controls for unresolved and active/null kinds, asserting kind-specific refusal and both repairs, with fail-first evidence; do not change the signed policy.
- **GC-02 — kind: substance; severity: low; must_fix: T-01, main-session-direct (DEC-174).** QA skill:38 incorrectly says INV-49 governs which kinds config may declare; pinned `check_state/brief.py:198–206,245–278` instead governs BRIEF verification-gap disclosure (prior:30). This is a false operational instruction, not prose style. Correct that instruction to the disclosure-only contract, preserving no waiver and the two repairs; do not alter INV-49 implementation.
- **Separate owned failures, not duplicate GC findings:** code:6 owns the high/substance SC-03 CLI bypass recommendation; QA:23–27 owns eight fixture-writer findings in T-01's `_kp_harness_repo` / `_kp_product_repos`. Both route to **T-01 main-session-direct**, not a squad. CLI execution is not claimed by these c0 artifacts.

## Decisions and pinned disposition

- **D-01 — partial, revised from c0's met:** the exercised pinned-policy selection is now independently green, but code:6 identifies an unclosed path around D-01's missing-pin refusal. This is conformance grading, not reopening the signed choice.
- **D-02 — partial, unchanged:** validator:1808–1824 and DEC-256:8548–8558 implement/describe the three gates and QA-judged conditionals (prior:35). Landed QA removes the missing-return limitation, but GC-01 still leaves all-verdict/matrix-independent omission proof incomplete. No observed runtime contradiction to those gates is inferred from that proof gap.
- **D-03 — met:** prior:36 cites pinned DEC-187:5339–5344 retaining Kaya's BLOCKED consequence, signed exclusions and no INV-49 waiver.
- **DEC-256 amend — met, unchanged:** `685e861a667efd13e3c9720dffe9dbb847d4207b:.harness/harness/docs/DECISIONS.md:8528–8530,8540–8563` replaces the actual universal default-branch clause with the QA pin exception and preserves non-QA behavior. Row identity: `decisions_affected[0]`; clause “A product's default branch is its contract.”; successor D-01; owner T-01 (prior:37). No disposition repair is needed; keep rows are not graded.

## Independent QA gate and boundaries

QA:14–32 records unit 65/65 exit 0 and integration 95/95 exit 1. The fixture producer regression is baseline-discriminated (eight findings versus zero); the missing-tsc failure is environmental, with a passing post-install diagnostic only. Neither changes the focused 52/52 behavioral evidence. Original red manifests remain red and untouched; no fresh matrix execution is claimed or requested in this reconciliation. Overall goal-check remains FAIL independently of that QA gate.

No source/docs fixes, tests, checks, builds, lint, formatters, or broad diff audit were performed here; only assigned evidence was read and this note written. Installed pre-change hook is not candidate proof. Open questions: none; classifications above are PM's own, and all concrete must-fix work has T-01 main-session-direct ownership.
