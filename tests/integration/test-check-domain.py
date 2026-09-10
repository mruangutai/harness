#!/usr/bin/env python3
"""FEAT-104: closed schema enforcement on run state.yaml writes."""
import json
import os
import sys

TESTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS, "..", ".."))
sys.path.insert(0, TESTS)

from check_domain_support import FIXTURE_MANIFEST, fire, fixture


DECLARED = {
    "id", "persona", "task", "seq", "depends_on", "outputs", "mutates_repo",
    "on_fail", "status", "verdict", "lead_verdict", "cycles", "max_cycles",
    "redispatches", "dispatched_at", "completed_at", "redispatched_at",
    "recompleted_at", "routed_by", "note", "artifact", "evidence",
}


def _state(version="2", step_lines=None):
    lines = [f"schema_version: {version}", "run_id: r1", "status: running", "steps:",
             "  - id: s1", "    status: pending"]
    lines.extend(step_lines or [])
    return "\n".join(lines) + "\n"


def _fire_new(content, slug):
    root = fixture(FIXTURE_MANIFEST)
    path = f".harness/harness/features/FEAT-X/runs/{slug}/state.yaml"
    return fire(root, path, content)


def _full_step_state():
    return """schema_version: 2
run_id: r1
status: complete
steps:
  - id: s1
    persona: harness-pm
    task: T-01
    seq: 1
    depends_on: []
    outputs: []
    mutates_repo: false
    on_fail: escalate
    status: complete
    verdict: PASS
    lead_verdict: PASS
    cycles: 0
    max_cycles: 3
    redispatches: 0
    dispatched_at: seq-1
    completed_at: seq-2
    redispatched_at: seq-3
    recompleted_at: seq-4
    routed_by: harness-product-lead
    note: done
    artifact: runs/r1/digest.md
    evidence:
      test_exit: 0
"""


def run_t06_cases():
    cases = []

    old_root = fixture(FIXTURE_MANIFEST)
    old_rel = ".harness/harness/features/FEAT-X/runs/old-unknown/state.yaml"
    old_target = os.path.join(old_root, old_rel)
    os.makedirs(os.path.dirname(old_target), exist_ok=True)
    with open(old_target, "w") as handle:
        handle.write(_state("1", ["    rogue_step_key: before"]))
    old = fire(
        old_root, old_rel, _state("1", ["    rogue_step_key: allowed"]))
    cases.append(("schema_version 1 preserves undeclared step key compatibility",
                  old.returncode == 0, old))

    strict = _fire_new(_state("2", ["    rogue_step_key: denied"]), "strict-unknown")
    cases.append(("schema_version 2 refuses an undeclared step key and names it",
                  strict.returncode == 2 and "undeclared step key" in strict.stderr
                  and "rogue_step_key" in strict.stderr, strict))

    evidence = _fire_new(_state("2", [
        "    evidence:", "      test_exit: 0", "      matrix_ok: true",
        "      changed_paths: [a, b]",
    ]), "evidence-ok")
    cases.append(("three identifier evidence keys are accepted",
                  evidence.returncode == 0, evidence))

    bad_name = _fire_new(_state("2", [
        "    evidence:", "      sentence key: wrong",
    ]), "evidence-name")
    cases.append(("an evidence key containing a space is refused as an undeclared step key",
                  bad_name.returncode == 2 and "undeclared step key" in bad_name.stderr,
                  bad_name))

    nested = _fire_new(_state("2", [
        "    evidence:", "      nested:", "        detail: wrong",
    ]), "evidence-nested")
    cases.append(("a nested evidence mapping is refused as an undeclared step key",
                  nested.returncode == 2 and "undeclared step key" in nested.stderr,
                  nested))

    schema = json.load(open(os.path.join(
        ROOT, ".claude", "skills", "harness", "bin", "run-state-schema.json")))
    schema_keys = set(schema["properties"]["steps"]["items"]["properties"])
    full = _fire_new(_full_step_state(), "full-step")
    cases.append(("all 22 declared step keys are individually present and accepted",
                  schema_keys == DECLARED and full.returncode == 0, full))

    version2 = _fire_new(_state("2"), "floor-two")
    cases.append(("schema_version floor accepts creation at version 2",
                  version2.returncode == 0, version2))

    version1 = _fire_new(_state("1"), "floor-one")
    cases.append(("schema_version floor refuses creation at version 1",
                  version1.returncode == 2 and "schema_version floor" in version1.stderr,
                  version1))

    absent = _fire_new(_state("2").replace("schema_version: 2\n", ""), "floor-absent")
    cases.append(("schema_version floor refuses creation without the field",
                  absent.returncode == 2 and "schema_version floor" in absent.stderr,
                  absent))

    string = _fire_new(_state('"2"'), "floor-string")
    cases.append(("schema_version floor refuses string 2 and names the type",
                  string.returncode == 2 and "schema_version floor" in string.stderr
                  and "string" in string.stderr, string))

    root = fixture(FIXTURE_MANIFEST)
    rel = ".harness/harness/features/FEAT-X/runs/existing/state.yaml"
    target = os.path.join(root, rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w") as handle:
        handle.write(_state("1", ["    legacy_key: remains_writable"]))
    update = fire(root, rel, _state("1", ["    legacy_key: updated"]))
    cases.append(("schema_version floor allows an existing version-1 update",
                  update.returncode == 0, update))

    failures = 0
    for name, passed, result in cases:
        if passed:
            print("ok   ", name)
        else:
            failures += 1
            print("FAIL ", name)
            print(f"      exit {result.returncode}: {result.stderr.strip()[:500]}")
    print(f"\n{len(cases) - failures}/{len(cases)} T-06 check-domain cases passed.")
    print("coverage tokens: undeclared step key; schema_version floor")
    print("ALL PASSED" if not failures else f"{failures} FAILING")
    return failures


if __name__ == "__main__":
    raise SystemExit(1 if run_t06_cases() else 0)
