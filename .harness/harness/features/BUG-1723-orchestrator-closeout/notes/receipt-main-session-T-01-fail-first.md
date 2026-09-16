# Fail-first receipt — BUG-1723 T-01 (close-run)

CloseRunTest run against feature-record.py at 5bfab2da (pre-change; tests added, verb absent). Captured 2026-09-16T05:08Z by Main.

```
FAIL: test_a_later_refusal_keeps_the_earlier_completed_stage (__main__.CloseRunTest.test_a_later_refusal_keeps_the_earlier_completed_stage)
FAIL: test_argument_shape_is_refused_before_any_stage_runs (__main__.CloseRunTest.test_argument_shape_is_refused_before_any_stage_runs)
FAIL: test_invalid_digest_stops_before_run_end (__main__.CloseRunTest.test_invalid_digest_stops_before_run_end)
FAIL: test_paired_task_station_and_judgement_land_in_one_act (__main__.CloseRunTest.test_paired_task_station_and_judgement_land_in_one_act)
FAIL: test_success_closes_the_run_and_prints_one_line_with_spend (__main__.CloseRunTest.test_success_closes_the_run_and_prints_one_line_with_spend)
FAIL: test_unknown_run_is_refused_naming_the_run_end_stage_with_no_later_stage (__main__.CloseRunTest.test_unknown_run_is_refused_naming_the_run_end_stage_with_no_later_stage)
Ran 6 tests in 0.469s
FAILED (failures=6)
```

All six red because argparse rejects the unknown verb (exit 2, no bytes moved): success, paired station+judgement, argument-shape refusals, invalid digest, unknown run, and later-refusal-retains-earlier-stage.
