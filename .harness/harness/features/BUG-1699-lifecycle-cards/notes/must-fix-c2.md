# Must-fix routing — BUG-1699-lifecycle-cards — c2

Raised by the operator-required fresh goalcheck at pinned `d7310f865e03534c233085e5f0a768eb9eca4687`: `notes/research-BUG-1699-lifecycle-cards-goalcheck-validate-c1.md`.

## Owning dev: harness-backend-dev — T-01

1. **GC-01 · substance · high · SC-11.** In `tests/unit/test-gh-board.py`, the active/terminal projection assertions at lines 430–471 execute after the runner's sole `FAILURES` exit block at lines 408–412. A broken assertion can print `FAIL` while the process exits 0, so the focused unit command and signed T-01 gate cannot prove SC-11.

Write a failing regression first that demonstrates a deliberately false late assertion yields non-zero. Repair the runner so every assertion is accounted before final exit, preserving existing test coverage and output conventions. Run `python3 tests/unit/test-gh-board.py`, the exact signed T-01 gate, and the configured unit/integration matrix. Commit only the T-01-owned test change plus fix receipt; do not touch product code or feature bookkeeping.

After the fix, qa, code, security, and ui must reverify the exact tip. QA must prove the late-assertion negative control fails before the fix, the final unit runner exits non-zero on assertion failure and 0 when green, both configured matrix kinds pass, and the signed T-01 gate passes. Code must check the runner repair for fail-open/silent paths and regressions. Security/UI self-scope. No goalcheck runs inside fix.yaml; a final canonical three-perspective goalcheck follows only if this fix team passes.
