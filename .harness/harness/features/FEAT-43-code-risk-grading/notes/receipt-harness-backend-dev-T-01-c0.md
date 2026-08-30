# T-01 receipt

## RED — before production module

Invocation:

```text
python3 .claude/skills/harness/bin/test-code-grade.py
```

Observed output:

```text
Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.claude/skills/harness/bin/test-code-grade.py", line 10, in <module>
    spec.loader.exec_module(code_grade)
  File "<frozen importlib._bootstrap_external>", line 846, in exec_module
  File "<frozen importlib._bootstrap_external>", line 982, in get_code
  File "<frozen importlib._bootstrap_external>", line 1039, in get_data
FileNotFoundError: [Errno 2] No such file or directory: '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.claude/skills/harness/bin/code_grade.py'
```

## Required verification

Invocation:

```text
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Observed output:

```text
run-unit-tests.sh: no harness root could be resolved from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.claude/skills/harness/bin — refusing to run
```

Exit status: 2.

A direct diagnosis showed the runner invokes `python3 -P`; this workstation's Python 3.9 rejects `-P` as an unknown option. This pre-existing runner/runtime incompatibility prevents the declared verification from reaching the registered tests. The scoped fixture command passed after implementation:

```text
PASS test-code-grade
```
