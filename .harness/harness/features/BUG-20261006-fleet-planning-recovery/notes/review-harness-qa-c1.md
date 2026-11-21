# QA gate — BUG-20261006-fleet-planning-recovery — run 2026-11-21-1-validator

**VERDICT: PASS** at `6451153169f469f5bd9d5f3f01bf89b82787b720`. Matrix floor met; both kinds green at the exact pin. Fail-first exists for every automated SC, but its **tier is weak** for SC-02/04/06 (see below). Two advisory gaps are named, none blocks.

## Phase 1 (before source): expected coverage from BRIEF + plan only
- SC-01: every feature-bound gh-sync command, build-entry and board reconcile bind to `factory.repo`; conflicting ancestor config cannot mutate Harness; missing/mismatched binding never falls back. Complete fake call log asserted.
- SC-02: ordinary open refuses invalid receipt; `recover-mirror` archives verbatim, creates only the product mirror, resumes with no duplicates, replays as no-op; uncertain create refuses; adopt-receipt role-exact.
- SC-03: unit — FAIL with 0 send-backs keeps 0; 1 evidenced send-back counts 1; idempotent replay; legacy residual kept; negative/bool/conflict rejected; run-end/close-run evidence duty.
- SC-04: INV-7 evidence grading, INV-39/40 preserved, historical refusal vs accepted return, hash-bound target-local evidence, traversal/symlink/external/changed-hash refusal.
- SC-05: `--refused-return` only for BLOCKED + expected contract rejection (exit 1); crash/valid/unreadable/other verdict do not qualify; repeat is stable.
- SC-06: live DEC-237 negatives (prose, fenced text, null, malformed) keep refusing; refusal provenance cannot satisfy live validation or excuse an unexplained missing complete-run digest.

## Matrix floor (harness.json, read)
- T-01 `cross_module` → `unit` + `integration` always. **Both satisfied.** T-01 also changes `feature-schema.json#github` shape; integration is already required, so `touches_config_shape` adds nothing.
- T-02 `docs` → no kind. T-03 `docs` → none. T-04/T-05 `config` → integration only `if touches_config_shape`; they are evidence notes with no schema/config change → not triggered.
- `functional`/`eval` are DEC-187 signed exclusions; `locally_run` probes: `tests/manual/probe-inflight-claim-lifecycle.py` is in T-01.files, but its kind's `detect` (`probe-omp-session-accessor`, `probe-handoff-comprehension`, `probe-issue-types`) does not match it → no recorded-run obligation.
- `matrix_ok: true`.

## Receipts vs. new execution (kept distinct)
- **Audited receipts (not re-executed here):** `notes/pinned-matrix-fad2e25c.md` (unit 57/57, integration 84/84, PASS; re-pinned d69cf444 with source blobs identical); earlier e9ecbd4c and f9a13cac FAILED receipts stand unrewritten; b3f55520 and 03c4d9c9 PASS receipts. Operator rulings for each extra matrix are in `operator-*-matrix-ruling-*.md` and `operator-ship-directive-2026-11-07.md` item 2. None of these receipts names `6451153`; later overlapping merges (#2184, #2205, #2213, #2192, FEAT-2206) post-date them.
- **New execution (mine, current-pin assurance):** pinned checkout at `6451153`, `env -u HARNESS_AGENT_TYPE` (expertise G-07). This is a validate-station run, not the signed plan's once-only matrix; no plan, receipt or ruling was altered. No remote calls (suites use fakes).
  - Unit, run 1, concurrent with integration: **exit 1**, 61 files, 114.51s. Sole failure `test-omp-hooks.py` ("mixed, reordered batch…" `this test timed out after 5000ms`, 6435ms; 136 pass / 1 fail). Under load (`test-feature-record.py` 108.9s vs 51.9s alone).
  - Unit, run 2, alone (rerun captured by this gate, not asserted): **exit 0**, 61/61 files, 54.00s; `test-omp-hooks.py` 137 pass / 0 fail. The 5000ms timeout is a load-sensitive test; the red run 1 is recorded, not erased.
  - Integration, single run (concurrent with unit run 1): **exit 0**, 87/87 files, 356.60s pool. Slowest: `test-gh-sync-abandon.py` 164.95s.
  - `FAIL BUG-1290 5a/5b/5c` lines in unit output are `test-factory-claim-mutation.py`'s deliberate mutation proof (G-09).
  - T-02 verify at pin: `check-decision-anchors.py` exit 0 (28 anchors, 0 failed); `gen-decisions-index.py --stdout | diff -` empty, exit 0.
- Limitation: I did not rerun the SC-08 operator checks (user ground truth, PASSED 2026-11-21 in `notes/uat.md`).

## Fail-first (my own reproduction — fix and tests landed together in squash 4a05030d)
Method: pinned checkout at pre-fix `c4e8bbc8` (= `4a05030d^`), overlay of the 24 test files from `4a05030d`, run named files. Pin `6451153` is green for the same files (above). Tier = natural red from the code, labelled **S** (semantic assertion failure) or **A** (signature-absent: `AttributeError`/`TypeError`/`unrecognized arguments` — proves the feature is missing, not its behaviour). No mutation proofs were run.

| SC | Named test | Pre-fix red (c4e8bbc8 + new tests) | Tier |
|---|---|---|---|
| SC-01 | `tests/integration/test-gh-sync-open.py` fleet cases | `FAIL fleet open uses remote default-branch product config and records target provenance`; `FAIL {open,start-task,status,record-pr,ship,abandon,reject,backlog,recover-terminal} refuses unproven active fleet receipts before any mutation` (9 commands) | S |
| SC-02 | `tests/integration/test-gh-sync-open.py` replacement cases | run aborts `AttributeError: feature_schema has no attribute resolve_evidence_ref` at first replacement case; `tests/unit/test-gh-sync-build-entry.py` `no attribute _replacement_plan`; `test-feature-schema-build-entry.py` `recovery_command_for() got an unexpected keyword argument 'replacement'` | A (plus the S reds above for ordinary-open refusal) |
| SC-03 | `tests/unit/test-feature-record.py` `test_zero_sendback_fail_and_one_sendback_preserve_legacy_residual`, `test_fail_is_not_a_sendback_and_impossible_attribution_is_rejected`, `test_new_zero_attribution_requires_evidence_before_any_write`, `test_replay_refuses_changed_evidence_before_any_write`, `test_run_end_cycle_accounting_is_idempotent_and_preserves_legacy_baseline` | FAIL: `Lists differ: [] != ['FEAT-77-record: cycles_used=0 but 1 FAIL…']` (the FAIL-count floor reproduced); `run-end --digest` `unrecognized arguments` exit 2 vs 0; `test_evidence_cannot_bless_boolean_float_or_absent_attribution` ERROR `resolve_evidence_ref` | S (floor) + A |
| SC-04 | `tests/integration/test-check-state-records.py` (`case_t06_inv37_receipt`, `case_historical_refusal_completion`); `test-feature-record.py` `test_other_run_namespace…`, `test_foreign_arbitrary_digest…`, `test_reader_rejects_cross_run_digest_replay…`, `test_superseded_receipts_remain_hash_bound…`; `test-digest-record.py` `test_direct_json_object_can_back_cycle_evidence…` | `FAIL T-06 INV-37 factory claims do not prove a mirror receipt`; five cross-run/hash FAILs; `DigestRecordError: no fenced YAML block loads to a mapping`; `case_historical_refusal_completion` → `AttributeError resolve_evidence_ref` | S for INV-37/replay/direct-JSON, **A for the historical-refusal reader case** |
| SC-05 | `tests/unit/test-feature-record.py` `test_refused_return_cannot_replace_a_missing_or_unreadable_digest` (3 subTests), `test_refusal_provenance_is_only_legal_for_blocked_runs`, `test_refused_return_takes_only_a_blocked_verdict`, `test_refused_return_is_refused_when_the_digest_validates`, `test_validator_crash_or_noncontract_failure_cannot_become_refusal_evidence` | FAIL / ERROR; the crash/valid/verdict cases ERROR at `resolve_evidence_ref` in setup | S (missing/unreadable, BLOCKED-only schema) + A (verdict, valid, crash) |
| SC-06 | `tests/integration/test-validate-digest.py` live negatives; reader side `case_historical_refusal_completion` | `test-validate-digest.py` with new tests **passes pre-fix (`ALL PASSED`)** — retained controls cannot redden. `case_historical_refusal_completion` pre-fix: `AttributeError resolve_evidence_ref` | **A only; no semantic red** |

Pre-fix receipts live in session artifacts only (not copied under the feature: my write grant is this note alone); every command is `env -u HARNESS_AGENT_TYPE python3 <file>` in a pre-fix checkout with the 4a05030d tests overlaid, so any peer can reproduce. `test_digest_count_is_an_integer_not_an_equal_float` passes pre-fix — a boundary test with no pre-change defect; its discrimination is unshown, not disproven.

## Findings (advisory; none changes the verdict)
1. **SC-06 evidence is thin.** `validate-digest.py` has no reference to refusal/provenance (grep), and `test-validate-digest.py` has none either. "Historical refusal provenance cannot satisfy live validation" holds by absence of any code path and is not asserted by a test; no mutant that makes the live path accept it is covered. Reader-side coverage ("cannot excuse an unexplained missing complete-run digest") is the pre-state/changed-hash assertions inside `case_historical_refusal_completion`, whose only pre-fix red is signature-absent.
2. **Controls removed/narrowed in 4a05030d** (T-01 owner, plus OMP-compat schema change): `test-digest-record.py::test_does_not_import_live_schema` deleted (it pinned historical reader independence from the live schema — the converse of finding 1); `test-validate-digest.py` dropped `"missing 'task_verify'"`/`"drifted"`/`"undeclared digest key"` message conjuncts (`_t04_canonical_failures` now `if not errors`), deleted two hint cases and `run_joint_hint_case`. Rejection of the malformed returns is still asserted; the wording and joint-hint followability are no longer pinned. The 2026-10-18 note justifies the validator edits as incidental wording locks; the `test_does_not_import_live_schema` deletion has no stated reason I found.
3. **Test timing:** `test-omp-hooks.py` has a 5000ms test that failed under double-suite load once (run 1) and passed alone; `test-feature-record.py` is 108.9s loaded / ~52s alone, far above T-01's 60s focused-chain ceiling — plan records that ceiling as met on the 5-command chain in 58.11s at b3f55520. I did not time the chain on `6451153`.
4. Code-grade (35 named grade-2) and security-reviewer matters are out of my lane.

## Principles applied
- Build the Lever (read `references/build-the-lever.md`) is NOT claimed as applied: its test requires a committed script, and this gate's write grant is this note alone. The reproduction is a documented recipe only (pinned pre-fix checkout, overlay of `git diff --name-only --diff-filter=AM HEAD 4a05030d -- tests/unit tests/integration`, per-file run), reusing `pinned-checkout.py`.

## Cleanup
Both pins (`harness-qa`, `harness-qa-prefix`) removed with `pinned-checkout.py remove`.
