# FEAT-2397 code review c1 — PASS

Both c0 code findings close; no new substantive defect found. Canonical grade **pass**; independently measured SC-12 changed-body bars all pass. This is not a green-CI or ship-readiness claim.

Reviewed `522c94b2b79e5e2021cb670910772428c17914b0..9c38040397bb115583e71b13f1a7ca4bf2f10c2e`. Merge-base independently confirmed; previous pin `53a89eb70251d1529dbffd8e50959c4590a032f7`, remediation `b9a8c3adb8c387d24d149e7054ade3fc4654f2b5`. Requirements/source/receipts read with git show, not post-pin HEAD. Full commit list inspected; no human-tagged commits or modified tracked source; only untracked validation records.

## Stage 1 — compliance passes

- SC-04: `.github/workflows/tests.yml:119`, `tests/integration/test-harness-yaml.py:30`, `notes/c1-evidence/t02-transient-522c94b2.txt:1` and `notes/c1-evidence/t02-transient-f5c89121.txt:1`: nine exports, both guidance lines and five assignments individually red/green (16 FAIL plus unchanged guidance-count positive control → 17 OK). Six covered workflow/helper blobs at f5c89121 equal pin. HARNESS and script/cwd fallbacks and root-negative assertions survive.
- SC-08: `.harness/harness/docs/DECISIONS-INDEX.md:13`, `.harness/harness/docs/SPEC.md:808`, `.harness/harness/docs/DECISIONS.md:7116`, `.omp/commands/harness.md:137`: c0 T-05 finding CLOSED. All 23 amend/strike tails independently checked against plan/authority: 20–29 words, durable feature/plan/D-NN successors, DEC-111 explicitly STRUCK with DEC-233 successor. DEC-81/218/222 remain rewritten, not struck. SPEC separates native model policy from guard checks; DEC-214 uses tool_input.task. Main's async edge matches preserved DEC-204 and settled Q2. t05-doctrine correction preserves its former false claim as history.
- SC-09: `.claude/skills/harness/bin/inject-expertise.py:12`, `.claude/skills/harness/bin/harness_yaml.py:781`, `.harness/harness/docs/DECISIONS.md:7933`: bootstrap, live systemMessage, retained request/tool/decision ABI, caps/precedence and authored .claude paths survive. Six bin comment-only module diffs contain only comments/docstrings. Frozen prior/context fixtures and Expertise data have no diff. DEC-108/109 and BUILD history retained. Removed model helper/call and JSONL reader have no shim.
- SC-12: `notes/c1-evidence/grade-522c94b2-to-b9a8c3ad.json:1`, `notes/c1-evidence/check-state-b9a8c3ad.txt:1`, `notes/t05-verify-literal.txt:1`, `tests/integration/test-check-domain.py:140`, `tests/integration/test-layout-migration.py:395`: actual-ref grading/corpus/cumulative receipts inspected; independent exhaustive grading below closes c0 T-03 finding. Both decomposed tests grade4. Same five outcomes, codes, unavailable lists, BLOCKED assertion, parity reader-set/cause assertions, order and fixture lifetime. Authorized case6 retains presence/deleted-name/survivor assertions and non-workflow exclusions. Stop/wake keeps qualifier/STRUCK checks, drops only ruled floor and adds detector controls. Fresh pin execution belongs to QA, not the earlier pinned receipt.
- SC-01/02/03/05/06/07/11: inspected complete frozen context oracle/newline tables; checker PID/error/parity cases; carried decoded-context/retry/once-only tests; schema/semantic/held-child refusal with claim retention/valid correction; old-env root negatives; actual OMP-accessor string-off assertion/mutations; native finite token/custom/default/equality/exclusion/retry witnesses; independent path identity/numeric probe assertions. All serve D-01..D-04; no scope finding. Settled rulings not reopened.
- SC-10: `notes/research-omp1910-observation.md:1` records Main's real19.1.0 nested numeric child/distinct main, 7/7 exit0 and issue2194 CLOSED. Probe/companion blobs independently match pin: `81a28131c1e233c415aacdf6162faa9583344236` / `8c3e9153faf876d97e3ef4c0c25f6c03a54c1e6d`. Not my live UAT.

## Stage 2 — quality and grading

Actually ran canonical `code-grade.py --base 522c94b2b79e5e2021cb670910772428c17914b0 --head 9c38040397bb115583e71b13f1a7ca4bf2f10c2e --json`: **93 records, 93 passing, 0 ungraded**, no severity/reason records. Inspected code_grade.py::_gate_file_records: selection is no pre-image OR strictly worse grade, not all changed bodies. Same-name functions bind by name; renamed equivalents can bind by body hash. Canonical pass binds DEC-209/digest code_grade, not exhaustive SC-12 acceptance.

Independently compared every executable-body hash (`_body_hashes`, leading docstrings stripped) in every changed Python path, grading through grade_source: c0 **155**, c1 **171** = 8 production +163 tests. **93 canonical +78 excluded-but-changed =171**; all production >=4, all tests >=3, zero below bar. Committed JSON's “93 changed functions” means gated records only. Actual base→b9a8c3ad receipt binds forward: no Python/runtime/workflow/test/doctrine blob differs b9a8c3ad→pin. No grade2 reason owed.

Fail-open inspection: checker import/call failures become unknown, not clean; legacy environment cannot restore bootstrap identity. Governed truthy-stop_hook_active yields still traverse held-child/schema/semantic checks before settlement. Usage failures are silent/retryable by D-03, contained before postDomain. Blocked answers cannot deliver context; decoding has no envelope fallback. No new silent authorization path found.

### All 78 excluded changed functions, independently graded

Notation `function@pin-line=grade`; paths exact, repeated directory prefixes grouped below.

Production under `.claude/skills/harness/bin/`:
- `harness_yaml.py`: `_resolve_identity@684=4`.
- `inject-expertise.py`: `_emit@86=5`, `_checker_result@109=4`, `_capped_body@148=4`.
- `validate-digest.py`: `hook_mode@3005=4`, `_pass_through@3052=4`.

Under `tests/integration/`:
- `check_domain_support.py`: `_env@36=5`.
- `check_state_support.py`: `_root_env@117=4`.
- `test-branch-create-gate.py`: `fire@50=5`, `fire_raw@66=5`, `_run_in@303=5`.
- `test-check-domain-grant.py`: `run_t12@419=4`.
- `test-check-domain.py`: `_feat65_fire@25=4`, `_feat2274_cases@140=4`, `_strict_hook_payload_case@375=4`.
- `test-check-instruction-paths.py`: `case_path_directions@65=4`.
- `test-check-state-corpus.py`: `check@33=5`.
- `test-check-state-shipped.py`: `check@55=5`.
- `test-corpus-non-regression.py`: `AuditFindings.test_a_fresh_clone_still_reports_every_baseline_finding@115=4`.
- `test-corpus-real-owner.py`: `check_state@84=5`.
- `test-dispatch-guard.py`: `case_5_main_session@163=5`, `_task@280=5`, `case_6_single_flight_refusal@334=3`, `case_7_allow_and_record@377=4`, `case_8_parallel_squad_stays_legal@398=4`, `case_9_stale_claim@425=4`, `_feat65_fire@455=4`, `case_10_library_missing@502=4`, `case_f2274_unavailable_outcome@597=4`, `_f2274_v2_member_dispatch@619=5`, `case_f2274_v2_legitimate_passthroughs_stay_quiet@663=4`, `case_11_missing_feature_line_refused@698=5`, `case_12_claim_lands_in_declared_worktree@727=4`, `case_27_guard_and_registry_resolve_one_feature_root@770=4`, `case_13_feature_line_must_be_first_and_valid@794=4`, `case_14_single_flight_is_per_feature@806=4`, `case_15_omp_dispatch_records_supervisor_and_receipt@826=4`, `case_15b_omp_main_dispatch_records_top_level_claim@843=4`, `case_15c_omp_main_eng_lead_on_all_direct_plan_refused@878=3`, `_main_start@925=4`, `case_15e_dec174_unresolvable_feature_keeps_prior_refusal@991=4`, `case_17_shell_less_persona_requires_matching_feature_root@1088=3`, `case_18_inverted_slug_refused_no_claim_and_paste_back_safe@1131=4`, `case_19_matching_slugs_not_refused@1170=5`, `case_20_no_run_dir_reference_untouched@1189=5`, `case_21_grant_less_manifest_fails_open_and_says_so@1206=4`, `case_22_derived_vocabulary_matches_invented_squad@1230=4`, `case_23_broken_derivation_distinguished_from_grant_less@1257=4`, `case_24_duplicate_hook_keys_are_rejected@1283=5`, `_fire_from@1295=5`, `case_27_spawn_targets_are_native_authority@1300=3`, `case_29_name_parameter_refused@1351=5`, `case_30_repository_header_binds_exact_factory_claim@1360=3`, `case_31_repository_binding_read_from_the_feature_worktree@1462=5`, `_distill_task@1532=5`, `_distill_fire@1541=5`, `main@1773=5`.
- `test-feature-corpus.py`: `hook@50=5`.
- `test-hooks-install.py`: `_sweep_env@225=5`.
- `test-inject-expertise.py`: `run_hook@64=5`, `get_context@69=5`, `case4d@261=4`.
- `test-layout-migration.py`: `_parity@395=4`.
- `test-lead-start-return.py`: `run_script@86=5`.
- `test-validate-digest.py`: `_t09_claims@1124=4`, `_t09_run@1133=5`, `_t09_return@1141=5`, `run_t09@1296=4`, `_t04_hook_failures@4208=4`, `run_dec156_worktree_red_case@5655=3`, `_f2274_fire_passes@6032=5`.

Other tests:
- `tests/manual/probe-omp-session-accessor.py`: `main@209=4`.
- `tests/unit/test-check-state-inv35.py`: `run_checker@43=4`.
- `tests/unit/test-lead-start-preflight.py`: `dispatch@138=4`.
- `tests/unit/test-lead-stop-and-wake.py`: `bound_site_cases@130=3`, `bound_cases@181=4`.
- `tests/unit/test-no-distribution.py`: `case6@432=5`.
- `tests/unit/test-prune-run-evidence.py`: `check_state@225=5`.

## Evidence limits / gate ownership

Compared pinned standalone env-i clone receipts: both contain identical seven Python FAIL rows (BUG1290 5a/5b/5c, repeated5b, factory-config assertion21 and two failing script summaries), plus identical five named FEAT2225 real-core Bun failures (product-lead/code-reviewer/dev-ops/orchestrator/backend-dev). Both remain **red**. Equal failures do not prove environmental causation or predict green CI. Two c0 standing regressions no longer appear. c0 integration95/95 and typecheck are historical outcomes, not fresh c1 runs.

Pinned check-state-b9a8c3ad receipt records 34 tracked features/exit0. Pinned README ends with a promise of a pin run: post-pin append is not pinned evidence and was not executed by me. QA/lead owns fresh c1-pin check-state under settled Q3 and final cumulative gates; this source review does not substitute a suite execution. Only assigned grading and read-only source/evidence probes ran, no suites/build/lint/formatter/live-host reruns or source edits.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** coordinated transport/model/identity migration without a host compatibility shim; internal Python ABI intentionally retained.
- **Delete First:** session-file reader/state/notices and duplicate model authority disappear rather than survive behind another layer.

Findings: none. Open questions: none. No additional checks requested beyond QA's already assigned final verification.
