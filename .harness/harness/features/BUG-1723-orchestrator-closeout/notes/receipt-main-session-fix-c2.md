# Fix c2 — BUG-1723 (validate c1 FAIL: C1-V01/V02/V03) — by Main, main-session-direct

- C1-V01 (T-03, high): references/ledger.md's seam paragraph now states INV-43 as a violation at every station, done included, with the BUG-285 census named and CANNOT VERIFY spelled out; no terminal-note wording remains anywhere under .claude/skills/harness or DECISIONS.md.
- C1-V03 (T-01, med): the spend-stage test now goes THROUGH `cmd_close_run`: every stage runs for real except the subprocess whose argv is `spend`, which is made to exit 3 at the subprocess seam. close-run exits 3 naming `spend`, keeps run-end's and the judgement's writes, prints no summary — bound to `_close_run_stages`' actual tuple, so a renamed or reordered stage fails the test.
- C1-V02 (T-01, med): the two c1 refusal arms captured red against the pre-close-run command (fac877f1^) in a throwaway worktree, 2026-09-16T06:15Z:

```
ERROR: test_spend_stage_refusal_through_close_run_names_spend_keeps_earlier_writes (__main__.CloseRunTest.test_spend_stage_refusal_through_close_run_names_spend_keeps_earlier_writes)
AttributeError: module 'feature_record_cli' has no attribute 'cmd_close_run'
FAIL: test_judgement_stage_refusal_names_it_keeps_run_end_and_never_reaches_spend (__main__.CloseRunTest.test_judgement_stage_refusal_names_it_keeps_run_end_and_never_reaches_spend)
AssertionError: 11 != 2 : usage: feature-record.py [-h]
feature-record.py: error: argument cmd: invalid choice: 'close-run' (choose from 'run-start', 'run-end', 'judgement', 'set-rework', 'raise-cycles', 'set-mission', 'spend', 'propose-rework')
Ran 2 tests in 0.090s
FAILED (failures=1, errors=1)
```

Verify: `python3 tests/unit/test-feature-record.py` OK; `run-unit-tests.py --kind integration` PASS.
