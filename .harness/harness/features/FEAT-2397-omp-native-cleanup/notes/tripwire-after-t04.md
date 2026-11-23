# Host tripwire after T-04 — FEAT-2397 — 2026-11-22

Condition 1 of the sign-off ruling (`notes/answers-2026-11-22-signoff.md`, AdvisorC2Signoff): right
after T-04 goes green, Main runs the repaired probe once on the live credentialled host as an
informal smoke test. If the observation fails, Main stops and returns to fable-advisor before T-05.
The formal T-06 receipt, with sanitized rows, still lands after T-05 at the final pin.

- **Launcher:** `/Users/molchairuangutai/.bun/bin/omp`. `omp --version` prints `omp/19.1.0`.
- **Tree:** worktree HEAD `29f80049bb548db83cffda61182b85c9c79050d8` (T-04 committed).
- **Command,** from the worktree: `python3 tests/manual/probe-omp-session-accessor.py`. It makes a
  live model call through the probe's pinned `--model anthropic/claude-sonnet-5`.
- **Result:** exit 0, wall time 7.0 s.

```
PASS - case1: the omp binary is on PATH
PASS - case1: the committed probe extension exists
PASS - case2: the probe produced at least one observation
PASS - case3: a nested task child session was observed, identified by its session path
PASS - case4: that child's getContextUsage returned finite tokens, contextWindow and percent
PASS - case5: a flat main session was observed
PASS - case6: the measured child and the main are distinct sessions
PASS - 7/7 checks passed
```

**Outcome: the tripwire is clear and T-05 may proceed.** A real task child's `getContextUsage()`
returns finite numbers on omp 19.1.0, identified independently of usage.
