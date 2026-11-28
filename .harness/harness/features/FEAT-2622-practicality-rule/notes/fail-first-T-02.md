# T-02 fail-first record

Verify run at the T-02 build tip before commit.

- The red-first block (tests/unit/test-practicality-record-panel.py at HEAD and over base 3e979ae3):

```
red-first: 5 of 5 cases; not green now or not red at base: []
```

  `record-panel-legacy-row-kept` passes at base, as the verify requires.
- test-practicality-record-panel.py, test-plan-merge.py and test-check-state-records.py exit 0; check_state/run_state.py is byte-identical to base.

## Deviation: the SC-14 block

The verify's last block runs base's test-plan-merge.py against the built plan-merge.py and looks for the `FAIL  record-panel exits 0 on a well-formed lead digest` line. The base suite never prints a report: its pool aborts on a ValueError in `case_f59_review_f10_panel_splice_keeps_a_comment_with_the_finding_it_followed`, whose exposure-less fixture the built writer now refuses, so the block prints "NOT red" with an empty detail. The base suite does exit 1.

The red the block asserts was measured directly, by running base's `case_f59_record_panel_writes_from_a_lead_digest` alone against the built plan-merge.py (PLAN_MERGE_BIN, base tests on PYTHONPATH):

```
FAIL  record-panel exits 0 on a well-formed lead digest
      | rc=5 'plan-merge: lead digest findings[0] is missing exposure — every finding carries exposure, and a reader that gave none is transcribed as exposure unrated by its lead (DEC-206).\n'
```

The SC-14 claim holds: base's test is red, with rc=5 naming exposure. The verify text's harness is what cannot read it.
