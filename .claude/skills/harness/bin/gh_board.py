#!/usr/bin/env python3
"""The ONE implementation of the harness board's station rule (FEAT-18, T-02).

Two consumers follow: `gh-sync.py` writes stations, `check-state.sh`'s INV-26 compares them.
Two copies of this logic is precisely the drift this feature exists to remove, so everything
about "which station is this at, and what should it be" lives here and nowhere else.

**THE FAKE-BINARY TRAP, and it is not optional to know.** `factory_gh.run_gh` reads the
`FACTORY_GH` environment variable to find the `gh` binary; `gh-sync.py` reads `GH_SYNC_GH`.
A test that injects a fake through `GH_SYNC_GH` alone leaves every call THIS module makes going
to the **real** `gh` — real network, real board, real writes. **Every test that exercises this
module, here and in T-03 and T-04, sets BOTH variables to the same fake.**

**This module raises; it never prints and never exits.** `factory_gh.preflight()` is never called
from here: its callers exit non-zero, and this module's callers must not (D-02 — a station failure
is loud on stderr and the run continues).
"""

import json
import os

import factory_gh


class BoardError(Exception):
    """A station operation failed while `gh` itself works.

    Carries `repo`, `issue_number` and `station` so a caller can print one line naming all three
    (D-02). A message that names only the class or the argv sends the reader back to the source
    to find out which card failed.
    """

    def __init__(self, repo, issue_number, station, detail):
        self.repo = repo
        self.issue_number = issue_number
        self.station = station
        self.detail = detail
        super().__init__(
            f"{repo}#{issue_number} -> {station}: {detail}"
        )


def load_board(root):
    """The board config from `harness.json`'s `github.board`, or None.

    **None means the station feature is not configured for this project** — an environmental
    precondition (D-02), never an error and never a violation. Returns None when the `github`
    block is absent, when `board` is absent or is not a mapping, or when any of `owner`,
    `number`, `station_field` is missing or empty.

    `number` is returned as an **int**, accepting an int or a digit string; anything else is
    unusable and returns None rather than raising, because an unusable config is the same
    not-configured state to every caller.
    """
    path = os.path.join(root, ".harness", "harness.json")
    try:
        with open(path) as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(cfg, dict):
        return None
    github = cfg.get("github")
    if not isinstance(github, dict):
        return None
    board = github.get("board")
    if not isinstance(board, dict):
        return None

    owner = board.get("owner")
    station_field = board.get("station_field")
    number = board.get("number")
    if not owner or not isinstance(owner, str):
        return None
    if not station_field or not isinstance(station_field, str):
        return None
    if isinstance(number, bool):
        # bool is a subclass of int; `true` is not a board number.
        return None
    if isinstance(number, int):
        pass
    elif isinstance(number, str) and number.strip().isdigit():
        number = int(number.strip())
    else:
        return None

    return {"owner": owner, "number": number, "station_field": station_field}


def derive_station(plan_doc):
    """The parent's station, from `plan.yaml` task statuses ALONE (D-03).

    Returns `"Building"` if any task is building; otherwise `"Review"` if there is at least one
    task and every task is done; otherwise **None**, meaning no verdict and no write.

    An absent `status` counts as `pending` — the PLAN.md corpus predates the field.

    It reads NOTHING from `feature.json` and takes no other argument. **The `Done` terminal
    exemption is the CALLER's**, deliberately, so that both callers apply it somewhere a reader
    can see rather than inheriting it invisibly from here.
    """
    if not isinstance(plan_doc, dict):
        return None
    tasks = plan_doc.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return None

    statuses = []
    for t in tasks:
        if not isinstance(t, dict):
            return None
        statuses.append(t.get("status") or "pending")

    if any(s == "building" for s in statuses):
        return "Building"
    if all(s == "done" for s in statuses):
        return "Review"
    return None


def board_stations(board, repo):
    """Every `repo` issue on the board, as {int issue number: station or None}.

    ONE call to `factory_gh.project_items`, which already refuses a truncated page by comparing
    `totalCount` — so a partial read raises rather than reporting an empty column.

    **An item with no status key is recorded with the value None rather than dropped.** Dropping
    it would make an unstationed card indistinguishable from a card that is not on the board, and
    those are two different findings.
    """
    items = factory_gh.project_items(board["owner"], board["number"])
    field = board["station_field"]
    out = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        content = item.get("content") or {}
        # content.repository, never the item's own `repository` key — the URL form and the
        # owner/name form name the same repository but only the latter compares equal.
        if content.get("repository") != repo:
            continue
        num = content.get("number")
        if num is None:
            continue
        # gh lowercases the field name into the item mapping; try the declared spelling first.
        if field in item:
            station = item.get(field)
        else:
            station = item.get(field.lower())
        out[int(num)] = station
    return out


def read_station(stations, issue_number):
    """(station, reason) — pure, no I/O.

    - `(station, None)` — on the board, with a station.
    - `(None, "not on the board")` — the issue number is absent from the mapping.
    - `(None, "no station set")` — present, with a None value.

    This exists because a lookup by a runtime-discovered key that MISSES otherwise leaves both
    sides of a comparison empty, the comparison reports clean for every record, and that silence
    reads as proof. The caller reports the reason.
    """
    key = int(issue_number)
    if key not in stations:
        return (None, "not on the board")
    station = stations[key]
    if station is None:
        return (None, "no station set")
    return (station, None)


def set_station(board, repo, issue_number, station):
    """Move one card. Raises `BoardError`; never prints, never exits.

    `factory_gh.preflight()` is deliberately NOT called — its callers exit non-zero and this
    module's callers must not.
    """
    try:
        item_id = factory_gh.issue_board_item_id(repo, issue_number, board["number"])
        if item_id is None:
            raise BoardError(
                repo, issue_number, station,
                f"issue carries no item on {board['owner']} project {board['number']}",
            )
        factory_gh.project_field_set(
            board["owner"], board["number"], item_id, board["station_field"], station,
        )
    except factory_gh.GhError as exc:
        raise BoardError(repo, issue_number, station, str(exc)) from exc
