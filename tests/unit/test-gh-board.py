#!/usr/bin/env python3
"""gh_board.py must get these right — offline, against a fake gh.

Every case asserts a VALUE, never that a call happened: a test that counts calls passes just as
well when the value is wrong, which is the vacuous shape this feature exists to remove.

**BOTH `FACTORY_GH` AND `GH_SYNC_GH` are set to the same fake in every case that touches gh.**
`factory_gh.run_gh` reads `FACTORY_GH` while `gh-sync.py` reads `GH_SYNC_GH`; a test injecting
through one alone sends the other module's calls to the REAL gh — real network, real board.

    ./test-gh-board.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import stat
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
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

# The station DECLARATION is an ordered lowercase LIST under FEAT-41 T-01, and carries no column
# names at all — factory_config.station_column derives those.
FULL_STATIONS = ("backlog", "plan", "ready", "building", "review", "done")


def full_board(**overrides):
    board = {"owner": "mruangutai", "number": 3, "station_field": "Status",
              "stations": list(FULL_STATIONS)}
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
    board = full_board(stations=["backlog", "ready", "building"])
    write_harness_json(tmp, {"board": board})
    exc = raised_exc(tmp)
    check("load_board raises naming the file and the key: station list incomplete",
          exc is not None and "github.board.stations" in str(exc) and path in str(exc), str(exc))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, ".harness", "harness.json")
    board = full_board(stations=list(FULL_STATIONS[:-1]) + [""])
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


# derive_station TAKES plan.yaml ALONE and returns a LOWERCASE station name (FEAT-41 T-02). The
# board argument is gone, so these calls pass one argument — and the arity itself is asserted
# below, because a stray second argument would otherwise be silently accepted by a **kwargs-ish
# signature and the "plan.yaml is the sole input" claim would rot unnoticed.
check("derive_station: one building among three -> building",
      gh_board.derive_station(plan("done", "building", "done")) == "building")
check("derive_station: three of three done -> review",
      gh_board.derive_station(plan("done", "done", "done")) == "review")
check("derive_station: two done one not-started -> None",
      gh_board.derive_station(plan("done", "done", "ready")) is None)
check("derive_station: empty task list -> None",
      gh_board.derive_station({"tasks": []}) is None)
check("derive_station: task with NO status key counts as not-started -> None",
      gh_board.derive_station(
          {"tasks": [{"id": "T-01"}, {"id": "T-02", "status": "done"}]}) is None)

# THE RETURN IS A STATION, NEVER A COLUMN. This is what the two deleted LOOKUP_BOARD cases
# become: they existed to prove derive_station read the declaration rather than spelling a
# literal, and now the opposite is required — it must return the lowercase station and leave
# every capitalisation to station_column. Asserting "not the column" is what would catch a
# well-meaning re-introduction of .capitalize() here.
for _statuses, _want in ((("done", "building", "done"), "building"),
                         (("done", "done", "done"), "review")):
    _got = gh_board.derive_station(plan(*_statuses))
    check(f"derive_station returns the lowercase station {_want!r}, not its board column",
          _got == _want and _got != factory_config.station_column(_want), _got)

# The board parameter is GONE, not merely unused: a two-argument call must fail loudly rather
# than be tolerated, or check-state.sh and board_lifecycle could keep passing a board forever.
try:
    gh_board.derive_station(plan("done"), full_board())
    check("derive_station rejects a second board argument", False, "accepted two arguments")
except TypeError:
    check("derive_station rejects a second board argument", True)

# ---------------- board_stations ----------------
# `board_stations` now calls `factory_gh.project_item_stations`, a GraphQL call whose fake
# payload is the `{"data": {"user": {"projectV2": {"items": {...}}}}}` envelope, never the flat
# `{"totalCount", "items"}` shape `project_items` used. `pageInfo.hasNextPage` is always False
# here — True would make `fake_gh`'s "same page for any argv" answer loop `project_item_stations`
# forever (its pagination reads `hasNextPage` off every response).
#
# Each block below gets its OWN fixture and its OWN `board_stations` call, wrapped in try/except
# per P-04: a mutation that makes the call raise must redden only the block whose fixture
# provokes it, never crash the whole suite and take out unrelated checks (the T-01 fixture-
# isolation lesson, repeated here for the content-null case).

with tempfile.TemporaryDirectory() as tmp:
    fake_gh(tmp, json.dumps({
        "data": {"user": {"projectV2": {"items": {
            "totalCount": 4,
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [
                {"content": {"number": 326, "repository": {"nameWithOwner": "mruangutai/harness"}},
                 "fieldValueByName": {"name": "Building"}},
                {"content": {"number": 99, "repository": {"nameWithOwner": "someone/else"}},
                 "fieldValueByName": {"name": "Done"}},
                {"content": {"number": 327, "repository": {"nameWithOwner": "mruangutai/harness"}},
                 "fieldValueByName": None},
                {"content": {"number": 328, "repository": {"nameWithOwner": "mruangutai/harness"}},
                 "fieldValueByName": {"name": "Review"}},
            ],
        }}}}
    }))
    board = {"owner": "mruangutai", "number": 3, "station_field": "Status"}
    try:
        st = gh_board.board_stations(board, "mruangutai/harness")
    except Exception as exc:  # noqa: BLE001 — a mutation that raises IS the failure, caught here
        st = f"<raised {exc!r}>"
    check("board_stations: item from another repository is EXCLUDED",
          isinstance(st, dict) and 99 not in st, repr(st))
    # THE READ HALF OF THE CASE BOUNDARY (FEAT-41 T-02): the board answered "Building", and what
    # comes back is lowercase. Asserting the capitalised form is ABSENT is the half that catches
    # a pass-through implementation, since "Building" == "Building" would satisfy a value check.
    check("board_stations: a board value is lowercased on read",
          isinstance(st, dict) and st.get(326) == "building", repr(st))
    # T-02's REQUIRED CASE, named explicitly: a board value of "Review" reads back as "review".
    check('board_stations lowercases a board value of "Review" to "review"',
          isinstance(st, dict) and st.get(328) == "review", repr(st))
    check("board_stations: no capitalised station survives the read",
          isinstance(st, dict)
          and not any(isinstance(v, str) and v != v.lower() for v in st.values()), repr(st))
    check("board_stations: item with NO status key is present with value None, not dropped",
          isinstance(st, dict) and 327 in st and st[327] is None, repr(st))

with tempfile.TemporaryDirectory() as tmp:
    # Isolated fixture: exactly one node, content null, nothing else — a mutation that crashes
    # on null content reddens only this block, never the three checks above.
    fake_gh(tmp, json.dumps({
        "data": {"user": {"projectV2": {"items": {
            "totalCount": 1,
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [
                {"content": None, "fieldValueByName": None},
            ],
        }}}}
    }))
    board = {"owner": "mruangutai", "number": 3, "station_field": "Status"}
    try:
        st = gh_board.board_stations(board, "mruangutai/harness")
    except Exception as exc:  # noqa: BLE001
        st = f"<raised {exc!r}>"
    check("board_stations: item with content null does not crash and is not in output",
          isinstance(st, dict) and len(st) == 0, repr(st))

# ---------------- read_station ----------------

# read_station is a pure lookup and never converts case; its inputs come from board_stations,
# which has already lowercased them.
stations = {326: "building", 327: None}
check("read_station: on the board with a station -> (station, None)",
      gh_board.read_station(stations, 326) == ("building", None))
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
        gh_board.set_station(board, "mruangutai/harness", 326, "building")
    except gh_board.BoardError as exc:
        raised = exc
    except Exception as exc:  # noqa: BLE001 — any other type is itself the failure
        raised = exc
    check("set_station: a failing gh raises BoardError",
          isinstance(raised, gh_board.BoardError), type(raised).__name__)
    text = str(raised) if raised else ""
    # THE MESSAGE NAMES THE STATION THE CALLER ASKED FOR, LOWERCASE — not the derived column.
    # The caller can grep its own source for "building"; "Building" appears nowhere it wrote.
    check("set_station: the error NAMES the issue number and the lowercase station attempted",
          "326" in text and "building" in text and "Building" not in text, text)

# T-02's REQUIRED CASE: set_station is the write half of the case boundary, so what reaches
# factory_gh.project_field_set must be the COLUMN, from a lowercase station in. This is asserted
# by capturing the argument rather than by reading the board back, because the conversion is the
# whole behaviour under test and a round-trip through a fake would hide a missing derivation.
_captured = {}


def _capture_field_set(owner, number, item_id, field, value, _c=_captured):
    _c["value"] = value


_orig_field_set = gh_board.factory_gh.project_field_set
_orig_item_id = gh_board.factory_gh.issue_board_item_id
try:
    gh_board.factory_gh.project_field_set = _capture_field_set
    gh_board.factory_gh.issue_board_item_id = lambda repo, num, board_number: "ITEM-1"
    gh_board.set_station(
        {"owner": "mruangutai", "number": 3, "station_field": "Status"},
        "mruangutai/harness", 326, "done",
    )
    check('set_station passes "Done" to project_field_set when given "done"',
          _captured.get("value") == "Done", _captured)

    # A station outside the six must raise FleetError and write NOTHING. It is LET PROPAGATE
    # rather than wrapped in BoardError: the fault is in the caller's vocabulary, not on the
    # board, and nothing should reach GitHub.
    _captured.clear()
    try:
        gh_board.set_station(
            {"owner": "mruangutai", "number": 3, "station_field": "Status"},
            "mruangutai/harness", 326, "Done",
        )
        check("set_station raises FleetError on a capitalised station and writes nothing",
              False, "did not raise")
    except factory_config.FleetError:
        check("set_station raises FleetError on a capitalised station and writes nothing",
              "value" not in _captured, _captured)
finally:
    gh_board.factory_gh.project_field_set = _orig_field_set
    gh_board.factory_gh.issue_board_item_id = _orig_item_id

print()
if FAILURES:
    print(f"{len(FAILURES)} FAIL")
    sys.exit(1)
print("all pass")


# --------------------------------------------------------------- project (FEAT-41 T-06) ------
# ONE function answers "which card goes where", so plan.yaml is the only input to the answer.
# Every value it returns is a LOWERCASE station; station_column is the one place a column name
# is produced, and project never calls it.
def _rec(issues=None, parent=None, source_issues=None):
    return {"issues": issues or {}, "parent": parent, "source_issues": source_issues or []}


def _plan(*statuses, top=None):
    doc = {"tasks": [{"id": f"T-{i:02d}", "status": s} for i, s in enumerate(statuses, 1)]}
    if top is not None:
        doc["status"] = top
    return doc


# --- each task sub-issue gets ITS OWN task's station, verbatim ---
_p = gh_board.project(_plan("building", "ready", "done"),
                      _rec(issues={"T-01": 11, "T-02": 12, "T-03": 13}))
check("project: each task card gets its own task's station",
      _p[11] == "building" and _p[12] == "ready" and _p[13] == "done", repr(_p))

# --- THE DELETED EXCEPTION (D-11). A task at ready projects to READY, never to backlog. This
# --- is the rule the old check-state.sh _EXPECT comment carried on the grounds that gh-sync
# --- open lands every sub-issue in backlog. It is gone, and T-10 settles the consequence.
_p = gh_board.project(_plan("ready", "ready"), _rec(issues={"T-01": 21, "T-02": 22}))
check("project: a ready task projects to ready, NOT to backlog",
      _p[21] == "ready" and _p[22] == "ready" and "backlog" not in _p.values(), repr(_p))

# --- TERMINAL FIRST, and the ordering is load-bearing. Every shipped feature has all tasks
# --- done, so derive_station returns review for all of them; derive-first would drag 22
# --- shipped parents backwards off Done. Measured at 8f8a6a3 against live board 3.
_p = gh_board.project(_plan("done", "done", top="done"), _rec(issues={}, parent=99))
check("project: a done top-level station beats derive_station's review (terminal first)",
      _p.get(99) == "done", repr(_p))

# --- A TERMINAL_MARKER card is ABSENT, never placed. D-05 says the marker names no column;
# --- this is where that becomes true. Without it FEAT-28 — abandoned, card at Done — becomes
# --- a write of a column that does not exist.
_p = gh_board.project(_plan("done", "done", top=factory_config.TERMINAL_MARKER),
                      _rec(issues={}, parent=98))
check("project: a TERMINAL_MARKER feature places NO parent card",
      98 not in _p, repr(_p))

# --- the parent, when not terminal, takes derive_station ---
_p = gh_board.project(_plan("done", "building"), _rec(issues={}, parent=97))
check("project: a non-terminal parent takes derive_station",
      _p.get(97) == "building", repr(_p))

# --- top-level station when there is no derivation ---
_p = gh_board.project(_plan("done", "ready", top="plan"), _rec(issues={}, parent=96))
check("project: with no derivation the parent takes the top-level station",
      _p.get(96) == "plan", repr(_p))

# --- ABSENT and ILLEGAL are DIFFERENT outcomes and must not share a code path. No derivation
# --- and no top-level station means the parent is absent — the same silence derive_station
# --- already returns — never a guess.
_p = gh_board.project(_plan("done", "ready"), _rec(issues={}, parent=95))
check("project: no derivation and no top-level station leaves the parent ABSENT",
      95 not in _p, repr(_p))

# --- source issues take the parent's station ---
_p = gh_board.project(_plan("building"), _rec(issues={}, parent=94, source_issues=[901, 902]))
check("project: each source issue takes the parent's station",
      _p.get(901) == "building" and _p.get(902) == "building", repr(_p))

_p = gh_board.project(_plan("done", "ready"), _rec(issues={}, source_issues=[903]))
check("project: with no parent station the source issues are absent too",
      903 not in _p, repr(_p))

# --- A VOCABULARY MISS IS THE ONE CASE THAT MUST NOT BE SILENT: it is the defect this feature
# --- exists to end. It names the task id AND the value.
for _bad in ("pending", "Building", "shipped"):
    _raised = None
    try:
        gh_board.project(_plan(_bad), _rec(issues={"T-01": 31}))
    except factory_config.FleetError as exc:
        _raised = str(exc)
    check(f"project: task station {_bad!r} raises FleetError naming the task and the value",
          _raised is not None and "T-01" in _raised and _bad in _raised, repr(_raised))

# --- it performs no I/O and produces no column: the returned values are stations, and a
# --- station's column differs from its name for every one of the six.
_p = gh_board.project(_plan("review"), _rec(issues={"T-01": 41}))
check("project: the value is a station, never a column",
      _p[41] == "review" and _p[41] != factory_config.station_column("review"), repr(_p))
