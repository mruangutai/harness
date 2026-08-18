#!/usr/bin/env python3
"""gh_board.py must get these right — offline, against a fake gh.

Every case asserts a VALUE, never that a call happened: a test that counts calls passes just as
well when the value is wrong, which is the vacuous shape this feature exists to remove.

**BOTH `FACTORY_GH` AND `GH_SYNC_GH` are set to the same fake in every case that touches gh.**
`factory_gh.run_gh` reads `FACTORY_GH` while `gh-sync.py` reads `GH_SYNC_GH`; a test injecting
through one alone sends the other module's calls to the REAL gh — real network, real board.

    ./test-gh-board.py    -> exit 0 all pass, 1 otherwise
"""
import json
import os
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gh_board  # noqa: E402
import factory_gh  # noqa: E402
import factory_config  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


def write_harness_json(root, github):
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "harness.json"), "w") as f:
        json.dump({"schema_version": 1, "github": github}, f)


def fake_gh(tmp, payload):
    """A gh that prints `payload` verbatim for any argv, exit 0."""
    path = os.path.join(tmp, "fake-gh")
    with open(path, "w") as f:
        f.write("#!/bin/bash\ncat <<'EOF'\n" + payload + "\nEOF\n")
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    os.environ["FACTORY_GH"] = path
    os.environ["GH_SYNC_GH"] = path
    return path


def fake_gh_failing(tmp):
    path = os.path.join(tmp, "fake-gh-fail")
    with open(path, "w") as f:
        f.write("#!/bin/bash\necho 'boom' >&2\nexit 3\n")
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    os.environ["FACTORY_GH"] = path
    os.environ["GH_SYNC_GH"] = path
    return path


# ---------------- load_board ----------------

FULL_STATIONS = {
    "backlog": "Backlog", "ready": "Ready", "building": "Building",
    "review": "Review", "done": "Done",
}


def full_board(**overrides):
    board = {"owner": "mruangutai", "number": 3, "station_field": "Status",
              "stations": dict(FULL_STATIONS)}
    board.update(overrides)
    return board


def raised_exc(root):
    """Call load_board(root), returning the raised FleetError, or None if it did not raise."""
    try:
        gh_board.load_board(root)
    except factory_config.FleetError as exc:
        return exc
    return None


with tempfile.TemporaryDirectory() as tmp:
    write_harness_json(tmp, {"sync": True, "repo": "o/r", "board": None})
    check("load_board: an explicit null board is accepted and returns None",
          gh_board.load_board(tmp) is None)

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    write_harness_json(tmp, {"sync": True, "repo": "o/r"})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: no board key",
          exc is not None and "github.board" in str(exc) and path in str(exc), str(exc))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    write_harness_json(tmp, {"board": "not-a-mapping"})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: board is not a mapping",
          exc is not None and "github.board" in str(exc) and path in str(exc), str(exc))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    board = full_board()
    del board["owner"]
    write_harness_json(tmp, {"board": board})
    exc = raised_exc(tmp)
    exc_text = str(exc) if exc else ""
    check("load_board raises naming the file and the key: owner missing",
          exc is not None and "github.board.owner" in exc_text and path in exc_text
          and "github.board.board" not in exc_text, exc_text)

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    write_harness_json(tmp, {"board": full_board(number=2.5)})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: number not an int",
          exc is not None and "github.board.number" in str(exc) and path in str(exc), str(exc))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    board = full_board()
    del board["station_field"]
    write_harness_json(tmp, {"board": board})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: station_field missing",
          exc is not None and "github.board.station_field" in str(exc) and path in str(exc),
          str(exc))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    board = full_board()
    del board["stations"]
    write_harness_json(tmp, {"board": board})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: stations missing",
          exc is not None and "github.board.stations" in str(exc) and path in str(exc), str(exc))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    board = full_board(stations={"backlog": "Backlog", "ready": "Ready", "building": "Building"})
    write_harness_json(tmp, {"board": board})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: stations key set wrong",
          exc is not None and "github.board.stations" in str(exc) and path in str(exc), str(exc))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    board = full_board(stations={**FULL_STATIONS, "review": ""})
    write_harness_json(tmp, {"board": board})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: a station value is empty",
          exc is not None and "github.board.stations" in str(exc) and path in str(exc), str(exc))

with tempfile.TemporaryDirectory() as tmp:
    write_harness_json(tmp, {"board": full_board(number="3")})
    b = gh_board.load_board(tmp)
    check("load_board: digit string '3' -> int 3",
          b is not None and b["number"] == 3 and isinstance(b["number"], int),
          repr(b))

# ---------------- derive_station ----------------

def plan(*statuses):
    return {"tasks": [{"id": f"T-{i:02d}", "status": s} for i, s in enumerate(statuses, 1)]}


# Cases 1 and 2 assert the literal DEC-192 names in both label and assertion, so they use a
# board declaring those exact names — label and assertion stay true.
DEC192_BOARD = full_board()

check("derive_station: one building among three -> Building",
      gh_board.derive_station(plan("done", "building", "done"), DEC192_BOARD) == "Building")
check("derive_station: three of three done -> Review",
      gh_board.derive_station(plan("done", "done", "done"), DEC192_BOARD) == "Review")
check("derive_station: two done one pending -> None",
      gh_board.derive_station(plan("done", "done", "pending"), DEC192_BOARD) is None)
check("derive_station: empty task list -> None",
      gh_board.derive_station({"tasks": []}, DEC192_BOARD) is None)
check("derive_station: task with NO status key counts as pending -> None",
      gh_board.derive_station(
          {"tasks": [{"id": "T-01"}, {"id": "T-02", "status": "done"}]}, DEC192_BOARD) is None)

# The two new lookup cases use a board whose station names are DELIBERATELY not the DEC-192
# names, so a case can only pass by actually reading board["stations"], not by a reintroduced
# literal in gh_board.py.
LOOKUP_BOARD = full_board(stations={**FULL_STATIONS, "building": "Col-B", "review": "Col-R"})

check("derive_station returns the declared building station",
      gh_board.derive_station(plan("done", "building", "done"), LOOKUP_BOARD) == "Col-B")
check("derive_station returns the declared review station",
      gh_board.derive_station(plan("done", "done", "done"), LOOKUP_BOARD) == "Col-R")

# ---------------- board_stations ----------------

with tempfile.TemporaryDirectory() as tmp:
    fake_gh(tmp, json.dumps({
        "totalCount": 3,
        "items": [
            {"content": {"repository": "mruangutai/harness", "number": 326}, "status": "Building"},
            {"content": {"repository": "someone/else", "number": 99}, "status": "Done"},
            {"content": {"repository": "mruangutai/harness", "number": 327}},
        ],
    }))
    board = {"owner": "mruangutai", "number": 3, "station_field": "status"}
    st = gh_board.board_stations(board, "mruangutai/harness")
    check("board_stations: item from another repository is EXCLUDED",
          99 not in st, repr(st))
    check("board_stations: item with a station is present with its value",
          st.get(326) == "Building", repr(st))
    check("board_stations: item with NO status key is present with value None, not dropped",
          327 in st and st[327] is None, repr(st))

# ---------------- read_station ----------------

stations = {326: "Building", 327: None}
check("read_station: on the board with a station -> (station, None)",
      gh_board.read_station(stations, 326) == ("Building", None))
check("read_station: absent from the mapping -> (None, 'not on the board')",
      gh_board.read_station(stations, 999) == (None, "not on the board"))
check("read_station: present with a None value -> (None, 'no station set')",
      gh_board.read_station(stations, 327) == (None, "no station set"))

# ---------------- set_station ----------------

with tempfile.TemporaryDirectory() as tmp:
    fake_gh_failing(tmp)
    board = {"owner": "mruangutai", "number": 3, "station_field": "Status"}
    raised = None
    try:
        gh_board.set_station(board, "mruangutai/harness", 326, "Building")
    except gh_board.BoardError as exc:
        raised = exc
    except Exception as exc:  # noqa: BLE001 — any other type is itself the failure
        raised = exc
    check("set_station: a failing gh raises BoardError",
          isinstance(raised, gh_board.BoardError), type(raised).__name__)
    text = str(raised) if raised else ""
    check("set_station: the raised error NAMES the issue number and the station attempted",
          "326" in text and "Building" in text, text)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAIL")
    sys.exit(1)
print("all pass")
