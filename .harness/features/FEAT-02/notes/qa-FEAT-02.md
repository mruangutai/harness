# QA Gate — FEAT-02 (VALIDATION, cycle 1)

**BLUF: PASS.** Matrix floor met, full suite green (exit 0), pre-fix proof holds with
exactly the T-01 defect cases failing. Minor advisory coverage gaps, none blocking.

- review_sha: d9b16e5323526d6f02228b48652ded84328a40cb (== worktree HEAD; both files clean)
- Diff scope confirmed: exactly `test-validate-digest.py` (+113) and `validate-digest.py` (+10)

## Matrix gate (change_type: bugfix → unit + bug-class match)

- **unit: satisfied.** `test_kinds.unit.cmd = .claude/skills/harness/bin/test-validate-digest.py`;
  4 named new tests exercise this change.
- **bug-class match: satisfied.** Bug class = first-match anchor shadowing by an echoed
  contract template. New cases hit all three shadowed anchors (verdict token, digest
  fields via `matrix_ok`, lead roll-up via members) plus hook mode.
- **Test-first: satisfied.** Test commit 6546b1d (21:12) precedes fix commit d9b16e5
  (21:13); T-01 evidence records the red run, and I reproduced it (below).

## Runs (2026-07-27)

1. `.claude/skills/harness/bin/test-validate-digest.py` → **exit 0**, "ALL PASSED":
   28/28 CLI + 10/10 hook + 2/2 template = 40 cases = 36 pre-existing + 4 new. **SC-02 met.**
2. Pre-fix proof (D-02): verified `/tmp/validate-digest-prefix.py` byte-identical to
   `git show 6546b1d^:.claude/skills/harness/bin/validate-digest.py` (diff -q), then
   `VALIDATE_DIGEST_BIN=/tmp/validate-digest-prefix.py .claude/skills/harness/bin/test-validate-digest.py`
   → **exit 1, exactly 3 failures**:
   - "echo shadow: missing matrix_ok in the real block is not masked by the echo" (got PASS, wanted matrix_ok)
   - "echo shadow: lead roll-up must read the real members, not the echo" (got PASS, wanted worst)
   - "[hook] echo shadow [hook]: missing matrix_ok behind an echo is exit 2" (got exit 0)
   Case (1) "valid real FAIL after a template echo still validates" is green pre-fix
   by design (PLAN T-01: it pins post-fix routing). No pre-existing case affected. **SC-01 met.**

## SC evidence (for pm goal-check)

- SC-01 → test-validate-digest.py cases at ~:788, :810, :816, :840 (the four "echo shadow" cases)
  plus the pre-fix run above.
- SC-02 → full-suite run, exit 0, 36 pre-existing cases green.

## Coverage gaps (advisory, non-blocking)

- No case asserts the real `artifact:` path is the one read when the echo carries a
  different one (covered structurally by the slice, not by a direct assertion).
- Untested echo variants: echo-only message (D-01 records this as undecidable —
  content, not format), real return above trailing `VERDICT:` prose (contract mandates
  return last; D-01 tradeoff), real verdict BLOCKED/ESCALATE behind an echo.

## Phase-1 delta

All six Phase-1 expected coverages present. The advisory variants above were my
Phase-1 "expected-but-unlisted" list; none warrants blocking a bugfix-scoped change.
