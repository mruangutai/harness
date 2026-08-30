#!/usr/bin/env python3
"""Tests for factory_config.py, the only reader of .harness/factory/fleet.yaml (SC-08).

WHY: every other factory tool takes its repository and board from this module and never from
the working directory. The two collapse-to-cwd defects this module exists to close are: (1) a
relative FLEET_PATH, which would resolve against whatever directory the tool happens to be run
from — catastrophic for factory_workspace.py and factory_land.py, which run inside a CHECKOUT OF
ANOTHER REPOSITORY; and (2) an unlisted repository read as though it were configured, because
nothing rejects it. Both are asserted here directly, along with the C-3 stream contract on
--show and the nine ways a fleet file can be malformed. Nothing here spawns a subprocess (this
file is UNIT, not INTEGRATION, for exactly that reason).

FEAT-24 T-02: the board no longer lives in fleet.yaml. A fleet member's board is read from ITS
OWN repository's .harness/harness.json at its default_branch — factory_config.product_config /
board_for — via one gh api read, faked here by monkeypatching factory_gh.file_at_ref on the
imported module object (fc.factory_gh.file_at_ref). No case in this file may invoke gh or make a
network call, and no case may call load_fleet() with no argument — FLEET_PATH binds at import to
the LIVE repository's fleet.yaml, so an omitted path passes for the wrong reason.
"""
import ast
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

import yaml

import factory_config as fc
import harness_boundary as hb

FAILS = 0
RAN = 0


def check(name, cond, detail=""):
    global FAILS, RAN
    # FEAT-24 T-02 MEMO TRAP GUARD: clear_product_config_memo() is the FIRST statement, so every
    # case begins with an empty memo — the PREVIOUS case's check() call already emptied it here.
    # This is structural, not conventional: a case that wants two (or more) memo-sensitive calls
    # counted together (e.g. two board_for calls whose combined call count it asserts) MUST make
    # ALL of them before invoking check(), because Python evaluates the `cond` argument before
    # calling check() — so the calls happen, then the memo clears. The memoisation case below
    # already does this.
    fc.clear_product_config_memo()
    RAN += 1
    if cond:
        print(f"ok    {name}")
    else:
        FAILS += 1
        print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))


@contextlib.contextmanager
def patched_file_at_ref(func):
    """Monkeypatch factory_gh.file_at_ref on the imported module object — never gh, never a
    network call — for the life of the `with` block."""
    saved = fc.factory_gh.file_at_ref
    fc.factory_gh.file_at_ref = func
    try:
        yield
    finally:
        fc.factory_gh.file_at_ref = saved


def good_fleet_dict(workspace_root="/tmp/does-not-need-to-exist/factories"):
    """FEAT-24 T-02: the board is no longer part of a fleet declaration at all. Every repos entry
    here carries only name and default_branch; the board is read remotely per repository (see
    board_for / product_config below)."""
    return {
        "schema": "factory-fleet/1",
        "repos": [
            {"name": "mruangutai/harness", "default_branch": "main"},
        ],
        "workspace_root": workspace_root,
    }


def write_fleet(dirpath, data):
    path = os.path.join(dirpath, "fleet.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return path


def deep_copy(d):
    return json.loads(json.dumps(d))


SIX_STATIONS = ("backlog", "plan", "ready", "building", "review", "done")


def full_stations(*, drop=None, extra=None, replace=None):
    """The station DECLARATION, which FEAT-41 T-01 makes an ordered LOWERCASE LIST rather than a
    mapping of six keys to six operator-chosen column names. There are no per-station overrides
    any more, and that absence is the point: the column name is DERIVED by
    factory_config.station_column, so a fixture cannot express a renamed column because the
    declaration cannot either.

    drop removes one station, extra appends one, replace substitutes the whole list — the three
    shapes the rejection cases need.
    """
    if replace is not None:
        # NOT list(replace) — that would turn a MAPPING into its list of keys, i.e. into the
        # valid declaration, and the pre-FEAT-41-mapping rejection case would pass while
        # asserting nothing. replace is substituted verbatim, whatever its container.
        return replace
    st = list(SIX_STATIONS)
    if drop is not None:
        st.remove(drop)
    if extra is not None:
        st.append(extra)
    return st


def board_dict(number, **station_kwargs):
    """A valid board mapping. stations is the ordered lowercase list mandated by FEAT-41 T-01
    (was a six-key mapping under FEAT-24 T-02 / D-06, widened to six by FEAT-33 T-02)."""
    return {
        "owner": "mruangutai",
        "number": number,
        "station_field": "Status",
        "stations": full_stations(**station_kwargs),
    }


def config_doc(board):
    """The shape product_config returns: a full document with a github block holding board —
    never a bare board mapping, because that is what the real remote file looks like."""
    return {"github": {"board": board}}


# --- 1. a well-formed fleet loads and its values round-trip -----------------------------
with tempfile.TemporaryDirectory() as td:
    good = good_fleet_dict()
    path = write_fleet(td, good)
    fleet = fc.load_fleet(path)
    check("(1) load_fleet round-trips repos[0].name",
          fleet["repos"][0]["name"] == "mruangutai/harness")
    check("(1) load_fleet round-trips workspace_root",
          fleet["workspace_root"] == good["workspace_root"])
    # NOTE: "(1) load_fleet round-trips board.owner" is REMOVED — load_fleet no longer carries a
    # board at all (repos[].board is now a REJECTED shape, see (load_fleet rejects a repos entry
    # carrying a board key) below). Its coverage relocates to "board_for resolves through
    # product_config", which asserts the returned board's owner field against a remote stub.

# --- (3) INVERTED: a repos entry with no board is now the CORRECT shape -------------------
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict()))
    check("(3) a repos entry has no board — this is the correct shape now",
          "board" not in fleet["repos"][0])
    # Also folds old (25)'s "'board' is absent from the loaded fleet" assertion — there is no
    # per-repo board in the loaded fleet at all any more, not merely no top-level block.

# --- 2-10 (subset). the surviving fleet-shape validation failures --------------------------
BAD_CASES = []


def add_bad_case(name, mutate):
    BAD_CASES.append((name, mutate))


def mut_schema(d):
    d["schema"] = "factory-fleet/2"


def mut_top_level_board_present(d):
    # A leftover top-level `board:` key is still an ERROR, never an ignored key (FEAT-16 T-08,
    # kept unchanged by FEAT-24 T-02 item 4).
    d["board"] = {
        "owner": "mruangutai",
        "number": 9,
        "station_field": "Status",
        "stations": ["ready", "building", "review"],
    }


def mut_repos_missing(d):
    del d["repos"]


def mut_repo_entry_bad(d):
    d["repos"] = [{"name": "no-slash-here", "default_branch": "main"}]


def mut_workspace_root_relative(d):
    d["workspace_root"] = "relative/path"


def mut_workspace_root_is_filesystem_root(d):
    # Review panel, 2026-08-11. "/" passes isabs and inverts the write guard:
    # check-domain.sh refuses any path under workspace_root belonging to no declared
    # repo, so with "/" every path on the machine is under it and /tmp/scratch.py
    # flips from no-verdict to BLOCKED — the opposite of REQ-05. Fails closed, so it
    # never wrongly permits; it still teaches an agent the guard is broken.
    d["workspace_root"] = "/"


add_bad_case("(2) schema is not factory-fleet/1", mut_schema)
add_bad_case("(2b) workspace_root is a filesystem root", mut_workspace_root_is_filesystem_root)
add_bad_case("(8b) a leftover top-level board key raises FleetError", mut_top_level_board_present)
add_bad_case("(9) repos is missing", mut_repos_missing)
add_bad_case("(10) a repo entry lacks a slash in its name", mut_repo_entry_bad)
add_bad_case("(11) workspace_root is not absolute", mut_workspace_root_relative)
# REMOVED from this loop: (3) [inverted, see above], (4)-(8) [repos[].board.* shapes — that
# entire code path is GONE from load_fleet after T-02 item 3; their coverage relocates to the
# eight "board_for raises naming the file and the key: <shape>" cases below, which drive the SAME
# eight malformed shapes through the surviving entry point, board_for/validate_board].

RAISED_MESSAGES = []

for name, mutate in BAD_CASES:
    with tempfile.TemporaryDirectory() as td:
        d = deep_copy(good_fleet_dict())
        mutate(d)
        path = write_fleet(td, d)
        try:
            fc.load_fleet(path)
            check(name, False, "did not raise FleetError")
        except fc.FleetError as e:
            RAISED_MESSAGES.append(str(e))
            check(name, True)
        except Exception as e:
            check(name, False, f"raised {type(e).__name__}: {e}")

# --- (8b) explicit key/next_step for a leftover top-level board key -----------------------
with tempfile.TemporaryDirectory() as td:
    d = deep_copy(good_fleet_dict())
    mut_top_level_board_present(d)
    path = write_fleet(td, d)
    try:
        fc.load_fleet(path)
        check("(8b) a leftover top-level board key raises FleetError", False, "did not raise")
    except fc.FleetError as e:
        check("(8b) a leftover top-level board key raises FleetError", True)
        # Discriminating, not "board" / "repos" substrings (those appear in almost every
        # FleetError this loader raises). "invalid: board —" pins the key to exactly "board"
        # (em dash U+2014, matching factory_cli.body / the C-3 checks above). "whole-fleet
        # board" pins the next_step to the TOP-LEVEL case specifically: FEAT-24 T-02 also
        # rejects a per-entry repos[].board key (:188-194), whose own message names
        # github.board and .harness/harness.json — both of which also appear in the
        # top-level message below, so neither alone would discriminate the two. "whole-fleet
        # board" appears nowhere else in factory_config.py (grep -c == 1) and only in the
        # top-level next_step, never the per-entry one.
        check("(8b) the message names key 'board' exactly", "invalid: board —" in str(e), str(e))
        check("(8b) the next_step names the whole-fleet key, not repos[].board",
              "whole-fleet board" in str(e), str(e))
        # The two checks above both pin the OFFENDING KEY (once via the "invalid: board —"
        # preamble, once via "whole-fleet board" naming which of the two board-shaped messages
        # this is) — neither pins the DESTINATION the operator is told to look at. Without a
        # present-AND-absent pair on the destination itself, a future edit could send this
        # message back to naming repos[].board, or drop the destination clause entirely, and
        # nothing here would redden. "github.board" alone does NOT discriminate this message from
        # the per-entry one at :188-194 (it appears in both) — it does not need to, since the two
        # checks above already establish WHICH message this is; this pair's job is the CONTENT of
        # the destination clause, not the message's identity. Mirrors plan.yaml:564-568's
        # present-AND-absent idiom for board_for's own owner/board pinning.
        check("(8b) the next_step points at github.board", "github.board" in str(e), str(e))
        check("(8b) the next_step no longer points at repos[].board",
              "repos[].board" not in str(e), str(e))

# also cover: repos is empty, repos is not a list, a repo lacks default_branch, workspace_root
# is missing
for name, mutate in [
    ("(12) repos is empty", lambda d: d.__setitem__("repos", [])),
    ("(13) repos is not a list", lambda d: d.__setitem__("repos", {"a": 1})),
    ("(14) a repo entry lacks default_branch",
     lambda d: d.__setitem__("repos", [{"name": "o/r"}])),
    ("(14d) workspace_root is missing", lambda d: d.pop("workspace_root")),
]:
    with tempfile.TemporaryDirectory() as td:
        d = deep_copy(good_fleet_dict())
        mutate(d)
        path = write_fleet(td, d)
        try:
            fc.load_fleet(path)
            check(name, False, "did not raise FleetError")
        except fc.FleetError as e:
            RAISED_MESSAGES.append(str(e))
            check(name, True)
        except Exception as e:
            check(name, False, f"raised {type(e).__name__}: {e}")
# REMOVED from this loop: (14b) repos[].board.stations empty value, (14c) repos[].board.number is
# a bool. Both drove board shapes through load_fleet, a path that is gone. (14b)'s coverage
# relocates to "board_for raises naming the file and the key: a station value is empty" below.
# (14c)'s coverage relocates to the direct validate_board() bool-rejection case below (kept under
# its own name, driven through the surviving public validator directly rather than through
# board_for, since it is testing validate_board's own isinstance/bool guard, not the remote-read
# plumbing).

# --- (14c) RELOCATED: validate_board still rejects a bool for number, driven directly -------
_bool_board = board_dict(3)
_bool_board["number"] = True
try:
    fc.validate_board(_bool_board, "github.board", "test-path")
    check("(14c) repos[].board.number is a bool, not an int", False, "did not raise")
except fc.FleetError:
    check("(14c) repos[].board.number is a bool, not an int", True)
except Exception as e:
    check("(14c) repos[].board.number is a bool, not an int", False, f"{type(e).__name__}: {e}")

# --- (6)/(28b) RELOCATED: a digit string is now VALID and is coerced to an int (item 2c) -----
_digit_board = board_dict(3)
_digit_board["number"] = "3"
try:
    _digit_result = fc.validate_board(_digit_board, "github.board", "test-path")
    _digit_ok = (_digit_result["number"] == 3 and isinstance(_digit_result["number"], int)
                 and not isinstance(_digit_result["number"], bool))
except Exception as e:
    _digit_ok, _digit_result = False, f"{type(e).__name__}: {e}"
check("(6)/(28b) validate_board coerces a digit string number to an int",
      _digit_ok, _digit_result)

# --- (15) (grammar): every collected FleetError message obeys C-3 -------------------------
check("(15) at least 9 FleetError messages were collected", len(RAISED_MESSAGES) >= 9,
      f"n={len(RAISED_MESSAGES)}")
for m in RAISED_MESSAGES:
    check(f"(15) FleetError message obeys C-3: {m[:70]!r}",
          "—" in m and "FleetError" not in m and "Traceback" not in m,
          f"msg={m!r}")

# --- (16)/(17). repo_entry on a listed and an unlisted name ---------------------------------
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict()))
    entry = fc.repo_entry(fleet, "mruangutai/harness")
    check("(16) repo_entry finds the listed repo", entry["default_branch"] == "main")
    try:
        fc.repo_entry(fleet, "someone/unlisted")
        check("(17) repo_entry raises FleetError for an unlisted name", False, "did not raise")
    except fc.FleetError as e:
        check("(17) repo_entry raises FleetError for an unlisted name", True)
        check("(17) the message names the unlisted name", "someone/unlisted" in str(e), str(e))

# NOTE: the two-argument station(fleet, key) was deleted in FEAT-16 T-08 — board_station is now
# the only station lookup (see the "(29)/(30)/(31) board_station"/"board_for" checks below), so
# there is no standalone "(18)/(19) station" case here any more.

# --- load_fleet REJECTS a repos entry carrying a board key (FEAT-24 T-02 item 3, D-08) --------
# This is the INVERSION of old (27)/(27b): under FEAT-16 T-08 an ABSENT per-repo board raised;
# under FEAT-24 T-02 a PRESENT one does. Same underlying "the board's home is enforced" property,
# proved in the opposite direction now that the home moved off fleet.yaml entirely.
with tempfile.TemporaryDirectory() as td:
    d = deep_copy(good_fleet_dict())
    d["repos"][0]["board"] = board_dict(3)
    path = write_fleet(td, d)
    try:
        fc.load_fleet(path)
        check("load_fleet rejects a repos entry carrying a board key", False, "did not raise")
    except fc.FleetError as e:
        msg = str(e)
        check("load_fleet rejects a repos entry carrying a board key",
              "repos[mruangutai/harness].board" in msg and "github.board" in msg
              and ".harness/harness.json" in msg, msg)
    except Exception as e:
        check("load_fleet rejects a repos entry carrying a board key", False,
              f"{type(e).__name__}: {e}")

# --- load_fleet still requires repos[].name, repos[].default_branch and workspace_root --------


def _raises_fleeterror(mutate_fn):
    with tempfile.TemporaryDirectory() as td:
        d = deep_copy(good_fleet_dict())
        mutate_fn(d)
        path = write_fleet(td, d)
        try:
            fc.load_fleet(path)
            return False
        except fc.FleetError:
            return True
        except Exception:
            return False


_name_bad = _raises_fleeterror(lambda d: d["repos"][0].__setitem__("name", "no-slash"))
_default_branch_missing = _raises_fleeterror(lambda d: d["repos"][0].pop("default_branch"))
_workspace_root_missing = _raises_fleeterror(lambda d: d.pop("workspace_root"))
check("load_fleet still requires repos[].name, repos[].default_branch and workspace_root",
      _name_bad and _default_branch_missing and _workspace_root_missing,
      (_name_bad, _default_branch_missing, _workspace_root_missing))

# --- validate_board: the ordered lowercase station LIST, accept/reject (FEAT-41 T-01) --------
# The pre-FEAT-41 form of this block used an independent per-key oracle (Col-BK/Col-PL/...)
# because the declaration carried six operator-chosen column names and comparing the returned
# mapping to the input mapping would have been x == x. THE ORACLE IS GONE BECAUSE THE FREEDOM IS
# GONE: the declaration is now exactly one list, the column names are derived by station_column,
# and the only accepting shape is list(MANDATED_STATIONS) in order. What replaces the oracle is
# station_column's own per-station assertions further down — one case per station, never a set
# comparison — which is where a wrong capitalisation can still be caught.
_list_board = board_dict(3)
try:
    _result = fc.validate_board(_list_board, "github.board", "test-path")
    _stations = _result["stations"]
    _ok = (
        _result is _list_board
        and tuple(_stations) == fc.MANDATED_STATIONS
        and isinstance(_stations, tuple)
    )
except Exception as e:
    _ok, _stations = False, f"{type(e).__name__}: {e}"
check("validate_board accepts the ordered lowercase station list, returns the board, and "
      "carries stations as a tuple of the six", _ok, _stations)

for _key in SIX_STATIONS:
    _board = board_dict(3, drop=_key)
    try:
        fc.validate_board(_board, "github.board", "test-path")
        check(f"validate_board rejects a station list missing {_key}", False, "did not raise")
    except fc.FleetError as e:
        check(f"validate_board rejects a station list missing {_key}",
              "github.board.stations" in str(e), str(e))
    except Exception as e:
        check(f"validate_board rejects a station list missing {_key}", False,
              f"{type(e).__name__}: {e}")

# (a) T-01's own case: a declaration that RENAMES one station is refused, and the message names
# the offending key. This is the shape an operator reaches for first — the board column is called
# "Icebox", so they rename the station to match — and it is exactly what FEAT-41 forbids: the six
# names are fixed and the COLUMN is derived from them, never the other way round.
for _key in SIX_STATIONS:
    _renamed = [("icebox" if s == _key else s) for s in SIX_STATIONS]
    _board = board_dict(3, replace=_renamed)
    try:
        fc.validate_board(_board, "github.board", "test-path")
        check(f"validate_board refuses a declaration that renames {_key}", False, "did not raise")
    except fc.FleetError as e:
        check(f"validate_board refuses a declaration that renames {_key}",
              "github.board.stations" in str(e), str(e))
    except Exception as e:
        check(f"validate_board refuses a declaration that renames {_key}", False,
              f"{type(e).__name__}: {e}")

# (b) the six names in a different ORDER is refused. The list is ordered because the order IS the
# workflow; a set comparison here would pass and is the reason this case is written per-rotation
# rather than once.
for _shift in range(1, 6):
    _rotated = list(SIX_STATIONS[_shift:]) + list(SIX_STATIONS[:_shift])
    _board = board_dict(3, replace=_rotated)
    try:
        fc.validate_board(_board, "github.board", "test-path")
        check(f"validate_board refuses the six names rotated by {_shift}", False, "did not raise")
    except fc.FleetError as e:
        check(f"validate_board refuses the six names rotated by {_shift}",
              "github.board.stations" in str(e), str(e))
    except Exception as e:
        check(f"validate_board refuses the six names rotated by {_shift}", False,
              f"{type(e).__name__}: {e}")

# A MAPPING is now the wrong shape outright — this is the pre-FEAT-41 declaration, and it must be
# refused rather than silently accepted by an implementation that only checks membership.
_mapping_board = board_dict(3, replace={k: k.capitalize() for k in SIX_STATIONS})
try:
    fc.validate_board(_mapping_board, "github.board", "test-path")
    check("validate_board refuses the pre-FEAT-41 six-key MAPPING", False, "did not raise")
except fc.FleetError as e:
    check("validate_board refuses the pre-FEAT-41 six-key MAPPING",
          "github.board.stations" in str(e), str(e))
except Exception as e:
    check("validate_board refuses the pre-FEAT-41 six-key MAPPING", False,
          f"{type(e).__name__}: {e}")

# The remedy line must name the exact list to write, or the operator cannot act on the refusal.
try:
    fc.validate_board(board_dict(3, drop="done"), "github.board", "test-path")
    _remedy_ok, _remedy = False, "did not raise"
except fc.FleetError as e:
    _remedy = str(e)
    _remedy_ok = all(s in _remedy for s in SIX_STATIONS)
check("validate_board's stations remedy names all six station names to write",
      _remedy_ok, _remedy)

# The five-station declaration .harness/harness.json carried before FEAT-33 widened it, now in
# list form. Kept because the file really held this shape once and a reader may still have it.
_five_pre_widening = board_dict(3, replace=["backlog", "ready", "building", "review", "done"])
try:
    fc.validate_board(_five_pre_widening, "github.board", "test-path")
    check("(X) validate_board rejects the five-station declaration carried before FEAT-33",
          False, "did not raise")
except fc.FleetError as e:
    check("(X) validate_board rejects the five-station declaration carried before FEAT-33",
          "github.board.stations" in str(e), str(e))
except Exception as e:
    check("(X) validate_board rejects the five-station declaration carried before FEAT-33",
          False, f"{type(e).__name__}: {e}")

# abandoned is NOT a seventh station. It names no board column and never reaches the board, so a
# declaration that adds it is refused exactly like any other extension.
_seven_board = board_dict(3, extra="abandoned")
try:
    fc.validate_board(_seven_board, "github.board", "test-path")
    check("(X) validate_board rejects a seventh station that adds abandoned", False,
          "did not raise")
except fc.FleetError:
    check("(X) validate_board rejects a seventh station that adds abandoned", True)
except Exception as e:
    check("(X) validate_board rejects a seventh station that adds abandoned", False,
          f"{type(e).__name__}: {e}")

# MANDATED_STATIONS must be exactly the six lowercase forms of feature-schema.json's status enum
# minus "Abandoned", read at runtime, so the two declarations cannot drift apart silently.
_schema_path = os.path.join(os.path.dirname(os.path.abspath(fc.__file__)), "feature-schema.json")
with open(_schema_path, encoding="utf-8") as f:
    _schema = json.load(f)
_schema_stations = {
    s.lower() for s in _schema["properties"]["status"]["enum"] if s != "Abandoned"
}
check("(X) MANDATED_STATIONS is exactly the six lowercase forms of feature-schema.json's status "
      "enum minus Abandoned",
      set(fc.MANDATED_STATIONS) == _schema_stations,
      (set(fc.MANDATED_STATIONS), _schema_stations))

# TERMINAL_MARKER is the schema's remaining status, lowercased — the one the six exclude. Pinning
# it against the schema is what stops it from silently becoming a seventh station later.
check("(X) TERMINAL_MARKER is the schema status the six stations exclude, lowercased",
      fc.TERMINAL_MARKER == "abandoned"
      and "Abandoned" in _schema["properties"]["status"]["enum"]
      and fc.TERMINAL_MARKER not in fc.MANDATED_STATIONS,
      (fc.TERMINAL_MARKER, _schema["properties"]["status"]["enum"]))

# --- station_column: the ONE place a capitalised station name is produced (FEAT-41 T-01) ------
# (c) ONE CASE PER STATION, never a set comparison. A set comparison passes when two stations
# swap their column names, and the whole purpose of this function is that the board column an
# agent writes is the one the board actually has.
_EXPECTED_COLUMNS = {
    "backlog": "Backlog", "plan": "Plan", "ready": "Ready",
    "building": "Building", "review": "Review", "done": "Done",
}
for _st, _col in _EXPECTED_COLUMNS.items():
    try:
        _got = fc.station_column(_st)
        _ok = _got == _col
    except Exception as e:
        _ok, _got = False, f"{type(e).__name__}: {e}"
    check(f"station_column({_st!r}) is exactly {_col!r}", _ok, _got)

# The six declared names must survive .capitalize() intact — the docstring's own claim. If a
# station were ever declared with an internal capital or a hyphen this would redden rather than
# silently producing a column the board does not have.
check("(X) every mandated station round-trips through station_column to a column that "
      "lowercases back to it",
      all(fc.station_column(s).lower() == s for s in fc.MANDATED_STATIONS),
      [(s, fc.station_column(s)) for s in fc.MANDATED_STATIONS])

# (d) station_column raises on TERMINAL_MARKER and on an already-capitalised name. The second is
# the likelier live mistake: a caller that has a column name and passes it back in would
# otherwise get "Done".capitalize() == "Done" and silently work, which is how a case boundary
# stops being a boundary.
for _bad in (fc.TERMINAL_MARKER, "Done", "Icebox", "", "DONE"):
    try:
        _got = fc.station_column(_bad)
        check(f"station_column({_bad!r}) raises FleetError", False, f"returned {_got!r}")
    except fc.FleetError as e:
        check(f"station_column({_bad!r}) raises FleetError",
              all(s in str(e) for s in SIX_STATIONS), str(e))
    except Exception as e:
        check(f"station_column({_bad!r}) raises FleetError", False,
              f"{type(e).__name__}: {e}")

# station_names returns the validated tuple, and is the accessor every other module uses instead
# of reaching into board["stations"] itself.
try:
    _names = fc.station_names(fc.validate_board(board_dict(3), "github.board", "test-path"))
    _names_ok = _names == fc.MANDATED_STATIONS and isinstance(_names, tuple)
except Exception as e:
    _names_ok, _names = False, f"{type(e).__name__}: {e}"
check("station_names returns the six mandated stations as a tuple", _names_ok, _names)

# --- board_for: the eight malformed shapes, driven through product_config + board_for ---------
# The SAME eight shapes T-04 drives through gh_board.load_board, driven here through the OTHER
# surviving validate_board caller, so the one validator is proved loud from both entry points.


def board_for_raise_case(shape_name, doc, present, absent=None,
                          repo="mruangutai/harness", branch="main"):
    with tempfile.TemporaryDirectory() as td:
        fleet = fc.load_fleet(write_fleet(td, good_fleet_dict()))
        with patched_file_at_ref(lambda r, p, ref, _doc=doc: json.dumps(_doc)):
            try:
                fc.board_for(fleet, repo)
                ok, msg = False, "did not raise"
            except fc.FleetError as e:
                msg = str(e)
                ok = (f"{repo}@{branch}:.harness/harness.json" in msg) and (present in msg)
                if absent is not None:
                    ok = ok and (absent not in msg)
            except Exception as e:
                ok, msg = False, f"{type(e).__name__}: {e}"
    check(f"board_for raises naming the file and the key: {shape_name}", ok, msg)


_b_owner_missing = board_dict(3)
del _b_owner_missing["owner"]
_b_number_not_int = board_dict(3)
_b_number_not_int["number"] = 2.5  # a FLOAT, never a digit string — item 2c makes "3" valid.
_b_station_field_missing = board_dict(3)
_b_station_field_missing["station_field"] = ""
_b_stations_missing = board_dict(3)
del _b_stations_missing["stations"]
_b_stations_key_set_wrong = board_dict(3, drop="done")
_b_station_value_empty = board_dict(3, replace=list(SIX_STATIONS[:-1]) + [""])

board_for_raise_case("no board key", {"github": {}}, present="github.board")
board_for_raise_case("board is not a mapping", {"github": {"board": "not-a-mapping"}},
                      present="github.board")
# THE where-CONTRACT PAIR (item 2a) is pinned on THIS shape — "owner missing" — matching T-04's
# load_board case on the SAME shape, so the contract is proved at both entry points.
board_for_raise_case("owner missing", config_doc(_b_owner_missing),
                      present="github.board.owner", absent="github.board.board")
board_for_raise_case("number not an int", config_doc(_b_number_not_int),
                      present="github.board.number")
board_for_raise_case("station_field missing", config_doc(_b_station_field_missing),
                      present="github.board.station_field")
board_for_raise_case("stations missing", config_doc(_b_stations_missing),
                      present="github.board.stations")
board_for_raise_case("stations key set wrong", config_doc(_b_stations_key_set_wrong),
                      present="github.board.stations")
board_for_raise_case("a station value is empty", config_doc(_b_station_value_empty),
                      present="github.board.stations")

# --- board_for raises when the product config declares no board (github block absent) --------
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict()))
    with patched_file_at_ref(lambda r, p, ref: json.dumps({})):
        try:
            fc.board_for(fleet, "mruangutai/harness")
            ok, msg = False, "did not raise"
        except fc.FleetError as e:
            ok, msg = True, str(e)
        except Exception as e:
            ok, msg = False, f"{type(e).__name__}: {e}"
    check("board_for raises when the product config declares no board", ok, msg)

# --- board_for resolves through product_config (relocates old (26), and (1)'s owner round-trip)
with tempfile.TemporaryDirectory() as td:
    _two_repo_fleet = {
        "schema": "factory-fleet/1",
        "repos": [
            {"name": "mruangutai/harness", "default_branch": "main"},
            {"name": "mruangutai/kaya-ai", "default_branch": "master"},
        ],
        "workspace_root": "/tmp/does-not-need-to-exist/factories",
    }
    fleet = fc.load_fleet(write_fleet(td, _two_repo_fleet))
    # BOTH repos now declare the SAME six stations, because FEAT-41 T-01 removed the freedom to
    # name a column per repo. What still varies per repo — and is what this case actually proves
    # board_for resolves — is the board NUMBER and the owner.
    _boards_by_repo = {
        "mruangutai/harness": board_dict(3),
        "mruangutai/kaya-ai": board_dict(2),
    }

    def _stub(repo, path, ref, _boards=_boards_by_repo):
        return json.dumps(config_doc(_boards[repo]))

    with patched_file_at_ref(_stub):
        _b1 = fc.board_for(fleet, "mruangutai/harness")
        _b2 = fc.board_for(fleet, "mruangutai/kaya-ai")
        _ok = (_b1["number"] == 3 and _b1["owner"] == "mruangutai"
               and _b2["number"] == 2
               and tuple(_b2["stations"]) == fc.MANDATED_STATIONS)
    check("board_for resolves through product_config", _ok, (_b1, _b2))

# --- product_config: no-checkout, remote-failure, no-fallback, memoisation (THE FIXTURE TRAP
# and THE MEMO TRAP) -------------------------------------------------------------------------

# (i) reads the remote at default_branch, with NO checkout present on disk.
with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as ws:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict(workspace_root=ws)))
    _repo = "mruangutai/harness"
    _board = board_dict(3)
    with patched_file_at_ref(lambda r, p, ref, _b=_board: json.dumps(config_doc(_b))):
        _no_checkout = not os.path.exists(fc.workspace_path(fleet, _repo))
        _result = fc.board_for(fleet, _repo)
        _ok = _no_checkout and _result["number"] == 3
    check("product_config reads the remote at default_branch with no checkout on disk",
          _ok, (_no_checkout, _result))

# (ii) a failing remote read raises FleetError naming repo, path and ref.
with tempfile.TemporaryDirectory() as td:
    # A distinctive default_branch (P-01: pick a value absent from every message's fixed prose)
    # so the ref assertion below cannot pass as a false-positive substring of unrelated text —
    # "main" is a 4-character token that could appear in ordinary next_step prose.
    _d = deep_copy(good_fleet_dict())
    _d["repos"][0]["default_branch"] = "trunk-xyzzy"
    fleet = fc.load_fleet(write_fleet(td, _d))

    def _boom(repo, path, ref):
        raise fc.factory_gh.GhError(
            ["gh", "api", "repos/mruangutai/harness/contents/.harness/harness.json"],
            1, "", "404", "gh call failed", "mruangutai/harness", "check gh auth and the ref",
        )

    with patched_file_at_ref(_boom):
        try:
            fc.product_config(fleet, "mruangutai/harness")
            _ok, _msg = False, "did not raise"
        except fc.FleetError as e:
            _msg = str(e)
            _ok = ("mruangutai/harness" in _msg and ".harness/harness.json" in _msg
                   and "trunk-xyzzy" in _msg)
        except Exception as e:
            _ok, _msg = False, f"{type(e).__name__}: {e}"
    check("product_config raises naming repo, path and ref when the remote read fails",
          _ok, _msg)

# (ii-b) the remote content is not JSON at all.
with tempfile.TemporaryDirectory() as td:
    _d = deep_copy(good_fleet_dict())
    _d["repos"][0]["default_branch"] = "trunk-not-json"
    fleet = fc.load_fleet(write_fleet(td, _d))

    with patched_file_at_ref(lambda r, p, ref: "not { valid json at all"):
        try:
            fc.product_config(fleet, "mruangutai/harness")
            _type_ok, _repo_ok, _path_ok, _ref_ok = False, False, False, False
            _msg = "did not raise"
        except fc.FleetError as e:
            _msg = str(e)
            _type_ok = True
            _repo_ok = "mruangutai/harness" in _msg
            _path_ok = ".harness/harness.json" in _msg
            _ref_ok = "trunk-not-json" in _msg
        except Exception as e:
            _type_ok, _repo_ok, _path_ok, _ref_ok = False, False, False, False
            _msg = f"{type(e).__name__}: {e}"
    check("product_config raises naming repo, path and ref when the remote content is not JSON",
          _type_ok and _repo_ok and _path_ok and _ref_ok, _msg)

# (ii-c) the remote content is JSON but not a mapping (a list here).
with tempfile.TemporaryDirectory() as td:
    _d = deep_copy(good_fleet_dict())
    _d["repos"][0]["default_branch"] = "trunk-not-mapping"
    fleet = fc.load_fleet(write_fleet(td, _d))

    with patched_file_at_ref(lambda r, p, ref: json.dumps([1, 2, 3])):
        try:
            fc.product_config(fleet, "mruangutai/harness")
            _type_ok, _repo_ok, _path_ok, _ref_ok = False, False, False, False
            _msg = "did not raise"
        except fc.FleetError as e:
            _msg = str(e)
            _type_ok = True
            _repo_ok = "mruangutai/harness" in _msg
            _path_ok = ".harness/harness.json" in _msg
            _ref_ok = "trunk-not-mapping" in _msg
        except Exception as e:
            _type_ok, _repo_ok, _path_ok, _ref_ok = False, False, False, False
            _msg = f"{type(e).__name__}: {e}"
    check("product_config raises naming repo, path and ref when the remote content is a JSON "
          "list, not a mapping",
          _type_ok and _repo_ok and _path_ok and _ref_ok, _msg)

# (iii) never falls back to a checkout, even when one exists on disk with a DIFFERENT board.
with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as ws:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict(workspace_root=ws)))
    _repo = "mruangutai/harness"
    _remote_board = board_dict(3)
    _checkout_board = board_dict(9)
    _checkout_dir = fc.workspace_path(fleet, _repo)
    os.makedirs(os.path.join(_checkout_dir, ".harness"), exist_ok=True)
    with open(os.path.join(_checkout_dir, ".harness", "harness.json"), "w", encoding="utf-8") as f:
        json.dump(config_doc(_checkout_board), f)
    with patched_file_at_ref(lambda r, p, ref, _b=_remote_board: json.dumps(config_doc(_b))):
        _result = fc.board_for(fleet, _repo)
        _ok = _result["number"] == 3
    check("product_config never falls back to a checkout", _ok, _result)

# (iii-b) FIX-C1 F-5: a failing remote read raises, even with a checkout PRESENT on disk carrying
# a valid board — D-03's clause is "no cached value is consulted when a read fails", and this is
# the one cell that clause depends on that no fixture in this file previously exercised. The
# checkout's board number (777333) is a value used nowhere else in this file, so a fallback would
# be caught either by the raise not happening or by the value leaking into the message.
with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as ws:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict(workspace_root=ws)))
    _repo = "mruangutai/harness"
    _stale_checkout_board = board_dict(777333)
    _checkout_dir = fc.workspace_path(fleet, _repo)
    os.makedirs(os.path.join(_checkout_dir, ".harness"), exist_ok=True)
    with open(os.path.join(_checkout_dir, ".harness", "harness.json"), "w", encoding="utf-8") as f:
        json.dump(config_doc(_stale_checkout_board), f)

    _stub_calls = []

    def _raising_stub_with_checkout(repo, path, ref, _calls=_stub_calls):
        _calls.append((repo, path, ref))
        raise fc.factory_gh.GhError(
            ["gh", "api", "repos/mruangutai/harness/contents/.harness/harness.json"],
            1, "", "500", "gh call failed", repo, "retry",
        )

    with patched_file_at_ref(_raising_stub_with_checkout):
        try:
            got = fc.board_for(fleet, _repo)
            _raised, _msg = False, "did not raise"
        except fc.FleetError as e:
            got, _raised, _msg = None, True, str(e)
    _ok = (_raised
           and len(_stub_calls) >= 1
           and "777333" not in _msg)
    check("product_config never falls back to a checkout on disk when the remote read fails",
          _ok, (got, _msg, _stub_calls))

# (iv) memoisation: a second board_for makes no second remote read; a failing read is never
# cached (both required by THE MEMO TRAP).
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict()))
    _repo = "mruangutai/harness"
    _board = board_dict(3)
    _calls = []

    def _counting_stub(repo, path, ref, _b=_board, _calls=_calls):
        _calls.append((repo, path, ref))
        return json.dumps(config_doc(_b))

    with patched_file_at_ref(_counting_stub):
        # Both memo-sensitive calls happen BEFORE the check() below, per the MEMO TRAP comment on
        # check() above — the cond is computed here, and only then does check() clear the memo.
        _b1 = fc.board_for(fleet, _repo)
        _b2 = fc.board_for(fleet, _repo)
        _mono_ok = len(_calls) == 1 and _b1 == _b2
    check("product_config memoises a successful read: a second board_for makes no second "
          "remote read", _mono_ok, (len(_calls), _b1, _b2))

    # A failing read must never be memoised: point the stub at a raiser, assert board_for raises,
    # then repoint it at a working stub and assert the NEXT call succeeds — WITHOUT an
    # intervening check() call, per the MEMO TRAP comment on check() above. An intervening
    # check() would clear the memo itself and let this assertion pass even if product_config
    # wrongly cached the failure, since the wipe (not the correct no-cache behaviour) would be
    # what makes the recovery call succeed.
    def _raising_stub(repo, path, ref):
        raise fc.factory_gh.GhError(["gh"], 1, "", "500", "gh call failed", repo, "retry")

    with patched_file_at_ref(_raising_stub):
        try:
            fc.board_for(fleet, _repo)
            _raised = False
        except fc.FleetError:
            _raised = True
        except Exception:
            _raised = False
    with patched_file_at_ref(lambda r, p, ref, _b=_board: json.dumps(config_doc(_b))):
        try:
            _recovered = fc.board_for(fleet, _repo)["number"] == 3
        except Exception:
            _recovered = False
    check("product_config memoisation: a failing read is not cached and the next call succeeds",
          _raised and _recovered, (_raised, _recovered))

# --- (29)/(30)/(31): board_station and board_for, via product_config stub -------------------
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, {
        "schema": "factory-fleet/1",
        "repos": [
            {"name": "mruangutai/harness", "default_branch": "main"},
            {"name": "mruangutai/kaya-ai", "default_branch": "master"},
        ],
        "workspace_root": "/tmp/does-not-need-to-exist/factories",
    }))
    _boards_by_repo = {
        "mruangutai/harness": board_dict(3),
        "mruangutai/kaya-ai": board_dict(2),
    }
    with patched_file_at_ref(
            lambda repo, path, ref, _boards=_boards_by_repo: json.dumps(config_doc(_boards[repo]))):
        _val = fc.board_station(fleet, "mruangutai/kaya-ai", "ready")
    # (29) NO LONGER "the per-repo ready OPTION": under FEAT-41 T-01 a repo cannot name its own
    # column, so what board_station returns is the DERIVED column for a station it has verified
    # the repo declares. The assertion is therefore station_column's output, not a fixture value —
    # and it must not be spelled "Ready" by hand here, or this case would pass against a
    # board_station that skipped the derivation and capitalised the key itself.
    check("(29) board_station returns the derived column for a station the repo's board declares",
          _val == fc.station_column("ready"), _val)

with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict()))
    with patched_file_at_ref(
            lambda r, p, ref, _b=board_dict(3): json.dumps(config_doc(_b))):
        try:
            fc.board_station(fleet, "mruangutai/harness", "nonexistent")
            check("(30) board_station raises FleetError on an unknown key", False, "did not raise")
        except fc.FleetError:
            check("(30) board_station raises FleetError on an unknown key", True)

with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict()))
    try:
        fc.board_for(fleet, "someone/unlisted")
        check("(31) board_for on an unlisted repository raises FleetError", False, "did not raise")
    except fc.FleetError as e:
        check("(31) board_for on an unlisted repository raises FleetError", True)
        check("(31) the message names the unlisted repository", "someone/unlisted" in str(e), str(e))

# --- FLEET_PATH is absolute -------------------------------------------------------------
check("(20) FLEET_PATH is an absolute path", os.path.isabs(fc.FLEET_PATH), fc.FLEET_PATH)

# --- HARNESS_PROJECT_DIR pointed at a dir with no MARKER: discarded, announced, and FLEET_PATH
# (bound at import from the SAME harness_boundary.resolve_root(fc._BIN_DIR) call) still sits
# under the root a fresh call falls back to — proving FLEET_PATH is wired through the shared
# resolver's discard-and-fallback behaviour, not merely coincidentally correct.
_saved_env = os.environ.get("HARNESS_PROJECT_DIR")
try:
    with tempfile.TemporaryDirectory() as td:
        os.environ["HARNESS_PROJECT_DIR"] = td
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            root = hb.resolve_root(fc._BIN_DIR)
        check("(21) a HARNESS_PROJECT_DIR with no MARKER is discarded",
              root != td, root)
        check("(21) discarding it is announced on stderr", err.getvalue().strip() != "",
              "stderr was empty")
        check("(21) the returned root still carries harness_boundary.MARKER",
              os.path.isfile(os.path.join(root, hb.MARKER)), root)
        check("(21) it is the same root factory_config.FLEET_PATH was built from",
              fc.FLEET_PATH.startswith(root + os.sep), (fc.FLEET_PATH, root))
finally:
    if _saved_env is None:
        os.environ.pop("HARNESS_PROJECT_DIR", None)
    else:
        os.environ["HARNESS_PROJECT_DIR"] = _saved_env

# --- workspace_path -----------------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, good_fleet_dict(workspace_root="/srv/factories")))
    check("(22) workspace_path joins workspace_root with the name after the slash",
          fc.workspace_path(fleet, "owner/name") == os.path.join("/srv/factories", "name"),
          fc.workspace_path(fleet, "owner/name"))
    check("(22) workspace_path does not use the owner-prefixed name",
          "owner/name" not in fc.workspace_path(fleet, "owner/name"))

# --- --show over a well-formed fleet: stdout parses as one json.loads ---------------------
with tempfile.TemporaryDirectory() as td:
    path = write_fleet(td, good_fleet_dict())
    out, err = io.StringIO(), io.StringIO()
    argv_saved = sys.argv
    sys.argv = ["factory_config.py", "--fleet", path, "--show"]
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                fc.factory_cli.run("config", fc._main, expected=(fc.FleetError,))
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = argv_saved
    check("(23) --show over a good fleet exits 0 (or None)", code in (0, None), f"code={code!r}")
    try:
        parsed = json.loads(out.getvalue())
        check("(23) --show's stdout parses as a single json.loads", True)
        check("(23) --show's payload has 'repos' and no top-level 'board'",
              "repos" in parsed and "board" not in parsed, parsed)
    except Exception as e:
        check("(23) --show's stdout parses as a single json.loads", False, str(e))

# --- --show over an invalid fleet: no stdout, one stderr line, exit 2 ---------------------
with tempfile.TemporaryDirectory() as td:
    d = deep_copy(good_fleet_dict())
    mut_schema(d)
    path = write_fleet(td, d)
    out, err = io.StringIO(), io.StringIO()
    argv_saved = sys.argv
    sys.argv = ["factory_config.py", "--fleet", path, "--show"]
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                fc.factory_cli.run("config", fc._main, expected=(fc.FleetError,))
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = argv_saved
    check("(24) --show over an invalid fleet writes nothing to stdout", out.getvalue() == "",
          repr(out.getvalue()))
    stderr_lines = [l for l in err.getvalue().split("\n") if l]
    check("(24) --show over an invalid fleet writes exactly one stderr line",
          len(stderr_lines) == 1, err.getvalue())
    check("(24) --show over an invalid fleet exits 2", code == 2, f"code={code!r}")


# ==========================================================================
# X — SC-18: "one fleet loader is the only reader of the fleet file," asserted STATICALLY, the
# same shape as SC-03's accepted evidence (a mechanical enumeration over factory_*.py), not by
# reading seven files.
#
# THE TRAP: "fleet.yaml" and "FLEET_PATH" are MENTIONED all over the codebase — in argparse
# --help strings, in an error message that PRINTS the resolved path, as a docstring word. A
# string-presence grep either false-positives on all of those or gets narrowed until it asserts
# nothing. The clause is about who OPENS/PARSES the fleet path, not who names it — so this
# enumerates actual `open(` / `harness_yaml.load_file(` CALL SITES via the AST — across every
# scope in a file: module scope itself, and every function/async function, so a module-scope
# read at import time is caught too, not just reads inside a `def` — and classifies each call's
# first argument as fleet-bearing two ways: (a) its source text names "fleet" (catches
# `args.fleet`, the `--fleet` CLI destination, any literal fleet.yaml path — the realistic shape
# a bypass would take), or (b) it is a parameter/local variable traced back, within the same
# scope, to a default value of `FLEET_PATH` (catches factory_config.py's own
# `load_fleet(path=FLEET_PATH)`, whose read call is `harness_yaml.load_file(path)` — the argument
# NAME says nothing about "fleet" at all, so (a) alone would miss the genuine reader).
# ==========================================================================

def _factory_files(bin_dir):
    return sorted(
        fn for fn in os.listdir(bin_dir)
        if fn.startswith("factory_") and fn.endswith(".py")
    )


def _is_fleet_default(node):
    """True when an expression is FLEET_PATH, `<x>.FLEET_PATH`, or an if-expression choosing
    between two such (the `args.fleet if args.fleet else factory_config.FLEET_PATH` shape)."""
    if isinstance(node, ast.Name) and node.id == "FLEET_PATH":
        return True
    if isinstance(node, ast.Attribute) and node.attr == "FLEET_PATH":
        return True
    if isinstance(node, ast.IfExp):
        return _is_fleet_default(node.body) or _is_fleet_default(node.orelse)
    return False


def _scope_body_walk(scope_node):
    """Like `ast.walk(scope_node)` but prunes at nested `FunctionDef`/`AsyncFunctionDef`
    boundaries: it yields the nested def itself (so callers can see it) but does not descend
    into its body — that body belongs to that def's own scope, enumerated separately. `ClassDef`
    and `Lambda` are NOT pruned: methods are reached and enumerated as their own scopes via the
    outer scope collection, and lambdas are not enumerated as scopes at all."""
    queue = list(ast.iter_child_nodes(scope_node))
    while queue:
        node = queue.pop(0)
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        queue.extend(ast.iter_child_nodes(node))


def _find_fleet_reads(bin_dir, files):
    """Enumerate every `open(` / `harness_yaml.load_file(` call across `files`, in `bin_dir`,
    whose first argument is fleet-path-bearing. Scans module scope and every function/async
    function scope (each pruned of its nested defs' bodies, so a call is attributed to exactly
    one scope). Returns (file, scopename, lineno, arg_source)."""
    hits = []
    for fname in files:
        path = os.path.join(bin_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src, filename=fname)
        scopes = [("<module>", tree)] + [
            (n.name, n) for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        for scope_name, func in scopes:
            args_node = getattr(func, "args", None)
            tainted = set()
            if args_node is not None:
                n_pos = len(args_node.args)
                n_def = len(args_node.defaults)
                for i, d in enumerate(args_node.defaults):
                    if _is_fleet_default(d):
                        tainted.add(args_node.args[n_pos - n_def + i].arg)
            for node in _scope_body_walk(func):
                if isinstance(node, ast.Assign):
                    tainted_rhs = _is_fleet_default(node.value) or (
                        isinstance(node.value, ast.Name) and node.value.id in tainted
                    )
                    if tainted_rhs:
                        for t in node.targets:
                            if isinstance(t, ast.Name):
                                tainted.add(t.id)
                if isinstance(node, ast.Call):
                    fn = node.func
                    is_load_file = (
                        isinstance(fn, ast.Attribute) and fn.attr == "load_file"
                        and isinstance(fn.value, ast.Name) and fn.value.id == "harness_yaml"
                    )
                    is_open = isinstance(fn, ast.Name) and fn.id == "open"
                    if not (is_load_file or is_open) or not node.args:
                        continue
                    arg0 = node.args[0]
                    arg_src = ast.unparse(arg0)
                    fleet_bearing = (
                        "fleet" in arg_src.lower()
                        or _is_fleet_default(arg0)
                        or (isinstance(arg0, ast.Name) and arg0.id in tainted)
                    )
                    if fleet_bearing:
                        hits.append((fname, scope_name, node.lineno, arg_src))
    return hits


_BIN_DIR = os.path.dirname(os.path.abspath(fc.__file__))
_FACTORY_FILES = _factory_files(_BIN_DIR)

# Self-test of _find_fleet_reads itself, against a throwaway fixture — not the real factory_*.py
# files — carrying exactly the two shapes a prior cut of the scanner silently missed: (a) a
# module-scope read (misses if `[("<module>", tree)]` is dropped from the scope list) and (b) a
# function-scope read reached only through an assign-chain, `_p = factory_config.FLEET_PATH` then
# `harness_yaml.load_file(_p)`, where `_p` is NOT fleet-bearing by source text (misses if the
# scope-body walk regresses from FIFO to LIFO, since the taint from `_p`'s Assign must be seen
# before the Call that reads it). A third, negative shape — a module-scope `os.path.join(...)`
# path computation, never passed to `open`/`load_file` — pins that it must NOT be reported.
_SELFTEST_SRC = (
    "import os\n"
    "import harness_yaml\n"
    "import factory_config\n"
    "\n"
    "_MODULE_PROBE = harness_yaml.load_file(factory_config.FLEET_PATH)\n"
    "\n"
    "_IGNORED_PATH = os.path.join('some', 'fleet.yaml')\n"
    "\n"
    "\n"
    "def _reader():\n"
    "    _p = factory_config.FLEET_PATH\n"
    "    harness_yaml.load_file(_p)\n"
)
_selftest_dir = tempfile.mkdtemp(prefix="factory-selftest-")
try:
    with open(os.path.join(_selftest_dir, "factory_selftest.py"), "w", encoding="utf-8") as f:
        f.write(_SELFTEST_SRC)
    _selftest_hits = _find_fleet_reads(_selftest_dir, ["factory_selftest.py"])
finally:
    shutil.rmtree(_selftest_dir, ignore_errors=True)
_selftest_scopes = sorted(h[1] for h in _selftest_hits)
_selftest_ok = len(_selftest_hits) == 2 and _selftest_scopes == ["<module>", "_reader"]

# Positive control: the enumeration must actually be scanning something real, or "nobody else
# reads the fleet" would hold vacuously for an empty file list — and _find_fleet_reads itself
# must find both the module-scope read and the assign-chain function-scope read in the fixture
# above, or the enumeration below is unprotected against the module-scope hole and the
# LIFO/FIFO taint-order regression that previously passed this suite silently.
check(
    "(X) sanity: factory_*.py enumeration is non-empty and includes factory_config.py, and "
    "_find_fleet_reads self-test finds both the module-scope read and the function-scope "
    "assign-chain read in a throwaway fixture, and reports nothing else (the negative "
    "os.path.join shape is not a hit)",
    len(_FACTORY_FILES) >= 4 and "factory_config.py" in _FACTORY_FILES and _selftest_ok,
    (_FACTORY_FILES, _selftest_hits),
)

_fleet_reads = _find_fleet_reads(_BIN_DIR, _FACTORY_FILES)
check(
    "(X) SC-18: exactly one scope, anywhere in factory_*.py (module scope or any function), "
    "opens/parses the fleet file",
    len(_fleet_reads) == 1,
    _fleet_reads,
)
check(
    "(X) SC-18: that one reader is factory_config.py's load_fleet — no other tool bypasses it",
    len(_fleet_reads) == 1 and _fleet_reads[0][0] == "factory_config.py"
    and _fleet_reads[0][1] == "load_fleet",
    _fleet_reads,
)


print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
