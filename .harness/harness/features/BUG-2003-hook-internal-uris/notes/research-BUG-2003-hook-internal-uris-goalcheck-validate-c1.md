# Goalcheck c1 — BUG-2003

**BLUF: PASS — all five signed criteria are met at c2170e265c30e36d6252668775ee41a8ebc93fb6.** Landed QA c1 evidence resolves the prior pending-execution disposition; no execution, source remediation or replan performed.

## Signed perspectives — one line each
- **operator — met:** SC-01 allowed URI write/edit pre/post cases and SC-03 exact forbidden-file payload/refusal, mixed-target and main-session controls passed at the pin; QA c1 records 107 pass / 0 fail and reproduces the mixed-target pre-fix failure (notes/review-harness-qa-c1.md:5–6,10–21).
- **security/harness owner — met:** SC-02's named refused-URI/MV cases passed and failed against the base adapter (QA c1:10–20); SC-04 retains pinned inspection of the shared fileDomain/domainTarget decision in preDomain/postDomain (.omp/extensions/harness-hooks.ts:265–347).
- **code maintainer — met:** SC-05 now has current-pin execution of the strengthened preservation assertions, plus four named discriminating failures against adapter base 7fba7e1d using the pin's tests (QA c1:5–6,10–22). Unchanged controls are passing preservation evidence, not claimed fail-first evidence.

## V1 closure and evidence distinction
V1 (kind: substance; severity: med; reader: harness-pm; task: T-01; SC-03) is **closed as a coverage defect**, independently inspected at the pin: mixed edit :1093–1110, forbidden write :1134–1157, main write/edit :1159–1171. Production preserves ordinary targets' original runner arguments, tool names and tool_input through fileDomain; main-session callbacks still return before domain enforcement. No scope change is needed.

Fail-first proves repaired URI behavior, not unchanged controls: QA c1 independently reproduces four named failures with the pin's test file against base adapter 7fba7e1d (103 pass / 4 fail), including the mixed-target case. Forbidden ordinary writes and main-session controls are preservation evidence and need not fail at the base. The older 106-pass receipt is not substituted for current-pin execution; QA c1 records the literal T-01 verify passing with 107 pass / 0 fail.

## SC outcomes
SC-01 met (QA c1:19; named allowed-URI case); SC-02 met (QA c1:20; refused-URI and MV cases); SC-03 met (QA c1:21; mixed edits, forbidden Write and main-session controls); SC-04 met by retained pinned inspection (.omp/extensions/harness-hooks.ts:265–347); SC-05 met (QA c1:10–22; four named red cases and current-pin green suite). T-01 traces to SC-01–05 (plan.yaml tasks[T-01].traces); every signed perspective is discharged, with no orphan criterion or dropped perspective.

## Prior disposition and resolution
The initial c1 disposition was BLOCKED solely on pending current-pin QA execution: operator/code maintainer partial, SC-03/SC-05 partial, Q1 blocking. V1 was already closed as a coverage defect; no new product finding was asserted. The landed notes/review-harness-qa-c1.md:5–6,10–22 records successful literal python3 tests/unit/test-omp-hooks.py execution at the review pin and discriminating base-adapter reproduction, resolving Q1 and promoting SC-03/SC-05 to met.

## Open questions
None. Q1 closed by QA c1 execution evidence; no tests/builds/linters/formatters were run during reconciliation.
