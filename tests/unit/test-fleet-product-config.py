#!/usr/bin/env python3
"""Tests for factory_config.product_config_report and factory_config's --check-product-configs
CLI flag (T-04, FEAT-56).

WHY: product_config_report is the fleet-wide reachability sweep every member's own
.harness/harness.json is proved reachable through before it is registered in fleet.yaml (D-04).
This file proves it drives product_config(fleet, name) once per declared repo, in declaration
order, catches only FleetError, and that the CLI flag turns an unreachable member into exit 2
(factory_cli.EXIT_REFUSED) while an all-reachable fleet exits 0.

Mirrors tests/unit/test-factory-config.py's conventions exactly: the same sys.path anchor
preamble, the same check()/FAILS/RAN accounting, and the same patched_file_at_ref contextmanager
shape that swaps fc.factory_gh.file_at_ref on the imported module object. This file is UNIT: no
subprocess, no gh, no network, and no case calls load_fleet() with no argument — FLEET_PATH binds
at import to the LIVE repository's fleet.yaml, so an omitted path would pass for the wrong
reason.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import contextlib
import io
import json
import sys
import tempfile

import yaml

import factory_config as fc

FAILS = 0
RAN = 0


def check(name, cond, detail=""):
    global FAILS, RAN
    # Same memo-trap guard test-factory-config.py's check() uses: clear the process memo as the
    # first statement of every check() call, so the NEXT case begins with an empty memo. A case
    # that wants two memo-sensitive calls counted together must make all of them before calling
    # check(), since Python evaluates `cond` before check() runs.
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


def two_repo_fleet_dict(workspace_root="/tmp/does-not-need-to-exist/factories"):
    """Two declared repos, in DECLARATION ORDER, so product_config_report's ordering claim and
    case (b)'s "exactly the first entry is not ok" claim both have something to distinguish."""
    return {
        "schema": "factory-fleet/1",
        "repos": [
            {"name": "mruangutai/repo-one", "default_branch": "trunk-report-one"},
            {"name": "mruangutai/repo-two", "default_branch": "trunk-report-two"},
        ],
        "workspace_root": workspace_root,
    }


def write_fleet(dirpath, data):
    path = _anchor_os.path.join(dirpath, "fleet.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return path


def run_main(argv):
    """Call fc._main() directly, in-process — never factory_cli.run — per T-04's own case (e):
    "assert SystemExit.code is 2 ... and that _main() returns without raising SystemExit". Both
    outcomes are asserted directly on _main() itself."""
    out, err = io.StringIO(), io.StringIO()
    argv_saved = sys.argv
    sys.argv = argv
    code, raised = None, False
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                fc._main()
            except SystemExit as e:
                raised = True
                code = e.code
    finally:
        sys.argv = argv_saved
    return code, raised, out.getvalue(), err.getvalue()


_FLEET = two_repo_fleet_dict()
_FIRST_NAME = _FLEET["repos"][0]["name"]
_FIRST_REF = _FLEET["repos"][0]["default_branch"]
_SECOND_NAME = _FLEET["repos"][1]["name"]


def stub_all_ok(repo, path, ref):
    return json.dumps({"read": "ok"})


def stub_first_gherror_second_ok(repo, path, ref, _first=_FIRST_NAME):
    """Raises factory_gh.GhError for the FIRST declared name, returns valid JSON for the
    second — case (b)'s exact shape."""
    if repo == _first:
        raise fc.factory_gh.GhError(
            ["gh", "api", f"repos/{repo}/contents/.harness/harness.json"],
            1, "", "404", "gh call failed", repo, "check gh auth and the ref",
        )
    return json.dumps({"read": "ok"})


def stub_first_not_json_second_ok(repo, path, ref, _first=_FIRST_NAME):
    """Returns invalid JSON for the FIRST declared name, valid JSON for the second — case (c)."""
    if repo == _first:
        return "not { valid json"
    return json.dumps({"read": "ok"})


# --- (a) two declared repos, stub returns valid JSON for both -> every entry ok --------------
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, two_repo_fleet_dict()))
    with patched_file_at_ref(stub_all_ok):
        report_a = fc.product_config_report(fleet)
    _a_all_ok = all(m["ok"] for m in report_a)
    _a_ok_count = sum(1 for m in report_a if m["ok"])
    _a_unreachable_count = len(report_a) - _a_ok_count
check("(a) two declared repos, both succeed -> every entry ok, ok count 2, unreachable 0",
      _a_all_ok and _a_ok_count == 2 and _a_unreachable_count == 0, report_a)
check("(a)/(d) len(report) equals len(fleet['repos'])",
      len(report_a) == len(fleet["repos"]), (len(report_a), len(fleet["repos"])))

# --- (b) stub raises GhError for the FIRST name, valid JSON for the second -------------------
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, two_repo_fleet_dict()))
    with patched_file_at_ref(stub_first_gherror_second_ok):
        report_b = fc.product_config_report(fleet)
    _b_entry0, _b_entry1 = report_b[0], report_b[1]
    _b_entry0_ok = (
        _b_entry0["ok"] is False
        and _b_entry0["repo"] == _FIRST_NAME
        and _FIRST_NAME in _b_entry0["detail"]
        and _FIRST_REF in _b_entry0["detail"]
    )
    _b_entry1_ok = (
        _b_entry1["ok"] is True
        and _b_entry1["repo"] == _SECOND_NAME
        and _b_entry1["detail"] == ""
    )
check("(b) the FIRST entry, asserted individually, is not ok and names repo and ref",
      _b_entry0_ok, _b_entry0)
check("(b) the SECOND entry, asserted individually, is ok with an empty detail",
      _b_entry1_ok, _b_entry1)
check("(b)/(d) len(report) equals len(fleet['repos'])",
      len(report_b) == len(fleet["repos"]), (len(report_b), len(fleet["repos"])))

# --- (c) stub returns invalid JSON for one repo -> that entry not ok, names invalid-JSON -----
with tempfile.TemporaryDirectory() as td:
    fleet = fc.load_fleet(write_fleet(td, two_repo_fleet_dict()))
    with patched_file_at_ref(stub_first_not_json_second_ok):
        report_c = fc.product_config_report(fleet)
    _c_entry0 = report_c[0]
    _c_ok = (_c_entry0["ok"] is False and "JSON" in _c_entry0["detail"]
             and _c_entry0["repo"] == _FIRST_NAME)
check("(c) invalid JSON content -> entry not ok, detail names the invalid-JSON failure",
      _c_ok, _c_entry0)
check("(c)/(d) len(report) equals len(fleet['repos'])",
      len(report_c) == len(fleet["repos"]), (len(report_c), len(fleet["repos"])))

# --- entries carry the exact declared keys, the module's own path constant, and declaration ---
# order (never a set/sorted comparison — order is the property under test).
_shape_ok = all(
    set(m.keys()) == {"repo", "ref", "path", "ok", "detail"} and m["path"] == fc._PRODUCT_CONFIG_PATH
    for m in report_a
)
check("every entry carries exactly repo/ref/path/ok/detail, path is _PRODUCT_CONFIG_PATH",
      _shape_ok, report_a)
check("product_config_report preserves fleet['repos'] declaration order",
      [m["repo"] for m in report_a] == [e["name"] for e in fleet["repos"]],
      ([m["repo"] for m in report_a], [e["name"] for e in fleet["repos"]]))

# --- (e) _main() exit codes, in-process, under --check-product-configs -----------------------

# (e-1) a failing member -> SystemExit.code == 2, and stdout still parses as the ONE payload.
with tempfile.TemporaryDirectory() as td:
    fleet_path = write_fleet(td, two_repo_fleet_dict())
    with patched_file_at_ref(stub_first_gherror_second_ok):
        code_e1, raised_e1, out_e1, err_e1 = run_main(
            ["factory_config", "--fleet", fleet_path, "--check-product-configs"]
        )
check("(e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing stub",
      raised_e1 and code_e1 == fc.factory_cli.EXIT_REFUSED, (raised_e1, code_e1))
try:
    _parsed_e1 = json.loads(out_e1)
    _payload_e1_ok = (
        isinstance(_parsed_e1, dict)
        and {"declared", "ok", "unreachable", "members"} <= set(_parsed_e1.keys())
        and _parsed_e1["declared"] == 2 and _parsed_e1["ok"] == 1 and _parsed_e1["unreachable"] == 1
    )
except Exception as _e:
    _payload_e1_ok, _parsed_e1 = False, f"{type(_e).__name__}: {_e}"
check("(e) stdout under failure parses as ONE JSON payload with declared/ok/unreachable/members",
      _payload_e1_ok, _parsed_e1)
check("(e) exactly one stderr line is written for the one unreachable member",
      len([l for l in err_e1.split("\n") if l]) == 1, repr(err_e1))

# (e-2) every member succeeds -> _main() returns without raising SystemExit.
with tempfile.TemporaryDirectory() as td:
    fleet_path = write_fleet(td, two_repo_fleet_dict())
    with patched_file_at_ref(stub_all_ok):
        code_e2, raised_e2, out_e2, err_e2 = run_main(
            ["factory_config", "--fleet", fleet_path, "--check-product-configs"]
        )
check("(e) --check-product-configs returns without SystemExit under an all-succeeding stub",
      not raised_e2, (raised_e2, code_e2))
try:
    _parsed_e2 = json.loads(out_e2)
    _payload_e2_ok = (
        isinstance(_parsed_e2, dict)
        and {"declared", "ok", "unreachable", "members"} <= set(_parsed_e2.keys())
        and _parsed_e2["declared"] == 2 and _parsed_e2["ok"] == 2 and _parsed_e2["unreachable"] == 0
    )
except Exception as _e:
    _payload_e2_ok, _parsed_e2 = False, f"{type(_e).__name__}: {_e}"
check("(e) stdout under success parses as ONE JSON payload with declared/ok/unreachable/members",
      _payload_e2_ok, _parsed_e2)
check("(e) no stderr line is written when nothing is unreachable",
      err_e2 == "", repr(err_e2))

print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
