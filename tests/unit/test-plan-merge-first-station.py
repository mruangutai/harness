#!/usr/bin/env python3
"""Unit floor for BUG-2420: `set-task-station` gives a task its FIRST station, in process.

A task drafted through `apply` carries no `status:` line of its own; `apply` ignores status on
existing items and `amend` refuses to add a field, so `set-task-station` is the one verb that can
lay the first station. Before the fix it exited 3 claiming the task was absent while listing it
as present. Three rows pin the contract: a status-less task gains its line at the task's field
indent, an existing line is rewritten with every other byte unchanged, and only a genuinely
absent task refuses. A fourth check proves the insert leaves a signed approval byte-identical,
and requires the insert to have SUCCEEDED, so an unchanged failed operation cannot satisfy it.

Drives the module's own `cmd_set_task_station` with the real destination guard, lock and atomic
writer, below the CLI subprocess the integration case drives.

    PLAN_MERGE_STATIONS=<path to stations.py>  optional: load a different stations.py (red runs)
    ./test-plan-merge-first-station.py         -> exit 0 all pass, 1 otherwise
"""
import argparse
import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))

import plan_merge  # noqa: E402,F401  the package must be importable before its stations module

_STATIONS = os.environ.get("PLAN_MERGE_STATIONS") or str(BIN / "plan_merge" / "stations.py")
_spec = importlib.util.spec_from_file_location("plan_merge.stations", _STATIONS)
stations = importlib.util.module_from_spec(_spec)
sys.modules["plan_merge.stations"] = stations
_spec.loader.exec_module(stations)

failures = []


def check(name, ok, detail=""):
    print("PASS" if ok else "FAIL", name, detail if not ok else "")
    if not ok:
        failures.append(name)


APPROVAL = ("approval:\n  date: '2026-11-22'\n  approved_by: Fixture Signer\n"
            "  status: approved\n")
# T-01's verify prose carries a `status:` line of its own: block-scalar text, never the task's
# station. PLAIN drops that prose, so the approval proof needs nothing but the first-station
# insert itself to succeed.
PLAN = ("schema: plan/1\nfeature: FEAT-99-fixture\n" + APPROVAL + "status: building\n"
        "tasks:\n"
        "- id: T-01\n  title: Drafted without a station\n  verify: |\n    status: prose\n"
        "- id: T-02\n  title: Already stationed\n  status: ready\n")
PLAIN = PLAN.replace("  verify: |\n    status: prose\n", "")


def set_station(plan_path, task, station):
    """(exit code, stdout, stderr) of one in-process set-task-station call."""
    out, err = io.StringIO(), io.StringIO()
    args = argparse.Namespace(file=str(plan_path), task=task, station=station)
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            stations.cmd_set_task_station(args)
            code = 0
        except SystemExit as stop:
            code = stop.code
    return code, out.getvalue(), err.getvalue()


def fixture(text=PLAN):
    """(root, plan path) for a fresh plan under a features directory the guard accepts."""
    root = Path(tempfile.mkdtemp(prefix="bug2420-"))
    feature = root / ".harness" / "harness" / "features" / "FEAT-99-fixture"
    feature.mkdir(parents=True)
    plan = feature / "plan.yaml"
    plan.write_text(text, encoding="utf-8")
    return root, plan


def changed_lines(before, after):
    """(lines only in before, lines only in after), each in text order."""
    b, a = before.splitlines(True), after.splitlines(True)
    return [x for x in b if x not in a], [y for y in a if y not in b]


# (row, task, station, expected exit, expected (removed, added) lines, stdout/stderr needles)
ROWS = (
    ("a status-less task gains its first station at its field indent",
     "T-01", "building", 0, ([], ["  status: building\n"]), ("STATION T-01 -> building",)),
    ("an existing status is rewritten and every other byte is unchanged",
     "T-02", "done", 0, (["  status: ready\n"], ["  status: done\n"]), ("STATION T-02 -> done",)),
    ("a genuinely absent task refuses with exit 3 and writes nothing",
     "T-09", "building", 3, ([], []), ("T-09", "T-01, T-02")),
)


def case_station_rows():
    for row, task, station, code, lines, needles in ROWS:
        root, plan = fixture()
        try:
            rc, out, err = set_station(plan, task, station)
            after = plan.read_text(encoding="utf-8")
            check(f"{row}: exit {code}", rc == code, f"rc={rc} out={out!r} err={err!r}")
            check(f"{row}: exactly the expected lines change", changed_lines(PLAN, after) == lines,
                  repr(changed_lines(PLAN, after)))
            check(f"{row}: reports its outcome", all(n in out + err for n in needles),
                  repr(out + err))
            check(f"{row}: prints APPLIED only on success", ("APPLIED" in out) == (code == 0),
                  repr(out))
        finally:
            shutil.rmtree(root, ignore_errors=True)


def case_first_station_lands_on_the_task_itself():
    """The inserted line belongs to T-01, not to its nested verify prose or to T-02."""
    root, plan = fixture()
    try:
        set_station(plan, "T-01", "building")
        lines = plan.read_text(encoding="utf-8").splitlines()
        t01 = lines.index("- id: T-01")
        check("the first station sits inside T-01's own mapping, before T-02",
              "  status: building" in lines[t01:lines.index("- id: T-02")], repr(lines))
        check("T-01's verify prose keeps its own `status: prose` line",
              "    status: prose" in lines, repr(lines))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_absent_task_message_is_about_absence():
    """The refusal names absence and the ids present, never a missing status field."""
    root, plan = fixture()
    try:
        _rc, _out, err = set_station(plan, "T-09", "building")
        check("the absent-task refusal never blames a status line", "status" not in err.lower(),
              repr(err))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_signed_approval_survives_the_first_station():
    """No re-sign: the insert succeeds and the approval block is byte-identical."""
    root, plan = fixture(PLAIN)
    try:
        rc, _out, _err = set_station(plan, "T-01", "building")
        after = plan.read_text(encoding="utf-8")
        check("the first-station insert on a signed plan succeeds", rc == 0, f"rc={rc}")
        check("the signed approval block is byte-identical after the insert",
              rc == 0 and APPROVAL in after and after.count("status: approved") == 1, after)
    finally:
        shutil.rmtree(root, ignore_errors=True)


for case in (case_station_rows, case_first_station_lands_on_the_task_itself,
             case_absent_task_message_is_about_absence,
             case_signed_approval_survives_the_first_station):
    case()

print("FAIL test-plan-merge-first-station.py" if failures
      else "PASS test-plan-merge-first-station.py")
sys.exit(1 if failures else 0)
