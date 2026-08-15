# Receipt — harness-backend-dev — T-03 — c1

**Task:** T-03 — gh-sync station writes: a `start-task` subcommand, the derived parent, the loud
failure posture.

**verify: cross-check.** Dispatch carried `python3 .claude/skills/harness/bin/test-gh-sync.py`;
`plan.yaml` T-03's `verify:` is identical, byte for byte (`plan.yaml:426-427`). No mismatch.

## Files touched

- `.claude/skills/harness/bin/gh-sync.py` — `parse_tasks()` now carries `status`; new
  `load_config()` return shape `(repo, board)`; new `_feature_status()` and
  `_apply_parent_rule()` helpers; new `cmd_start_task()`; `cmd_close_task()` reordered
  (parent write before close); `main()` dispatch and usage string gained `start-task`;
  module docstring's NEVER A GATE paragraph rewritten for the three-way split.
- `.claude/skills/harness/bin/test-gh-sync.py` — three new fake-gh fixtures
  (`FAKE_GH_STATIONS`, `FAKE_GH_STATIONS_ITEM_EDIT_FAILS`, `FAKE_GH_STATIONS_CLOSE_FAILS`),
  three new fixture helpers (`write_harness_json_board`, `write_plan_yaml`, `stage_station`),
  and the six new test blocks from T-03's intent (start-task, close-task-ordering,
  Done-exemption, the loud pair, no-board-configured).

## RED — the six new tests failing against unchanged `gh-sync.py`

**Disclosure:** the first RED run (below, run A) crashed with an uncaught `StopIteration`
before the suite finished, truncating how many of the 19 new checks actually executed — the
ordering assertion used a bare `next()` with no default. That crash is itself strong RED
evidence for the one check it hit, but it left several other new checks (including the loud
pair's stderr assertion) never observed failing. Per P-13, I fixed the crash to a clean `FAIL`
(guarding the two `next()` calls with `next(..., None)` and an explicit index check) and then
**reconstructed a full RED run** against the exact pre-change file, verified by hash, per
P-09/P-13.

### Run A — first RED, crashed mid-suite (kept for the record)

Command: `python3 .claude/skills/harness/bin/test-gh-sync.py` (run immediately after the new
test blocks were appended, before any production edit to `gh-sync.py`).

```
FAIL  start-task exits 0
      gh-sync: ERROR — unknown command 'start-task'

FAIL  start-task sets T-02's OWN issue station to Building
      []
FAIL  start-task then sets the PARENT's station to Building (distinct item id)
      []
FAIL  exactly two field-sets, one per item id
      []
ok    close-task on the last task exits 0 even though the close fails (SKIP, not a gate)
FAIL  close-task sets the parent to Review
      []
ok    the sub-issue close was ATTEMPTED (and is the thing that failed)
Traceback (most recent call last):
  File ".../test-gh-sync.py", line 1106, in <module>
    logO.index(next(l for l in logO if "--id ITEM_40" in l)) <
               ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
StopIteration
```

### Run B — reconstructed full RED, hash-pinned

After guarding the ordering check, I hashed the finished `gh-sync.py`
(`sha256: d325443f2538fc64ea709948e002779120d06cb85250155a5534e974e9690d85`), overwrote it with
`git show HEAD:.claude/skills/harness/bin/gh-sync.py` (hash of that pre-change blob:
`20d7332434f348a6014c6538c80a4951e7edd49cf5141596f8fa1a4e51b253fd`), and re-ran the exact
signed `verify:` command against it.

**Prediction, made before running:** exactly seven checks redden — the four `start-task`
checks, `close-task sets the parent to Review`, the ordering check, and
`loud pair (item-edit fails): stderr carries the gh-sync: ERROR line naming issue 40`.
Everything else (the Done-exemption trio, both halves of the gh-absent loud-pair case, the
three no-board-configured checks) stays green by construction — those are absence/invariance
assertions that hold whether or not the station-write code exists, so they have no power to
redden pre-implementation; that is stated here rather than left implicit.

Observed: **exactly those seven, no more, no fewer** — confirmed by exit status and by
`grep FAIL` against the run's full output:

```
$ python3 .claude/skills/harness/bin/test-gh-sync.py
...
FAIL  start-task exits 0
FAIL  start-task sets T-02's OWN issue station to Building
FAIL  start-task then sets the PARENT's station to Building (distinct item id)
FAIL  exactly two field-sets, one per item id
FAIL  close-task sets the parent to Review
FAIL  the parent write is ORDERED BEFORE the close in the log
      ['auth status\x01', 'issue close 43 --repo implentio/fake\x01']
FAIL  loud pair (item-edit fails): stderr carries the gh-sync: ERROR line naming issue 40

7 FAILED
$ echo $?
1
```

This matched the prediction exactly (P-07). Restored the implementation with the exact text
edited earlier in this session (not a re-derivation), re-hashed —
`d325443f2538fc64ea709948e002779120d06cb85250155a5534e974e9690d85`, identical to before the
swap — and confirmed `git status --porcelain` shows only `gh-sync.py`, `test-gh-sync.py`, this
receipt, and the pre-existing (not-mine) `STATE.md` diff. Re-ran the signed `verify:` once
more: `ALL PASSED`, exit 0.

## GREEN — full run after implementation

Command: `python3 .claude/skills/harness/bin/test-gh-sync.py`

```
[... 79 prior "ok" lines, unchanged behaviour ...]
ok    start-task exits 0
ok    start-task sets T-02's OWN issue station to Building
ok    start-task then sets the PARENT's station to Building (distinct item id)
ok    exactly two field-sets, one per item id
ok    close-task on the last task exits 0 even though the close fails (SKIP, not a gate)
ok    close-task sets the parent to Review
ok    the sub-issue close was ATTEMPTED (and is the thing that failed)
ok    the parent write is ORDERED BEFORE the close in the log
ok    close-task on a Done feature exits 0
ok    close-task on a Done feature makes no item-edit call at all
ok    close-task on a Done feature still closes the sub-issue
ok    loud pair (item-edit fails): process still exits 0
ok    loud pair (item-edit fails): stderr carries the gh-sync: ERROR line naming issue 40
ok    loud pair (item-edit fails): the issue call that follows it still happened
ok    loud pair (gh absent): one SKIP line, exit 0
ok    loud pair (gh absent): no item-edit call is even attempted
ok    no board configured: open exits 0
ok    no board configured: close-task exits 0
ok    no board configured: no item-edit call is ever made

ALL PASSED
```

Exit status: `0`.

## Signed verify: command — exact invocation and result

```
$ python3 .claude/skills/harness/bin/test-gh-sync.py
...
ALL PASSED
$ echo $?
0
```

**`task_verify: pass`.**

## Other runners

`.claude/skills/harness/bin/run-unit-tests.sh --kind integration` — exit 0. Includes
`PASS test-gh-sync.py` alongside `test-check-state.py`, `test-check-plan-routes.py`, and
every other registered integration script; 106/106 checks in `test-factory-integration.py`
and no other regression.

`.claude/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0. `test-gh-board.py` and
`test-branch-create-gate.py` both PASS unchanged; `test-gh-sync.py` correctly does **not**
appear in this list — T-02's registration keeps it integration-only, and this task did not
move it (per the explicit instruction not to).

## Design notes for the reviewer

- `_apply_parent_rule` is the single helper, called from exactly `cmd_start_task` and
  `cmd_close_task` — two callers, one implementation (constraint 3 in the dispatch).
- `derive_station(plan_doc)` is called with its existing one-argument signature;
  `gh_board.py` was not touched (DEC-174 carve-out respected).
- The Done terminal exemption reads `feature.json`'s `status` directly in `gh-sync.py`
  via the new `_feature_status()` — a single-purpose reader, never compared against
  anything else.
- `close-task`'s parent write is ordered strictly before its `issue close` (`gh()` call);
  the comment at that call site states the ordering and why. Pinned by the
  `close-task on the last task ...` test using `FAKE_GH_STATIONS_CLOSE_FAILS`, which makes
  the close fail while the parent's `item-edit` still succeeds and is logged first.
- No station write is routed through `gh()`/`skip()`. Every `set_station` call is wrapped
  in `try/except gh_board.BoardError`, printed once to stderr as `gh-sync: ERROR - ...`,
  and the function returns normally so the caller continues. No retry anywhere on this path.
- `load_config()`'s new return shape `(repo, board)` — `board` is `None` for an
  unconfigured project, which prints one line and lets the rest of the invocation proceed
  unchanged (verified against the existing 18-scenario open/abandon/ship/backlog suite,
  all of which run with no `github.board` key and are unaffected).
- Minor, unspecified-by-intent asymmetry worth flagging to a reviewer rather than silently
  resolving: `start-task`/`close-task`'s `_apply_parent_rule` silently skips the parent
  write on an unparseable `plan.yaml` (treated the same as "no verdict"), while
  `parse_tasks()` (called earlier in `close-task`, for the `absorbs` lookup) `die()`s loudly
  on the same condition. In practice `close-task` never reaches the quiet path — it dies
  first — but `start-task` does not call `parse_tasks()`, so an unparseable plan there is
  genuinely quiet. INV-26 (T-04) is the invariant that would catch the resulting drift; I
  did not widen T-03's scope to add a second stderr line for a shape the intent did not name.

## Out-of-scope observation

`.harness/features/FEAT-18-board-truth/STATE.md` shows as modified in `git status` at the
time this receipt was written. I did not write to that path — it is outside my granted
files (`gh-sync.py`, `test-gh-sync.py`, this receipt) and outside anything my commands
touch. Recorded here, and in `open_questions`, rather than acted on.

## Verdict

PASS. `open_questions`: one non-blocking note about `STATE.md` drifting outside my writes
(see above) so it is not misattributed to this task. No `expertise_update` (routine, no
durable lesson beyond what Expertise P-07/P-09/P-13/P-14 already cover — this run is a clean
instance of all four, not a new pattern).
