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

import factory_config
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
    """The board config from `harness.json`'s `github.board`, validated, or None.

    **`github.board: null` is the only DECLARED no-board path** — the shape
    `templates/harness.json` ships (D-07). It is NOT the only path returning None, and an earlier
    version of this docstring said it was: measured 2026-08-19, five of six non-error paths mean
    "no board". The four undeclared ones return None without raising — no `github` key at all,
    `github` not a mapping, the whole file not a mapping, and the file absent or unparseable.
    The last is arguably correct: a project with no `harness.json` genuinely has no board.

    EXACTLY ONE unusable shape RAISES `factory_config.FleetError` naming the harness.json path
    and the offending key: a `github` block that IS a mapping and carries no `board` key
    (indistinguishable from a typo — never treated the same as an explicit null). A `board`
    present but not a mapping, or carrying any field `factory_config.validate_board` rejects
    (`owner`, `number`, `station_field`, `stations`), raises as well. A caller that wants to catch this must import
    `factory_config` and catch `factory_config.FleetError`.

    Field validation itself — including the digit-string-to-int coercion for `number` — is
    delegated ENTIRELY to `factory_config.validate_board`, the one board validator in the tree
    (FEAT-24 D-05); nothing here re-implements or re-coerces any of it. The returned mapping is
    exactly what that function returns: `owner`, `number` (normalised to an int), `station_field`
    and `stations`.
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
    if "board" not in github:
        raise factory_config.FleetError(
            "board key missing", "github.board", f"declare github.board in {path}",
        )
    board = github["board"]
    if board is None:
        return None
    return factory_config.validate_board(board, "github.board", path)


def derive_station(plan_doc, board):
    """The parent's station, from `plan.yaml` task statuses ALONE (D-03), named through the
    board's OWN declared station options rather than a hardcoded literal (FEAT-24 T-04).

    Returns `board["stations"]["building"]` if any task is building; otherwise
    `board["stations"]["review"]` if there is at least one task and every task is done;
    otherwise **None**, meaning no verdict and no write. The derivation rule itself is
    unchanged; only the station NAMES now come from the board rather than being spelled here.

    An absent `status` counts as `pending` — the PLAN.md corpus predates the field.

    It reads NOTHING from `feature.json`. **The `Done` terminal exemption is the CALLER's**,
    deliberately, so that both callers apply it somewhere a reader can see rather than
    inheriting it invisibly from here.
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
        return board["stations"]["building"]
    if all(s == "done" for s in statuses):
        return board["stations"]["review"]
    return None


def board_stations(board, repo):
    """Every `repo` issue on the board, as {int issue number: station or None}.

    ONE call to `factory_gh.project_item_stations` (FEAT-29 T-02) — the targeted, cost-1 GraphQL
    query, never `factory_gh.project_items`'s whole-board `item-list` scan. That call already
    refuses a truncated or unreadable page, raising `GhError` rather than reporting an empty
    column; nothing here catches it, so it propagates unchanged.

    **An item with no station value is recorded with the value None rather than dropped.**
    Dropping it would make an unstationed card indistinguishable from a card that is not on the
    board, and those are two different findings. `project_item_stations` already returns the
    station directly (no raw item dict, no field-name lookup needed here).
    """
    items = factory_gh.project_item_stations(
        board["owner"], board["number"], board["station_field"],
    )
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
        out[int(num)] = item.get("station")
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
