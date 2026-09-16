# Fail-first receipt — BUG-1716 T-03 (amendment judgement, overrule route, signed hashes)

New tests run against feature-record.py / feature-schema.json at 07424285 (pre-change). Captured 2026-09-16T05:36Z by Main.

```
FAIL: test_judgement_accepts_the_amendment_kind_with_a_task_field_decision (__main__.AmendmentTest.test_judgement_accepts_the_amendment_kind_with_a_task_field_decision)
FAIL: test_overrule_refuses_no_match_a_non_amendment_and_a_repeat_without_writing (__main__.AmendmentTest.test_overrule_refuses_no_match_a_non_amendment_and_a_repeat_without_writing)
FAIL: test_overrule_refuses_two_amendments_at_one_timestamp_without_writing (__main__.AmendmentTest.test_overrule_refuses_two_amendments_at_one_timestamp_without_writing)
FAIL: test_overrule_selects_exactly_the_entry_at_that_timestamp (__main__.AmendmentTest.test_overrule_selects_exactly_the_entry_at_that_timestamp)
FAIL: test_amendment_kind_is_valid_and_overruled_true_only_on_it (__main__.SchemaTest.test_amendment_kind_is_valid_and_overruled_true_only_on_it)
FAIL: test_signed_task_hashes_is_a_t_nn_to_sha256_map (__main__.SchemaTest.test_signed_task_hashes_is_a_t_nn_to_sha256_map)
Ran 51 tests in 5.268s
FAILED (failures=6)
FAIL accepted_signed_task_hashes_and_amendment_judgement ["sample.json: undeclared key 'signed_task_hashes' at /. This file holds execution state only. An operator ruling goes in that feature's plan.yaml under approval.rulings; run narrative, findings and corrections go in that run's digest; current state and open questions go in STATE.md; measurements, research and receipts go in notes/.", "sample.json: /judgements/0/kind: 'amendment' is not one of ['mission', 'finding_kind', 'regate', 'continue', 'succession']", "sample.json: undeclared key 'overruled' at /judgements/1. This file holds execution state only. An operator ruling goes in that feature's plan.yaml under approval.rulings; run narrative, findings and corrections go in that run's digest; current state and open questions go in STATE.md; measurements, research and receipts go in notes/.", "sample.json: /judgements/1/kind: 'amendment' is not one of ['mission', 'finding_kind', 'regate', 'continue', 'succession']"]
PASS rejected_signed_task_hash_sc_key
PASS rejected_signed_task_hash_uppercase
PASS rejected_signed_task_hash_short
PASS rejected_signed_task_hash_list
PASS rejected_overruled_false
PASS rejected_overruled_regate
1 FAILURE(S): ['accepted_signed_task_hashes_and_amendment_judgement']
```
