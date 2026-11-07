#!/usr/bin/env python3
"""FEAT-2081 SC-02/SC-03: pure validation branches of check-integration-shards.py.

Each case builds in-memory manifests against an explicit expected file list and asserts the
defect statuses (1 = valid but incomplete/failed, 2 = malformed evidence or unusable input)
and that the diagnostic names the defect. The all-success exact-coverage control must pass.
"""
import copy
import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
GATE = os.path.join(ROOT, ".claude", "skills", "harness", "bin", "check-integration-shards.py")
SHA = "a" * 40
OTHER = "b" * 40
EXPECTED = ["tests/integration/test-a.py", "tests/integration/test-b.py",
            "tests/integration/test-c.py", "tests/integration/test-d.py",
            "tests/integration/test-e.py"]
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, "" if condition else detail)
    if not condition:
        failures.append(name)


def load_gate():
    spec = importlib.util.spec_from_file_location("check_integration_shards", GATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(index, paths, sha=SHA, rcs=None):
    rcs = rcs or [0] * len(paths)
    return {"schema": 1, "tested_commit": sha, "kind": "integration", "shard_index": index,
            "shard_count": 4, "selected_files": list(paths), "runner_exit": 0,
            "completed_files": [{"path": p, "returncode": rc} for p, rc in zip(paths, rcs)]}


def exact():
    return {"m1.json": manifest(1, EXPECTED[:2]), "m2.json": manifest(2, EXPECTED[2:3]),
            "m3.json": manifest(3, EXPECTED[3:]), "m4.json": manifest(4, [])}


def run(gate, docs, expected=EXPECTED, checks="success", matrix="success"):
    defects = gate.conclusion_defects(checks, matrix)
    defects += gate.evidence_defects(docs, SHA, 4, expected)
    return defects


def expect(gate, name, docs, status, needle, **kw):
    defects = run(gate, docs, **kw)
    text = " | ".join(message for _status, message in defects)
    check(f"{name}: exit {status}", gate.exit_status(defects) == status, text or "no defects")
    check(f"{name}: diagnostic names '{needle}'", needle in text, text or "no defects")


def mutate(fn):
    docs = exact()
    fn(docs)
    return docs


def conclusion_cases(gate):
    for field in ("checks", "matrix"):
        for value in ("failure", "skipped", "cancelled", "missing"):
            expect(gate, f"{field}-result {value} rejected", exact(), 1,
                   f"{field}-result is {value}", **{field: value})
        expect(gate, f"{field}-result unrecognized rejected", exact(), 2,
               f"{field}-result 'neutral' is not one of", **{field: "neutral"})
        expect(gate, f"{field}-result absent rejected", exact(), 2,
               f"{field}-result was not supplied", **{field: None})


def manifest_set_cases(gate):
    expect(gate, "missing manifest for shard 3", mutate(lambda d: d.pop("m3.json")), 1,
           "no manifest for shard 3")
    expect(gate, "duplicate shard id", mutate(lambda d: d.update(
        {"m3b.json": manifest(3, [])})), 1, "shard 3 has 2 manifests")
    expect(gate, "extra manifest beyond shard count", mutate(lambda d: d.update(
        {"m5.json": manifest(5, [])})), 1, "shard_index 5 outside 1..4")
    expect(gate, "foreign commit", mutate(lambda d: d["m2.json"].update(tested_commit=OTHER)), 1,
           f"tested_commit {OTHER} is not the supplied {SHA}")
    expect(gate, "foreign suite kind", mutate(lambda d: d["m2.json"].update(kind="unit")), 1,
           "kind 'unit' is not integration")
    expect(gate, "foreign shard count", mutate(lambda d: d["m2.json"].update(shard_count=3)), 1,
           "shard_count 3 is not 4")
    expect(gate, "malformed manifest (not an object)", mutate(lambda d: d.update(
        {"m2.json": ["x"]})), 2, "m2.json: manifest must be a JSON object")
    expect(gate, "wrong schema", mutate(lambda d: d["m2.json"].update(schema=2)), 2,
           "schema must be 1")
    expect(gate, "unreadable manifest", mutate(lambda d: d.update(
        {"m2.json": gate.Malformed("Expecting value: line 1 column 1")})), 2,
           "m2.json: malformed JSON")


def field_cases(gate):
    expect(gate, "non-integer return code", mutate(
        lambda d: d["m1.json"]["completed_files"][0].update(returncode="0")), 2,
           "returncode must be an integer")
    expect(gate, "boolean return code", mutate(
        lambda d: d["m1.json"]["completed_files"][0].update(returncode=False)), 2,
           "returncode must be an integer")
    expect(gate, "non-integer runner_exit", mutate(lambda d: d["m1.json"].update(runner_exit=None)),
           2, "runner_exit must be an integer")
    expect(gate, "non-normalized path", mutate(lambda d: _rename(d["m1.json"], 0,
           "./tests/integration/test-a.py")), 2, "not a normalized repository-relative path")
    expect(gate, "absolute path", mutate(lambda d: _rename(d["m1.json"], 0,
           "/repo/tests/integration/test-a.py")), 2, "not a normalized repository-relative path")
    expect(gate, "runner_exit nonzero", mutate(lambda d: d["m1.json"].update(runner_exit=1)), 1,
           "runner_exit 1")
    expect(gate, "completed file failed", mutate(
        lambda d: d["m1.json"]["completed_files"][1].update(returncode=3)), 1,
           "tests/integration/test-b.py returned 3")


def _rename(doc, position, path):
    doc["selected_files"][position] = path
    doc["completed_files"][position]["path"] = path


def coverage_cases(gate):
    expect(gate, "omitted file", mutate(lambda d: _drop(d["m3.json"], 1)), 1,
           "tests/integration/test-e.py: omitted")
    expect(gate, "within-shard duplicate", mutate(lambda d: _add(d["m1.json"], EXPECTED[0])), 1,
           "duplicated within shard 1")
    expect(gate, "cross-shard duplicate", mutate(lambda d: _add(d["m4.json"], EXPECTED[0])), 1,
           "tests/integration/test-a.py: completed 2 times")
    expect(gate, "unexpected file", mutate(
        lambda d: _add(d["m4.json"], "tests/integration/test-zzz.py")), 1,
           "tests/integration/test-zzz.py: unexpected")
    expect(gate, "selected without completion", mutate(
        lambda d: d["m3.json"]["completed_files"].pop()), 1,
           "selected but has no completed record")
    expect(gate, "completed without selection", mutate(
        lambda d: d["m3.json"]["selected_files"].pop()), 1, "completed but not selected")
    expect(gate, "empty expected suite", exact(), 1, "no tests/integration/test-*.py",
           expected=[])
    expect(gate, "selection union is not coverage", mutate(
        lambda d: d["m3.json"].update(completed_files=[])), 1,
           "tests/integration/test-d.py: omitted")


def _drop(doc, position):
    doc["selected_files"].pop(position)
    doc["completed_files"].pop(position)


def _add(doc, path):
    doc["selected_files"].append(path)
    doc["completed_files"].append({"path": path, "returncode": 0})


def positive_cases(gate):
    defects = run(gate, exact())
    check("all-success exact coverage passes", gate.exit_status(defects) == 0, repr(defects))
    docs = {f"m{i}.json": manifest(i, []) for i in (1, 2, 3)}
    docs["m4.json"] = manifest(4, EXPECTED)
    defects = run(gate, docs)
    check("empty individual shards pass when the suite is covered", gate.exit_status(defects) == 0,
          repr(defects))
    check("filter keeps only top-level tests/integration/test-*.py", gate.integration_paths([
        "tests/integration/test-a.py", "tests/integration/sub/test-b.py",
        "tests/integration/helper.py", "tests/unit/test-c.py", "tests/integration/test-d.txt",
        "xtests/integration/test-e.py"]) == ["tests/integration/test-a.py"])
    before = copy.deepcopy(exact())
    run(gate, before)
    check("validation does not mutate evidence", before == exact())


def main():
    try:
        gate = load_gate()
    except (OSError, ImportError, SyntaxError) as error:
        print(f"FAIL cannot load gate: {error}")
        return 1
    for group in (conclusion_cases, manifest_set_cases, field_cases, coverage_cases,
                  positive_cases):
        try:
            group(gate)
        except Exception as error:  # a missing API is a red case, not a crash
            check(f"{group.__name__} ran", False, f"{type(error).__name__}: {error}")
    print(f"{len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
