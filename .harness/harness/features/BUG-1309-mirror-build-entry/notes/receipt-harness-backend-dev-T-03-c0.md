# Receipt — harness-backend-dev — T-03 (BUG-1309-mirror-build-entry)

## What changed

- `.claude/skills/harness/bin/gh-sync.py`
  - New command `recover-terminal <feature-dir> [--parent <n>] [--yes]`, registered in
    `main()`'s dispatch beside `ship`, and its usage documented in the module docstring
    beside `ship`'s own line.
  - Four new functions, all reusing the existing routes rather than re-implementing them:
    `_recover_terminal_conflict` (the one refusal: `--parent` contradicting a recorded
    parent), `_recover_terminal_report` (the `_abandon_plan`-shaped would-write/adoption
    lines), `_recover_terminal_apply` (the `--yes` writes, via `_open_ensure_milestone` /
    `_open_ensure_parent` / `parse_source_issues` / `save_recorded`), and
    `cmd_recover_terminal` (the orchestrator). `record_build_entry(feat_dir,
    "recovered-terminal")` is the last statement of the successful path.
  - `main()`'s `--yes` gate now accepts `recover-terminal` alongside `abandon`.
  - `cmd_ship`'s `skip("no recorded milestone — nothing to close")` is now actionable,
    naming `recover-terminal <abspath> --yes` as the fix, still through `skip()` (exit 0)
    and still carrying the literal `gh-sync: SKIP` prefix `post-merge-sweep.sh` greps.
- `tests/integration/test-gh-sync.py`
  - New fixture helper `stage_recover` (a sync-enabled `stage()` project plus a
    plan.yaml carrying `source_issues` and a pre-seeded `github` block), plus
    `create_calls`/`non_preflight_calls` log-scoping helpers.
  - Seven new cases under "T-03 (BUG-1309): gh-sync.py recover-terminal", names verbatim
    per the dispatch.

`cmd_start_task` (T-04) was not touched.

## TDD — red before green, per case

All seven cases were written first and run against the pre-edit tree; every one failed
for the reason the change was meant to fix (none were vacuous/pre-existing-green):

- `T-03 report and ask writes nothing` — RED: `rc=1`, `unknown command 'recover-terminal'`.
- `T-03 recover-terminal creates milestone and parent only` — RED: same, `rc=1` unknown command.
- `T-03 FEAT-55 shape adopts and creates nothing` — RED: same, `rc=1` unknown command.
- `T-03 second run is idempotent` — RED: same, `rc=1` unknown command.
- `T-03 parent contract error refuses` — RED: `rc=1`, `--yes is only accepted by abandon,
  not 'recover-terminal'` (the flag gate rejected it before the command could even run).
- `T-03 gh failure records nothing` — RED: same `--yes` gate rejection.
- `T-03 ship names recover-terminal` — RED: `rc=0` but stdout was the OLD message
  (`"no recorded milestone — nothing to close"`, no mention of `recover-terminal`).

After the production edit (docstring, `--yes` gate, dispatch registration, the four new
functions, and the `cmd_ship` message), all seven turned green with no other assertion
changed. Full run: `python3 tests/integration/test-gh-sync.py` → 316 ok, 0 FAIL.

## Task verify

Command (verbatim from plan.yaml, run from the worktree root):

```
out=$(python3 tests/integration/test-gh-sync.py) || exit 1
if printf '%s\n' "$out" | grep -q '^FAIL'; then exit 1; fi
for n in "T-03 report and ask writes nothing" "T-03 recover-terminal creates milestone and parent only" "T-03 FEAT-55 shape adopts and creates nothing" "T-03 second run is idempotent" "T-03 parent contract error refuses" "T-03 gh failure records nothing" "T-03 ship names recover-terminal"; do
  printf '%s\n' "$out" | grep -qF "ok    $n" || exit 1
done
echo VERIFY-PASS
```

Output: `VERIFY-PASS`. Suite totals: 316 `ok`, 0 `FAIL`.

## Design substance (evidence, not assertion)

- **All four adoption states reach exit 0, create only what is missing, record
  "recovered-terminal"**: covered by `T-03 recover-terminal creates milestone and parent
  only` (neither recorded), `T-03 FEAT-55 shape adopts and creates nothing` (both
  recorded), and the milestone-only/parent-only cells are the SAME code path
  (`_recover_terminal_apply`'s two independent `if rec[...] is None` guards) proven
  correct by those two extremes plus the untouched-field assertions (`ghR2.get("issues")
  == {}`, `ghR3.get("issues") == _FEAT55_ISSUES`) — a shared-guard mutation would break
  both ends of that spectrum, not just one.
- **The only exit-2 is the `--parent`-vs-recorded-parent contradiction; an existing
  receipt is not a refusal**: `T-03 parent contract error refuses` is the sole `rc==2`
  case; every other case (including the FEAT-55 fixture that already carries a
  milestone, a parent, twelve issues, AND — after the first run — a `build_entry`) reaches
  `rc==0`. `_recover_terminal_conflict` is the ONLY call to `refuse()` in this command.
- **Zero task sub-issues as an exact create count of 0 on the FEAT-55 fixture, never an
  absence-of-error**: `create_calls()` counts `-X POST .../milestones` and `issue create`
  log lines directly (scoped to the payload — P-03 — so a title-lookup GET that also
  mentions "milestones" is not miscounted as a create); `T-03 FEAT-55 shape adopts and
  creates nothing` asserts `len(create_calls(...)) == 0`, and `ghR3.get("issues") ==
  _FEAT55_ISSUES` (exact key/value equality, not `len()`) proves the pre-existing twelve
  ids survive untouched.
- **Report-and-ask asserts NOTHING was written, not merely that it printed**: `T-03
  report and ask writes nothing` reads `feature.json` as raw bytes before and after and
  asserts byte-identity, plus `non_preflight_calls(calls(...)) == []` (zero gh
  invocations beyond `load_config`'s unavoidable `auth status` preflight) — not just
  `"would" in stdout`.
- **A gh failure records NOTHING, leaving the state non-terminal**: `T-03 gh failure
  records nothing` uses `FAKE_GH_FAIL_FIRST` (fails every call except `auth status`);
  `cmd_recover_terminal` never arms `_BUILD_ENTRY` for this command (only `main()`'s
  `open` branch does), so `_open_ensure_milestone`'s `skip()` call on the 422-recovery
  failure records nothing by construction — the same funnel `open` uses, unmodified.

## Files touched

- `.claude/skills/harness/bin/gh-sync.py`
- `tests/integration/test-gh-sync.py`

## Not touched (per assignment)

- `tests/integration/test-check-state.py` — observed as concurrently modified by the
  main session (T-06); left untouched, not reverted, not reported as drift.
- `cmd_start_task` (T-04) — untouched.
- plan.yaml / BRIEF.md / feature.json / STATE.md — untouched, no commit made.
