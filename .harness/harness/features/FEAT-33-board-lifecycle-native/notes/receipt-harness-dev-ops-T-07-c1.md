# Receipt — harness-dev-ops — T-07 — c1

**T-07 done.** `cmd_start_task` in `gh-sync.py` now refuses to drive a CLOSED card, or one
already at the board's `done` station, backwards to `building` — and the station literal is
de-hardcoded to `board["stations"]["building"]`.

## The guard

Sits inside `if board is not None:`, immediately before the existing `set_station`/
`_apply_parent_rule` call it now gates (`.claude/skills/harness/bin/gh-sync.py`, `cmd_start_task`):

```python
stations = gh_board.board_stations(board, repo)          # ONE board read, reused for both halves
current_station, _ = gh_board.read_station(stations, issue_num)
state = (factory_gh.issue_view(repo, issue_num, ["state"]) or {}).get("state")
if state == "CLOSED" or current_station == board["stations"]["done"]:
    print(one refusal line naming #issue, tid, current_station, reason)
    return   # before set_station, before _apply_parent_rule
```

Condition: **refuse when EITHER `state == "CLOSED"` OR `current_station == board["stations"]["done"]`.**
Both reads are wrapped in one `try`; `factory_gh.GhError` (either read) is caught, printed as one
`gh-sync: ERROR -` line, and control falls through to the original write — never a gate.

## Regression case (verbatim from the plan) + RED proof

> Replay #642's exact shape first and assert it goes RED against the pre-change code: issue
> closed, card at Done, start-task invoked — assert no station write argv reaches the fake and
> the refusal line is printed.

Added as `#642 replay` in `test-gh-sync.py` (`tmpN2`, issue #326/T-02, `GUARD_STATE=CLOSED`,
`GUARD_STATION_NAME=Done`). Asserts: exit 0, zero `item-edit` calls of any kind reach the fake,
and stdout carries `gh-sync: refusing #326` naming T-02 and `Done`.

**RED proof, run separately against the pre-fix code** (checked out from `HEAD` at `215a1fd`,
before this task's edit — a byte-diff confirmed `gh-sync.py:772` there is still the literal
`gh_board.set_station(board, repo, issue_num, "Building")` with no guard): replaying the exact
same fixture (closed issue #326, card at Done) against that binary produced

```
returncode: 0
stdout: gh-sync: issue #326 (T-02) -> Building
        gh-sync: parent #40 -> Building
item-edit calls: ['project item-edit --id ITEM_326 ... --single-select-option-id OPT_BUILDING',
                  'project item-edit --id ITEM_40 ... --single-select-option-id OPT_BUILDING']
ASSERTION 'no station write of any kind reaches the fake': FAIL (RED)
ASSERTION 'refusal line printed': FAIL (RED)
```

i.e. the pre-fix code drove BOTH the closed/Done sub-issue and its parent to Building — reproducing
#642/#643 exactly. The probe script and its throwaway `bin-old/` copy were deleted immediately
after (scratchpad only, never committed; `git status` afterward shows only my two files touched).

## Every other case added, with its red proof

All five live in `test-gh-sync.py` right after the existing start-task block (`tmpN2`–`tmpN7`).
Each is a **presence** assertion on `item-edit` argv content or a refusal/print line — never an
absence-only check that could pass vacuously — and each was proved red by ACTUALLY mutating
`gh-sync.py` on disk, re-running `test-gh-sync.py`, confirming the specific check(s) failed, then
byte-diffing the file back against my fix (`IDENTICAL` every time) before moving on:

1. **Open issue at Backlog → still writes Building** (`tmpN3`, `GUARD_STATE=OPEN`,
   `GUARD_STATION_NAME=Backlog`, asserts both the sub-issue's and the parent's `item-edit` land
   with `OPT_BUILDING`). Mutant: the guard condition replaced with `if True:` (always refuse).
   Result: `FAIL open at Backlog: still writes the sub-issue's station to Building` /
   `FAIL open at Backlog: still writes the parent's station too` (2 of 18 checks reddened, the
   rest — including the refusal cases, which an always-refuse guard still satisfies — stayed ok).
2. **Open issue, card already Done → refused** (`tmpN4`). Mutant: condition narrowed to
   `if state == "CLOSED":` (drops the station half of the OR). Result:
   `FAIL open but card at Done: refused, no station write reaches the fake` /
   `FAIL open but card at Done: refusal line printed`.
3. **Closed issue, card at Building (not yet Done) → still refused** (`tmpN5`). Mutant: condition
   narrowed to `if current_station == board["stations"]["done"]:` (drops the state half). Result:
   `FAIL closed but card at Building: refused, no station write reaches the fake` /
   `FAIL closed but card at Building: refusal line printed`.
4. **Board/issue read raises → falls through, still writes Building** (`tmpN6`, dedicated fake
   `FAKE_GH_STATIONS_GUARD_READ_FAILS` whose `items(first: 100, after:` case exits 1, asserting
   BOTH item-edits still land AND one `gh-sync: ERROR` line naming #326 prints). Mutant: `except
   factory_gh.GhError` changed to `except ValueError` (wrong exception type — the real
   `GhError` now propagates uncaught). Result: all four checks in this case reddened, including
   the exit-0 check — an uncaught exception crashes the whole invocation non-zero, which is
   exactly the "guard must not gate" property this case exists to pin.
5. **De-hardcoding** (`tmpN7`, dedicated fake `FAKE_GH_STATIONS_CUSTOM` whose field options are
   named Todo/Planned/Queued/Doing/Checking/Shipped, `stations=CUSTOM_STATIONS` with
   `building: "Doing"`, asserting the `item-edit` selects `OPT_DOING`, that no call contains
   `OPT_BUILDING` at all, and stdout contains `-> Doing`/never `-> Building`). Mutant run
   specifically for this case: the write call reverted to the literal
   `gh_board.set_station(board, repo, issue_num, "Building")`. Result:
   `FAIL custom stations: sets the sub-issue's station to the DECLARED building option (OPT_DOING),
   not the hardcoded literal OPT_BUILDING`. Mechanism, confirmed by a standalone repro against
   this exact fixture: that board's field offers no option named "Building" at all, so
   `gh_board.set_station` raises `BoardError` ("project field option not found: Building") before
   any `item-edit` for the sub-issue is attempted — caught by `cmd_start_task`'s own
   `except gh_board.BoardError`, printed to STDERR (`gh-sync: ERROR - implentio/fake#326 ->
   Building: project field option not found: Building`), and the child's own success `print` line
   is skipped entirely (only the parent's `-> Doing` line survives, from `_apply_parent_rule`,
   whose station comes from `derive_station`/board-declared values and was never mutated). The
   "prints declared name" sub-check stayed green under this mutant for that reason — the print it
   guards never executes on the reddened path — so the item-edit-content assertion is what
   actually discriminates this case, not the print assertion; noted here rather than left
   implied.

The existing `FAKE_GH_STATIONS` fixture (shared with the pre-existing start-task test) was
extended with the two new query shapes the guard's reads need (`items(first: 100, after:` for
`gh_board.board_stations`, `issue view` for `factory_gh.issue_view`), defaulted via
`GUARD_STATE=OPEN`/no station when the env vars are unset — so the untouched pre-existing
start-task test (`tmpN`, no `GUARD_*` vars set) exercises the guard's happy path unchanged and
still passes with its original assertions.

## Verify

Task's exact `verify:` (`plan.yaml` T-07):
```
.claude/skills/harness/bin/run-unit-tests.sh --kind all
```
Ran it TWICE. First run (before the mutation-testing pass below): exit 0, tail ends
`PASS test-dispatch-guard.py` / `[exited with code 0]`. Second run, AFTER restoring the file to
byte-identical following every mutant above (confirmed via `diff` = identical each time, and a
final `git status`/`git diff --stat` showing only `gh-sync.py` and `test-gh-sync.py` touched):
completed with exit code 0 (confirmed by the background task's own completion summary), full log
2667 lines, `grep -c '^FAIL'` = 0, and `test-gh-sync.py` reports `PASS`. Independently also ran
`python3 .claude/skills/harness/bin/test-gh-sync.py` directly, standalone, after the final
restore: `ALL PASSED` — every existing check plus all thirteen new T-07 checks reported `ok`.

## Scope discipline

Only `.claude/skills/harness/bin/gh-sync.py` and `.claude/skills/harness/bin/test-gh-sync.py`
touched (`git diff --stat`: 46 / 276 lines respectively). Confirmed via `git diff --stat` that
`board_lifecycle.py`, `test-board-lifecycle.py`, `test-factory-integration.py` and
`run-unit-tests.sh` (T-04's files) carry no diff from my work, and `DECISIONS.md`/
`DECISIONS-INDEX.md`/`plan.yaml` changes present in `git status` are T-09's/the orchestrator's,
not mine — untouched by this task. No `## Approval` or `approval.status` edited. Nothing
committed.

## Note on change_type / digest enum

Plan.yaml marks T-07 `change_type: bugfix`. `validate-digest.py:158` gives `dev-ops` the enum
`{config, scaffolding, infra, ci}` — no `bugfix` member. Per the dispatch's own instruction this
is issue #778 (already filed): reporting the rejection rather than silently reclassifying.
`DIGEST.change_type` below is substituted to `infra` (closest of the four to "fixing a script's
own control flow"; not a claim that `bugfix` and `infra` mean the same thing).
