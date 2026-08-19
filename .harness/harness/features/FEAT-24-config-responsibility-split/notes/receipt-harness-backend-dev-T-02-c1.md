# Receipt — harness-backend-dev — FEAT-24 T-02, cycle 1 (TESTS AND FIXTURES ONLY)

## Scope actually touched

- `.claude/skills/harness/bin/test-factory-config.py` — rewritten in full. All 26 new ok-line
  texts from the intent are present, verbatim.
- This receipt.
- `factory_config.py` was **not opened for writing** in this spawn (only read, to establish the
  RED baseline and confirm the migration surface). Confirmed clean by an actually-run command:

```
$ git status --short .claude/skills/harness/bin/factory_config.py; echo "status_rc=$?"
status_rc=0
```
(no output before the echo — the file is untouched)

## Verify block cross-check

Diffed the dispatch's verbatim `verify:` block against `plan.yaml`'s T-02 `verify:` block
byte-for-byte (via a small extraction script + `diff`): **IDENTICAL**. No mismatch to report.

## RED-FIRST EVIDENCE (expected red — not this spawn's verdict)

Command:
```
python3 .claude/skills/harness/bin/test-factory-config.py 2>&1; echo "RC=$?"
```
Literal output:
```
Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/test-factory-config.py", line 120, in <module>
    fleet = fc.load_fleet(path)
  File "/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/factory_config.py", line 152, in load_fleet
    raise FleetError(
    ...<3 lines>...
    )
factory_config.FleetError: fleet key invalid: repos[mruangutai/harness].board — give mruangutai/harness its own board: {...} block with owner, number, station_field and stations in /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpbmauagzl/fleet.yaml
RC=1
```
(Re-run after the advisor-driven fixes below — same line number, same shape: the earliest
`good_fleet_dict()`/`load_fleet()` pairing in the file is still line 120, unaffected by edits made
further down.)

**Why it looks like this, not like a per-case FAIL list**: the very first fixture load in the
file (`good_fleet_dict()`, line ~120, boardless per migration) hits the OLD `load_fleet`, which
still requires `repos[].board` at HEAD (`factory_config.py:151-156`) — so the whole module dies on
an uncaught `FleetError` before a single `check()` call ever runs, let alone the module-scope
`fc.clear_product_config_memo()` reference the FIXTURE TRAP / MEMO TRAP would additionally break
on. This is reason 2 from the dispatch ("migrated fixtures... fail the OLD loader"), observed
before reason 1 (`clear_product_config_memo` AttributeError) even gets a chance to fire, because
Python never reaches `check()`'s body. Both are correct and expected; I did not un-migrate the
fixture to make it print a nicer trace.

Compensating evidence — the three new symbols do not exist yet at HEAD:
```
$ grep -nE 'def (validate_board|product_config|clear_product_config_memo)' .claude/skills/harness/bin/factory_config.py
(empty — no output, RC=1)
```

## Corrections made after an advisor review, before returning

Three defects were caught and fixed before this receipt was finalized — all in the assertion
shape, none in the ledger dispositions:

1. **The five `accepts` cases compared a value to itself.** `validate_board` mutates its board
   argument in place and returns it (item 2c), so `_result["stations"][key] == _board["stations"][key]`
   was `x == x` — it could not redden for any non-raising implementation, including one that
   dropped a key from `_STATION_KEYS`. Fixed with an independent oracle, `_EXPECTED_STATIONS`,
   giving each of the five keys a distinctive value (`Col-BK`/`Col-RD`/`Col-BL`/`Col-RV`/`Col-DN`)
   so a reverted key set reddens exactly the cases naming the dropped key(s), not all five at
   once on an unguarded raise. Also wrapped the call in `try/except` so a raising implementation
   in spawn 2 produces five honest FAIL lines instead of killing the module mid-run (which would
   otherwise misreport as `(16) repo_entry finds the listed repo` "vanishing").
2. **The memo "failing read is not cached" assertion was defeated by its own guard.** The
   original sequence had a `check()` call between the raising-stub assertion and the
   working-stub assertion; `check()`'s unconditional `clear_product_config_memo()` would wipe
   any wrongly-cached failure before the recovery call ran, so the second assertion passed
   regardless of whether `product_config` actually caches failures. Fixed by collapsing both
   halves into one `check()` call with no intervening call, per the MEMO TRAP's own stated
   constraint (all memo-sensitive calls before the evaluating `check()`).
3. **P-01 and a next_step completeness gap.** The remote-failure case asserted `"main" in str(exc)`
   — a 4-character token that could be satisfied by unrelated `next_step` prose rather than by
   the ref actually being echoed. Fixed by giving that one fixture a distinctive
   `default_branch: "trunk-xyzzy"` and asserting on that instead. Separately, the
   `load_fleet rejects a repos entry carrying a board key` case now also asserts
   `.harness/harness.json` is present in the message, matching item 3's requirement that the
   next_step names the new home, not just the old key.

Also fixed the digit-string coercion case (`(6)/(28b)`) to wrap its `validate_board` call in
`try/except`, for the same "honest per-case FAIL instead of module death" reason as fix 1.

## Mechanical ok-line confirmation (26 new + the pinned `(16)`)

Because the suite dies at line 120 before any `check()` ever prints, nothing that RUNS the file
proves the ok-line texts match the verify's `has "..."` arguments. Confirmed statically instead,
via `ast.parse` over the test file (not by running it, and not by trusting my own reading):
walked every `check(...)` call's first argument, `ast.literal_eval`'d it (this correctly folds
Python's adjacent-string-literal concatenation, e.g. the memoisation line split across two source
lines — a plain `grep -F` on the full string would find nothing there, which is not a defect),
separately confirmed `FIVE_STATIONS == ("backlog", "ready", "building", "review", "done")` and the
eight literal first-arguments to `board_for_raise_case` calls in source order. Result: all 27
required strings (26 new ok-lines + the pinned pre-existing `(16) repo_entry finds the listed
repo`) are present, character-for-character, none missing.

## Case ledger — every pre-existing case, its disposition

| Pre-existing case | Disposition | Destination (if relocated) |
|---|---|---|
| (1) load_fleet round-trips board.owner | removed | `board_for resolves through product_config` (asserts `b1["owner"]=="mruangutai"` against a remote stub) |
| (1) load_fleet round-trips repos[0].name | kept unchanged | — |
| (1) load_fleet round-trips workspace_root | kept unchanged | — |
| (2) schema is not factory-fleet/1 | kept unchanged | — |
| (2b) workspace_root is a filesystem root | kept unchanged | — |
| (3) a repos entry has no board | inverted | now `(3) a repos entry has no board — this is the correct shape now` (positive case) |
| (4) repos[].board is not a mapping | removed, coverage relocated | `board_for raises naming the file and the key: board is not a mapping` |
| (5) repos[].board.owner is empty | removed, coverage relocated | `board_for raises naming the file and the key: owner missing` |
| (6) repos[].board.number is not an int | removed, coverage relocated (digit-string driver no longer invalid) | `board_for raises naming the file and the key: number not an int` (now driven by a float, 2.5) — plus a NEW positive case `(6)/(28b) validate_board coerces a digit string number to an int` for the now-accepted "3" |
| (7) repos[].board.station_field is empty | removed, coverage relocated | `board_for raises naming the file and the key: station_field missing` |
| (8) repos[].board.stations does not carry exactly ready/building/review | removed, coverage relocated | `board_for raises naming the file and the key: stations key set wrong` |
| (8b) a leftover top-level board key raises FleetError (loop case) | kept unchanged | — |
| (8b) explicit key/next_step block (2nd instance) | kept unchanged | — |
| (9) repos is missing | kept unchanged | — |
| (10) a repo entry lacks a slash in its name | kept unchanged | — |
| (11) workspace_root is not absolute | kept unchanged | — |
| (12) repos is empty | kept unchanged | — |
| (13) repos is not a list | kept unchanged | — |
| (14) a repo entry lacks default_branch | kept unchanged | — |
| (14b) repos[].board.stations carries an empty value | removed, coverage relocated | `board_for raises naming the file and the key: a station value is empty` |
| (14c) repos[].board.number is a bool, not an int | re-driven through `validate_board` directly | kept under its own name, calls `fc.validate_board()` directly rather than through `load_fleet`/`board_for` |
| (14d) workspace_root is missing | kept unchanged | — |
| (15) at least 9 FleetError messages were collected | kept unchanged (mechanism identical; underlying raising-case count is now 10, still ≥9) | — |
| (15) FleetError message obeys C-3: ... (per-message loop) | kept unchanged | — |
| (16) repo_entry finds the listed repo | kept unchanged | — (pinned by verify) |
| (17) repo_entry raises FleetError for an unlisted name | kept unchanged | — |
| (17) the message names the unlisted name | kept unchanged | — |
| (20) FLEET_PATH is an absolute path | kept unchanged | — |
| (21) CLAUDE_PROJECT_DIR discard/announce/still-works (3 checks) | kept unchanged | — |
| (22) workspace_path joins / does not use owner-prefixed name (2 checks) | kept unchanged | — |
| (23) --show over a good fleet (4 checks) | kept unchanged | — |
| (24) --show over an invalid fleet (3 checks) | kept unchanged | — |
| (25) a fleet whose single repos entry carries its own board loads | removed, coverage relocated | `(3) a repos entry has no board — this is the correct shape now` |
| (25) 'board' is absent from the loaded fleet | removed, coverage relocated | `(3) a repos entry has no board — this is the correct shape now` |
| (26) board_for returns repos[0]'s own board number | removed, coverage relocated | `board_for resolves through product_config` |
| (26) board_for returns repos[1]'s own board number | removed, coverage relocated | `board_for resolves through product_config` |
| (27) a repos entry with no board raises FleetError | inverted, coverage relocated | `load_fleet rejects a repos entry carrying a board key` |
| (27) the message names the repository missing its board | inverted, coverage relocated | `load_fleet rejects a repos entry carrying a board key` |
| (27b) the next_step names all four required board fields | removed (no longer the shape of the message; item 3's next_step names the new file/key instead) | `load_fleet rejects a repos entry carrying a board key` |
| (28a) repos[].board.owner is empty | removed, coverage relocated | `board_for raises naming the file and the key: owner missing` |
| (28b) repos[].board.number is not an int | removed, coverage relocated (digit string now valid) | `(6)/(28b) validate_board coerces a digit string number to an int` |
| (28c) repos[].board.station_field is empty | removed, coverage relocated | `board_for raises naming the file and the key: station_field missing` |
| (28d) repos[].board.stations does not carry exactly ready/building/review | removed, coverage relocated | `board_for raises naming the file and the key: stations key set wrong` |
| (29) board_station returns the per-repo ready option ... | kept unchanged (fixture migrated to a `product_config` stub; same assertion) | — |
| (30) board_station raises FleetError on an unknown key | kept unchanged (fixture migrated) | — |
| (31) board_for on an unlisted repository raises FleetError (2 checks) | kept unchanged (fixture migrated: `per_repo_fleet_dict`-shaped inline dict dropped its `board` key) | — |
| (X) sanity / SC-18 checks (3 checks) | kept unchanged | — |

No `removed` row above lacks a destination ok-line.

## The `where`-contract pinned pair

Attached to the **`owner missing`** shape, in `board_for_raise_case("owner missing", ...)`:
asserts `github.board.owner` present in `str(exc)` **and** `github.board.board` absent — two
separate boolean terms ANDed, not one substring check on a concatenation. Matches T-04's future
`load_board` case on the same shape name, per the intent's instruction to pin the pair on the
same shape across both entry points.

## Q3 — the `what` slot recommendation

`validate_board`'s five raise sites currently say `"fleet key invalid"` as the `what` slot
(`factory_config.py:80, 84, 90, 95, 105`). After T-02, neither surviving caller (`board_for` via
`github.board`, and T-04's `gh_board.load_board` via the same) reads `fleet.yaml` — both read a
`harness.json`.

**Recommendation: leave `"fleet key invalid"` unchanged.** Argument: the `what` slot names the
error CLASS — "a key inside a board-validation payload is malformed" — not the file it came from.
The file is never lost because `next_step` always ends `in {path}`, and `path` is caller-supplied
(`repos[<name>].board`'s fleet.yaml path today; `github.board`'s `<repo>@<branch>:harness.json`
after T-02/T-04). Renaming `what` to something file-neutral (e.g. `"board key invalid"`) would be
more accurate but touches five call sites purely for wording, in a validator whose docstring
(item 2) already states plainly that `where` is a caller-supplied prefix serving both a fleet
entry and a `harness.json` `github` block — so the file-specific word "fleet" in `what` is at
worst a mild misnomer, not a wrong fact, and every message still names the right file via `path`.
If spawn 2's author disagrees, the alternative exact string I'd propose is `"board key invalid"`
(drops "fleet", keeps everything else), applied identically at all five sites — but I am not
making that edit; this is a recommendation for spawn 2, per the instruction not to touch
`factory_config.py` in this spawn.

## Deferred out of scope (per dispatch, explicit)

- **Post-migration mutation proofs are deferred.** They require mutating `factory_config.py`
  after it exists, and that write is refused by the boundary hook until the main session clears
  it (this dispatch's central constraint — `resolve_fleet()` at `harness_boundary.py:263` calls
  `load_fleet()` on the live `fleet.yaml`, which has a `board` key at `fleet.yaml:26`, and the
  migrated loader will reject it, `sys.exit(2)`-ing every governed write). A continuation spawn
  runs them once that block is cleared.
- Other suites going red (`test-factory-claim.py`, `test-factory-decompose.py`,
  `test-factory-land.py`, `test-factory-integration.py`, `test-check-domain.py`) is T-03's job,
  not touched here.
- `factory_config.py`, `fleet.yaml`, `check-state.sh`, `check-domain.sh`,
  `bash-write-guard.sh`, `validate-digest.py` — not written.

## Note on this spawn's own verify, and the VERDICT

This task's `verify:` (quoted and diffed above) is **not expected to pass** in this cycle — it
exercises the module through `python3 test-factory-config.py`, which requires the migrated
`factory_config.py` (spawn 2's deliverable, explicitly out of scope here). Ran it anyway,
read-only, confirming it fails for exactly the reasons above (module dies before any `has()`
check can even inspect output).

`VERDICT: BLOCKED`, not `PASS` or `FAIL`. `task_verify: fail` and `suite: fail` are both literally
true — I ran both and both failed — and the digest contract only forbids `fail`/`n/a` alongside
`PASS`; `fail` with `BLOCKED` is legal. `FAIL` would claim "retrying or looping back is
meaningful," which is false: the one remaining write this task needs (`factory_config.py`) is a
refused write in this spawn by design (the `harness_boundary.classify()` → `resolve_fleet()` →
`load_fleet()` → `fleet.yaml:26`'s board key chain), not something a retry of THIS cycle can fix.
`BLOCKED` routes to the tier that holds the pen — spawn 2, after the main session clears the
boundary.
