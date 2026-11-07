# Operator rework raise - BUG-2169 - 2026-11-07

After fix c1 (`2026-11-07-3-fix-c1-validator`, FAIL: GC-01(b) open, F-1 and GC-01(a) resolved)
consumed the signed 1 round / 45 minutes, the operator selected **Raise by 1 round** in response
to: "The 1-round budget is used and GC-01(b) is still open. How should I proceed?"

Option text: "Add one round (~45 min). I make the advice test pretend to be each platform so
every branch fails before the fix on the Ubuntu image, then send it back to validation."

New ruling: 2 rounds / 90 minutes. Scope unchanged: test-only change in
`tests/unit/test-lead-start-preflight.py` (T-01), no production change.
