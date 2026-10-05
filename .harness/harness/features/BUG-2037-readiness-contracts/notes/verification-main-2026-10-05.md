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
