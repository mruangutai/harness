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
import sys
import tempfile
from pathlib import Path

from unit_support import BIN

from check_support import Checks  # noqa: E402

import plan_merge  # noqa: E402,F401  the package must be importable before its stations module

_STATIONS = os.environ.get("PLAN_MERGE_STATIONS") or str(BIN / "plan_merge" / "stations.py")
_spec = importlib.util.spec_from_file_location("plan_merge.stations", _STATIONS)
stations = importlib.util.module_from_spec(_spec)
sys.modules["plan_merge.stations"] = stations
_spec.loader.exec_module(stations)

C = Checks()
check = C.check


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


@contextlib.contextmanager
def fixture(text=PLAN):
    """The plan path of a fresh plan under a features directory the guard accepts; removed after."""
    with tempfile.TemporaryDirectory(prefix="bug2420-") as root:
        feature = Path(root) / ".harness" / "harness" / "features" / "FEAT-99-fixture"
        feature.mkdir(parents=True)
        plan = feature / "plan.yaml"
        plan.write_bytes(text.encode("utf-8"))
        yield plan


def plan_bytes(plan):
    """The plan file exactly as written: bytes decoded with no newline translation, so a CR or
    a reordered line can never read as the expected text."""
    return plan.read_bytes().decode("utf-8")


# (row, task, station, expected exit, the COMPLETE expected file, stdout/stderr needles). Whole-
# file equality is the byte-preservation proof: a membership diff would miss reordered or
# duplicated lines and a CRLF-terminated insert.
ROWS = (
    ("a status-less task gains its first station at its field indent",
     "T-01", "building", 0, PLAN.replace("- id: T-01\n", "- id: T-01\n  status: building\n"),
     ("STATION T-01 -> building",)),
    ("an existing status is rewritten and every other byte is unchanged",
     "T-02", "done", 0, PLAN.replace("  status: ready\n", "  status: done\n"),
     ("STATION T-02 -> done",)),
    ("a genuinely absent task refuses with exit 3 and writes nothing",
     "T-09", "building", 3, PLAN, ("T-09", "T-01, T-02")),
)


def case_station_rows():
    """Run every row once; returns {task: (stderr, file after)} for the cases that reuse a run."""
    runs = {}
    for row, task, station, code, expected, needles in ROWS:
        with fixture() as plan:
            rc, out, err = set_station(plan, task, station)
            after = plan_bytes(plan)
        runs[task] = (err, after)
        check(f"{row}: exit {code}", rc == code, f"rc={rc} out={out!r} err={err!r}")
        check(f"{row}: the whole file is exactly the expected bytes", after == expected,
              repr(after))
        check(f"{row}: reports its outcome", all(n in out + err for n in needles),
              repr(out + err))
        check(f"{row}: prints APPLIED only on success", ("APPLIED" in out) == (code == 0),
              repr(out))
    return runs


def case_first_station_lands_on_the_task_itself(runs):
    """The inserted line belongs to T-01, not to its nested verify prose or to T-02."""
    lines = runs["T-01"][1].splitlines()
    t01 = lines.index("- id: T-01")
    check("the first station sits inside T-01's own mapping, before T-02",
          "  status: building" in lines[t01:lines.index("- id: T-02")], repr(lines))
    check("T-01's verify prose keeps its own `status: prose` line",
          "    status: prose" in lines, repr(lines))


def case_absent_task_message_is_about_absence(runs):
    """The refusal names absence and the ids present, never a missing status field."""
    err = runs["T-09"][0]
    check("the absent-task refusal never blames a status line", "status" not in err.lower(),
          repr(err))


def case_signed_approval_survives_the_first_station():
    """No re-sign: the insert succeeds and the approval block is byte-identical."""
    with fixture(PLAIN) as plan:
        rc, _out, _err = set_station(plan, "T-01", "building")
        after = plan_bytes(plan)
    check("the first-station insert on a signed plan succeeds", rc == 0, f"rc={rc}")
    check("the signed approval block is byte-identical after the insert",
          rc == 0 and APPROVAL in after and after.count("status: approved") == 1, after)


runs = case_station_rows()
case_first_station_lands_on_the_task_itself(runs)
case_absent_task_message_is_about_absence(runs)
case_signed_approval_survives_the_first_station()
sys.exit(C.report())
