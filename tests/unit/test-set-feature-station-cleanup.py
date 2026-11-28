#!/usr/bin/env python3
"""plan-merge.py set-feature-station's rejected cleanup failure path (FEAT-2641 T-10, D-05).

Loads bin/plan_merge/stations.py with the bin directory on sys.path and calls _clean_rejected
directly with working_files.clean patched to fail, so the exit-10 report is graded without any
permission-based unremovable directory (inert for root).
"""
import contextlib
import importlib
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BIN = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, BIN)

stations = importlib.import_module("plan_merge.stations")
import working_files  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(f"{'ok' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n      | {detail}"))
    if not ok:
        FAILS.append(name)


def fixture():
    root = tempfile.mkdtemp(prefix="set-station-cleanup-")
    feature_dir = os.path.join(root, ".harness", "harness", "features", "FEAT-0-probe")
    os.makedirs(os.path.join(feature_dir, "notes"))
    with open(os.path.join(feature_dir, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("feature: FEAT-0-probe\nstatus: rejected\ntasks: []\n")
    with open(os.path.join(feature_dir, "notes", "x.md"), "w", encoding="utf-8") as f:
        f.write("x\n")
    return root, os.path.join(feature_dir, "plan.yaml")


def run(plan, fake_clean):
    original = stations.working_files.clean
    stations.working_files.clean = fake_clean
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = stations._clean_rejected(plan)
    finally:
        stations.working_files.clean = original
    return rc, out.getvalue(), err.getvalue()


def case_oserror_after_a_removal():
    root, plan = fixture()
    try:
        removed = os.path.join(os.path.dirname(plan), "notes")

        def fake_clean(feature_dir, owner_root, dry_run=False, emit=print):
            emit(f"removed {removed}")
            raise OSError("simulated removal failure")

        rc, _out, err = run(plan, fake_clean)
        check("OSError mid-cleanup returns 10", rc == 10, f"rc={rc}")
        check("stderr says the station rejected was recorded",
              "station rejected was recorded" in err, err)
        check("stderr names the path removed before the failure",
              f"removed before the failure: {removed}" in err, err)
        check("stderr carries the feature-worktree.py clean command for FEAT-0-probe",
              "feature-worktree.py clean" in err and "--id FEAT-0-probe" in err, err)
        check("stderr says not to write the station again",
              "do not write the station again" in err, err)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_working_files_error_before_any_removal():
    root, plan = fixture()
    try:
        def fake_clean(feature_dir, owner_root, dry_run=False, emit=print):
            raise working_files.WorkingFilesError("simulated refusal")

        rc, _out, err = run(plan, fake_clean)
        check("WorkingFilesError returns 10", rc == 10, f"rc={rc}")
        check("WorkingFilesError reports no removed path",
              "removed before the failure" not in err, err)
        check("WorkingFilesError report says the station was recorded",
              "station rejected was recorded" in err and "simulated refusal" in err, err)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    case_oserror_after_a_removal()
    case_working_files_error_before_any_removal()
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
