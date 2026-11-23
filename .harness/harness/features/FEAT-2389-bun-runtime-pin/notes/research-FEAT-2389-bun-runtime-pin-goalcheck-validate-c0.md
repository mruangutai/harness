# FEAT-2389-bun-runtime-pin — validate goalcheck c0
Run: r-20261122-2-validate-validator

SC-01–03 deliver the runtime pin and maintenance policy; SC-04 is pending-ci, NOT met. This completed read-only assessment is not merge clearance.

Authority: BRIEF.md and plan.yaml at fea15955785ac4d9202cccb43302c8ffefdc8152; base 51c2efebdd8ada060295c5b4adda68d93aabb27a. Inspection evidence: notes/review-harness-code-reviewer-c0.md:9-13, independently cross-checked against git show/git diff at the supplied pin. No builds, tests, linters or source edits performed.

## Perspectives
- **operator — partial / pending-ci:** T-01 traces SC-01 and SC-04; the pinned value and recorded local verification are established, but complete green CI bound to the accepted review SHA is not. Authority: brief-perspective:BRIEF.md#operator.
- **code maintainer — met, with a low form note:** T-01 traces SC-02 and SC-03; the sole manifest pin, workflow source comment and manual production-host upgrade policy are discoverable without conflating dependency updates. Authority: brief-perspective:BRIEF.md#code maintainer.

## Success criteria
| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | inspection | Pinned package.json:4 is bun@1.3.14. Pinned notes/receipts/T-01-red.txt:1-4 records baseline null/equality exit 1; T-01-verify.txt:1-5 records both equality checks and successful typecheck, exit 0. Reviewer :9 accepts these as pre-commit execution evidence, not a claim of execution at review_sha. |
| SC-02 | met | inspection | Pinned .github/workflows/tests.yml:66 adds the single source comment; :68 and :385 remain input-free. Base-to-pin workflow diff contains only that comment; reviewer :10. |
| SC-03 | met | inspection | Pinned README.md:240-242 states the separate manifest runtime pin and production-host/manual-only/never-Dependabot policy; existing dependency-update guidance remains. Reviewer :11 confirms the policy; sentence-count departure is recorded separately below. |
| SC-04 | pending-ci | inspection | PR https://github.com/mruangutai/harness/pull/2433; run https://github.com/mruangutai/harness/actions/runs/45112028584 was in_progress, with shard 1 unfinished and no overall conclusion. Run head is 37715236af198a7d5fe5066ba7c26d45b9b894ac, not review_sha; exact-pin run/check queries returned zero. |

## Findings and external hold
- **F-01 — kind: form; severity: low; owner: T-01; non-gating.** README.md:240-242 adds two sentences rather than the one-sentence BRIEF constraint. Required policy is present; consolidating the explanation would correct the literal form departure. Reviewer :11 concurs. This is not a runtime defect or a reason to rerun gates.
- **H-01 — pending external execution; owner: T-01 evidence / Main before merge; not a source finding.** Main must reconcile CI's newer head with the accepted review pin, then confirm every job green and resolved Bun logs across both setup sites, including matrix instances. Completed checks/job 137486319514 and shard-2/job 137486319698 logs already report obtaining 1.3.14 from package.json and downloading bun-v1.3.14; checks Typecheck succeeded. These observations concern the newer CI head only and do not discharge SC-04. No source remediation is requested for pending CI.

## Decision dispositions
Pinned plan.yaml declares decisions: [] and decisions_affected: []. There are zero amend/strike rows to grade, no DEC outcome rows to manufacture, and no promised decision-file edit. The three-file implementation introduces no observed contradiction requiring an undeclared disposition.

## Open questions
- Before merge, does completed PR CI evidence establish every SC-04 clause at the accepted reviewed SHA? Main owns this external evidence closure; QA alone owns the final required local gate.
