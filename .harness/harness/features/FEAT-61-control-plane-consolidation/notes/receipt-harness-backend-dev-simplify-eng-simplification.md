# SIMPLIFICATION receipt — FEAT-61-control-plane-consolidation

**Reviewed range:** `066638e8acf68b47e74637006a01c8823cff939c..c7b0558466f0767de1f1ab31bd549f49817fb613`

## Finding 1

- **File:** `.claude/skills/harness/bin/gh-sync.py`
- **Line:** 967
- **One-line summary:** `task_finished` is a one-caller pass-through to `factory_config.is_finished`.
- **Concrete maintenance/cognitive cost:** It makes readers of the station-review transition follow a separate helper and maintain a function and docstring that add no policy, validation, refusal translation, or reuse point.
- **Concrete simpler alternative:** Delete `task_finished` and call `factory_config.is_finished(...)` directly in the existing `cmd_status` list comprehension at line 1538. The existing `try`/`except FleetError` remains intact, preserving strictness, refusal handling, and observable bytes.

## Scope and method

- This was the read-only **SIMPLIFICATION** angle over the exact range above.
- Changed modules and wrappers received the deletion test. D-01 through D-11 and all 15 entries in `notes/build-divergences.md` were treated as settled.
- No validation commands or tests were run, per the read-only assignment.
- No source, test, plan, or configuration files were edited; this receipt is the sole file written.
