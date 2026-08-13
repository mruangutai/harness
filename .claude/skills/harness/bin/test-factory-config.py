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

FAILS = 0
RAN = 0


def check(name, cond, detail=""):
    global FAILS, RAN
    RAN += 1
    if cond:
        print(f"ok    {name}")
    else:
        FAILS += 1
        print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))


def good_fleet_dict(workspace_root="/tmp/does-not-need-to-exist/factories"):
    """The board is PER-REPO (FEAT-16 T-08) — there is no top-level `board:` any more. Every
    repos entry carries its own board mapping."""
    return {
        "schema": "factory-fleet/1",
        "repos": [
            {
                "name": "mruangutai/harness",
                "default_branch": "main",
                "board": {
                    "owner": "mruangutai",
                    "number": 3,
                    "station_field": "Status",
                    "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
                },
            },
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


# --- 1. a well-formed fleet loads and its values round-trip -----------------------------
with tempfile.TemporaryDirectory() as td:
    good = good_fleet_dict()
    path = write_fleet(td, good)
    fleet = fc.load_fleet(path)
    check("(1) load_fleet round-trips board.owner",
          fleet["repos"][0]["board"]["owner"] == "mruangutai")
    check("(1) load_fleet round-trips repos[0].name",
          fleet["repos"][0]["name"] == "mruangutai/harness")
    check("(1) load_fleet round-trips workspace_root",
          fleet["workspace_root"] == good["workspace_root"])

# --- 2-10. the nine validation failures --------------------------------------------------
BAD_CASES = []


def add_bad_case(name, mutate):
    BAD_CASES.append((name, mutate))


def mut_schema(d):
    d["schema"] = "factory-fleet/2"


def mut_board_missing(d):
    del d["repos"][0]["board"]


def mut_board_not_mapping(d):
    d["repos"][0]["board"] = "not-a-mapping"


def mut_owner_empty(d):
    d["repos"][0]["board"]["owner"] = ""


def mut_number_not_int(d):
    d["repos"][0]["board"]["number"] = "3"


def mut_station_field_empty(d):
    d["repos"][0]["board"]["station_field"] = ""


def mut_stations_wrong_keys(d):
    d["repos"][0]["board"]["stations"] = {"ready": "Ready", "building": "Building"}


def mut_top_level_board_present(d):
    # A leftover top-level `board:` key is now an ERROR, never an ignored key (FEAT-16 T-08).
    d["board"] = {
        "owner": "mruangutai",
        "number": 9,
        "station_field": "Status",
        "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
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
add_bad_case("(3) a repos entry has no board", mut_board_missing)
add_bad_case("(4) repos[].board is not a mapping", mut_board_not_mapping)
add_bad_case("(5) repos[].board.owner is empty", mut_owner_empty)
add_bad_case("(6) repos[].board.number is not an int", mut_number_not_int)
add_bad_case("(7) repos[].board.station_field is empty", mut_station_field_empty)
add_bad_case(
    "(8) repos[].board.stations does not carry exactly ready/building/review",
    mut_stations_wrong_keys)
add_bad_case("(8b) a leftover top-level board key raises FleetError", mut_top_level_board_present)
add_bad_case("(9) repos is missing", mut_repos_missing)
add_bad_case("(10) a repo entry lacks a slash in its name", mut_repo_entry_bad)
add_bad_case("(11) workspace_root is not absolute", mut_workspace_root_relative)

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
        # (em dash U+2014, matching factory_cli.body / the C-3 checks above); "repos[].board"
        # appears only in THIS next_step — the per-repo-missing-board error says
        # "repos[<name>].board", never the bracket-empty form.
        check("(8b) the message names key 'board' exactly", "invalid: board —" in str(e), str(e))
        check("(8b) the next_step mentions repos[].board", "repos[].board" in str(e), str(e))

# also cover: repos is empty, repos is not a list, a repo lacks default_branch
for name, mutate in [
    ("(12) repos is empty", lambda d: d.__setitem__("repos", [])),
    ("(13) repos is not a list", lambda d: d.__setitem__("repos", {"a": 1})),
    ("(14) a repo entry lacks default_branch",
     lambda d: d.__setitem__("repos", [{"name": "o/r"}])),
    ("(14b) repos[].board.stations carries an empty value",
     lambda d: d["repos"][0]["board"].__setitem__(
         "stations", {"ready": "", "building": "Building", "review": "Review"})),
    ("(14c) repos[].board.number is a bool, not an int",
     lambda d: d["repos"][0]["board"].__setitem__("number", True)),
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

# --- 13 (grammar): every collected FleetError message obeys C-3 ---------------------------
check("(15) at least 9 FleetError messages were collected", len(RAISED_MESSAGES) >= 9,
      f"n={len(RAISED_MESSAGES)}")
for m in RAISED_MESSAGES:
    check(f"(15) FleetError message obeys C-3: {m[:70]!r}",
          "—" in m and "FleetError" not in m and "Traceback" not in m,
          f"msg={m!r}")

# --- 11. repo_entry on an unlisted name ----------------------------------------------------
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
# the only station lookup (see the "(29)/(30) board_station" checks below), so there is no
# standalone "(18)/(19) station" case here any more.

# --- 12b. per-repo board: board_for, board_station, and the four repos-prefixed field rules --


def board_dict(number, ready="Ready", building="Building", review="Review"):
    return {
        "owner": "mruangutai",
        "number": number,
        "station_field": "Status",
        "stations": {"ready": ready, "building": building, "review": review},
    }


def per_repo_fleet_dict(workspace_root="/tmp/does-not-need-to-exist/factories"):
    """A fleet whose single repos entry carries its own board."""
    return {
        "schema": "factory-fleet/1",
        "repos": [
            {"name": "mruangutai/harness", "default_branch": "main", "board": board_dict(3)},
        ],
        "workspace_root": workspace_root,
    }


def two_repo_fleet_dict(workspace_root="/tmp/does-not-need-to-exist/factories"):
    """Two repos entries, each carrying its own board on a different board number."""
    return {
        "schema": "factory-fleet/1",
        "repos": [
            {"name": "mruangutai/harness", "default_branch": "main", "board": board_dict(3)},
            {
                "name": "mruangutai/kaya-ai",
                "default_branch": "master",
                "board": board_dict(2, ready="Todo"),
            },
        ],
        "workspace_root": workspace_root,
    }


with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, per_repo_fleet_dict()))
    check("(25) a fleet whose single repos entry carries its own board loads",
          fleet["repos"][0]["board"]["number"] == 3)
    check("(25) 'board' is absent from the loaded fleet — there is no top-level block",
          "board" not in fleet)

with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, two_repo_fleet_dict()))
    check("(26) board_for returns repos[0]'s own board number",
          fc.board_for(fleet, "mruangutai/harness")["number"] == 3)
    check("(26) board_for returns repos[1]'s own board number",
          fc.board_for(fleet, "mruangutai/kaya-ai")["number"] == 2)

with tempfile.TemporaryDirectory() as td:
    d = deep_copy(two_repo_fleet_dict())
    del d["repos"][1]["board"]
    path = write_fleet(td, d)
    try:
        fc.load_fleet(path)
        check("(27) a repos entry with no board raises FleetError", False, "did not raise")
    except fc.FleetError as e:
        check("(27) a repos entry with no board raises FleetError", True)
        check("(27) the message names the repository missing its board",
              "repos[mruangutai/kaya-ai].board" in str(e), str(e))

REPO_BOARD_BAD_CASES = []


def add_repo_board_bad_case(name, mutate):
    REPO_BOARD_BAD_CASES.append((name, mutate))


def mut_repo_board_owner_empty(d):
    d["repos"][0]["board"]["owner"] = ""


def mut_repo_board_number_not_int(d):
    d["repos"][0]["board"]["number"] = "3"


def mut_repo_board_station_field_empty(d):
    d["repos"][0]["board"]["station_field"] = ""


def mut_repo_board_stations_wrong_keys(d):
    d["repos"][0]["board"]["stations"] = {"ready": "Ready", "building": "Building"}


add_repo_board_bad_case("(28a) repos[].board.owner is empty", mut_repo_board_owner_empty)
add_repo_board_bad_case("(28b) repos[].board.number is not an int", mut_repo_board_number_not_int)
add_repo_board_bad_case(
    "(28c) repos[].board.station_field is empty", mut_repo_board_station_field_empty)
add_repo_board_bad_case(
    "(28d) repos[].board.stations does not carry exactly ready/building/review",
    mut_repo_board_stations_wrong_keys)

for name, mutate in REPO_BOARD_BAD_CASES:
    with tempfile.TemporaryDirectory() as td:
        d = deep_copy(per_repo_fleet_dict())
        mutate(d)
        path = write_fleet(td, d)
        try:
            fc.load_fleet(path)
            check(name, False, "did not raise FleetError")
        except fc.FleetError as e:
            check(name, "repos[mruangutai/harness].board." in str(e), str(e))
        except Exception as e:
            check(name, False, f"raised {type(e).__name__}: {e}")

with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, two_repo_fleet_dict()))
    check("(29) board_station returns the per-repo ready option when the entry has its own "
          "board", fc.board_station(fleet, "mruangutai/kaya-ai", "ready") == "Todo")

with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, per_repo_fleet_dict()))
    try:
        fc.board_station(fleet, "mruangutai/harness", "nonexistent")
        check("(30) board_station raises FleetError on an unknown key", False, "did not raise")
    except fc.FleetError as e:
        check("(30) board_station raises FleetError on an unknown key", True)

with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, per_repo_fleet_dict()))
    try:
        fc.board_for(fleet, "someone/unlisted")
        check("(31) board_for on an unlisted repository raises FleetError", False, "did not raise")
    except fc.FleetError as e:
        check("(31) board_for on an unlisted repository raises FleetError", True)
        check("(31) the message names the unlisted repository", "someone/unlisted" in str(e), str(e))

# --- FLEET_PATH is absolute -------------------------------------------------------------
check("(20) FLEET_PATH is an absolute path", os.path.isabs(fc.FLEET_PATH), fc.FLEET_PATH)

# --- CLAUDE_PROJECT_DIR pointed at a dir with no probe file: discarded, announced, still works
_saved_env = os.environ.get("CLAUDE_PROJECT_DIR")
try:
    with tempfile.TemporaryDirectory() as td:
        os.environ["CLAUDE_PROJECT_DIR"] = td
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            root = fc.harness_root()
        check("(21) a CLAUDE_PROJECT_DIR with no probe file is discarded",
              root != td, root)
        check("(21) discarding it is announced on stderr", err.getvalue().strip() != "",
              "stderr was empty")
        check("(21) the returned root still has a readable probe file",
              os.access(os.path.join(root, "docs", "harness", "SPEC.md"), os.R_OK), root)
finally:
    if _saved_env is None:
        os.environ.pop("CLAUDE_PROJECT_DIR", None)
    else:
        os.environ["CLAUDE_PROJECT_DIR"] = _saved_env

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
