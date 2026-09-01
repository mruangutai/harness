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


def derive_station(plan_doc):
    """The parent's station, from `plan.yaml` task statuses ALONE (D-03), as a LOWERCASE station
    name (FEAT-41 T-02).

    Returns `"building"` if any task is building; otherwise `"review"` if there is at least one
    task and every task is done; otherwise **None**, meaning no verdict and no write.

    THE `board` PARAMETER IS GONE. Its only two uses were the two `board["stations"][...]`
    indexings this function no longer performs, and a parameter the body never reads would
    contradict this docstring's own claim that `plan.yaml` is the sole input. Both call sites —
    check-state.sh's INV-26 and board_lifecycle — drop the argument. The station names are
    spelled here as the lowercase literals they now are; the board's COLUMN name is derived
    later, once, by factory_config.station_column, and only when a value is actually written.

    An absent `status` counts as the not-started station — the PLAN.md corpus predates the field.

    It reads NOTHING from `feature.json`. **The terminal exemption is the CALLER's**,
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
        statuses.append(t.get("status") or "ready")

    if any(s == "building" for s in statuses):
        return "building"
    if all(s == "done" for s in statuses):
        return "review"
    return None


def project(plan_doc, rec):
    """Return {issue number: lowercase station} for every card this feature records.

    THE STATION POLICY LIVES HERE AND NOWHERE ELSE — which card goes where, and when. plan.yaml
    is the only input to the answer. It DERIVES NOTHING for a task: it SELECTS. The word in
    plan.yaml and the column on the board are the same word with the same meaning, which is the
    whole point of FEAT-41.

    NO `board` PARAMETER, deliberately: every value returned is a lowercase station, and
    factory_config.station_column is the one place a column name is produced — once, at the
    moment a value is actually written.

    `rec` is what gh-sync.load_recorded returns: `rec["issues"]` maps task id to sub-issue
    number, `rec["source_issues"]` is a list, `rec["parent"]` is a number or None.

    THE RULES:

    - Each task sub-issue gets its own task's station, VERBATIM AND WITH NO EXCEPTION. A task at
      the ready station projects to the ready station. The old ready-to-backlog exception —
      carried from check-state.sh's `_EXPECT` comment on the grounds that `gh-sync open` lands
      every sub-issue in backlog — is DELETED by D-11. T-10's one-time board pass settles the
      consequence.

    - THE PARENT'S RULE IS TERMINAL FIRST, and this ordering is load-bearing. When the feature's
      top-level station is `done` or the TERMINAL_MARKER, that wins outright and derive_station
      is NOT consulted. MEASURED at 8f8a6a3 against live board 3 on 2026-08-25: every shipped
      feature has all tasks done, so derive_station returns `review` for all of them, and
      derive-first would project 22 of the 23 parent cards to Review while they sit correctly at
      Done — T-10's pass would then drag 22 shipped parents backwards. Terminal first makes that
      count zero. DEC-203 says the harness writes Done at ship; derive_station is an in-flight
      review detector and was never meant to outrank a recorded terminal station.

    - A CARD WHOSE STATION IS THE TERMINAL_MARKER IS ABSENT FROM THE MAPPING, never placed. D-05
      says the marker names no column and never reaches the board; this is where that becomes
      true rather than merely stated. Without this clause FEAT-28 — abandoned, with its card at
      Done — becomes a write of a column that does not exist.

    - Each source issue gets the parent's station.

    - ABSENT AND ILLEGAL ARE DIFFERENT OUTCOMES AND DO NOT SHARE A CODE PATH. A station that is
      legal but not derivable — the parent with no derivation and no top-level station — is
      ABSENT, never guessed; an absent key means no write, the same silence derive_station
      already returns. A station OUTSIDE the vocabulary raises FleetError naming the task id and
      the value, because a vocabulary miss is the defect this feature exists to end and is the
      one case that must not be silent.

    Pure: no I/O, no gh binary, unit-testable.
    """
    legal = frozenset(factory_config.MANDATED_STATIONS) | {factory_config.TERMINAL_MARKER}
    placed = _task_cards(plan_doc, rec, legal)

    parent_station = _parent_station(plan_doc, legal)
    if parent_station is None:
        # No verdict and no write — for the parent AND for its source issues, which take the
        # parent's station or nothing. Absent, never guessed.
        return placed

    parent = (rec or {}).get("parent")
    if parent is not None:
        placed[parent] = parent_station
    for number in (rec or {}).get("source_issues") or []:
        placed[number] = parent_station
    return placed


def _task_statuses(plan_doc):
    """{task id: station} off the plan, with an absent status read as the not-started station.

    Absent reads as `ready` for the same reason derive_station does it: the PLAN.md corpus
    predates the field, and a task nobody has touched has not started.
    """
    tasks = plan_doc.get("tasks") if isinstance(plan_doc, dict) else None
    if not isinstance(tasks, list):
        return {}
    return {str(t.get("id")): (t.get("status") or "ready")
            for t in tasks if isinstance(t, dict)}


def _station_remedy(verb_prefix=""):
    """The remedy line every illegal-station error shares: the verb, then every legal value.

    Extracted because `_task_cards` and `_parent_station` each hand-built it (FEAT-41 F-05), and
    the duplicated half was the part that must not drift — the vocabulary list. A reader who is
    told a value is illegal and NOT told the legal set has to go find factory_config themselves.

    `verb_prefix` carries whatever the caller's verb needs before `--station`, which is a task id
    for one caller and nothing for the other.
    """
    return ("set it with plan-merge.py " + (verb_prefix or "set-feature-station ")
            + "--station <one of "
            + f"{' '.join(factory_config.MANDATED_STATIONS)}>")


def _task_card(task_id, number, by_id, legal):
    """`(number, station)` for one recorded task, or None when it places no card.

    None covers two different routes to the same outcome, deliberately: the plan has no such
    task (a stale record, which is gh-sync's business rather than a vocabulary miss), or the
    task is at the TERMINAL_MARKER, which DEC-203 gives no board column at all.

    An illegal station RAISES rather than returning None, because that is the one case the
    operator has to act on. Extracted from `_task_cards` (FEAT-41 F-05).
    """
    station = by_id.get(str(task_id))
    if station is None:
        return None
    if station not in legal:
        # NAMES THE TASK ID AND THE VALUE. `value` is what the operator can act on, so it
        # carries both — a station alone would not say which task to go fix.
        raise factory_config.FleetError(
            f"task {task_id} station not in the vocabulary",
            f"{task_id}={station}",
            _station_remedy(f"set-task-station --task {task_id} "),
        )
    if station == factory_config.TERMINAL_MARKER:
        return None
    return number, station


def _task_cards(plan_doc, rec, legal):
    """Each recorded task sub-issue, at ITS OWN task's station, verbatim.

    A recorded id with no task in the plan is skipped rather than raised on: the plan is the
    truth and a stale record is gh-sync's business, not a vocabulary miss.
    """
    by_id = _task_statuses(plan_doc)
    placed = {}
    for task_id, number in ((rec or {}).get("issues") or {}).items():
        pair = _task_card(task_id, number, by_id, legal)
        if pair is not None:
            placed[pair[0]] = pair[1]
    return placed


def _parent_station(plan_doc, legal):
    """The parent's station, TERMINAL FIRST — or None, meaning no write.

    Returns None for the TERMINAL_MARKER as well as for no-verdict, because both mean the same
    thing to the caller: place no card. They reach it by different routes and that is why the
    marker is tested BEFORE derive_station rather than filtered out afterwards.
    """
    top = plan_doc.get("status") if isinstance(plan_doc, dict) else None
    if top is not None and top not in legal:
        raise factory_config.FleetError(
            "the feature's top-level station is not in the vocabulary",
            str(top),
            _station_remedy(),
        )
    if top == factory_config.TERMINAL_MARKER:
        return None
    if top == "done":
        return "done"
    derived = derive_station(plan_doc)
    if derived is not None:
        return derived
    return top


def _repo_item_station(item, repo):
    """`(issue_number, station)` for a board item belonging to `repo`, or None to skip it.

    Extracted from `board_stations` (FEAT-41 F-05), which regressed from grade 4 to 3 on
    cognitive when T-02 added the lowercasing below to a loop that already carried three guards.
    The seam is real: deciding WHICH items count and what they say is a different job from
    assembling the mapping.

    None means SKIP THIS ITEM ENTIRELY — it is not on the right repository, or it is not shaped
    like an item at all. That is different from a `station` of None, which means the item IS on
    the board and simply has no station set; `board_stations` records those rather than dropping
    them, because an unstationed card and an absent card are two different findings.

    THE STATION IS LOWERCASED HERE (FEAT-41 T-02) — the read half of the case boundary whose
    write half is `set_station`. Between them, every station value inside the harness is
    lowercase and the only capitals live on GitHub. None stays None: an absent station is not
    the string "none".
    """
    if not isinstance(item, dict):
        return None
    content = item.get("content") or {}
    # content.repository, never the item's own `repository` key — the URL form and the
    # owner/name form name the same repository but only the latter compares equal.
    if content.get("repository") != repo:
        return None
    num = content.get("number")
    if num is None:
        return None
    station = item.get("station")
    return int(num), (station.lower() if isinstance(station, str) else station)


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

    **A value read back from the board is LOWERCASED HERE (FEAT-41 T-02), so no comparison
    anywhere else has to know the board's casing.** This is the read half of the case boundary
    whose write half is `set_station`; between them, every station value inside the harness is
    lowercase and the only capitals live on GitHub. None stays None — an absent station is not
    the string "none".
    """
    items = factory_gh.project_item_stations(
        board["owner"], board["number"], board["station_field"],
    )
    out = {}
    for item in items:
        pair = _repo_item_station(item, repo)
        if pair is not None:
            out[pair[0]] = pair[1]
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

    `station` ARRIVES LOWERCASE (FEAT-41 T-02) and is converted to the board's exact column name
    by `factory_config.station_column` — the write half of the case boundary whose read half is
    `board_stations`. A station outside the mandated six raises `FleetError` from
    `station_column` and that is LET PROPAGATE, not wrapped: a caller naming a station that does
    not exist is a programming error in the caller, not a board failure to report against an
    issue, and BoardError's message would frame it as the latter.

    The `BoardError` message keeps naming the station the caller ASKED FOR, lowercase, because
    that is the value the caller can find in its own source; the capitalised column name appears
    nowhere the caller would recognise.

    `factory_gh.preflight()` is deliberately NOT called — its callers exit non-zero and this
    module's callers must not.
    """
    column = factory_config.station_column(station)
    try:
        item_id = factory_gh.issue_board_item_id(repo, issue_number, board["number"])
        if item_id is None:
            raise BoardError(
                repo, issue_number, station,
                f"issue carries no item on {board['owner']} project {board['number']}",
            )
        factory_gh.project_field_set(
            board["owner"], board["number"], item_id, board["station_field"], column,
        )
    except factory_gh.GhError as exc:
        raise BoardError(repo, issue_number, station, str(exc)) from exc
