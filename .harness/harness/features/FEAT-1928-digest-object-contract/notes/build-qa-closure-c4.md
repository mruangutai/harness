# Build-side pre-pin coverage closure — FEAT-1928

This is the main-session DEC-174 build gate, not a replacement for the independent final QA verdict. The independent c3 QA report remains BLOCKED against its superseded pin 828b3605.

## Expected coverage and matrix judgement

Reuse the independently derived Phase 1 expectations in `review-harness-qa-c3.md`, rather than derive expectations from the implementation: T-01 api requires unit; T-02 and T-04 cross_module require unit and integration; T-03 and the signed T-05 are docs. The pre-cutover main control-plane `.harness/harness.json` still requires that floor. File-only loaders do not trigger api's touches_db_or_external predicate. Both touched locally-run kinds require actual recorded runs.

- **unit: satisfied.** Full canonical kind run: 46 files, 8 workers, exit 0, 22.36s. Hooks: 112 pass/0 fail/567 expectations. The earlier run's sole failure was the complexity guard for `_append_authorization_case`; fixture lifetime was separated from assertions, then the entire unit gate passed. No threshold was lowered.
- **integration: satisfied.** Full canonical kind run: 74 files, 8 workers, exit 0, 113.67s. Includes durable record consumers, append authorization, exact claim release, shadows, plan readers, and the unrelated-claim preservation mutation proof.
- **inflight_claim_lifecycle_live: locally_run, recorded.** `live-omp-probe.md` now retains actual credentialed execution: 28/28 PASS, 170.31s, including successful nested lead settlement, real suite execution, unrelated claim byte identity and empty final registry. Earlier failed attempts remain disclosed.
- **digest_object_contract_live: locally_run, recorded.** `live-digest-object-probe-current.md` records actual native null rejection and same-job/session conforming retry: 18/18 PASS. Its uncommitted-source provenance is not final SC-05 evidence; T-05 remains building until the required clean committed refresh and receipt verification.

## Coverage adequacy / prior findings

The c3 independently derived coverage-to-SC mapping and reproduced automated fail-first table remain the baseline: schema dispatch/refusal (SC-01), object-only persona returns (SC-02), closed/ref-free structural schemas and provider suites (SC-03), null/retry (SC-04), retained validator boundaries (SC-06), and append/history/plan-consumer behavior (SC-07). New authorization cases add wrong-parent and ambiguous-run startup refusal, cross-squad/run/feature artifact refusal and symlink-parent protection, alongside authorized append/correction/idempotency behavior. The full suites exercise these paths. No expected automated coverage was dropped.

- c3 F1 is closed by actual lifecycle execution, not a dry run.
- c3 F2 is closed by the literal canonical-reader self-test: ALL PASS, 47 checks; signed T-01 and T-04 commands passed. The census retains 158 rows over 96 Python files, with zero unresolved live rows.
- c3 F3/Q2 are addressed by actual native execution and schema-bound rejection, plus the retained **17/18 FAIL** in `live-digest-object-probe-native-red.md` before the hook changed to permit native handling. The same child then retries successfully; no last-turn fallback was restored.
- The terminal provider suites were executed: 111 pass/0 fail/221 expectations across the four signed suites. Installed-runtime provenance remains distinct from checkout-source corroboration.
- SC-06 is the operator-approved exact 291-case / 14 enumerated-delta contract; no waiver or narrowed census is claimed.

**Build-side matrix and coverage-adequacy gate: PASS for the source quality pass.** Final pin-bound proof, independent QA and goal-check, and ship remain outstanding; this note does not mark any success criterion met.
