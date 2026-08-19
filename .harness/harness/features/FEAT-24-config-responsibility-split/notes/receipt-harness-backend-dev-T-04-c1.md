# Receipt — harness-backend-dev — T-04 — c1

## 1. Verify-block cross-check

Dispatch verify text compared line-by-line against `plan.yaml` T-04's `verify:` block —
**identical**, no mismatch.

## 2. Verbatim verify output

```
$ out=$(python3 .claude/skills/harness/bin/test-gh-board.py 2>&1); rc=$?
$ has() { printf '%s\n' "$out" | sed -E 's/^(ok|PASS)[ -]+//' | grep -qxF "$1"; }
$ for shape in "no board key" "board is not a mapping" "owner missing" "number not an int" "station_field missing" "stations missing" "stations key set wrong" "a station value is empty"; do
    has "load_board raises naming the file and the key: $shape" || { echo "T-04: the raise case for '$shape' did not pass or did not run"; exit 1; }
  done
$ has "derive_station returns the declared building station" || { ... }
$ has "derive_station returns the declared review station" || { ... }
$ has "derive_station: two done one pending -> None" || { ... }
$ printf '%s\n' "$out" | grep -E "^FAIL" && { ... }
$ test "$rc" = 0 || { ... }
$ grep -nE '"(Building|Review|Backlog|Ready|Done|Plan)"' .claude/skills/harness/bin/gh_board.py && { ... }
$ grep -qF "def derive_station" .claude/skills/harness/bin/gh_board.py || { ... }
$ sync_out=$(python3 .claude/skills/harness/bin/test-gh-sync.py 2>&1); sync_rc=$?
$ bs_out=$(python3 .claude/skills/harness/bin/test-board-station.py 2>&1); bs_rc=$?
... (all guard clauses passed silently — no lines printed)
T-04 GREEN
```

Full raw run (all four guard clauses silent, terminal line only):

```
T-04 GREEN
```

Individually confirmed:
- `test-gh-board.py`: rc=0, 25 PASS lines, 0 FAIL.
- `test-gh-sync.py`: rc=0, 104 `ok` lines, 0 FAIL.
- `test-board-station.py`: rc=0, 12 PASS lines, 0 FAIL.
- `grep -nE '"(Building|Review|Backlog|Ready|Done|Plan)"' gh_board.py` — zero hits (double-quoted).
- `grep -nE "'(Building|Review|Backlog|Ready|Done|Plan)'" gh_board.py` — zero hits (single-quoted;
  checked in addition to the verify's own grep, since the verify clause only matches double
  quotes — see item 6).
- Non-reader survey (`wayfind.py`, `layout_migration.py`, `check-plan-routes.py`,
  `branch-create-gate.sh`): all four positive-control greps matched (`def `/`#!/`), all four
  negative greps for `board_for|load_board|station_field|stations|["board"]` returned zero hits.

## 3. `bin/check-state.sh` observed state — NOT fixed, as instructed

```
$ bash .claude/skills/harness/bin/check-state.sh
Traceback (most recent call last):
  File "<stdin>", line 1156, in <module>
TypeError: derive_station() missing 1 required positional argument: 'board'
$ echo $?
1
```

Exit 1, three lines total (traceback + exit marker), effectively no invariant report — exactly the
shape the dispatch predicted (item 2's arity change hits `check-state.sh:1180`'s unwrapped call).
Not touched. T-05 (main-session-direct) repairs the call site.

## 4. Per-case ledger — `test-gh-board.py`

| Pre-existing case (label at HEAD) | Disposition | New ok-line |
|---|---|---|
| `load_board: no board key -> None` | converted to a raise case | `load_board raises naming the file and the key: no board key` |
| `load_board: board missing station_field -> None` | converted to a raise case | `load_board raises naming the file and the key: station_field missing` |
| `load_board: non-numeric number -> None` | converted to a raise case (driver stays a non-digit string, `"three"`) | `load_board raises naming the file and the key: number not an int` — **note**: I used a float (`2.5`) for a NEW case with this same ok-line via `full_board(number=2.5)`; the original fixture's non-digit-string driver (`"three"`) was folded into the same converted case rather than kept as a second one, since the ok-line is singular. Both a float and a non-digit string are now invalid — only one case is required by the plan text. |
| `load_board: digit string '3' -> int 3` | **kept as a passing case, unchanged assertion** — now succeeds via `validate_board`'s coercion, with `stations` added to the fixture so the full 5-key map validates | same label, unchanged |
| `derive_station: one building among three -> Building` | kept, now driven with a `DEC192_BOARD` (`stations.building == "Building"`) so label and assertion both stay literally true | same label |
| `derive_station: three of three done -> Review` | kept, same `DEC192_BOARD` | same label |
| `derive_station: two done one pending -> None` | kept verbatim (pinned by verify) | same label |
| `derive_station: empty task list -> None` | kept | same label |
| `derive_station: task with NO status key counts as pending -> None` | kept | same label |

New cases added (not conversions): `load_board: an explicit null board is accepted and returns
None`; the raise cases for `board is not a mapping`, `owner missing`, `stations missing`,
`stations key set wrong`, `a station value is empty`; `derive_station returns the declared
building station`; `derive_station returns the declared review station`.

**All five original `derive_station` cases survive and pass** — confirmed in the run above (5
`derive_station:` PASS lines plus the 2 new lookup PASS lines = 7 total `derive_station*` PASS
lines).

The `owner missing` case pins the full key path: asserts `"github.board.owner" in str(exc)` AND
`"github.board.board" not in str(exc)`.

## 5. `load_board` docstring, quoted in full

```
    """The board config from `harness.json`'s `github.board`, validated, or None.

    **None means this project has explicitly declared it has no board** — `github.board: null`,
    the shape `templates/harness.json` ships (D-07). That is the ONLY non-error path.

    Every other unusable shape RAISES `factory_config.FleetError` naming the harness.json path
    and the offending key: the `github` block absent, the `board` key absent (indistinguishable
    from a typo — never treated the same as an explicit null), `board` present but not a
    mapping, or any field `factory_config.validate_board` rejects (`owner`, `number`,
    `station_field`, `stations`). A caller that wants to catch this must import
    `factory_config` and catch `factory_config.FleetError`.

    Field validation itself — including the digit-string-to-int coercion for `number` — is
    delegated ENTIRELY to `factory_config.validate_board`, the one board validator in the tree
    (FEAT-24 D-05); nothing here re-implements or re-coerces any of it. The returned mapping is
    exactly what that function returns: `owner`, `number` (normalised to an int), `station_field`
    and `stations`.
    """
```

States the `FleetError` raise explicitly, per the operator's ruling, and names the module a
caller must import to catch it.

## 6. Station-literal check — both quoting styles

Confirmed via two separate greps (double-quoted, the verify's own clause; single-quoted, run
manually) — zero hits in either style. See item 2.

## 7. What changed in `gh-sync.py` and `board-station.py`

**`gh-sync.py`**
- `load_config` no longer catches `gh_board.load_board`'s raise; its docstring now states the
  explicit-null-only exemption and the raise-propagates contract.
- `main()` wraps `load_config(root)` in `try/except factory_config.FleetError`: on catch, prints
  `str(exc)` **verbatim**, prefixed `gh-sync: `, to **stderr**, and `sys.exit(2)`.
- `_apply_parent_rule` now calls `gh_board.derive_station(plan_doc, board)`.
- Module docstring's "THREE-WAY split" paragraph rewritten to a four-way split, documenting the
  new loud-failure branch alongside the existing SKIP/ERROR/caller-error branches.

**`board-station.py`**
- `main()` wraps `gh_board.load_board(root)` in `try/except factory_config.FleetError`: on
  catch, `err(str(exc))` (stderr, `board-station: ` prefix) and `return 2`.
- Module docstring's EXIT CONTRACT paragraph rewritten: exit 2 now covers both a caller mistake
  and an unusable board declaration; the remaining environmental preconditions (including an
  explicit null board) still exit 0.

Stream / exit / message shape, both tools: **stderr**, **exit 2**, `str(exc)` printed verbatim
(never recomposed) so the `next_step` half of `factory_cli.body`'s message is preserved.

## Collateral fixture repair (not itemized in T-04's task text, but required to keep the suite green)

`test-gh-sync.py`'s `stage()` and `write_harness_json_board()` fixtures previously omitted the
`board` key entirely (the pre-T-04 "no board configured" shape). Under this task's own change
that shape now raises, so every `open`/`ship`/`abandon`/etc. fixture using `stage()` would have
started raising `FleetError` at `load_config` regardless of what the individual case was testing.
Fixed by adding an explicit `"board": None` to `stage()`'s default fixture and to the ~22 inline
`json.dump({"github": {...}})` calls that previously carried no board key — all of which are
about the OPEN/SHIP/ABANDON lifecycle, not board behaviour, so this is fixture repair, not a
weakened assertion. `write_harness_json_board`'s `board=False` semantics changed from "omit the
key" to "write an explicit null" for the same reason (its one caller, the pre-existing
`FEAT-09-no-board` case, already tested the explicit-null contract in spirit — D-07's
environmental precondition). All existing `stage_station`/`write_harness_json_board(board=True)`
fixtures gained a `stations` map (5 DEC-192 keys) since `validate_board` now requires it.

`test-board-station.py`'s four `station_field`-only board fixtures (cases 1, 3, 6, 7) gained the
same `stations` map for the same reason.

## Files touched

- `.claude/skills/harness/bin/gh_board.py`
- `.claude/skills/harness/bin/test-gh-board.py`
- `.claude/skills/harness/bin/gh-sync.py`
- `.claude/skills/harness/bin/test-gh-sync.py`
- `.claude/skills/harness/bin/board-station.py`
- `.claude/skills/harness/bin/test-board-station.py`

Not committed — pen is the lead's, T-04 lands with T-05.
