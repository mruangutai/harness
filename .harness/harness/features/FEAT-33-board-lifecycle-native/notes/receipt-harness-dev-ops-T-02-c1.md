# Receipt — harness-dev-ops — T-02 — c1

## Verdict

PASS. `.claude/skills/harness/bin/run-unit-tests.sh --kind all` exits 0, zero real FAIL
lines. All nine files named in T-02 ran and PASSed, including the three integration-kind
ones (test-gh-sync.py, test-check-state.py, test-factory-integration.py).

## _STATION_KEYS widened to six

`factory_config.py`:
- `_STATION_KEYS` (line 41): `("backlog","ready","building","review","done")` →
  `("backlog","plan","ready","building","review","done")`.
- The FleetError remediation string in `validate_board`'s stations branch reworded to
  "set exactly backlog, plan, ready, building, review and done, each a non-empty option
  name, in {path}". The comparison itself (`set(stations.keys()) != set(_STATION_KEYS)`)
  is untouched — exact set equality, both directions, per D-05.

`.harness/harness.json`: `github.board.stations` gained `"plan": "Plan"` (measured on
board 3, 2026-08-22, case sensitive per DEC-192). `github.board._note` reworded from
"Four keys, resolved BY NAME at runtime" to "Six keys — backlog, plan, ready, building,
review, done — resolved BY NAME at runtime"; nothing else in that note changed.

`gh_board.derive_station` and `check-state.sh` were not touched, per the plan.

## Edit count per file

| File | Edits |
|---|---|
| `factory_config.py` | 2 (constant, FleetError message) |
| `.harness/harness.json` | 2 (`_note` reworded, `stations` gained `plan`) |
| `test-factory-config.py` | rename `FIVE_STATIONS`→`SIX_STATIONS` + add "plan" (1), both derived loops renamed to the new identifier (1, `replace_all`), `_EXPECTED_STATIONS` gained `"plan": "Col-PL"` + section comment reworded (1), accept-loop check label reworded (1), **3 new cases + 1 schema-drift assertion added** (see below) |
| `test-gh-board.py` | 1 (`FULL_STATIONS`) |
| `test-gh-sync.py` | 1 (`FULL_STATIONS`, integration-kind) |
| `test-factory-integration.py` | 3 — `default_board()`'s dict (the plan's named site, integration-kind) **plus two unplanned fixes**: the GH_STATE fake's GraphQL `options` list and its `OPT_*`→name mapping both lacked a `plan`/`Plan` entry and reddened `(H) decompose/claim/land against the two-board fleet` once the declared board carried six keys |
| `test-factory-claim.py` | 2 (`repo_board`'s keyword signature + its dict — the plan's own "two edits" site) |
| `test-board-station.py` | 4 (:138, :184, :244, :260 after earlier edits shifted line numbers by +1 each after the first) |
| `test-factory-land.py` | 3 (:56 real names, :93 real names, :106 Other-* scheme) |
| `test-factory-decompose.py` | 3 planned (:195, :223, :236) **plus one unplanned fix**: `Recorder.field_options`, a *list* of option names (not a dict keyed by station) mirroring `good_fleet_dict`'s values, was missed by the plan's dict-literal scan and reddened `(2)`/`(3)` once `good_fleet_dict` started declaring `plan` |
| `test-check-state.py` | 2 (:1333 real names, :1616 Icebox/Primed/WIP/Shipped scheme, gave `plan` the value `"Drafted"`) |

Total = 19 station-map edits (matches the plan's own count) + 4 prose reword edits (the
plan's own four sites, all in `test-factory-config.py`/`test-factory-claim.py`) + 2
`factory_config.py` edits + 2 `harness.json` edits + **3 edits the plan's re-derivation did
not name** (see "What the plan missed" below).

## What the plan missed, and why

The plan's re-derivation scanned for "each dict literal whose key set is a subset of the
six station keys and lacks plan" — a scan that only catches dicts *keyed by station name*.
Two fixture shapes evaded it because they carry the same value set without that key shape:

1. `test-factory-decompose.py`'s `Recorder.field_options` — a plain `list` of the board's
   "live" option names, standing in for what a real GitHub Projects v2 field would report.
   `factory_decompose.py`'s `_validate_stations` checks every declared station value against
   this list; once `good_fleet_dict` declared `plan: "Plan"`, decompose started refusing with
   "station option not offered by the board: plan='Plan'" and 18 checks in that file went
   red (verified before the fix: `18 of 98 FAILING`, all with that exact stderr).
2. `test-factory-integration.py`'s GH_STATE fake — the GraphQL `options` array and the
   `OPT_*`→name mapping used by its stateful `gh` stub, both dicts keyed by synthetic option
   IDs, not by station name. `(H) decompose/claim/land against the two-board fleet` reddened
   with the identical "station option not offered" message once `default_board()` (already
   fixed per the plan) declared `plan`.

Both are now fixed (added `"Plan"`/`OPT_PLAN` alongside the existing entries). This is a real
gap in the plan's own scan, not a defect I introduced — flagging it in case a future scan
using the same dict-literal heuristic needs to also catch id→name and value-only-list
station fixtures.

## The three new validate_board cases — how each is red-proved

Added to `test-factory-config.py`, immediately after the existing per-key accept/reject
loops (before the `board_for` section):

All three were mutation-tested directly against `factory_config.py`, not just reasoned
about. Sequence: backed up `factory_config.py`, applied a mutant, ran
`test-factory-config.py`, captured the result, restored from backup, `diff`-confirmed the
restore was byte-identical, then moved to the next mutant.

1. **(a) six-key map, all six non-empty values, is ACCEPTED and returned.** Mutant: reverted
   `_STATION_KEYS` to the pre-widening five-key tuple
   `("backlog", "ready", "building", "review", "done")`. Measured result:
   `FAIL  (X) validate_board accepts a six-key map with all six non-empty values, and returns it`.
   Case reddens because `board_dict(3)` now derives from `SIX_STATIONS` and the five-key
   comparison rejects it — this is exactly the window T-01 left open on kaya-ai's board.
2. **(b) the five-key map `.harness/harness.json` carried before this change is REJECTED
   with a FleetError whose key is `github.board.stations`.** Same five-key mutant as (a).
   Measured result:
   `FAIL  (X) validate_board rejects the five-key map .harness/harness.json carried before this change`
   — under the mutant this five-key map is the *accepted* shape again, so the case's
   `except FleetError` branch is never reached and it reports "did not raise".
3. **(c) a seven-key map adding `abandoned` is REJECTED.** Mutant: loosened the comparison
   from `set(stations.keys()) != set(_STATION_KEYS)` to
   `not set(stations.keys()).issuperset(set(_STATION_KEYS))` — i.e. exact equality relaxed to
   "at least the required keys". Measured result:
   `FAIL  (X) validate_board rejects a seven-key map that adds abandoned` — confirms the case
   is a genuine COUNT/exactness guard, not a vacuous pass. Per the plan, this is deliberately
   NOT the discriminating evidence for SC-08 (a mutant naming the seventh key "banana" would
   redden this case identically) — that discriminator is T-04's own "no argv contains the
   string Abandoned" case.

After each mutant, `factory_config.py` was restored from the pre-mutant backup and `diff`
confirmed byte-identical before applying the next mutant or moving on; the final restore was
verified the same way, then `test-factory-config.py` was re-run once more to confirm all
89/89 checks pass clean.

Also added: an assertion that `set(fc._STATION_KEYS)` equals the six lowercase forms of
`feature-schema.json`'s `status` enum minus `"Abandoned"`, read at runtime from
`.claude/skills/harness/bin/feature-schema.json` (not restated as a literal). Confirmed this
enum currently reads `["Backlog","Plan","Ready","Building","Review","Done","Abandoned"]`
(feature-schema.json, `properties.status.enum`).

## check-state.sh inertness proof

Ran `.claude/skills/harness/bin/check-state.sh` before any edit and after every edit in this
task. Both runs: exit code 1, 442 lines. Sorted-and-hashed both captures:
`md5(before) == md5(after) == e2efb254fe63ff8dec3c6efe586ee6a3`. `diff` between the sorted
captures produced no output — **the two finding sets are identical**, not merely
exit-code-equal. Full captures saved at:
- `notes/check-state-before-T-02.txt`
- `notes/check-state-after-T-02.txt`

## Verify

```
.claude/skills/harness/bin/run-unit-tests.sh --kind all
```
Exit code 0. Zero lines matching `^FAIL `. All 14 grep hits for the substring "FAIL" are
`ok`-prefixed lines whose test *names* contain the word "FAIL" (e.g. "FAIL over an
escalating member is rejected", "dev-ops suite: fail + PASS stays accepted"), not actual
failures — confirmed by inspecting each hit. The nine T-02 files each printed their own
`PASS <filename>` summary line: test-factory-config.py, test-factory-decompose.py,
test-factory-claim.py, test-factory-land.py, test-gh-board.py, test-board-station.py,
test-gh-sync.py, test-check-state.py, test-factory-integration.py.

## Must-not-change sites — confirmed untouched and still correct

- `test-factory-config.py:427` (line moved to `:484` after my edits) —
  `del _b_stations_key_set_wrong["stations"]["done"]` — still rejects (five keys after the
  delete, exact-set equality still rejects five against six).
- `test-gh-board.py:146,154` — three-key and empty-value cases — untouched, still reject.
- `test-factory-config.py:157` (`mut_top_level_board_present`) — three-key stations map
  inside a top-level-`board`-key case — untouched, that case's point is the leftover
  top-level key, not station count.

Confirmed via an AST scan of every `test-*.py` in the bin directory for dict literals whose
key set is a subset of the six station keys and lacks `plan`: only these three sites remain,
all three intentional.

## Files touched

- `.claude/skills/harness/bin/factory_config.py`
- `.claude/skills/harness/bin/test-factory-config.py`
- `.claude/skills/harness/bin/test-gh-board.py`
- `.claude/skills/harness/bin/test-factory-land.py`
- `.claude/skills/harness/bin/test-factory-decompose.py`
- `.claude/skills/harness/bin/test-factory-claim.py`
- `.claude/skills/harness/bin/test-board-station.py`
- `.claude/skills/harness/bin/test-gh-sync.py`
- `.claude/skills/harness/bin/test-check-state.py`
- `.claude/skills/harness/bin/test-factory-integration.py`
- `.harness/harness.json`
