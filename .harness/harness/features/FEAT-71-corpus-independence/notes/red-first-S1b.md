# Red-first receipt — slice S1b (handoff exemptions and state-checker literals)

Baseline pin: `4a05030d` (origin/main). Baseline clone: `git clone --no-local -q /Users/molchairuangutai/GitHub/harness /private/tmp/feat71-base-S1b && git -C /private/tmp/feat71-base-S1b checkout -q --detach 4a05030d`; the new test files were copied into it and run with `CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR` set to the clone. The clone was removed afterwards.

## tests/integration/test-check-state-handoff.py

Command: `python3 tests/integration/test-check-state-handoff.py`

Baseline (new test, 4a05030d implementation and config): **exit 1**. 31 ok, 4 FAIL, each for the historical dependency:

```
FAIL - case (g.2): INV-17 RAISES for FEAT-0190-fixture at Done with no notes: no id is exempt
FAIL - case (g.3): INV-17 RAISES for FEAT-0290-fixture at Done with no notes: no id is exempt
FAIL - case (t14-g): a plan-exempt feature still has its EXISTING note shape-checked (1 shape) while missing notes stay suppressed (0 missing) and the exemption is reported (0 reported)
FAIL - FEAT-54 no harness.json names a feature-folder path (146 found)
        .harness/harness.json: .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/handoff-build.md
        .harness/harness.json: .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/handoff-plan.md
        ...
```

- g.2/g.3: `HANDOFF_EXEMPT_LITERAL` matched by prefix (`feat.startswith(("FEAT-01", "FEAT-02"))`), so a synthetic id sharing that prefix owed nothing.
- t14-g: the same prefix skip silently swallowed the missing notes, so the plan-keyed exemption never ran and never reported.
- FEAT-54 config case: the baseline `.harness/harness.json` held 146 dead feature-note paths under `handoff_done_when_baseline`.

Worktree: **exit 0**. All 35 cases are ok, including the four above:
`ok - case (g.2) … FEAT-0190-fixture …`, `ok - case (g.3) … FEAT-0290-fixture …`, `ok - case (t14-g) … (1 shape) … (0 missing) … (1 reported)`, `ok - FEAT-54 no harness.json names a feature-folder path (0 found)`.

Converse check: the 4a05030d test file run against the worktree implementation gives **exit 1**. It fails exactly on the removed dependencies: `case (g.2): INV-17 stays quiet for the literal exemption set (FEAT-01 at Done, no notes)`, `case (t14-g): a literal-exempt feature … (2 missing)`, and `FEAT-54 baselined missing section is exempt`.

## tests/integration/test-check-state-records.py (INV-37 / T-06; BUILD_ENTRY_ERA_EXEMPT was deleted by S1a)

Command: `python3 tests/integration/test-check-state-records.py`

Changes:
- The case `T-06 INV-37 silent on an era-exempt feature` (fixture `BUG-1030-stale-anchor-write-hazard`) is replaced by `T-06 INV-37 fires for any feature id with no build_entry` on synthetic `BUG-9-x`.
- The `BUG-1030-stale-anchor-write-hazard` building-station row was removed from the recover-terminal trigger tuple.
- The fixture id `FEAT-9001-fixture-non-era` was renamed to `FEAT-9001-fixture`, because the era concept is gone.

Baseline (new test, 4a05030d): **exit 0**. All T-06 lines are ok. No red is possible here. The baseline exemption was an exact-membership set of real feature ids, so a synthetic id can never be a member, and the only fixture that could turn this red is a dead real id, which the contract forbids.

Converse check: the 4a05030d test file run against the worktree implementation gives **exit 1**:
```
FAIL - T-06 INV-37 silent on an era-exempt feature
FAIL - T-06 recovery_command_for returns recover-terminal for each trigger alone
```
Both failures come from the deleted era set alone.

Worktree: **exit 0** (32 ok), including `ok - T-06 INV-37 fires for any feature id with no build_entry`.

## Other targeted runs (worktree, exit 0)

- `tests/integration/test-check-state-plans.py`: exit 0 (50 ok). Docstring only: a dead-folder path became a bare provenance reference.
- `tests/integration/test-check-state-feat59.py`: exit 0 (114 ok). Unchanged; the `BUG-285-canonical-reader` mention at :757 is a provenance comment.
- `tests/unit/test-handoff-done-when.py`: exit 0. Unchanged; its fixtures are already synthetic (FEAT-90/91/92).
- `tests/unit/test-handoff-policy.py`: exit 0 (21 passed). Unchanged.
- `tests/integration/test-upgrade-config.py`: exit 0 (13 ok). Unchanged; upgrade-config.py never carried the key.
- `python3 -c 'import json;json.load(open(".harness/harness.json"))'`: succeeds.
- `grep -rnE "HANDOFF_EXEMPT_LITERAL|handoff_done_when_baseline|handoff_baseline" .claude tests .harness/harness.json`: no matches (exit 1).

## Files changed

- `.claude/skills/harness/bin/check_state/seams.py`: deleted `HANDOFF_EXEMPT_LITERAL` and its prefix skip. `_inv17_owed_stems(fy, status)` now owes every absent seam note uniformly. `_inv17_missing_headings(hl)` demands all five sections of every note, with no baseline lookup. Comments that pointed at dead-folder paths were rewritten as bare provenance, and the exemption comment now names only the plan-keyed exemption.
- `.claude/skills/harness/bin/check_state/ctx.py`: deleted `_load_handoff_baseline` / `ctx.handoff_baseline` and its call.
- `.claude/skills/harness/bin/check_state/plan.py`: a comment path into the dead FEAT-34 folder became a bare provenance reference. The :403 `FEAT-40` / `BUG-1071` mentions are provenance and were kept.
- `.harness/harness.json`: removed `_handoff_done_when_baseline_note` and `handoff_done_when_baseline` (146 dead paths). Nothing else was touched.
- `tests/integration/test-check-state-handoff.py`: g.2 asserts the uniform rule on synthetic prefix-sharing ids. t14-g uses the plan-keyed exemption and asserts that it is reported. The FEAT-54 cases drop the baseline-config parameter and the baselined variants, and gain a config case: no harness.json or template string names a feature-folder path. `MSD` was hoisted to module level for reuse.
- `tests/integration/test-check-state-records.py`: era-exempt INV-37 expectation → uniform violation on `BUG-9-x`; dead-id trigger row removed; fixture id renamed.
- `tests/integration/test-check-state-plans.py`: a docstring path into the dead FEAT-34 folder became a bare provenance reference.

Not changed (verified): `templates/harness.json` and `upgrade-config.py` never carried the key. `handoff_policy.py` contains only provenance prose. `check_state/feature_record.py` contains only provenance comments.
