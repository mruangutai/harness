# T-03 c1 receipt — PASS

## Result

The signed integration verification passes under the compatible Homebrew Python. No T-03 implementation or contract-test change was necessary.

## Runtime and signed invocation

PATH was set to `/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`, which selected `/opt/homebrew/bin/python3` (`Python 3.14.5`).

Command (verbatim from `plan.yaml`):

```sh
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```

Exit status: `0`.

## Observed result

The complete observed output is retained at `artifact://65` (820 lines; output was too long to reproduce safely here). It ends with:

```text
PASS test-code-grade-cli
PASS test-code-grade-cli.py
```

No failures were reported; the runner completed successfully in 171.32 seconds.

## Registration audit

The required literal `.claude/skills/harness/bin/test-code-grade-cli.py` remains in `test_kinds.integration.detect`, and `test-code-grade-cli.py` remains in `INTEGRATION_SCRIPTS`. The diff from the task baseline (`6e4a273`) shows the CLI registration as the T-03 addition and retains all existing runner registrations.

`test-merge-gitignore.py` was pre-existing in `run-unit-tests.sh` and its literal was already present in `harness.json` at baseline `6e4a273`. Its current harness.json presence is preservation of an existing integration registration, not T-03 scope expansion; no unrelated registration was added to repair another task.
