# MF-01 receipt — PASS

**Conclusion:** MF-01 was a real test-reliability defect, not a merge-gitignore defect. The mutation rewrote equal-length text in the same filesystem timestamp tick; CPython could then load the baseline `.pyc`, yielding the false `bash=0, write=0` result. The test now prevents bytecode writes for both isolated hook subprocesses, while retaining the named mutation and required `(2, 2)` assertion.

## Evidence and diagnosis

- Current candidate before correction: direct `python3 .agents/skills/harness/bin/test-bash-write-guard.py` exited 0 (`27/27` worktree-boundary cases; ONE IMPLEMENTATION passed).
- Clean base control: exported `0fa8f336e55dc57bca09a9f7df0524a35195ee7e` with `git archive` to a temporary directory, ran the identical targeted program, then removed the directory (`cleanup-exit=0`). It exited 1 at `26/27`; the sole failure was ONE IMPLEMENTATION with `bash=0, write=0`.
- The target test and the three guard/module inputs had identical base/current blobs before correction: `test-bash-write-guard.py=5f494142`, `bash-write-guard.sh=0b1bbb89`, `check-domain.sh=c6b581e`, `harness_boundary.py=de9689e`, `harness_yaml.py=a5c5367`. The failure therefore pre-existed FEAT-36's merge-gitignore coverage.
- Hypothesis: a same-size, same-mtime source mutation lets timestamp-validated bytecode retain the baseline module. Falsifier: disabling bytecode writes would still produce `0/0`. Control: `PYTHONDONTWRITEBYTECODE=1 python3 .agents/skills/harness/bin/test-bash-write-guard.py` exited 0 with ONE IMPLEMENTATION `(2, 2)`, confirming the cache mechanism.
- The initial prescribed all-kinds gate also reproduced the same sole failure. The minimal correction sets `PYTHONDONTWRITEBYTECODE=1` only in the isolated mutation fixture's child-hook environment; it neither changes production guards nor weakens the mutation assertion.

## Source identities

| State | test-bash-write-guard.py | bash-write-guard.sh | check-domain.sh | harness_boundary.py | harness_yaml.py | test-merge-gitignore.py | run-unit-tests.sh | harness.json |
|---|---|---|---|---|---|---|---|---|
| before | 5f494142 | 0b1bbb89 | c6b581e | de9689e | a5c5367 | 06507a2 | b688261 | ca29860 |
| after | a4ff275 | 0b1bbb89 | c6b581e | de9689e | a5c5367 | 06507a2 | b688261 | ca29860 |

Candidate HEAD remained `9403fca5252dbe6e5527aa20de3d5d9d3e5f8b1d`; only `.agents/skills/harness/bin/test-bash-write-guard.py` changed in this repair.

## T-01 verification

```sh
python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
.agents/skills/harness/bin/run-unit-tests.sh --kind all
```

Exit code: **0** (149.70s). Summary: direct merge-gitignore program `7 passed; 0 failed`; all-kinds runner reported `PASS test-bash-write-guard.py` with ONE IMPLEMENTATION passing `(2, 2)` and `27/27` worktree-boundary cases, then `PASS test-merge-gitignore.py`; no runner failures.

## Disposition

- Modified files: `.agents/skills/harness/bin/test-bash-write-guard.py`.
- Remaining must-fix items: none.
- Open questions: none.
- Escalations: none.
- expertise_update: [].
