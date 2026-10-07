# FEAT-2081 — retrospective PLAN goalcheck

**Partial coverage: the plan preserves the operator's intended safety and performance contract, but omits the CI history prerequisite for its mandatory differential audit test. Return T-03/T-04 for PM amendment and operator re-signature before implementation.**

## Question and perspective grades

does this plan deliver the operator's stated intent?

- **operator — partial:** SC-02/03/04/05/09/10 → T-02/T-04/T-06 (T-03 supplies audit reduction). Fail-closed coverage, every existing gate, concluding shard-only cancellation, and four-shard timing are specified; F1 prevents the passing CI/UAT prerequisite from being reliably reachable.
- **code maintainer — partial:** SC-01/06/07/08 → T-01/T-03, with T-05 documentation and T-06 timing. Weighted deterministic partitioning, unknown-file inclusion, attributed completed-file evidence, unsharded regressions, and unchanged audit findings are specified; F1 leaves SC-06's baseline comparison unavailable on a normal CI checkout.

These are plan-coverage grades, not delivered SC verdicts. All SC-01–SC-10 remain **not_met: no implementation or executed acceptance evidence exists yet**.

## Identity and authority

Read both signed documents using git show at **7ea60c88325d54630bd12465766889707125afa3**. Both record approval on 2026-10-04. Read-only git hash-object of the live feature-tree files matches the pinned blobs byte-for-byte: BRIEF.md **173711982dd0f5989514ef139e0b58754ed9d4f3**; plan.yaml **123d92e2d789fb5bf467fde4842159e886dc4910**. Thus live brief content, task fields, and acceptance content match the reviewed pin; no document drift was observed.

Original intent: [issue #2081](https://github.com/mruangutai/harness/issues/2081), notes/research-brief-intake.md, and notes/research-plan-correction.md. The signed BRIEF Constraints OQ-01/02/03 supersede historical check-state claims and threshold recommendations. Four shards, below 100 seconds in three consecutive runs, lower audit medians on both existing paths, shard-only cancellation, no check-state wiring, and the out-of-scope list remain untouched. DEC-174/183/211 support direct enforcement-path execution, preservation of the integration context, and complete isolated attributed selection respectively.

## Finding F1

**kind: substance; severity: high; tasks: T-03, T-04; affected criteria: SC-06, SC-08, SC-09, SC-10.**

**Scenario:** T-03 requires the new discovered integration test to extract the checker from baseline **8e0b9e900986d4e0e07414ffedb1c09a2a6a7554** using git. The pinned workflow uses bare actions/checkout@v4; T-04 preserves setup but specifies no baseline fetch or fixture supply. A fresh Actions checkout at a later tested commit contains only that commit by default, not the baseline object. The shard assigned test-structure-audit-single-pass.py cannot obtain its mandatory baseline blob; if it fails honestly, required integration cannot pass, and SC-09's restored control and SC-10's consecutive passing runs cannot be collected. If it skips the differential case, it violates SC-06 and exchanges safety for a green result. This is a prospective failure inferred from the signed task plus the documented checkout contract, not an executed failure.

**Pointers:** pinned plan.yaml T-03.intent baseline-extraction paragraph; T-04.intent setup preservation; pinned .github/workflows/tests.yml jobs.integration.steps checkout. [actions/checkout v4 documentation](https://github.com/actions/checkout/blob/v4/README.md) states that only one commit is fetched by default.

**Proposed fix:** amend T-04.intent to ensure the exact baseline object is available before integration execution, through an explicit baseline fetch or sufficient checkout history. Amend T-03.intent to bind differential extraction to that provision and fail explicitly if unavailable, never skip or silently use current code. Include the baseline-provision step in pinned workflow inspection and its setup time in T-06's existing timing ledger. Aggregator discovery of the current tested commit does not itself require historical fetches. Do not add check-state wiring or weaken the differential criterion.

**Signature effect:** remedy changes signed task intent/verification prerequisites in T-03/T-04; **operator re-signature is required**. No BRIEF acceptance change or threshold relaxation is proposed. No plan, BRIEF, approval, or panel record was changed here.

## Evidence completeness and execution boundaries

- T-01 specifies independent red-first witnesses for deterministic completeness, weighting/ties, unknown files, argument handling, empty shards, and completed-versus-selected records; SC-07/08 also require targeted unsharded regressions, not an already-green suite.
- T-02 grounds expected coverage in the supplied commit's independently discovered paths, with two-commit/conflicting-working-tree fixtures. Each non-success conclusion and omission/duplication/unexpected/missing-completion defect has its own rejection and an exact-coverage positive control. Safety does not depend on duration history or selected-file lists alone.
- T-03 specifies exact node-visit reduction, independent violating rule witnesses, and baseline/current findings, ordering, exit/stdout/stderr controls on both settled entry paths. Traversal reduction is not wall-time evidence; audit timing remains a separately controlled three-sample median comparison.
- T-04/SC-04/05 require pinned human inspection of context identity, always condition, triggers, main cancellation policy, and each existing gate individually. Local YAML parsing or synthetic needs results cannot establish actual GitHub scheduling/cancellation behavior, nor workflow deletion protection.
- T-06 correctly keeps SC-09/10 user-executed: throwaway-PR negative cases and restored control, tested SHAs/Actions URLs, three consecutive sub-100-second passing four-shard runs, and lower controlled audit medians on both paths. Its draft/ready/passed boundary prevents preparation checks from manufacturing UAT success. The 170-second baseline is honestly identified as pool time, not full-job time.
- Explicit depends_on ordering is coherent: independent T-01/T-03 → T-02 → T-04 → T-05 → T-06. T-02 owns final reader classification after runner/checker changes; final whole-suite validation follows all changes. F1 is a missing environmental dependency, not a reason to revise those settled task routes.

## Open questions

- **F1 (blocking before implementation):** PM/operator should amend and re-sign the explicit pinned-baseline provisioning contract for T-03/T-04, or record an explicit operator disposition of this high substance finding. No unsettled product-scope question remains.

No builds, tests, linters, formatters, plan checks, or UAT runs were executed. Only document/source reads and read-only git document identity inspection were performed.
