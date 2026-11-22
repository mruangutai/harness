# T-01 RED — tests/integration/test-omp-native-gate-runtime.py at baseline 1e0b0149

Run from a `git archive 1e0b0149` export (.omp/extensions, .claude/skills/harness/bin, tests) with the new suite copied in.

## A. Baseline as-is: `python3 tests/integration/test-omp-native-gate-runtime.py` → exit 1

```
FAIL  control: a normal broad-gate pass is allowed with no unavailable outcome
FAIL  control: a broad gate's explicit refusal stays a block, not unavailable
FAIL  control: a narrow gate's structured deny of a matching command stays a block
FAIL  control: a narrow gate allows an unrelated command with no unavailable outcome
FAIL  broad check-domain, guarded crash: the call is allowed and reported unavailable
FAIL  broad check-domain, startup failure before the guard: the call is allowed and reported unavailable
FAIL  broad check-domain, missing gate: the call is allowed and reported unavailable
FAIL  broad check-domain, missing interpreter: the call is allowed and reported unavailable
FAIL  broad check-domain, spawn error (not executable): the call is allowed and reported unavailable
FAIL  broad check-domain, unexpected termination (SIGKILL): the call is allowed and reported unavailable
FAIL  broad bash-write-guard.py, guarded crash: allowed and reported unavailable
FAIL  broad bash-write-guard.py: the outcome names the script stem 'bash-write-guard', not a diagnostic label
...
0 passed, 43 failed in 1.3s
```

Every runPolicy case reports `runPolicy is not exported`; no corpus exists.

## B. Baseline + test-side export shim (`function runPolicy` → `export function runPolicy`; no behaviour change) → exit 1

```
ok    control: a normal broad-gate pass is allowed with no unavailable outcome
ok    control: a broad gate's explicit refusal stays a block, not unavailable
ok    control: a narrow gate's structured deny of a matching command stays a block
ok    control: a narrow gate allows an unrelated command with no unavailable outcome
FAIL  broad check-domain, guarded crash: the call is allowed and reported unavailable
FAIL  broad check-domain, startup failure before the guard: the call is allowed and reported unavailable
FAIL  broad check-domain, missing gate: the call is allowed and reported unavailable
FAIL  broad check-domain, missing interpreter: the call is allowed and reported unavailable
FAIL  broad check-domain, spawn error (not executable): the call is allowed and reported unavailable
FAIL  broad check-domain, unexpected termination (SIGKILL): the call is allowed and reported unavailable
FAIL  broad bash-write-guard.py, guarded crash: allowed and reported unavailable
FAIL  broad bash-write-guard.py: the outcome names the script stem 'bash-write-guard', not a diagnostic label
FAIL  broad dispatch-guard.py, guarded crash: allowed and reported unavailable
FAIL  broad dispatch-guard.py: the outcome names the script stem 'dispatch-guard', not a diagnostic label
FAIL  broad validate-digest.py, guarded crash: allowed and reported unavailable
FAIL  broad validate-digest.py: the outcome names the script stem 'validate-digest', not a diagnostic label
ok    validate-digest, absent digest_object: still a refusal, not unavailable
ok    validate-digest, null digest_object: still a refusal, not unavailable
ok    validate-digest, empty digest_object: still a refusal, not unavailable
FAIL  validate-digest, unknown persona schema: allowed and reported unavailable
FAIL  narrow gh-close-gate, startup failure before the guard: a matching command is refused
ok    narrow gh-close-gate, startup failure before the guard: an unrelated command is allowed silently
FAIL  narrow gh-close-gate, missing gate: a matching command is refused
FAIL  narrow gh-close-gate, missing gate: an unrelated command is allowed silently
FAIL  narrow gh-close-gate, missing interpreter: a matching command is refused
FAIL  narrow gh-close-gate, missing interpreter: an unrelated command is allowed silently
FAIL  narrow gh-close-gate, spawn error (not executable): a matching command is refused
FAIL  narrow gh-close-gate, spawn error (not executable): an unrelated command is allowed silently
FAIL  narrow gh-close-gate, unexpected termination (SIGKILL): a matching command is refused
ok    narrow gh-close-gate, unexpected termination (SIGKILL): an unrelated command is allowed silently
FAIL  narrow gh-close-gate, dependency failure after applicability: a matching command is refused
ok    narrow gh-close-gate, dependency failure after applicability: an unrelated command is allowed silently
FAIL  narrow branch-create-gate.py, dependency failure: a matching command is refused
ok    narrow branch-create-gate.py, dependency failure: an unrelated command is allowed silently
FAIL  narrow branch-create-gate.py, missing gate: a matching command is refused
FAIL  narrow branch-create-gate.py, missing gate: an unrelated command is allowed silently
FAIL  narrow plan-sign-gate.py, dependency failure: a matching command is refused
ok    narrow plan-sign-gate.py, dependency failure: an unrelated command is allowed silently
FAIL  narrow plan-sign-gate.py, missing gate: a matching command is refused
FAIL  narrow plan-sign-gate.py, missing gate: an unrelated command is allowed silently
FAIL  test-gh-close-gate.py exposes APPLICABILITY_CORPUS with matching and unrelated entries
FAIL  test-branch-create-gate.py exposes APPLICABILITY_CORPUS with matching and unrelated entries
FAIL  test-plan-sign-gate.py exposes APPLICABILITY_CORPUS with matching and unrelated entries
12 passed, 31 failed in 4.0s
```

Selected failure details (pre-edit behaviour):

```
FAIL  broad check-domain, guarded crash: the call is allowed and reported unavailable
      {'blocked': False, 'unavailable': None, 'reason': None}
FAIL  broad check-domain, startup failure before the guard: the call is allowed and reported unavailable
      {'blocked': False, 'unavailable': None, 'reason': 'File "/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/feat2274-runtime-dvbq6yba/.agents/skills/harness/bin/check-domain.py", line 2\n    this is not pytho
FAIL  broad check-domain, missing gate: the call is allowed and reported unavailable
      {'threw': "Error: ENOENT: no such file or directory, posix_spawn '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/feat2274-runtime-060ptn1j/.agents/skills/harness/bin/check-domain.py'"}
FAIL  broad check-domain, missing interpreter: the call is allowed and reported unavailable
      {'threw': "Error: ENOENT: no such file or directory, posix_spawn '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/feat2274-runtime-vwa3_yd9/.agents/skills/harness/bin/check-domain.py'"}
FAIL  broad check-domain, spawn error (not executable): the call is allowed and reported unavailable
      {'threw': "Error: EACCES: permission denied, posix_spawn '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/feat2274-runtime-s62b0at6/.agents/skills/harness/bin/check-domain.py'"}
FAIL  broad check-domain, unexpected termination (SIGKILL): the call is allowed and reported unavailable
      {'blocked': False, 'unavailable': None, 'reason': 'check-domain.py exited null'}
```

Finding: a missing gate, missing interpreter or spawn error makes runPolicy THROW at baseline; omp fails a throwing tool_call handler closed, so one missing broad gate blocked every governed call.
