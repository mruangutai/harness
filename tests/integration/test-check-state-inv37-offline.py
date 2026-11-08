#!/usr/bin/env python3
"""check-state.py INV-37 grades a bound feature locally when gh is not authenticated (#2190).

With gh offline (tokenless CI), a bound feature's `factory.repo` is checked locally: it must be well-formed and present in fleet.yaml. Its receipt and provenance are graded against that repository, and no remote product-config read is made. With gh authenticated, full remote `resolve_binding` verification is unchanged, including a failed remote read being a violation (operator decision 2026-11-08, amending DEC-221).

Every `gh` call goes to a python fake on FACTORY_GH. The fake answers `auth status` as configured and logs every contents read, so "no remote read" is asserted, not assumed.

    ./test-check-state-inv37-offline.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import sys
import tempfile
from check_state_support import _run_with_gh_streams

BOUND = "FEAT-9002-bound-fixture"
OWNER = "FEAT-9003-owner-fixture"
_STATIONS = ["backlog", "plan", "ready", "building", "review", "done"]

_FAKE = r'''#!%(python)s
import base64, json, os, re, sys
args = sys.argv[1:]
here = os.path.dirname(os.path.abspath(__file__))
world = json.load(open(os.path.join(here, "world.json")))
if args[:2] == ["auth", "status"]:
    sys.exit(0 if world["online"] else 1)
if args[:1] == ["api"] and len(args) > 1 and "/contents/" in args[1]:
    with open(os.path.join(here, "contents.log"), "a") as log:
        log.write(args[1] + "\n")
    if not world["online"]:
        print("gh: To get started with GitHub CLI, please run:  gh auth login", file=sys.stderr)
        sys.exit(4)
    m = re.fullmatch(r"repos/([^/]+/[^/]+)/contents/\.harness/harness\.json\?ref=(.+)", args[1])
    doc = world["contents"].get(m[1]) if m else None
    if doc is None:
        print("gh: Not Found (HTTP 404)", file=sys.stderr)
        sys.exit(1)
    print(base64.b64encode(json.dumps(doc).encode()).decode())
    sys.exit(0)
print(json.dumps({"totalCount": 0, "items": []}))
'''


def _root(tmp, owner_sync=True, fleet=("org/prod",), online=False, remote=True):
    """Owner config (org/repo, no board), a fleet, and the fake gh with its world."""
    h = os.path.join(tmp, ".harness")
    os.makedirs(os.path.join(h, "factory"))
    with open(os.path.join(h, "harness.json"), "w") as f:
        json.dump({"github": {"sync": owner_sync, "repo": "org/repo", "board": None}}, f)
    with open(os.path.join(h, "factory", "fleet.yaml"), "w") as f:
        f.write("schema: factory-fleet/1\nrepos:\n")
        for name in fleet:
            f.write(f"  - name: {name}\n    default_branch: main\n")
        f.write(f"workspace_root: {tmp}\n")
    product = {"github": {"sync": True, "repo": "org/prod",
                          "board": {"owner": "org", "number": 9, "station_field": "Status",
                                    "stations": _STATIONS}}}
    with open(os.path.join(tmp, "world.json"), "w") as f:
        json.dump({"online": online, "contents": {"org/prod": product} if remote else {}}, f)
    fake = os.path.join(tmp, "gh")
    with open(fake, "w") as f:
        f.write(_FAKE % {"python": sys.executable})
    os.chmod(fake, 0o755)
    return h, fake


def _feature(h, segment, feat, github, factory=None):
    fd = os.path.join(h, segment, "features", feat)
    os.makedirs(fd)
    doc = {"feature_id": feat, "github": github}
    if factory is not None:
        doc["factory"] = factory
    with open(os.path.join(fd, "feature.json"), "w") as f:
        json.dump(doc, f)
    task = {"id": "T-01", "title": "fixture", "change_type": "bugfix",
            "execution_mode": "main-session-direct", "files": ["fixture"],
            "verify": "true", "intent": "fixture"}
    with open(os.path.join(fd, "plan.yaml"), "w") as f:
        f.write(f"schema: plan/1\nfeature: {feat}\nstatus: ready\ntasks:\n  - {json.dumps(task)}\n")


def _bound(h, github, repo="org/prod"):
    _feature(h, "prod", BOUND, github, {"repo": repo})


def _run(tmp, fake):
    """(INV-37 lines, contents reads made, traceback seen)."""
    _c, out, err = _run_with_gh_streams(tmp, fake)
    log = os.path.join(tmp, "contents.log")
    reads = open(log).read().split() if os.path.exists(log) else []
    return [l for l in out.splitlines() if "INV-37" in l], reads, "Traceback" in out + err


def _has(lines, *needles):
    return any(all(n in l for n in needles) for l in lines)


OPENED = {"build_entry": "opened", "repo": "org/prod"}


def _i1_offline_valid_opened_is_clean():
    with tempfile.TemporaryDirectory() as tmp:
        h, fake = _root(tmp)
        _bound(h, OPENED)
        lines, reads, tb = _run(tmp, fake)
    return ("(i.1) offline: a fleet-listed bound feature with an opened receipt for factory.repo "
            "is clean and reads nothing remote", not tb and not lines and reads == [],
            f"lines={lines} reads={reads}")


def _i2_offline_terminal_with_owner_sync_off_is_clean():
    with tempfile.TemporaryDirectory() as tmp:
        h, fake = _root(tmp, owner_sync=False)
        _bound(h, {"build_entry": "recovered-terminal", "repo": "org/prod"})
        lines, reads, tb = _run(tmp, fake)
    return ("(i.2) offline, owner sync off: a recovered-terminal bound receipt is clean",
            not tb and not lines and reads == [], f"lines={lines} reads={reads}")


def _offline_receipt_case(github):
    with tempfile.TemporaryDirectory() as tmp:
        h, fake = _root(tmp)
        _bound(h, github)
        lines, reads, tb = _run(tmp, fake)
    graded = (not tb and reads == [] and _has(lines, BOUND, "no usable Build-entry receipt")
              and not _has(lines, "invalid authoritative"))
    return graded, lines


def _i3_offline_missing_receipt_is_graded():
    ok, lines = _offline_receipt_case({})
    ok = ok and _has(lines, BOUND, "receipt absent or incomplete")
    return ("(i.3) offline: a missing receipt is the receipt finding, not a binding finding",
            ok, f"lines={lines}")


def _i4_offline_owner_repo_conflicts_with_factory_repo():
    ok, lines = _offline_receipt_case({"build_entry": "opened", "repo": "org/repo"})
    ok = ok and _has(lines, "'org/repo' conflicts with bound repository 'org/prod'")
    return ("(i.4) offline: github.repo naming the owner is graded against factory.repo",
            ok, f"lines={lines}")


def _i5_offline_unproven_active_mirror():
    ok, lines = _offline_receipt_case({"build_entry": "opened", "milestone": 1, "parent": 16})
    ok = ok and _has(lines, "nonempty mirror has no matching github.repo provenance")
    return ("(i.5) offline: an active bound mirror without github.repo stays unproven",
            ok, f"lines={lines}")


def _i6_offline_invalid_binding_still_fails():
    failures = []
    for repo in ("not a repository", 5, "", "org/gone"):
        with tempfile.TemporaryDirectory() as tmp:
            h, fake = _root(tmp)
            _bound(h, OPENED, repo=repo)
            lines, reads, tb = _run(tmp, fake)
        if tb or reads or not _has(lines, BOUND, "invalid authoritative repository binding"):
            failures.append((repo, lines, reads))
    return ("(i.6) offline: malformed, non-string, empty and unlisted factory.repo stay invalid "
            "authoritative bindings with no remote read", not failures, f"failures={failures}")


def _i7_online_matching_remote_is_clean_and_read():
    with tempfile.TemporaryDirectory() as tmp:
        h, fake = _root(tmp, online=True)
        _bound(h, OPENED)
        lines, reads, tb = _run(tmp, fake)
    return ("(i.7) online: full remote verification runs and a matching config is clean",
            not tb and not lines and any("repos/org/prod/contents/" in r for r in reads),
            f"lines={lines} reads={reads}")


def _i8_online_remote_failure_stays_a_violation():
    with tempfile.TemporaryDirectory() as tmp:
        h, fake = _root(tmp, online=True, remote=False)
        _bound(h, OPENED)
        lines, reads, tb = _run(tmp, fake)
    return ("(i.8) online: an unreadable remote product config is still an invalid binding",
            not tb and reads != [] and _has(lines, BOUND, "invalid authoritative repository binding"),
            f"lines={lines} reads={reads}")


def _i9_owner_controls_beside_a_bound_feature():
    results = {}
    for entry in ("opened", None):
        with tempfile.TemporaryDirectory() as tmp:
            h, fake = _root(tmp)
            _bound(h, OPENED)
            owner = {"build_entry": entry, "repo": "org/repo"} if entry else {}
            _feature(h, "harness", OWNER, owner)
            lines, _reads, tb = _run(tmp, fake)
        results[entry] = (tb, lines)
    clean_tb, clean = results["opened"]
    bad_tb, bad = results[None]
    ok = (not clean_tb and not bad_tb and not clean
          and _has(bad, OWNER, "receipt absent or incomplete") and not _has(bad, BOUND))
    return ("(i.9) offline: owner features keep their receipt results beside a clean bound one",
            ok, f"clean={clean} bad={bad}")


def main():
    scenarios = (_i1_offline_valid_opened_is_clean,
                 _i2_offline_terminal_with_owner_sync_off_is_clean,
                 _i3_offline_missing_receipt_is_graded,
                 _i4_offline_owner_repo_conflicts_with_factory_repo,
                 _i5_offline_unproven_active_mirror,
                 _i6_offline_invalid_binding_still_fails,
                 _i7_online_matching_remote_is_clean_and_read,
                 _i8_online_remote_failure_stays_a_violation,
                 _i9_owner_controls_beside_a_bound_feature)
    allok = True
    for name, ok, detail in (scenario() for scenario in scenarios):
        print(f"{'ok' if ok else 'FAIL'} - {name}")
        if not ok:
            print("      " + detail)
        allok = allok and ok
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
