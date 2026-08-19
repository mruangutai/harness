# Receipt — harness-backend-dev — fix-c4

Task: make SC-02's `ready` assertion discriminating in `test-factory-decompose.py`
(`.harness/harness/features/FEAT-24-config-responsibility-split/BRIEF.md:59-62`).

## The defect

`stations.ready` was fixtured as the literal DEC-192 value `"Ready"` at two sites
(`test-factory-decompose.py:196`, `:224`), and every assertion reading it compared against the
same literal. Hardcoding `factory_decompose.py:399`'s `ready_option` to `"Ready"` therefore reddened
nothing — the "real" lookup and the fallback literal were indistinguishable.

## Fixture value chosen: `"Promoted"`

Clears all four constraints:
1. Not `"Ready"`.
2. Does not contain `"Ready"` as a substring (rules out the `:1161` `in`-check trap — `"Not-Ready"`
   or `"Ready-Now"` would pass vacuously against that check).
3. Distinct from every `Other-*` value at `:237` (`Other-Backlog`, `Other-Ready`, `Other-Building`,
   `Other-Review`, `Other-Done`) — keeps T-03's A-vs-B discrimination intact.
4. Does not collide with `Building` / `Review` / `Backlog` / `Done`, and is not `"Redy"` (the D4-4
   typo fixture at `:1149`).

Also mirrors the naming convention already in the tree (`Icebox`, `Promoted`, `Col-R`).

## Six sites updated (verified by grep, all `"Ready"` literals gone)

| Site | What | Change |
|---|---|---|
| `:97` | `Recorder.field_options` | `"Ready"` → `"Promoted"` (load-bearing: `_validate_stations` rejects a declared station the live board doesn't offer) |
| `:196` | `good_fleet_dict` `stations.ready` | `"Ready"` → `"Promoted"` |
| `:224` | `two_repo_fleet_dict` repo A `stations.ready` | `"Ready"` → `"Promoted"` |
| `:413` | `(2) both stations set...` assertion body | `== "Ready"` → `== "Promoted"` (label at `:412` byte-frozen, unchanged) |
| `:519` | `(7) resume: ...` assertion body | `== "Ready"` → `== "Promoted"` (label at `:518` byte-frozen, unchanged) |
| `:1161` | `(D4-4)` real-options grep | `"Ready" in err` → `"Promoted" in err` (label at `:1160` byte-frozen, unchanged) |
| `:1198-1199` | `(T-03)` label + assertion | label text `(Ready)` → `(Promoted)` (not byte-frozen — carries the value); assertion `== "Ready"` → `== "Promoted"` |

**Discrepancy from the dispatch:** the dispatch said the `two_repo_fleet_dict` docstring
(`:206-212`) and the `Recorder.field_options` comment (`:93-97`) "name the option" and need
updating. I read both at source — neither contains the literal `"Ready"` or any other station-value
literal; they refer to "station option names" / "numbers/options" generically. No edit was needed
or made at those two prose sites. Reporting this as a finding per the dispatch's own instruction,
not silently resolving it.

## Baseline (before any edit)

    181/181 checks passed.

sha256 of `factory_decompose.py` before any mutation:
`eebe8c96765b7fde5af203d0e68e7dc8e9579ef1cc1b9e23ba2ebb2df3b28208`

## After the six-site edit (green again, before mutating)

    181/181 checks passed.

Same count as baseline — the edit is a pure rename, no case added or removed.

## Mutation: `factory_decompose.py:399` `ready_option = factory_config.board_station(fleet, args.repo, "ready")` → `ready_option = "Ready"`

FAIL lines (literal, verbatim):

    FAIL  (2) both stations set to the fleet's ready option
    FAIL  (7) resume: the item's station is set to the ready option
    FAIL  (T-03) the station set to A's own ready option (Promoted), never B's (Other-Ready)

Count line (literal):

    3 of 181 FAILING.

**Matches the dispatch's prediction exactly**: three named cases reddened (not one, not four), and
`(D4-4) typo fleet: stderr names the board's real options` (`:1160-1161`) **stayed green** —
confirmed by its absence from the FAIL set above. That case exits 2 before any station is set
(exercises `project_field_options`/the option-list plumbing, not the `ready_option` lookup), so it
correctly can't see this mutation. The prediction held; no discrepancy to report there.

## Restore proof

sha256 after restore:
`eebe8c96765b7fde5af203d0e68e7dc8e9579ef1cc1b9e23ba2ebb2df3b28208`
(matches pre-mutation hash byte-for-byte)

    $ git diff --exit-code -- .claude/skills/harness/bin/factory_decompose.py; echo "diff exit=$?"
    diff exit=0

    $ git status --porcelain .claude/skills/harness/bin/
     M .claude/skills/harness/bin/test-factory-decompose.py

Only `test-factory-decompose.py` is modified; `factory_decompose.py` is clean; no stray
`.bak`/`-e` file left.

## Green again on the restored tree

    181/181 checks passed.

## Full suite

`.claude/skills/harness/bin/run-unit-tests.sh --kind all`, run last, on the restored tree.

Red set: **empty** (`grep -c "^FAIL"` on the captured output returned `0`). Exit code: `0`.
Every listed test file reports `PASS`, including `test-factory-decompose.py`,
`test-factory-config.py`, `test-check-state.py`, `test-gh-board.py`, `test-factory-integration.py`.

## Pure-addition/no-weakening diff

    $ git diff -- .claude/skills/harness/bin/test-factory-decompose.py | grep '^-' | grep -v '^---'
    -        self.field_options = ["Ready", "Building", "Review", "Backlog", "Done"]
    -                    "backlog": "Backlog", "ready": "Ready", "building": "Building",
    -                        "backlog": "Backlog", "ready": "Ready", "building": "Building",
    -          all(c[1][4] == "Ready" for c in field_calls), field_calls)
    -          any(c[1][4] == "Ready" for c in field_calls), field_calls)
    -          "Ready" in err and "Building" in err and "Review" in err, err)
    -    check("(T-03) the station set to A's own ready option (Ready), never B's (Other-Ready)",
    -          all(c[1][4] == "Ready" for c in field_calls)

Every removed line is a 1-for-1 literal swap (`"Ready"` → `"Promoted"`) with an identical-shape `+`
line replacing it — no assertion, case, or `check(...)` call was deleted. The three byte-frozen
ok-line labels (`:412`, `:518`, `:1160`) do not appear in this list — confirmed unchanged by direct
grep above.

## Extra check: T-03's plan.yaml verify block (not this dispatch's own task — no T-NN was quoted in
the dispatch, so `task: none` per DEC-175 — but T-03's verify reads `test-factory-decompose.py`
output and its `hasin` check names the same byte-frozen label `(2) both stations set to the fleet's
ready option` this fix touches, so it was worth confirming directly)

Ran `plan.yaml:604-621`'s exact block, verbatim, against the restored tree:

    T-03 GREEN

The block only `hasin`-matches the byte-frozen label text, never a station value literal, so the
`Ready` → `Promoted` rename does not disturb it.

## Scope note: SC-02's other four keys were not re-measured here

This fix closes only the `ready` key's vacuous-pass gap, per dispatch scope. `backlog`, `building`,
`review`, `done` were reported by qa as already discriminating through `gh_board.derive_station` /
INV-26 with non-DEC-192 fixture values; that claim was taken as given, not independently
re-mutation-tested in this run. SC-02 should not be read as fully re-verified end-to-end by this
receipt — only the `ready` gap it was scoped to close.

## files_touched

- `.claude/skills/harness/bin/test-factory-decompose.py`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/receipt-harness-backend-dev-fix-c4.md`

`factory_decompose.py` is NOT in this list — restore confirmed byte-identical above.
