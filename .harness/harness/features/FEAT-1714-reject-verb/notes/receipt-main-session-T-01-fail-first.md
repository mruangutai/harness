# Fail-first receipt — FEAT-1714 T-01 (reject digest contract)

The 14 new orchestrator digest cases run against validate-digest.py at 0411623e (pre-change). Captured 2026-09-16T05:24Z by Main.

```
FAIL  rejected: reject judgement with a superseding issue is accepted
FAIL  rejected: superseded_by none (should not be planned) is accepted
FAIL  rejected: no judgement mapping is refused naming it
FAIL  rejected: kind other than reject is refused
FAIL  rejected: superseded_by zero is refused
FAIL  rejected: superseded_by negative is refused
FAIL  rejected: superseded_by boolean is refused
FAIL  rejected: empty reason is refused
FAIL  rejected: reason over 240 characters is refused
FAIL  rejected: multiline reason is refused
FAIL  rejected: a missing key is refused
ok    rejected: an extra key is refused
FAIL  rejected: cycles_used must be integer zero
ok    a judgement mapping on any other status is refused
```

Every case is red because `rejected` is not yet a status — including the negative cases, which must fail-then-pass by refusing for the RIGHT reason (superseded_by/reason/kind/cycles_used), not for an unknown status.

## feature-record.py / feature-schema.json (ledger half)

```
FAIL: test_judgement_accepts_reject_with_the_superseding_issue_as_decision (__main__.JudgementTest.test_judgement_accepts_reject_with_the_superseding_issue_as_decision)
FAIL: test_judgement_reject_kind_is_accepted_by_the_strict_schema (__main__.SchemaTest.test_judgement_reject_kind_is_accepted_by_the_strict_schema)
Ran 42 tests in 4.305s
FAILED (failures=2)
```

Red: `reject` is not in JUDGEMENT_KINDS (argparse choices, exit 2) nor in the schema enum.
