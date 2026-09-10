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


def _existing_write(slug, before, after):
    root = fixture(FIXTURE_MANIFEST)
    rel = f".harness/harness/features/FEAT-X/runs/{slug}/state.yaml"
    target = os.path.join(root, rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w") as handle:
        handle.write(before)
    return fire(root, rel, after)


def _undeclared_cases():
    old = _existing_write(
        "old-unknown", _state("1", ["    rogue_step_key: before"]),
        _state("1", ["    rogue_step_key: allowed"]))
    strict = _fire_new(
        _state("2", ["    rogue_step_key: denied"]), "strict-unknown")
    return [
        ("schema_version 1 preserves undeclared step key compatibility",
         old.returncode == 0, old),
        ("schema_version 2 refuses an undeclared step key, names it and gives its route",
         strict.returncode == 2 and "undeclared step key" in strict.stderr
         and "rogue_step_key" in strict.stderr
         and "run-state-schema.json" in strict.stderr
         and "`evidence`" in strict.stderr, strict),
    ]


def _evidence_cases():
    evidence = _fire_new(_state("2", [
        "    evidence:", "      test_exit: 0", "      matrix_ok: true",
        "      changed_paths: [a, b]",
    ]), "evidence-ok")
    bad_name = _fire_new(_state("2", [
        "    evidence:", "      sentence key: wrong",
    ]), "evidence-name")
    nested = _fire_new(_state("2", [
        "    evidence:", "      nested:", "        detail: wrong",
    ]), "evidence-nested")
    return [
        ("three identifier evidence keys are accepted",
         evidence.returncode == 0, evidence),
        ("an evidence key containing a space is refused as an undeclared step key",
         bad_name.returncode == 2 and "undeclared step key" in bad_name.stderr,
         bad_name),
        ("a nested evidence mapping is refused as an undeclared step key",
         nested.returncode == 2 and "undeclared step key" in nested.stderr,
         nested),
    ]


def _declared_shape_case():
    with open(os.path.join(
            ROOT, ".claude", "skills", "harness", "bin",
            "run-state-schema.json")) as handle:
        schema = json.load(handle)
    schema_keys = set(schema["properties"]["steps"]["items"]["properties"])
    result = _fire_new(_full_step_state(), "full-step")
    return (
        "all 22 declared step keys are individually present and accepted",
        schema_keys == DECLARED and result.returncode == 0, result,
    )


def _floor_creation_cases():
    version2 = _fire_new(_state("2"), "floor-two")
    version1 = _fire_new(_state("1"), "floor-one")
    absent = _fire_new(
        _state("2").replace("schema_version: 2\n", ""), "floor-absent")
    string = _fire_new(_state('"2"'), "floor-string")
    return [
        ("schema_version floor accepts creation at version 2",
         version2.returncode == 0, version2),
        ("schema_version floor refuses creation at version 1",
         version1.returncode == 2 and "schema_version floor" in version1.stderr,
         version1),
        ("schema_version floor refuses creation without the field",
         absent.returncode == 2 and "schema_version floor" in absent.stderr,
         absent),
        ("schema_version floor refuses string 2 and names the type",
         string.returncode == 2 and "schema_version floor" in string.stderr
         and "string" in string.stderr, string),
    ]


def _floor_update_cases():
    legacy = _existing_write(
        "existing", _state("1", ["    legacy_key: remains_writable"]),
        _state("1", ["    legacy_key: updated"]))
    downgrade = _existing_write(
        "downgrade", _state("2"), _state("1"))
    return [
        ("schema_version floor allows an existing version-1 update",
         legacy.returncode == 0, legacy),
        ("schema_version floor refuses a version-2 checkpoint downgrade",
         downgrade.returncode == 2
         and "schema_version downgrade" in downgrade.stderr, downgrade),
    ]


def _report(cases):
    failures = 0
    for name, passed, result in cases:
        if passed:
            print("ok   ", name)
            continue
        failures += 1
        print("FAIL ", name)
        print(f"      exit {result.returncode}: {result.stderr.strip()[:500]}")
    print(f"\n{len(cases) - failures}/{len(cases)} T-06 check-domain cases passed.")
    print("coverage tokens: undeclared step key; schema_version floor")
    print("ALL PASSED" if not failures else f"{failures} FAILING")
    return failures


def run_t06_cases():
    cases = _undeclared_cases()
    cases.extend(_evidence_cases())
    cases.append(_declared_shape_case())
    cases.extend(_floor_creation_cases())
    cases.extend(_floor_update_cases())
    return _report(cases)


if __name__ == "__main__":
    raise SystemExit(1 if run_t06_cases() else 0)
