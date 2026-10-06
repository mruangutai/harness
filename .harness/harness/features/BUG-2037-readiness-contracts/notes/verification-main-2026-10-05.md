# Direct enforcement repair verification — 2026-10-05

## Authority and boundary

Operator authorized the separate readiness repair; see authorization-2026-10-05.md. DEC-174 main-session carve-out applies: MAIN authored production changes and regressions and ran all commands directly. Read-only researchers/reviewers did not edit or run gates. No PR, merge to main, issue closure, or #2037 UAT judgment is authorized or claimed.

## Confirmed defects and corrections

- The original QA predicate rejects PASS with empty fail_first even when the actual approved #2037 BRIEF has only UAT/inspection SCs. Known explicit nonautomated modes now exempt only this fail-first requirement. Automated, missing, unknown and undecodable context remain rejected. The actual perspective-tagged BRIEF initially still failed; a tagged-criterion regression caught that grammar divergence. Digest validation now shares SC_LINE_RE with check_state.brief while retaining bounded per-SC verification lines.
- Retryable invalid yields released the live job claim before validation, making same-job correction lose its real digest binding. Regressions now prove the same claim stays live on refusal and releases only after an accepted corrected return, preserving unrelated claims and refused target bytes. No binding is synthesized.
- A lead registered under eng cannot acquire the canonical engineering binding. run-start now reuses digest_destination.LEAD_SQUADS to reject mismatches before writing; old historical labels are not renamed.
- Successful --refused-return closure lacked machine-readable disposition, so INV-15 required an accepted fence that could not exist. Closure now stores return_disposition: refused, restricted by schema to a closed BLOCKED entry. INV-15 exempts only the unique matching run and host. Ordinary completed runs remain checked. Refused history survives ordinary run-end; PASS cannot erase/rewrite it. Reapplying refused closure to an already BLOCKED run preserves original ended_at, so historical annotation cannot inflate measured wall time.

## Failing-before / passing-after

Observed RED then GREEN for: known nonautomated QA, perspective-tagged SCs, undecodable BRIEF, retained retry claim, durable refused marker, schema rejection of a refused PASS, canonical squad registration, INV-15 refusal disposition, refusal-history preservation, historical timestamp preservation, and refusal to rewrite a prior PASS. Tests exercise public subprocess paths where available; the mode predicate uses real temporary BRIEFs, not source-text assertions.

The first broad validator run exposed outdated release expectations and invalid documentor/QA fixtures. Corrected fixtures use each persona's real schema; target-byte and unrelated-claim assertions remain. A broad integration run exposed a nullable record path in INV-15; the helper now explicitly handles unknown records. A later unit run exposed the new mode test's complexity grade; flattened fixture setup and explicit expected outcome restored the required bar. Prior failures remain in raw artifacts, not reclassified as green.

## Exercised verification

- Final unit: python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit — exit 0, 46 files, 25.91 seconds wall; artifact://184. feature-record: 88 tests. OMP hooks: 137 tests, 747 assertions.
- Final integration: python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration — exit 0, 73 files, 72.92 seconds wall; artifact://185. Includes exact-claim and unrelated-byte preservation checks.
- Canonical check-state.py before commit: exit 0; artifact://172. Historical NOTE diagnostics remain visible. This notes-only direct repair has no fabricated governed feature ledger.
- check-skill-weight.py ., check-skill-refs.py ., check-instruction-paths.py — exit 0: 53,885 words across 16 roles, 73 referenced files, 68 instruction files, zero violations.
- All new production predicates _run_end_time, _refused_closed_run and _known_nonautomated_criteria grade 4; new test helpers grade 4/5. Differential grading of the committed range remains required before review.

## Smoke proof, not only tests

MAIN created a disposable registered run and live claim, called the real digest_destination.py CLI, and received its actual binding. The real validate-digest.py --hook rejected an invalid yield with exit 2 and one live claim. Reusing that binding with the corrected object succeeded with exit 0, appended a durable YAML fence, and left zero claims. The throwaway root was removed. This is direct CLI smoke, not live OMP UAT.

MAIN also exercised _qa_errors against the actual approved #2037 BRIEF: after the shared grammar fix, known nonautomated criteria are True and the valid PASS payload returns no errors. No SC conduct or operator judgment follows from that result.

## Independent quality pass

Four concurrent read-only angles: RepairReuse, RepairSimplicity, RepairEfficiency, RepairAltitude. Reuse caught perspective grammar divergence; altitude caught ordinary run-end erasing refusal history. Both were reproduced, fixed by MAIN, and confirmed resolved read-only. Simplification/efficiency reported no findings. Pinned code/security review and resumption of #2037 remain pending.

## Historical migration provenance

The actual preflight orchestrator SuccessfulCougar.jsonl line 130 invoked close-run for preflight-eng with --refused-return --verdict BLOCKED; the following real tool result reported successful CLOSED refused-return at 2026-10-05T04:38:10.205Z. The actual review orchestrator IrrelevantPigeon.jsonl line 154 did the same for simplify-eng; result at 2026-10-05T05:24:54.778Z reported successful CLOSED refused-return and exit=0. Those existing records may receive only the missing disposition through the repaired CLI, retaining timing, tokens, verdict, old squad labels and every prior judgment. Neither prose PASS nor historical ESCALATE is accepted retroactively.

## Pinned review corrections

Independent code/security review of 2880a6148559e442fd0b8a30d51c2147d5e5f101 found a foreign-BRIEF exemption bypass; code review also found an unrelated-section verification-mode bypass and ordinary replay retiming refused history. MAIN reproduced all three before production changes:

- Real validate-digest.py --hook, with a genuine QA claim on an automated feature and an artifact under a sibling UAT-only feature: incorrectly accepted exit 0 and released the claim. It now rejects exit 2 for missing fail_first. Context uses the unique registered feature selected by trusted runtime identity and corroborates the artifact directory; lookup uncertainty cannot waive evidence.
- An SC with no verification mode followed by a separate section containing verify: uat: incorrectly produced no errors. Mode lookup now reuses check_state.brief's actual continuation-block parser; the unrelated-section case is rejected.
- Ordinary run-end replay of an already refused BLOCKED entry: incorrectly changed ended_at from 2026-10-05T10:00:00+00:00 to 2026-10-05T13:23:50+00:00. The regression now passes with the original timestamp preserved; attempted PASS still leaves bytes unchanged.

The three focused regressions pass. Canonical accessor classification follows the renamed registered_feature lookup; lead authorization remains required by registered_destination. New production functions grade 4/5 and the foreign-BRIEF integration case grades 3 against its test bar of 3. Full-suite and fresh pinned review evidence follow below when observed; the initial pin is not approved.

## Latest verification and external blocker

- Updated unit suite: exit 0, 46 files, 35.94 seconds wall; artifact://206. Includes 88 feature-record tests and 137 OMP hook tests.
- Updated integration suite: exit 0, 73 files, 138.03 seconds wall; artifact://215. The previous run, artifact://207, failed only a mocked forwarding test that supplied no registered feature record; that wiring-only test was removed, not repinned to pretend unknown context is authoritative. The real cross-feature hook rejection regression remains.
- Updated static trio: exit 0, 53,895 words across 16 roles, 73 referenced files, 68 instruction files, zero violations.
- Fresh-process smoke of the actual approved #2037 artifact/runtime feature pair resolves the exact original feature directory, recognizes its explicit nonautomated criteria, and returns no QA mode errors. This does not claim a live QA PASS or UAT conduct.
- Canonical checker: exit 1, artifact://217, only INV-25 and INV-29 violations for the unrelated standing detached worktree /private/tmp/feat2081-base. Actual git worktree registration confirms that path. MAIN did not create, remove, move or alter it.

No next commit was made after this checker failure. Corrections remain in the separate repair worktree; 2880a614 remains the initial unapproved pin. Fresh pinned review, original-feature dependency integration, historical disposition annotation and live #2037 UAT await owner-authorized cleanup of the external worktree. No gate was weakened or bypassed.

Operator selected “Leave it for its owner.” The unrelated worktree is preserved; no removal or relocation is authorized. Resumption requires that owner's cleanup and a passing canonical checker.

## Authorized finalization — 2026-10-06

Operator authorized the immediate next step only: reconcile the separate repair with current main, verify, commit, and obtain fresh pinned code/security reviews. Original #2037 integration, historical annotation, live UAT, PR and merge remain outside this step.

- Reconciled immutable main 2d28b79e3e7b5ae5623bd47dd87eab53a4a0c724. Preserved all corrections in exact stash 01bfa65d14ab56f30e30487adf59cd1d3af49a3f; applied that object, not a mutable stash index. The safety copy is retained.
- Adopted main's supported sparse conversion with worktree-state.py --repair while the repair checkout was clean, then replayed the uncommitted merge and restored corrections. The sole resolver conflict retains both exact feature-identity validation and upstream checkout-local corpus semantics. Layout verification reports only dirty (8), never structural 3/4/7.
- Unit suite: exit 0, 52 files, 26.66 seconds wall; artifact://231. Includes 88 feature-record tests and 138 OMP hook tests, 768 assertions.
- Integration suite: exit 0, 80 files, 92.59 seconds wall; artifact://232. Includes 81/81 exact-claim checks, 37/37 undeclared-key checks, and byte-identical unrelated-claim sentinel.
- Static trio: exit 0, 54,123 words across 16 roles; 73 referenced files; 68 instruction files, zero violations.
- Canonical check-state.py: exit 0 before commit, with only the expected dirty-layout advisory. The former external-worktree blocker no longer prevents this checker; MAIN did not remove or relocate that checkout.
- Canonical worktree differential grading: all 17 new/worsened functions meet their bars. Production grades are 4/5; the foreign-BRIEF regression is grade 3 against test bar 3. Pinned CLI differential grading follows the commit.
- Fresh real CLI smoke: eng registration rejects atomically; engineering registers; historical BLOCKED refusal annotation and ordinary replay preserve the original timestamp and bytes. Attempted PASS exits 11 through schema refusal and leaves bytes unchanged. The first smoke expected argument-refusal exit 2 incorrectly; the corrected smoke observed the actual schema exit 11 without changing production behavior. Disposable roots were removed.
- Fresh retry lifecycle smoke: real registry run-start CLI creates one process-owned claim; real validator --hook rejects an incomplete object with exit 2 and retains that exact claim; a corrected object on the same runtime job exits 0 and releases it. Disposable root was removed. This is CLI smoke, not live OMP UAT.
- Four fresh parallel read-only angles completed: RepairReuseFresh, RepairSimpleFresh and RepairEfficientFresh have no findings. RepairAltitudeFresh identifies the pre-existing unbounded _inspection_sc_ids interpretation as a briefing-row: defer migrating that separate citation consumer to the bounded parser because it changes behavior outside this repair. No assertion was weakened and no code apply followed the pass.

Fresh pinned code/security review is still required; the initial pin 2880a614 remains unapproved. This section does not convert any historical refusal or #2037 UAT criterion to PASS.

## Fresh pinned review failures and corrective round — 2026-10-06

The fresh code and security readers both returned FAIL against 81d0ddafd9326c71ca0209ed0f3f8e4e8d17c378, base 2d28b79e3e7b5ae5623bd47dd87eab53a4a0c724. Their receipts are RepairCodeReviewFresh and RepairSecurityReviewFresh. That pin remains unapproved:

- High: malformed, nonmapping or undecodable registered feature records escaped the readiness lookup as FeatureJsonError; a disappeared record could escape as AttributeError. The outer hook guard then returned success without validating the QA object.
- Medium: historical refused annotation/replay could replace positive cycle attribution, feature totals and measured tokens.
- Medium: legacy PASS without timing fields could be rewritten as a refused BLOCKED closure.

MAIN observed each defect through the real CLI and wrote permanent regressions before production edits. The attributed two-file RED run had three failing feature-record cases and four failing hook cases; the same run passed after the narrow repairs. A subsequent legacy BLOCKED/no-timing accounting boundary also failed before its correction and passed in the full suite.

The correction catches the canonical typed read error at the readiness lookup, refuses a nullable registered record, protects terminal verdicts independently of timing availability, and preserves historical refused accounting or atomically refuses conflicting explicit values. Open-run accounting still records the supplied result. The ledger reference documents these boundaries.

The first expanded history predicate failed the production grade bar (cognitive 10, grade 3). Replacing timing-based history detection with the BLOCKED terminal identity removes that extra branch: all 25 new/worsened functions now meet the worktree differential bars, production at least 4 and tests at least 3.

Fresh standalone accounting smoke observed exit 2 with unchanged bytes for conflicting cycles, conflicting measured tokens and legacy PASS; matching replay and legacy BLOCKED annotation exited 0 with preserved accounting. Its first invocation used a non-feature temporary path and was correctly refused with exit 9; the corrected disposable fixture used the supported features-directory layout.

Fresh hook smoke used the real registry run-start CLI with a live supervisor PID. A corrupt registered record returned exit 2 with the process-owned claim and artifact byte-identical. Repairing that record and resubmitting the same runtime/object returned exit 0 and released the claim. Disposable roots were removed. This remains CLI smoke, not live OMP UAT.

Settled-source verification after the terminal-status simplification:

- Full unit suite: exit 0, 52 files, 30.24 seconds wall; artifact://275. Includes 92 feature-record tests and 138 OMP hook tests, 768 assertions.
- Full integration suite: exit 0, 80 files, 91.38 seconds wall; artifact://276. Exact-claim 81/81, undeclared-key 37/37, unrelated-claim sentinel byte-identical.
- Static trio passed: 54,123 words across 16 roles, 73 referenced files, 68 instruction files and zero violations.
- Final real run-end smoke exercised legacy BLOCKED without timing: conflicting cycles exited 2 atomically; matching cycles exited 0 with totals and tokens preserved. A genuine PENDING closure exited 0 and recorded supplied cycle 1 and token 7. The disposable root was removed.
- Four final parallel read-only angles (RepairReuseSettled, RepairSimpleSettled, RepairEfficientSettled, RepairAltitudeSettled) returned no findings. No source/test apply followed this pass.
- Canonical check-state.py exited 0 before the replacement commit, with only the expected seven-path dirty-layout advisory. Fresh review must assess the replacement immutable pin; these results do not approve 81d0ddaf or the original #2037 feature.

## Replacement-pin review findings — 2026-10-06

RepairCodeReview7429 and RepairSecurityReview7429 both returned FAIL for 7429b89aff0f7baf5119bba5f5d4a5a0304d92d5 against the same immutable main base. They independently confirmed the prior corrections, but found additional readiness and durable-evidence gaps. This pin is not approved.

Hypotheses before production edits:

- Checkout ambiguity: readiness calls the registry's intentional owner fallback, so a stale inspection-only owner BRIEF can waive evidence when two feature worktrees match. A real two-worktree hook fixture with automated worktree criteria and an owner artifact should expose acceptance; refusal without changing production would falsify this trace.
- Annotation counting: the existing citation-oriented regex ignores empty verification labels and reads only the first value token. A bounded inspection criterion with a trailing empty verify label should incorrectly waive evidence; existing rejection would falsify the hypothesis.
- Durable lead evidence: canonical record read errors remain untranslated in shared registration, so authorization's second read escapes its expected refusal handler after genuine binding issuance. Corrupting the record after startup should return success without a durable digest; ordinary exit-2 refusal with unchanged claim/artifact would falsify this trace.

## Second corrective round verification — 2026-10-06

- Before production changes, all four new cases failed against 7429b89a: trailing empty verification label, extra-valued mode, ambiguous linked checkouts, and canonical record corruption after genuine lead binding issuance. The attributed validate-digest run exited 1 in 11.46 seconds. The first ambiguity fixture had a missing harness marker and was falsely green; correcting only that disposable fixture reproduced the fourth failure before production edits.
- Shared registration now translates canonical FeatureJsonError into AuthorizationError for all authorization callers. Readiness uses the strict boundary resolver rather than the registry's ambiguity-suppressing owner fallback. A dedicated annotation pattern counts empty labels and validates the entire sole value; the separate citation-oriented consumer is unchanged.
- Focused attributed validate-digest run: exit 0, 11.32 seconds wall. All new cases pass; unrelated live-claim sentinel remained byte-identical.
- Worktree differential grading against immutable main base: 29 gated functions, all pass their production/test bars.
- Full canonical unit suite: exit 0, 52 files, 28.78 seconds wall; artifact://297. Includes 92 feature-record tests and 138 OMP hook tests with 768 assertions.
- Full canonical integration suite: exit 0, 80 files, 88.24 seconds wall; artifact://298. Exact-claim 81/81, undeclared-key 37/37, unrelated-claim sentinel byte-identical.
- Static trio after documenting exact annotation values: pass; 54,138 words across 16 roles, 73 referenced files, 68 instruction files, zero violations.
- Disposable real QA hook smoke: ambiguous checkouts, empty duplicate annotation, and extra-valued mode each exit 2 with the exact claim and artifact unchanged. Removing the disposable linked checkouts and supplying one complete inspection annotation allows the same job to exit 0 and releases its exact claim; artifact remains unchanged.
- Disposable real lead startup/yield smoke: a genuine binding is issued while the canonical record is valid; corrupting that record makes the yield exit 2 without changing claim or artifact. Restoring the record permits the identical object to exit 0, preserves the original artifact prefix, durably writes the complete parsed object, and releases its exact claim. The fixture's valid verdict is FAIL, not PASS: an initial throwaway assertion incorrectly expected PASS; the corrected smoke compares the parsed durable object to the actual fixture, with no production change.
- Disposable smoke roots were removed. This is CLI enforcement evidence, not live OMP UAT. The original #2037 integration and UAT remain outside this authorization.
- Final four parallel read-only quality angles (RepairReuseSecond, RepairSimplifySecond, RepairEfficientSecond, RepairAltitudeSecond) returned no findings. No source/test apply followed this pass.
- Canonical check-state.py exited 0 before pinning, with only the expected five-path dirty-layout advisory. Fresh code/security approval must refer to the replacement immutable pin, not either failed prior pin.
