# BUG-2190 exit goal-check — FAIL

The fix is evidenced, but two signed automated clauses lack carrying assertions. No scope change or new operator approval is required: complete the existing T-01 evidence contract.

## Perspectives

- **operator — partial:** SC-01 met; SC-02 and SC-03 partial. Tokenless bound receipts work, while required recovery-target assertions and malformed-factory-shape regression coverage are missing.
- **code maintainer — pass:** SC-04, SC-05 and SC-06 met on the recorded build evidence and pinned tests: online remote-read refusal, owner controls, no-plan exclusion, real local validation and unchanged resolver delegation are represented. Shared resolver has no feature change.

## Criterion evidence

All source/test references below are at review pin 33c0c181e62c5e75692c8320fc01aaaaf06fa40b; production baseline c6bd42d20fa9bf58e4c1dd3ede417caefc23a853. Exclude FEAT-71 corpus-prune content merged at 907225c1. Paths abbreviated relative to PRODUCT.

| SC | Outcome | Evidence |
|---|---|---|
| SC-01 | met | tests/integration/test-check-state-inv37-offline.py#_i1_offline_valid_opened_is_clean and #_i2_offline_terminal_with_owner_sync_off_is_clean; build-evidence-2026-11-08.md:20,41-43 records baseline red and final green. |
| SC-02 | partial | Integration #_i3, #_i4, #_i5 assert classification, provenance and zero reads; build evidence:21 records wrong baseline classification. None asserts the recovery-command repository. |
| SC-03 | partial | Integration #_i6 covers malformed names, non-string, empty and unlisted repo; unit #case_offline_invalid_bindings_still_fail plus build evidence:35-37 records bypass-mutant rejection; SC-01 supplies the red valid twin. Both fixture builders always construct a factory mapping, so malformed factory shapes have no test. |
| SC-04 | met | Integration #_i1, #_i7_online_matching_remote_is_clean_and_read, #_i8_online_remote_failure_stays_a_violation; unit #case_online_keeps_full_remote_verification; build evidence:20,24,41-42. |
| SC-05 | met | Integration #_i9_owner_controls_beside_a_bound_feature, #_i10_offline_legacy_and_sync_off_controls, #_i11_offline_bound_feature_without_a_plan_is_ineligible; build evidence:22-24,42. |
| SC-06 | met | tests/unit/test-check-state-inv37-local-binding.py#case_offline_valid_bound_is_clean, #case_offline_receipts_are_graded_against_factory_repo, #case_offline_invalid_bindings_still_fail, #case_online_keeps_full_remote_verification and #case_owner_path_is_unchanged; build evidence:26-37,41. |

## Findings

- **G-01 — kind: coverage; severity: medium; task: T-01; SC-02.** A recovery formatter could instruct recovery against org/repo while the provenance finding correctly names org/prod; all new assertions would remain green. Add carrying evidence asserting factory.repo in recovery guidance and excluding the owner target. Inspection of board.py#_inv37_finding passing repo to recovery_command_line supports implementation intent but cannot substitute for the signed assertion requirement.
- **G-02 — kind: coverage; severity: medium; task: T-01; SC-03.** A nonmapping factory such as a string/list is bound by feature_schema.has_repository_binding, but neither test supplies it. Removing the mapping guard in board.py#_inv37_local_repo would leave new tests green while this case can raise instead of emitting invalid authoritative binding. Obtain the declared malformed-shape and zero-read evidence.

## Authority and verification limits

Consulted BRIEF SC-01..06, approved plan T-01, settled research, notes/operator-signature-2026-11-08.md:5-15, AGENTS.md Project map, SPEC.md onboarding:427-455, DECISIONS-INDEX and DEC-220/221. DEC-221:7264-7272 expressly authorizes this offline exception; it is not an unauthorized weakening of the shared resolver. T-01 currently owns board.py, table.py, both tests, reader inventory and decision/index updates. Earlier intake's narrower file prose is historical; no added scope question is raised.

No builds, tests, linters or formatters executed by this reader. Passing-run claims above come from the committed main-session build receipt, not a new execution or a current QA DIGEST. Independent QA remains a separate validation gate; this assessment does not claim it passed. Main/QA should use the unchanged literal T-01 verify after any authorized correction.

## Open questions

None. Both gaps return to QA/main within existing approved scope; do not narrow the signed criteria.
