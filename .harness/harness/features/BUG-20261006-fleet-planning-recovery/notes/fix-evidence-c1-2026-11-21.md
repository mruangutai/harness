# BUG-20261006 fix c1 evidence (main session, DEC-174), 2026-11-21

Validate run `2026-11-21-1-validator` (pin `64511531`) failed with one high finding and three medium coverage gaps, all against T-01. This cycle answers all four. No plan amendment was needed: every touched path is already a T-01 file.

## 1. High: LABEL reconciliation ownership was blind to repository (`board_lifecycle.py`)

**Before.** LABEL in the owner repository collected every record's parent, source and task numbers. Kaya's task #17 therefore made an unrelated, closed not_planned Harness #17 eligible for `reconcile --apply` to add `abandoned`.

**Fix (`843a16dc`).**
- `_label_scope` and `_label_owned_numbers` count a record's tickets only when the record's mirror provably lives in the audited repository:
  - a record bound to another repository is skipped;
  - `mirror_evidence_problems` and `mirror_provenance_problem` must both be clean.
- An unreadable corpus, an unreadable or malformed record, or an invalid binding becomes a report-only LABEL residual naming the record. `_fixable` already excludes findings with no `issue_number`, so these residuals never widen what reconcile writes. This reverses #2151's broad-rule fallback for the owner repository; advisor ruling Inv26RoutingAdvisor (2026-11-21) found no DEC behind that fallback.
- Other repositories keep the broad rule, unchanged.

**Regression (`8d5fbaf2`, committed red first).** In `tests/integration/test-board-lifecycle.py`:
- Collision: a record bound to `acme/other` owning #17 yields no LABEL finding on `acme/widget#17` and no `issue edit`.
- Same-repo control: the identical record bound to `acme/widget` yields the finding and exactly one label write.
- The six malformed-record cases from #2151 now assert the residual and that no label write occurs.

**Base (pre-fix `board_lifecycle.py`), exit 1.**
- FAIL: the collision case. This is the reviewer's scenario, now executed rather than inferred.
- FAIL: all six malformed cases.
- PASS: the same-repo control.

**Fix:** exit 0.

## 2–4. Medium: SC-01, SC-04 and SC-06 integration coverage (`35d46417`)

All are discriminated by mutants. Harness `/tmp/b06_mutants.py` edits one source file in place, runs the named cases, and restores the file byte-for-byte.

| SC | New integration cases | Mutant | Result |
|---|---|---|---|
| SC-01 | `test-gh-sync-open.py`, `fleet_bound_command_cases`: after a bound `open`, each of status, start-task, record-pr, ship, abandon, reject, backlog and recover-terminal exits 0, names `product/app` and never calls `owner/harness`. `fleet_config_failure_cases`: unreadable config, a config naming another repository, a config with sync off, and a `factory.repo` absent from the fleet each refuse `open`, with no receipt, no mutation and no owner call. | M-OWNER: `resolve_binding` ignores `factory.repo` and falls back to the owner (the pre-fix behaviour) | **KILLED**: all 12 FAIL |
| SC-04 | `test-check-state-records.py` `case_inv7_counts_evidence_not_fail_verdicts`, through the real reader: three FAILs against a total of 1 give no violation; an evidenced 0 draws no note; an unevidenced 1 is a "without evidence" note; an absent count is an "unknown attribution" note. | M-INV7: the pre-fix `inv_7` from `4a05030d^` (FAIL-count floor) | **KILLED**: 3 FAIL |
| SC-06 | `test-check-state-records.py` `case_refusal_provenance_never_satisfies_live_validation`: after `record-refusal` on run R, live `validate-digest.py` still rejects R's prose; `close-run` refuses the same prose for a new run S and leaves `feature.json` unchanged; complete run Q with no digest is still a violation. | M-LIVE: `validate-digest.py` accepts any digest whose hash is a recorded refusal | **KILLED** |

## Green (after the grade-bar split, `HEAD` of this cycle)

- `test-board-lifecycle.py`, `test-gh-sync-open.py` and `test-check-state-records.py` all exit 0. All three mutants are re-run against the split code: M-INV7, M-OWNER and M-LIVE are each still **KILLED**, and every source is restored byte-for-byte.
- Configured kinds: unit 61/61 files and integration 87/87 files, both exit 0.
- `check-plan-routes.py --canonical-reader-audit`: 0 unresolved reader sites. The LABEL helpers reuse the existing `load_feature_json` and `_feature_dirs` readers.
- `code-grade.py --base fbff8150 --head <cycle head>`: all 23 changed functions PASS their bars.
  - The first measurement failed. `_audit_findings` and `_label_owned_numbers` graded 3 (bar 4). The new test cases and `main` graded 1–3 (bar 3).
  - The LABEL block was split into `_label_class_findings` and `_label_record_owner`.
  - The test cases were split into fixture and assertion helpers.
  - `test-check-state-records.py main` became a case table.
- pyflakes: no new findings. The pre-existing unused `ms_idx` in `test-gh-sync-open.py` is untouched.
