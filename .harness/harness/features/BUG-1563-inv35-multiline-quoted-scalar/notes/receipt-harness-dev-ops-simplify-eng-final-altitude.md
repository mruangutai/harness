# Altitude assessment — BUG-1563 INV-35

**Conclusion: leave.** Zero actionable altitude findings.

The quote-state is owned at the raw-source INV-35 scanner's authoritative seam in `.claude/skills/harness/bin/check-state.sh:148-279`: parsing has already discarded the data this invariant protects, while the per-plan physical-line loop holds exactly the state required to bridge continuation lines. Moving that state outward or into either test would split one rule across drift-prone homes; a helper extraction would not deepen the module or reduce its interface.

Both coverage layers exercise the checker process interface callers use, rather than duplicating the scanner: integration fixtures call the shared `run()` wrapper (`tests/integration/test-check-state-plans.py:792-833`, `tests/integration/check_state_support.py:96-99`), and the focused unit test invokes the real checker against isolated roots (`tests/unit/test-check-state-inv35.py:35-55`). The intentionally overlapping three outcomes therefore close distinct test-kind surfaces without introducing an alternate authority.

Inspected:
- `.claude/skills/harness/bin/check-state.sh:148-279`
- `tests/integration/test-check-state-plans.py:729-834, 973-1028`
- `tests/unit/test-check-state-inv35.py:1-98`
- Direct helper: `tests/integration/check_state_support.py:21-99`

No product, test, or helper files were mutated. No validation commands were run.
