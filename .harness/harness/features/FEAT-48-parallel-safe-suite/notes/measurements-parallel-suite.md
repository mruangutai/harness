# FEAT-48 parallel-suite measurements

## Shared-tree isolation

The control used a complete private bin copy. It replaced that copy's `test-check-domain.py` with the pinned pre-fix `ea6f51f` blob, polled the copy's `feature_schema.py`, and verified the live module's bytes and `st_mtime_ns` stayed unchanged. The post-fix probe polled the live module during a complete suite run.

```text
control command: isolated_bin(tempfile.mkdtemp()); git show ea6f51f:.claude/skills/harness/bin/test-check-domain.py > <copy>/test-check-domain.py; python3 <copy>/test-check-domain.py
control exit 1
control broken reads 4968
live feature_schema.py bytes equal true
live feature_schema.py mtime equal true
post-fix command: bash .claude/skills/harness/bin/run-unit-tests.sh --kind all, with concurrent live feature_schema.py polling
post-fix exit 0
post-fix broken reads 0
```

control method: isolated bin copy
control broken reads 4968
post-fix broken reads 0

## Ten consecutive runs

Command for every run:

```text
bash .claude/skills/harness/bin/run-unit-tests.sh --kind all
```

```text
run 1 exit 0 42.64s
run 2 exit 0 42.73s
run 3 exit 0 42.88s
run 4 exit 0 44.70s
run 5 exit 0 43.05s
run 6 exit 0 43.19s
run 7 exit 0 42.97s
run 8 exit 0 43.12s
run 9 exit 0 43.63s
run 10 exit 0 47.82s
```

tree condition: committed implementation at `993ac997`; no process wrote bin or any source file during any run

Ten clean runs do not prove the race is gone: the old hazard previously survived six consecutive clean eight-worker runs. The static invariant and runtime mutation check carry that claim.

## Representative pool output

The serial baseline measured during planning was 247s. A representative post-fix full run on this 12-core M3 Pro emitted:

```text
PASS test-suite-independence.py
pool: 8 workers, 63 files, 42.40s wall
slowest: test-check-state.py 40.80s, test-gh-sync.py 40.15s, test-check-plan-routes.py 33.46s
```

pool: 8 workers, 63 files, 42.40s wall
slowest: test-check-state.py 40.80s, test-gh-sync.py 40.15s, test-check-plan-routes.py 33.46s
PASS test-suite-independence.py
