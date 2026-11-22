# Goal-check c1 — FEAT-2337

**FAIL: two bounded T-03 landing defects; no new approval or UAT required.** Async/receipt implementations and DEC-100's amendment are present. Final QA and code-reviewer notes had not been produced when read; the automated outcomes below are therefore partial evidence assessments, not invented test failures. I ran no suites, benchmarks, builds, linters or candidate gates.

## Subject and authority

All source citations below are **git show 6143625f5262f246d51d642662899a44a8d545d9:<path>**. Live feature.json review_sha agrees. Working HEAD had advanced to 04db582f for ledger work; it was not the grading subject. Independently inspected `git diff 0d7326e4 6143625f -- . ':!.harness/harness/features'`: 24 files, matching T-01/T-02/T-03's 23 files plus expressly approved tests/integration/test-merge-gate.py. Merge 27f8d569 has 0d7326e4 as its upstream parent. The obsolete d04c765a pre-edit baseline is NOT this assessment's base.

AGENTS.md Project map supplies this product's .harness/harness/docs/SPEC.md and DECISIONS.md; conventional docs/spec.md, docs/decisions.md and architecture guidance are absent. Requirements include approved BRIEF/plan, research-*-plan-apply.md and all four answers-2026-11-22-* rulings: delegated signature, grading-base movement, fix-run receipts/feature-local dirt exemption, and merge-gate narrow timeouts. The extra merge test is approved scope, not unauthorized growth.

## Concrete findings

- **GC-01 — kind: substance; task: T-03; SC-08; must_fix.** tests/unit/test-code-grade.py:313-316 still pins FEAT2337_BASE to d04c765a; :370 feeds it to the cumulative grader. The settled grading-base ruling explicitly moves the base on another main merge (answers-2026-11-22-grading-base.md:18-19). That happened at 27f8d569. Comparing d04c765a..0d7326e4 imports four functions in tests/integration/test-plan-merge.py and four in tests/unit/test-plan-merge-union-head.py, neither file changed by this feature. Thus the promised feature-only gate also grades unrelated upstream work. Set its constant/comment to the settled current immutable feature base 0d7326e40137dfce63f5b7b33af95ee126f90971; QA owns the new-pin grading receipt. This is a scoped boundary defect even if all imported functions happen to grade green.
- **GC-02 — kind: substance; task: T-03; SC-09 / D-02; must_fix.** DECISIONS.md:8428-8433 states a fix receipt requires a clean working tree, without the approved feature-directory exception. SPEC.md:1604-1606, fix.yaml:90, harness-qa.md:60 and harness-validator-lead.md:101 similarly say clean. The binding follow-up ruling (answers-2026-11-22-fix-run-receipts.md:44-51) permits tracked/untracked dirt under the trusted feature's own directory; validate-digest.py:2576-2589 implements that exception, and test-validate-digest.py:2372-2373 asserts acceptance. State this settled exception in the current decision and make the standing shorthand unambiguous; do not tighten behavior. This routes to the existing decision/guidance owner, not a scope-change approval.

## Perspectives — complete coverage, delivery not yet fully discharged

| Perspective | Outcome | SC / pinned deliverable and evidence |
|---|---|---|
| operator | partial | SC-01/02/03/07: async spawn/timeout/classification at harness-hooks.ts:451-524; ordered all-settled five-gate composition :552-580; awaited lifecycle migration :1458-2211. Named heartbeat/delay/settlement/composition tests are present; t01-red-green.md and merge-gate-narrow-red-green.md discriminate old behavior. Final QA pin-bound outcomes pending. |
| orchestrator | partial | SC-04/06: benchmark protocol and exit wiring at test-omp-native-gate-runtime.py:84-180,365-366,563-627; receipt trigger and validation at validate-digest.py:2362-2668. t02-red-green.md and t02-fixrun-red-green.md capture refusal/acceptance transitions. The builder benchmark explicitly is NOT acceptance; dedicated idle-host review-pin benchmark pending QA. |
| code maintainer | partial | SC-05/09: one shared CI/receipt validator at check-integration-shards.py:113-260; old defaults retained. DEC-100 landed in place and DEC-255/index/current guidance exist. GC-02 prevents complete current-truth discharge. |
| reader | partial | SC-08/10: explicit-only cumulative grader and mutant exist, but GC-01 violates the settled grading boundary. Clean-cutover source inspection succeeds. Final QA's runtime identity and review-pin receipts were not yet available. |

## SC outcomes and traceability

Paths without directory prefixes in this table are under tests/unit/ or tests/integration/ as named. Historical build notes are evidence of red-first conduct, not a substitute for final QA's pin-bound DIGEST.

| SC | Verdict | Tasks | Evidence / remaining proof |
|---|---|---|---|
| SC-01 | partial | T-01 | unit/omp-hooks.test.ts:4292-4375,4500-4540: named budget, heartbeat, delayed authorization/yield/injection, readiness, rollback and lifecycle release. t01-red-green.md:9-45 records 24 red cases. Final QA unit result pending. |
| SC-02 | partial | T-01 | integration/test-omp-native-gate-runtime.py:432-486,596-609: real copied-process timeout and abnormal-exit cases, guarded/unrelated merge outcomes; default failure matrix :650-796. t01-red-green.md:47-74 and merge-gate-narrow-red-green.md:64-83 provide red-first receipts. Final QA integration result pending. |
| SC-03 | partial | T-01 | unit/omp-hooks.test.ts:4423-4490: reversed completion, every unavailable notice, rejection isolation, unrelated commands and real five-process barrier. t01-red-green.md:25-45 shows discriminating failures. Final QA unit result pending. |
| SC-04 | partial | T-01 | integration/test-omp-native-gate-runtime.py:128-140,365-366,563-627 supplies 3 warmups/15 alternating pairs and nonzero ratio verdict. t01-red-green.md:66-72 proves failing-ratio exit wiring; :99 expressly disclaims acceptance. Idle-host benchmark samples, medians, ratio and identities at this pin must come from final QA. |
| SC-05 | partial | T-02,T-03 | unit/test-integration-shard-validation.py:176-249 and integration/test-integration-shard-aggregation.py:232-280 cover unit discovery, exact coverage, CLI integration defaults/four shards and tested-tree binding. t02-red-green.md:47-105 captures red/green. Final QA unit result pending. |
| SC-06 | partial | T-02,T-03 | integration/test-validate-digest.py:1881-1943,2106-2143,2311-2437 uses production-runner receipts and exact-pin/descendant/foreign/revert/fix-run refusal tables; test-check-domain-grant.py:1228-1340 covers narrow authored/template grants and wrong-role/feature/checkout refusals. t02-red-green.md:62-95, t02-fixrun-red-green.md:62-95 and t03-red-green.md:89-125 carry red-first evidence. Final QA integration result pending. |
| SC-07 | partial | T-02,T-03 | validate-digest.py:2429-2504 binds live lineage, registered run/pin and safe receipt path; test-validate-digest.py:2545-2597 and run_bug2253_cases at :7115 retain wrong/ambiguous checkout and all-file diagnostic cases. t02-red-green.md:112-169 records migrations and claim-release invariants. Final QA integration result pending. |
| SC-08 | partial | T-03 | GC-01. Explicit --feat2337 mode and grade-2 control exist at unit/test-code-grade.py:310-448; no added exemptions. t03-red-green.md:118-124 captures an actual failing grade-2 command. Its simulated/pre-merge green result is not final review-pin proof. |
| SC-09 | partial | T-03 | DECISIONS.md:1372-1421,8394-8462; DECISIONS-INDEX.md:109,238; SPEC.md:766-775,1589-1621; QA/validator roles, verification skill, validate/fix teams and README:179-181 carry the cutover/repair/commit/CI guidance. GC-02 is the specific current-truth gap. Reviewer corroboration pending; these are my direct pinned-content observations. |
| SC-10 | partial | T-01,T-02,T-03 | Independent pinned inspection finds the cutover present: runPolicy is async at harness-hooks.ts:517; remaining spawnSync at :1021 is unrelated git. validate-digest.py replaces the old seam/rerun/parser block with receipt checking :2371-2668. Five original gate processes and bootstrap/applicability authorities remain; their source files and .github/workflows/tests.yml are unchanged. Build notes distinguish candidate from installed enforcement; no installed receipt-operation or TypeScript-typecheck claim. Final reviewer corroboration and QA runtime-identity record are pending, not missing shipped behavior. |

## Decisions — every affected row accounted for

**Row 0, DEC-100 amend → D-01: met.** At 6143625f5262f246d51d642662899a44a8d545d9, .harness/harness/docs/DECISIONS.md:1372-1421 replaces the nominated clause in place: async policy, one killed 30-second process-group budget, broad unavailable/narrow matching refusal/helper conventions, all-five concurrency and stable composition. :1402-1409 includes the approved merge-gate correction. DECISIONS-INDEX.md:109 points to its actual :1316 heading with a 28-word ruling tail. T-03 owns this landing; D-01's implementation is at harness-hooks.ts:451-580.

**D-02 / new DEC-255: partial (GC-02, T-03).** DECISIONS.md:8394-8462 lands the receipt authority, production command, shared schema authorities, validate/fix distinction, repair, force-add, explicit forgery trust boundary and #2356 residual. Index :238 points at :8394 with a 29-word tail. No number reuse or amendment appendix. Its clean-tree wording still needs the settled exception.

**Rows 1-21 are keep, preserved; not amend/strike landing grades under DEC-254.** Every declared clause remains present in its own pinned decision section. Individual anchors in .harness/harness/docs/DECISIONS.md:

| Row | DEC | Preserved clause line | Row | DEC | Preserved clause line | Row | DEC | Preserved clause line |
|---|---|---:|---|---|---:|---|---|---:|
| 1 | DEC-174 | 4483 | 2 | DEC-205 | 6642 | 3 | DEC-234 | 7885 |
| 4 | DEC-254 | 8323 | 5 | DEC-120 | 2337 | 6 | DEC-179 | 4813 |
| 7 | DEC-182 | 5049 | 8 | DEC-187 | 5291 | 9 | DEC-202 | 6238 |
| 10 | DEC-232 | 7778 | 11 | DEC-127 | 2706 | 12 | DEC-188 | 5381 |
| 13 | DEC-204 | 6559 | 14 | DEC-208 | 6792 | 15 | DEC-211 | 6860 |
| 16 | DEC-213 | 6958 | 17 | DEC-218 | 7134 | 18 | DEC-233 | 7803 |
| 19 | DEC-237 | 7996 | 20 | DEC-238 | 8063 | 21 | DEC-250 | 8114 |

DEC-174/205/234 sections are unchanged from 0d7326e4; implementation remained main-session-direct, no copied prologue was replaced, and standing CI is retained. No strike rows exist. Keep preservation does not assert that every pre-existing implementation of those decisions is defect-free.

## Evidence timing and close boundary

At this assessment's single read, notes/review-harness-qa-c1.md and notes/review-harness-code-reviewer-c1.md did not exist. Do not reinterpret that concurrent delivery state as missing shipped tests or an execution failure. Lead should consume their final outputs without commissioning duplicate executions; this note did not wait or poll. GC-01/02 are independently pinned source findings, not dependent on those artifacts being absent.

This feature is still validated by pre-existing installed/control-plane #919 rerun enforcement. Candidate receipt acceptance is exercised only by candidate tests; launcher path/version/hash and source pin must remain separate in QA evidence. Main must still force-add candidate manifests with the committed closed validate record (delegated signature condition). That future close duty cannot honestly be marked completed now, but is not a new automated gate or an already-failed SC. Receipt acceptance/CI do not detect an omitted force-add. Known #2356/#2359/#2344/#2257 and the two named canonical-reader baseline failures are not new regressions here. No UAT criterion exists. No scope/approval question remains; remediate the two T-03 defects and assess final QA evidence.

## Final assessment addendum — 2026-11-22

**FAIL: GC-02 remains a medium-severity substance finding owned by T-03. Final evidence now discharges the automated SCs; the independent integration gate remains red and requires owner/main disposition.** This addendum supersedes the earlier pending-evidence outcomes and GC-01's asserted mandatory base movement; preceding prose is retained as the historical assessment, not the current disposition. No verification was rerun.

### Concrete finding dispositions

- **GC-01: retracted as a must-fix; severity low, kind substance, advisory only.** Direct commit metadata and ancestry show T-03 commit 352ceebe (12:52:25 -0800) preceded main merge 27f8d569 (13:06:39 -0800). The ruling's last bullet expressly applies to another merge *before T-03's tip is committed*. That condition was not met. My earlier claim that the ruling required 0d7326e4 was too broad and is withdrawn. Its feature-only rationale remains relevant: d04c765a also includes unrelated upstream functions in the eventual cumulative population, so its passing result must not be described as exclusively feature-owned grading. But the approved fixed base is d04c765a, every feature test is included, all 156 graded functions pass, and the grade-2 mutant discriminates. This is neither an unmet SC-08 nor authority to silently change the ruling. No repair or approval is requested.
- **GC-02: survives; severity medium, kind substance, must_fix, T-03; SC-09 and D-02/DEC-255 partial.** At review pin 6143625f5262f246d51d642662899a44a8d545d9, .harness/harness/docs/DECISIONS.md:8428-8433 still requires an unqualified clean working tree. The approved answers-2026-11-22-fix-run-receipts.md:44-51 permits dirt confined to the trusted feature directory, implemented at validate-digest.py:2576-2589 and exercised at test-validate-digest.py:2372-2373. SPEC.md:1604-1606 and the previously inventoried standing guidance carry the same ambiguity. This is a current documentation/behavior mismatch, not a request to tighten implementation or reopen scope. The reviewer's broad SC-09 approval does not refute this specific pinned clause.
- **GC-03: severity high, kind tests, owner-manifest environment gate obstacle; T-03/SC-06 interplay, not a candidate product defect.** Final QA's production integration run exits 1: test-check-plan-routes.py reports owner-manifest DEVIATION in cases 04/05/15/17/19d/19d2. The same pinned file passes in an independent clone. The candidate QA grant and owner manifest differ. The integration receipt truthfully records runner_exit 1, so matrix_ok is false and validation cannot pass. This requires main/operator disposition, not a source/test workaround or speculative rerun. It does not turn passing receipt/grant behavior tests into an unmet SC-06.

### Final perspective and SC outcomes

Evidence references below are notes/review-harness-qa-c1.md (QA) and notes/review-harness-code-reviewer-c1.md (review), both at this feature's canonical notes directory. Source anchors remain pinned to 6143625f5262f246d51d642662899a44a8d545d9.

| Perspective | Final outcome | Discharging SCs |
|---|---|---|
| operator | met | SC-01/02/03/07, named passing unit/integration assertions and retained red-first receipts |
| orchestrator | met | SC-04/06, dedicated benchmark and real-runner receipt/grant tests |
| code maintainer | partial | SC-05 met; SC-09 partial due to GC-02 |
| reader | met | SC-08 grading/mutant and SC-10 pinned cutover plus distinct installed-runtime identity |

| SC | Final verdict | Method | Final evidence |
|---|---|---|---|
| SC-01 | met | automated | QA:14,18,29; 214 Bun tests green; budget/heartbeat/delayed-helper assertions; t01-red-green.md natural RED |
| SC-02 | met | automated | QA:15,18,30; test-omp-native-gate-runtime.py and test-merge-gate.py green, focused 37/37; timeout/abnormal process assertions and retained natural RED |
| SC-03 | met | automated | QA:14,18,31; omp-hooks.test.ts all-five barrier/order/rejection tests green and retained natural RED |
| SC-04 | met | automated | QA:19-22,32; dedicated run after suites, no other suite reported running; 3 warmups/15 alternating pairs, medians 177.5/53.7 ms, ratio 0.302; all samples and identities recorded; failing-ratio nonzero wiring retained as expressly required |
| SC-05 | met | automated | QA:14,18,33; test-integration-shard-validation.py unit_kind_cases and aggregation kind_seam_cases green, prior natural RED |
| SC-06 | met | automated | QA:15,18,34; test-validate-digest.py receipt cases 78/78 and test-check-domain-grant.py 21/21, zero-rerun witness, fix-run and refusal cases with natural RED |
| SC-07 | met | automated | QA:15,35; test-validate-digest.py run_bug919_qa_matrix_cases/run_bug2253_cases and migrated refusal diagnostics green, retained natural RED |
| SC-08 | met | automated | QA:17,36; explicit committed-pin mode grades all 156 functions >=3 against approved d04c765a; retained grade-2 mutant red. GC-01 temporal correction above applies |
| SC-09 | partial | inspection | Review:11 corroborates cutover/index/boundaries; pinned DECISIONS.md:8431 contradicts settled feature-directory exception (GC-02, T-03) |
| SC-10 | met | inspection | Review:12,16-18; pinned harness-hooks.ts:451-563 and validate-digest.py:2371-2670; QA:23 records installed launcher/version/hash separately and unchanged #919 host enforcement |

Host load 3.93/3.70 on 12 CPUs and sibling readers are disclosed, not concealed. SC-04 requires no other suite, not zero host load: QA's dedicated after-suites execution satisfies that clause on its account. No benchmark rerun is requested. Fail-first evidence is retained builder capture except QA's stated first-hand controls; no new independent historical execution is implied.

### Final decision dispositions and close boundary

- **DEC-100 amend, affected row 0: met**, inspection at 6143625f5262f246d51d642662899a44a8d545d9:.harness/harness/docs/DECISIONS.md:1372-1421; T-03. The intended clause is replaced in place. Keep rows are not disposition-graded; no strike rows exist.
- **D-02 / DEC-255: partial**, inspection at 6143625f5262f246d51d642662899a44a8d545d9:.harness/harness/docs/DECISIONS.md:8428-8433; T-03 must land the approved feature-directory exception (GC-02). This remains an explicit sc_status outcome even though DEC-255 is a new decision rather than an amend/strike row.
- QA's final production receipts are runs/r-20261122-4-validate-validator/qa/manifest-unit.json and manifest-integration.json. Their ignored status requires main's later force-add with the closed run record, not a finding that this future duty has failed. No installed candidate receipt acceptance is claimed.
- No new goal, approval or UAT is proposed. No open product question remains. GC-02 and the separate GC-03 gate obstacle prevent unconditional validation success; pending final QA/reviewer delivery is no longer a finding or missing-evidence claim.

### Same-run classification correction

**GC-03: severity high; kind substance.** This supersedes the invalid kind token tests above; tests describes its evidence surface, not its finding classification. The actual production integration gate is red because the linked checkout's candidate QA grant differs from the owner manifest. It remains an environmental/non-product gate obstacle requiring main/operator disposition, not a candidate behavior defect. No evidence, severity, scope, SC outcome or remediation ownership changes.
