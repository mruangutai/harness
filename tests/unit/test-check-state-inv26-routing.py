#!/usr/bin/env python3
"""check_state.board.inv_26 routes each feature's card read by its own binding (#2180).

In-process, with no subprocess and no network. The real gh_board supplies the projection and
comparison. Only its one GitHub read, `board_stations_for`, is replaced by a recorder, and the
binding resolver by a table. Every case calls the PUBLIC `inv_26(ctx)`, so it grades the
behaviour and not the helper layout: at the pre-fix tree, each case fails on routing or on an
escaped GhError, never on a missing name.

    ./test-check-state-inv26-routing.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import tempfile
import types

import artifact_accessors  # noqa: E402
import factory_gh  # noqa: E402
import gh_board  # noqa: E402
from check_state import board  # noqa: E402

FAILURES = []
_STATIONS = ["backlog", "plan", "ready", "building", "review", "done"]
_OWNER = ("org/repo", {"owner": "org", "number": 3, "station_field": "status",
                       "stations": _STATIONS})
_PROD = ("org/prod", {"owner": "org", "number": 9, "station_field": "status",
                      "stations": _STATIONS})


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


class _Ctx:
    """The slice of check_state's Ctx that INV-26 reads, the pre-#2180 slice included (H,
    fpath), so the cases grade the same public call against either tree."""

    def __init__(self, root, cj, features, gh_ok=True):
        self.root, self.cj, self._gh_ok = root, cj, gh_ok
        self.H = os.path.join(root, ".harness")
        self.fpath = lambda feat, name: os.path.join(".harness", "harness", "features", feat, name)
        self.features = sorted(features)
        self._docs = {f: doc for f, (doc, _plan) in features.items()}
        self.plan_docs = {f: plan for f, (_doc, plan) in features.items()}
        self.probed = 0

    def gh_ok(self, _gh_bin):
        self.probed += 1
        return self._gh_ok

    def station(self, feat):
        return self.plan_docs[feat]["status"]

    def record(self, feat):
        return self._docs[feat], None


def _feature(issues, parent, repo=None):
    doc = {"github": {"milestone": 1, "parent": parent, "issues": issues, "source_issues": []}}
    if repo:
        doc["factory"] = {"repo": repo}
    plan = {"status": "building",
            "tasks": [{"id": t, "status": "building"} for t in sorted(issues)]}
    return doc, plan


def _modules(cards, bindings, fail=None):
    """(gb, fs, log): gh_board with a recording read, and a table-driven resolver."""
    log = {"reads": [], "resolved": []}

    def board_stations_for(board_cfg, repo, numbers):
        # The real read's contract: absent = not on the board, values lowercased on read.
        log["reads"].append((repo, board_cfg["number"], sorted(numbers)))
        if repo in (fail or {}):
            raise factory_gh.GhError(["api", "graphql"], 1, "", fail[repo],
                                     "gh api graphql failed", "api graphql", "gh: " + fail[repo])
        held = cards.get(repo, {})
        return {n: held[n].lower() for n in numbers if n in held}

    def resolve_binding(doc, _root):
        repo = doc["factory"]["repo"]
        log["resolved"].append(repo)
        if repo not in bindings:
            raise artifact_accessors.FleetError("repository not in fleet", repo, "known repos: org/prod")
        return bindings[repo][0], bindings[repo][1], {}

    gb = types.ModuleType("gh_board")
    gb.__dict__.update(gh_board.__dict__)
    gb.board_stations_for = board_stations_for
    fs = types.SimpleNamespace(
        has_repository_binding=lambda doc: bool((doc.get("factory") or {}).get("repo")),
        resolve_binding=resolve_binding)
    return gb, fs, log


def _run(features, cards, bindings=None, fail=None, owner_sync=True, gh_ok=True):
    gb, fs, log = _modules(cards, bindings if bindings is not None else {"org/prod": _PROD}, fail)
    real_load = board.harness_boundary.load_repo_module
    with tempfile.TemporaryDirectory() as root:
        cj = {"github": {"sync": owner_sync, "repo": _OWNER[0], "board": _OWNER[1]}}
        os.makedirs(os.path.join(root, ".harness"))
        with open(os.path.join(root, ".harness", "harness.json"), "w") as f:
            json.dump(cj, f)
        ctx = _Ctx(root, cj, features, gh_ok)
        board.harness_boundary.load_repo_module = {"gh_board": gb, "feature_schema": fs}.get
        try:
            bad, _warn = board.inv_26(ctx)
        except factory_gh.GhError as error:
            bad = [f"ESCAPED GhError: {error}"]
        finally:
            board.harness_boundary.load_repo_module = real_load
    return bad, log, ctx


def _has(bad, *needles):
    return any(all(n in line for n in needles) for line in bad)


def case_bound_and_owner_read_separately():
    features = {"FEAT-O": _feature({"T-01": 41}, 40),
                "FEAT-P": _feature({"T-01": 41, "T-02": 17}, 16, "org/prod")}
    cards = {"org/repo": {40: "Building", 41: "Building"},
             "org/prod": {16: "Building", 17: "Building", 41: "Review"}}
    bad, log, _ctx = _run(features, cards)
    reads = sorted(log["reads"])
    check("u.1 each binding is read once, for its own numbers only",
          reads == [("org/prod", 9, [16, 17, 41]), ("org/repo", 3, [40, 41])], f"reads={reads}")
    check("u.1 the bound card is judged on its own board; the owner twin is clean",
          _has(bad, "FEAT-P", "T-01", "review") and not _has(bad, "FEAT-O"), f"bad={bad}")


def case_owner_sync_off_keeps_bound():
    features = {"FEAT-O": _feature({"T-01": 41}, 40),
                "FEAT-P": _feature({"T-01": 17}, 16, "org/prod")}
    cards = {"org/prod": {16: "Building", 17: "Backlog"}}
    bad, log, _ctx = _run(features, cards, owner_sync=False)
    check("u.2 owner sync off: the unbound feature is skipped, the bound one still read",
          log["reads"] == [("org/prod", 9, [16, 17])] and _has(bad, "FEAT-P", "T-01", "backlog"),
          f"reads={log['reads']} bad={bad}")


def case_failed_read_is_cannot_verify():
    features = {"FEAT-O": _feature({"T-01": 41}, 40),
                "FEAT-P": _feature({"T-01": 17}, 16, "org/prod")}
    cards = {"org/repo": {40: "Building", 41: "Backlog"}}
    bad, _log, _ctx = _run(features, cards,
                           fail={"org/prod": "Could not resolve to an Issue with the number of 17."})
    check("u.3 a GhError read is CANNOT VERIFY naming the feature and GitHub's answer",
          _has(bad, "CANNOT VERIFY", "FEAT-P", "Could not resolve")
          and not any("ESCAPED" in line for line in bad), f"bad={bad}")
    check("u.3 the healthy owner feature beside it is still compared",
          _has(bad, "FEAT-O", "T-01", "backlog"), f"bad={bad}")


def case_unresolvable_binding():
    features = {"FEAT-O": _feature({"T-01": 41}, 40),
                "FEAT-M": _feature({"T-01": 17}, 16, "org/gone")}
    cards = {"org/repo": {40: "Building", 41: "Building"}}
    bad, log, _ctx = _run(features, cards)
    check("u.4 an unresolvable binding is CANNOT VERIFY naming the feature and the error",
          _has(bad, "CANNOT VERIFY", "FEAT-M", "org/gone"), f"bad={bad}")
    check("u.4 its numbers never reach the owner read",
          log["reads"] == [("org/repo", 3, [40, 41])], f"reads={log['reads']}")


def case_offline_records_nothing():
    features = {"FEAT-P": _feature({"T-01": 17}, 16, "org/prod")}
    bad, log, ctx = _run(features, {}, gh_ok=False)
    check("u.5 unauthenticated gh: no finding, no read, no binding resolution",
          bad == [] and log == {"reads": [], "resolved": []} and ctx.probed == 1,
          f"bad={bad} log={log} probed={ctx.probed}")


def case_nothing_in_flight_probes_nothing():
    features = {"FEAT-O": _feature({}, 40)}
    bad, log, ctx = _run(features, {})
    check("u.6 no recorded issue anywhere: gh is not even probed",
          bad == [] and ctx.probed == 0 and log["reads"] == [], f"probed={ctx.probed}")


def main():
    case_bound_and_owner_read_separately()
    case_owner_sync_off_keeps_bound()
    case_failed_read_is_cannot_verify()
    case_unresolvable_binding()
    case_offline_records_nothing()
    case_nothing_in_flight_probes_nothing()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
