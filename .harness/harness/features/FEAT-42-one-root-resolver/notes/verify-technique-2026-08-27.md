# Why the parity proofs are shaped the way they are — 2026-08-27

Main session, executing the main-session-direct lane. Written because three of these points
were discovered by a verify block passing for the wrong reason, and the plan's own field
budget (DEC-182) is the right place for the instruction, not the argument.

## The reverted copy needs its siblings

T-05's verify originally did `git show 3952814:$B/check-plan-routes.py > /tmp/f42-cpr-old.py`
and ran the suite against that path. A bare `/tmp` file has no sibling `bin`, so the reverted
copy could not import `harness_yaml`. All 87 cases died in tracebacks, `grep -E '^(PASS|FAIL)'`
filtered every one of them away, and an EMPTY before-set diffed clean against an empty
after-set. The block passed and proved nothing.

The fix is the mirror the six gate cutovers already use: copy the whole `bin` directory, then
revert inside the mirror only the files the task touched.

## Do not set HARNESS_PROJECT_DIR around a suite that sets its own roots

The first mirror attempt exported `HARNESS_PROJECT_DIR=$M` around the run.
`test-check-plan-routes.py:45-53` sets and unsets `CLAUDE_PROJECT_DIR` per case and leaves the
other name alone, so the outer value won the reverted copy's chain in every case and pointed
all 87 at the mirror instead of their own fixtures. **40 of them failed that way.** The mirror
exists only so the reverted copy has a directory to import from.

## One case cannot be graded through a mirror

`case_19a2_argvless_names_the_root_it_scanned` asserts the argv-less run names `REPO_ROOT` —
the root derived from the TEST FILE's own location, which is the live checkout. A mirrored copy
correctly scans the mirror, so it fails there by construction. It is excluded BY NAME, and the
verify fails if the case ever stops existing, so the exclusion cannot rot into a silent hole.

## `test -s` is not a floor

Six blocks asserted the before-set was non-empty. Measured at T-10: the capture matched
`^(PASS|FAIL)` while `test-check-domain.py` prints its verdicts as `ok`, so a **one-line**
before-set satisfied `test -s` and the diff compared one line against one line. The capture is
now `^(ok|PASS|FAIL)` and each block carries a numeric floor under a measured count:

| Suite | Verdict lines | Floor |
| --- | --- | --- |
| `test-check-domain.py` | 201 | 190 |
| `test-bash-write-guard.py` | 99 | 90 |
| `test-check-state.py` | 145 | 135 |
| `test-branch-create-gate.py` | 8 | 8 |
| `test-gh-close-gate.py` | 48 | 44 |
| `test-inject-expertise.py` | 17 | 16 |
| `test-check-plan-routes.py` | 87 | 80 |

## Both names, one value

Every gate suite steers its fixtures with `CLAUDE_PROJECT_DIR`. `resolve_root` reads
`HARNESS_PROJECT_DIR` and no other name, so after a cutover each of those cases points the gate
at the live checkout. Each suite now has one `_env(root, **kw)` helper setting BOTH names to
the same value. Both, because the reverted copy reads `HARNESS_PROJECT_DIR` first and
`CLAUDE_PROJECT_DIR` second: the two copies must resolve the same root or the proof compares
two different trees.
