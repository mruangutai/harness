# FEAT-67 — red-first receipts

Written after the implementation pin `e9ed16de` (this file is not inside it). Base
`00c7219e4026081e70614647f3f98726afb2c381` = origin/main at the signed plan.

## Baseline suite receipts (before any production edit)

Captured in the feature worktree at `00c7219e` by `/tmp/feat67-baseline.py` →
`/tmp/feat67-baseline.json` (raw stdout/stderr retained; sha1 per stream). All eleven
executable owning suites exit 0:

```
  0 tests/integration/test-check-domain.py out=1733B err=0B
  0 tests/integration/test-check-domain-artifact.py out=5110B err=0B
  0 tests/integration/test-check-domain-claims.py out=2221B err=0B
  0 tests/integration/test-check-domain-grant.py out=5874B err=0B
  0 tests/integration/test-check-domain-post.py out=4458B err=0B
  0 tests/integration/test-check-domain-worktree-parity.py out=4062B err=0B
  0 tests/integration/test-check-domain-worktree.py out=4496B err=0B
  0 tests/integration/test-check-domain-approval.py out=6319B err=0B
  0 tests/integration/test-bash-write-guard.py out=12206B err=0B
  0 tests/integration/test-check-omp-port.py out=1304B err=0B
  0 tests/integration/test-validate-digest.py out=23815B err=0B
```

`tests/unit/test-code-grade.py` is the twelfth named suite: it is the bar-4 lock, not a
byte-compared boundary, and it passes at the base and at the pin (at the pin only after the
stale `parse_digest: 1` self-grading exemption was removed, D-05 — the same failure FEAT-66
MF-04 recorded).

## SC-01 red: the plan's inline grade assertion at the base

Run in the feature worktree at `00c7219e` before any production edit (the verify block's
`python3 -c` extracted verbatim to `/tmp/feat67-grade-assert.py`):

```
FEAT-67 grades [('.claude/skills/harness/bin/check-domain.py', 'approval_guard', 1), ('.claude/skills/harness/bin/check-omp-port.py', 'check', 1), ('.claude/skills/harness/bin/validate-digest.py', 'parse_digest', 1)]
exit=1
```

The same assertion re-run in a clean detached checkout of the base is reproduced in
`notes/clean-pin-byte-receipts.md` beside the green run at the pin.

## SC-02 fail-first

Byte identity has no pre-fix red form; the baseline-versus-pin comparison above and in the
clean-pin receipt is this criterion's fail-first equivalent (operator ruling 2026-09-26,
FEAT-66 validate c0 MF-05; BRIEF SC-02).
