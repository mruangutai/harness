# Receipt — T-05 — harness-backend-dev — c1

**BLUF: GREEN. `board-station.py` and its seven-case suite exist, `test-board-station.py` is
registered in `UNIT_SCRIPTS`, and the plan's verbatim `verify:` clause for T-05 prints
`T-05 GREEN`.**

## Red run — verbatim, extracted programmatically, before anything was written

Invocation:
```
python3 -c "
import yaml
p=yaml.safe_load(open('.harness/harness/features/FEAT-23-ship-flow-fixes/plan.yaml'))
print([t for t in p['tasks'] if t['id']=='T-05'][0]['verify'])" | bash
```
Output:
```
T-05: .claude/skills/harness/bin/board-station.py does not exist
```
Exit code: **1**. Matches the receipted red at `b7ae135` and the dispatch's expected line
exactly.

## Iron Law discipline — a self-caught lapse, disclosed

I wrote `board-station.py` before the test file existed (a lapse — RED was not watched first).
Caught before any GREEN run: recorded `sha256sum` of the file
(`fc74f8372db73b760bf7edd8f5934cd66e705262b39300e8f817abc9f67f5413`), moved it out of the tree to
the scratchpad, wrote `test-board-station.py` and registered it in `UNIT_SCRIPTS`, ran the suite
and watched all 8 checks FAIL for the correct reason (`can't open file
'.../board-station.py'`), then restored the file from the scratchpad copy and re-verified the
hash matched before running GREEN. RED was genuinely observed, not skipped — see the FAIL output
below.

RED suite output (`python3 .claude/skills/harness/bin/test-board-station.py`), abbreviated to the
label lines:
```
FAIL  board-station moves the named issue to the named station — rc=2 stdout='' stderr="...can't open file '.../board-station.py'..."
FAIL  the field-set invocation actually carries the issue number and the station — []
FAIL  board-station with no board configured writes nothing and exits 0 — rc=2 stdout='' log=[]
FAIL  board-station reports a BoardError on stderr naming issue and station and exits 0 — rc=2 ...
FAIL  board-station rejects a missing argument with exit 2 — rc1=2 rc2=2 rc3=2 ...
FAIL  board-station outside a harness root writes nothing and exits 0 — rc=2 stdout='' log=[]
FAIL  board-station with github.sync false writes nothing and exits 0 — rc=2 stdout='' log=[]
FAIL  board-station exits 0 when set_station raises a non-BoardError exception — rc=2 ...
8 FAIL
```
Exit code: **1**.

## Green run — verbatim

`python3 .claude/skills/harness/bin/test-board-station.py`:
```
PASS  board-station moves the named issue to the named station
PASS  the field-set invocation actually carries the issue number and the station
PASS  board-station with no board configured writes nothing and exits 0
PASS  board-station reports a BoardError on stderr naming issue and station and exits 0
PASS  board-station rejects a missing argument with exit 2
PASS  board-station outside a harness root writes nothing and exits 0
PASS  board-station with github.sync false writes nothing and exits 0
PASS  board-station exits 0 when set_station raises a non-BoardError exception

all pass
```
Exit code: **0**.

`bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit` (and separately `--kind all`):
exit **0**, `PASS test-board-station.py` present in both runs.

## Task's `verify:` — full clause, re-run after the work — verbatim final line

```
T-05 GREEN
```
Exit code: **0**.

## The four traps

1. **Variable-first `harness.json` read** (`board-station.py`), mirroring `gh-sync.py:122-123`:
   ```
   harness_json_path = os.path.join(root, ".harness", "harness.json")
   if not os.path.isfile(harness_json_path):
   ```
   Confirmed it does not trip `test-check-plan-routes.py`'s `case_20`: ran
   `test-check-plan-routes.py` standalone (it is in `INTEGRATION_SCRIPTS`, outside this task's
   own `--kind unit` conjunct) and it prints `PASS case_20_board_station_py_probes_the_manifest`
   — the file's ONE visible probe is the root-probe walk (which legitimately names
   `team-config.yaml` on the same logical line, same as `gh-sync.py`'s own walk); the
   `harness.json` variable-first read is invisible to the scan by construction, as intended.

2. **Every one of the seven cases sets both `FACTORY_GH` and `GH_SYNC_GH`** — one `run()` helper
   in `test-board-station.py` installs the fake and sets both env vars identically for every
   invocation; no case path skips it.

3. **The non-BoardError case** (`FAKE_GH_NON_JSON`): the fake answers the
   `projectItems(first: 100)` GraphQL call with an exit-0 body that is plain text, not JSON.
   `factory_gh.run_gh(json_out=True)` calls `json.loads` unguarded on that response inside
   `gh_board.issue_board_item_id`, raising a bare `ValueError` — never caught by
   `gh_board.set_station`'s `except factory_gh.GhError` — so it reaches `board-station.py`'s
   broad `except Exception` exactly as item 6 requires. Asserted: exit 0, stderr begins
   `board-station: ERROR - `, and both the issue number and station appear in it.

4. **`UNIT_SCRIPTS` registration**: `"test-board-station.py"` appended to the array in
   `.claude/skills/harness/bin/run-unit-tests.sh` (one-line edit, no other array touched).
   `INTEGRATION_SCRIPTS` untouched. `.harness/harness.json` untouched.

## Case 1 assertion strength

The first case (`board-station moves the named issue to the named station`) is followed by a
second, dedicated assertion (`the field-set invocation actually carries the issue number and the
station`) that greps the fake's call log for the `project item-edit` invocation and checks it
carries `OPT_PLAN` (the option id `set_station` resolved for `"Plan"`) and `ITEM_326` (the item id
resolved for issue 326) — not merely `r.returncode == 0`. A tool that wrote nothing at all would
fail this second check even if it happened to exit 0.

## Files touched

- `.claude/skills/harness/bin/board-station.py` (new)
- `.claude/skills/harness/bin/test-board-station.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (one-line `UNIT_SCRIPTS` edit)

## Bounds respected

No commit, no `git add`, no `gh` writes. `check-domain.sh`, `bash-write-guard.sh`,
`validate-digest.py`, `check-state.sh` untouched. `plan.yaml`, `BRIEF.md`, `feature.json`,
`STATE.md`, `.harness/harness.json` untouched. `gh-sync.py`, `test-gh-sync.py`, `gh_board.py`
untouched (called, not edited). Arch finding G's duplication (this file re-derives
`load_config`'s github-block precondition policy rather than importing it) is left as the signed
residual per the dispatch — not moved into `gh_board.py`.

## Open questions

None.
