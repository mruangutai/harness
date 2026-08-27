# Observations - harness-documentor

- 2026-08-27 (T-05): a dispatch's "expected green" list named `test-lead-stop-and-wake.py --check-kinds`; that flag does not exist (argparse rc=2, usage lists only `--self-check | --group`). Running the named command beat trusting the expectation.
- 2026-08-27 (T-05): the task intent asserted the platform nudge text "appears nowhere under .claude/, .harness/ or docs/"; grep found four matches (the rule's own denial, the guard test, BRIEF, plan.yaml). Wrote the constraint without the falsifiable grep claim rather than transcribing a signed-but-untrue sentence.
