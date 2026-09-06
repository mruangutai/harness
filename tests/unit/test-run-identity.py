#!/usr/bin/env python3
"""Behavior tests for the write-once run identity witness (BUG-1305 T-01)."""
import importlib.util
import os
import re
import tempfile

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT = os.environ.get("RUN_IDENTITY_BIN") or os.path.join(
    ROOT, ".claude", "skills", "harness", "bin", "run_identity.py")
failures = []


def check(name, condition, detail=""):
    if condition:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def module():
    spec = importlib.util.spec_from_file_location("_run_identity_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case_seed_is_write_once():
    mod = module()
    with tempfile.TemporaryDirectory() as run_dir:
        doc = {"run_id": "r1", "feature": "F", "squad": "eng", "host": "omp"}
        check("fresh seed is recorded", mod.record_seed(run_dir, doc, "session-1", "uid-1"))
        path = mod.marker_path(run_dir)
        first = open(path, "rb").read()
        marker = mod.read_marker(run_dir)
        check("seed has exact seven keys", set(marker) == {
            "run_id", "feature", "squad", "host", "identity", "run_uid", "created_at"}, marker)
        check("seed values are retained", marker["run_id"] == "r1" and marker["identity"] == "session-1" and marker["run_uid"] == "uid-1", marker)
        check("second seed is refused", not mod.record_seed(run_dir, {"run_id": "r2"}, "session-2", "uid-2"))
        check("second seed leaves bytes unchanged", open(path, "rb").read() == first)
    missing = os.path.join(tempfile.gettempdir(), "bug1305-no-such-run", "child")
    check("missing directory seed fails open", mod.record_seed(missing, {}, None, None) is False)


def case_marker_absent_and_unreadable():
    mod = module()
    with tempfile.TemporaryDirectory() as run_dir:
        check("absent marker is None", mod.read_marker(run_dir) is None)
        path = mod.marker_path(run_dir)
        for name, content in (("truncated", "{"), ("array", "[]")):
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            try:
                mod.read_marker(run_dir)
            except mod.MarkerUnreadable:
                check(f"{name} marker is unreadable", True)
            else:
                check(f"{name} marker is unreadable", False)


def case_uid_mint_and_injection():
    mod = module()
    values = [mod.mint_uid() for _ in range(1000)]
    check("minted uid shape", all(re.fullmatch(r"[0-9a-f]{32}", value) for value in values))
    check("minted uids are distinct", len(set(values)) == 1000)
    with tempfile.TemporaryDirectory() as root:
        state = os.path.join(root, "state.yaml")
        with open(state, "w", encoding="utf-8") as fh:
            fh.write("run_id: alpha\n# keep this comment\n")
        check("uid injection succeeds", mod.inject_uid(state, "u1"))
        result = open(state, encoding="utf-8").read()
        check("uid injection preserves text and parses", "# keep this comment\nrun_uid: u1\n" in result and yaml.safe_load(result)["run_uid"] == "u1", result)
        before = open(state, "rb").read()
        check("existing uid is not replaced", mod.inject_uid(state, "u2") is False)
        check("existing uid bytes unchanged", open(state, "rb").read() == before)
        no_newline = os.path.join(root, "no-newline.yaml")
        with open(no_newline, "w", encoding="utf-8") as fh:
            fh.write("run_id: beta")
        check("separator newline inserted", mod.inject_uid(no_newline, "u3") and open(no_newline, encoding="utf-8").read() == "run_id: beta\nrun_uid: u3\n")
        check("missing checkpoint fails open", mod.inject_uid(os.path.join(root, "missing.yaml"), "u4") is False)


def case_seed_conflict_guards():
    mod = module()
    with tempfile.TemporaryDirectory() as run_dir:
        doc = {"run_id": "A", "feature": "F", "squad": "eng", "host": "omp", "run_uid": "old"}
        mod.record_seed(run_dir, doc, "session", "old")
        marker = mod.read_marker(run_dir)
        check("identical seed fields agree", mod.conflict(marker, doc) is None)
        reason = mod.conflict(marker, {**doc, "run_id": "B"})
        check("run id conflict names both values", reason is not None and "A" in reason and "B" in reason, reason)
        reason = mod.conflict(marker, {**doc, "squad": "qa"})
        check("squad conflict names field and values", reason is not None and "squad" in reason and "eng" in reason and "qa" in reason, reason)
        check("run uid is not a seed conflict", mod.conflict(marker, {**doc, "run_uid": "new"}) is None)
    with tempfile.TemporaryDirectory() as run_dir:
        mod.record_seed(run_dir, {"feature": "F", "host": "omp"}, None, None)
        marker = mod.read_marker(run_dir)
        check("born-null run_id stays writable", mod.conflict(marker, {"run_id": "A", "feature": "F", "host": "omp"}) is None)
        check("born-null squad stays writable", mod.conflict(marker, {"feature": "F", "squad": "eng", "host": "omp"}) is None)


def case_uid_conflicts():
    mod = module()
    check("legacy prior without uid is allowed", mod.uid_conflict({"run_id": "A"}, {"run_id": "B", "run_uid": "new"}) is None)
    check("legacy null uid is allowed", mod.uid_conflict({"run_uid": None}, {"run_uid": "new"}) is None)
    check("same uid is allowed", mod.uid_conflict({"run_uid": "same"}, {"run_uid": "same"}) is None)
    reason = mod.uid_conflict({"run_uid": "old"}, {"run_uid": "new"})
    check("different uid reason names both", reason is not None and "old" in reason and "new" in reason, reason)
    reason = mod.uid_conflict({"run_uid": "old"}, {"run_id": "A"})
    check("missing incoming uid explains recovery", reason is not None and "old" in reason and "carry" in reason and "witness" in reason, reason)


def main():
    for case in (case_seed_is_write_once, case_marker_absent_and_unreadable,
                 case_uid_mint_and_injection, case_seed_conflict_guards,
                 case_uid_conflicts):
        try:
            case()
        except Exception as exc:
            check(case.__name__, False, repr(exc))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
