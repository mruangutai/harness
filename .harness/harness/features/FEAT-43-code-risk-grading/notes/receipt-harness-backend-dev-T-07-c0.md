# T-07 c0 receipt

## Result

Gate policy loading and evaluation now reject absent, unreadable, unparsable, and invalid policy inputs loudly through `GatePolicyError`. The unit runner retains T-01's `test-code-grade.py` registration and appends T-07's `test-gate-policy.py`; neither is an integration registration.

## Test-first evidence

After creating the policy assertions and registering their script, but before `gate_policy.py` existed, the required invocation exited 1. Its exact failure tail was:

```text
Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.claude/skills/harness/bin/test-gate-policy.py", line 13, in <module>
    spec.loader.exec_module(gate_policy)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 755, in exec_module
  File "<frozen importlib._bootstrap_external>", line 892, in get_code
  File "<frozen importlib._bootstrap_external>", line 950, in get_data
FileNotFoundError: [Errno 2] No such file or directory: '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.claude/skills/harness/bin/gate_policy.py'
FAIL test-gate-policy.py
```

Full exact red-run output: `artifact://26`.

## Required verification

Invocation (verbatim; with `/opt/homebrew/bin` prepended to `PATH` so `python3` resolved to Python 3.14.5):

```text
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Exit status: 0.

Exact T-07 output:

```text
ok    loader resolves qa_gate by name from fixture
ok    loader resolves review by name from fixture
ok    loader resolves uat by name from fixture
ok    loader resolves merge by name from fixture
ok    unrecognised qa_gate policy: names qa_gate
ok    unrecognised qa_gate policy: carries offending value
ok    non-string qa_gate policy: names qa_gate
ok    non-string qa_gate policy: carries offending value
ok    absent gates block: names gates
ok    absent gates block: carries offending value
ok    absent named gate: names merge
ok    absent named gate: carries offending value
ok    unparseable configuration: names config
ok    unparseable configuration: carries offending value
ok    unreadable configuration: names config
ok    unreadable configuration: carries offending value
ok    review blocks must_fix even without a severity escalation
ok    review passes a clean medium-severity report
ok    review blocks high severity
ok    blocking review blocks findings
ok    advisory review always passes
ok    unknown review severity raises loudly: names severity_max
ok    unknown review severity raises loudly: carries offending value
ok    blocking QA does not fail skipped suite
ok    QA detail reports skipped suite
ok    blocking QA blocks failed suite
ok    advisory QA always passes
PASS test-gate-policy.py
```

Full exact final green-run output: `artifact://29`.

## Registration confirmation

`run-unit-tests.sh` `UNIT_SCRIPTS` contains both `test-code-grade.py` (T-01) and the appended `test-gate-policy.py` (T-07). `INTEGRATION_SCRIPTS` remains unchanged and contains neither registration.
