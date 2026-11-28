"""factory_support.py — fleet fixtures and the in-process CLI driver shared by factory tests.

    from unit_support import ROOT                     # puts tests/ on sys.path
    from factory_support import (STATIONS, board, board_stub, fleet, invoke, repo,
                                 split_boards, write_fleet, write_yaml)

Fleet builders return fresh dicts; mutate them freely.
    STATIONS                          the mandated ordered station list (a tuple; board() copies it)
    board(owner, number, station_field)
                                      a repository's own github.board block
    repo(name, default_branch="main", board=None)
                                      one fleet repos[] entry; `board` is a TEST-SIDE carrier,
                                      included only when given and stripped by split_boards
    fleet(workspace_root, repos)      {"schema": "factory-fleet/1", "repos": repos, "workspace_root"}
    split_boards(fleet_dict) -> (clean_fleet, {repo_name: board})
                                      the fleet without repos[].board, and the boards it carried
    board_stub(boards_by_repo)        a stand-in for factory_config.product_config(fleet, repo_name)
                                      returning {"github": {"board": boards_by_repo.get(repo_name)}}
Files.
    write_yaml(path, data) -> path    yaml.safe_dump, parent directories created
    write_fleet(dirpath, data) -> path
                                      write_yaml(dirpath/fleet.yaml, data)
Driver.
    invoke(fn, argv=None) -> Invocation(code, raised, out, err)
        Calls fn() with stdout and stderr captured and, when argv is given, sys.argv swapped for
        the call and restored after. A SystemExit is caught and reported RAW: raised is True and
        code is SystemExit.code exactly, None included. A normal return gives raised False and
        code None. Callers differ on None versus 0 on purpose, so each coerces for itself
        (`code or 0`). Any other exception propagates after argv is restored.

Monkeypatching stays with the caller: use unittest.mock.patch.object(fc, "product_config",
board_stub(boards)) around invoke().
"""
import collections
import contextlib
import io
import os
import sys

import yaml

STATIONS = ("backlog", "plan", "ready", "building", "review", "done")

Invocation = collections.namedtuple("Invocation", "code raised out err")


def board(owner, number, station_field):
    return {"owner": owner, "number": number, "station_field": station_field,
            "stations": list(STATIONS)}


def repo(name, default_branch="main", board=None):
    entry = {"name": name, "default_branch": default_branch}
    if board is not None:
        entry["board"] = board
    return entry


def fleet(workspace_root, repos):
    return {"schema": "factory-fleet/1", "repos": list(repos), "workspace_root": workspace_root}


def split_boards(fleet_dict):
    boards = {}
    clean_repos = []
    for entry in fleet_dict["repos"]:
        entry = dict(entry)
        carried = entry.pop("board", None)
        if carried is not None:
            boards[entry["name"]] = carried
        clean_repos.append(entry)
    return dict(fleet_dict, repos=clean_repos), boards


def board_stub(boards_by_repo):
    def product_config(_fleet, repo_name):
        return {"github": {"board": boards_by_repo.get(repo_name)}}
    return product_config


def write_yaml(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle)
    return path


def write_fleet(dirpath, data):
    return write_yaml(os.path.join(dirpath, "fleet.yaml"), data)


def invoke(fn, argv=None):
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    if argv is not None:
        sys.argv = list(argv)
    code, raised = None, False
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                fn()
            except SystemExit as exc:
                code, raised = exc.code, True
    finally:
        sys.argv = saved_argv
    return Invocation(code, raised, out.getvalue(), err.getvalue())
