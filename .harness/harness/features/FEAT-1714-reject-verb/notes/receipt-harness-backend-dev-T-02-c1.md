# T-02 implementation receipt — FEAT-1714

## Implemented

- Declared `TERMINAL_STATIONS = ("abandoned", "rejected")` while retaining `TERMINAL_MARKER` for T-03.
- Migrated generic terminal consumers in `handoff_done_when.py`, `gh_board.py`, and `board_lifecycle.py` to the ordered terminal set.
- Added `gh-sync.py reject` report/confirmation behavior, including successor and one-line-reason validation, parent-only lifecycle mutations, confirmation gating, and numeric-only `superseded` labeling and rejected-station attempt.
- Added regression coverage for rejected terminal consumers and reject's report, confirmation, `none`, and fail-closed validation paths.

## Verification

Passed:

```sh
python3 tests/unit/test-factory-config.py
python3 tests/unit/test-handoff-done-when.py
python3 tests/unit/test-gh-board.py
python3 tests/integration/test-board-lifecycle.py
```

`python3 tests/integration/test-gh-sync-abandon.py` has one remaining failure:

```text
FAIL  reject numeric: closes only parent then reseats it, comments, labels, closes milestone, and records rejected last
```

The command performs its remote parent-only lifecycle actions, but the final sanctioned `_record_station(..., "rejected")` call is refused by the current T-03-owned `plan-merge.py`, whose legal vocabulary is still `MANDATED_STATIONS + TERMINAL_MARKER`. T-02 does not change that T-03-only surface and does not bypass `plan-merge.py`; therefore `plan.yaml` cannot yet record `rejected`.
