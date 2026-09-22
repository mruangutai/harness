#!/usr/bin/env python3
"""FEAT-104: closed schema enforcement on run state.yaml writes."""
import json
import os
import subprocess
import sys

TESTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS, "..", ".."))
sys.path.insert(0, TESTS)

from check_domain_support import FIXTURE_MANIFEST, fire, fixture
from isolated_bin import isolated_bin


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
    missing = _fire_new(
        _state("2").replace("    status: pending\n", ""), "strict-missing")
    return [
        ("schema_version 1 preserves undeclared step key compatibility",
         old.returncode == 0, old),
        ("schema_version 2 refuses an undeclared step key, names it and gives its route",
         strict.returncode == 2 and "undeclared step key" in strict.stderr
         and "rogue_step_key" in strict.stderr
         and "run-state-schema.json" in strict.stderr
         and "`evidence`" in strict.stderr, strict),
        ("schema_version 2 names a missing required step key",
         missing.returncode == 2
         and "missing required step key" in missing.stderr
         and "status" in missing.stderr, missing),
    ]


def _declared_type_cases():
    invalid = _fire_new(
        _state("2", ["    cycles: three"]), "declared-type")
    return [
        ("a declared step field with the wrong type is distinguished from an undeclared key",
         invalid.returncode == 2
         and "declared step field has invalid value" in invalid.stderr
         and "cycles" in invalid.stderr
         and "run-state-schema.json" in invalid.stderr
         and "under `evidence`" not in invalid.stderr,
         invalid),
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


# FEAT-61 T-03: the step schema is read through artifact_accessors.load_run_step_contract.
# The file is decoded STRICTLY — a duplicate key is a refusal, not a silent last-wins —
# while a mis-shaped document keeps the natural KeyError/TypeError the existing catch
# boundary has always printed, so those two receipts are byte-identical before and after.
def _schema_copy_fire(schema_text, slug):
    """A fresh version-2 checkpoint write through a copy of the hook whose sibling
    run-state-schema.json holds `schema_text`."""
    root = fixture(FIXTURE_MANIFEST)
    iso = isolated_bin(root)
    with open(os.path.join(iso, "run-state-schema.json"), "w", encoding="utf-8") as handle:
        handle.write(schema_text)
    return fire(root, f".harness/harness/features/FEAT-X/runs/{slug}/state.yaml",
                _state("2"), hook=os.path.join(iso, "check-domain.py"))


def _run_schema_contract_cases():
    with open(os.path.join(ROOT, ".claude", "skills", "harness", "bin",
                           "run-state-schema.json"), encoding="utf-8") as handle:
        live = handle.read()
    duplicate = live.replace('  "title":', '  "title": "duplicate",\n  "title":', 1)
    if duplicate == live:
        raise AssertionError("INCONCLUSIVE: the live schema carries no top-level title key")
    dup = _schema_copy_fire(duplicate, "schema-duplicate-key")
    bare_items = _schema_copy_fire(
        '{"properties": {"steps": {"items": {"type": "object"}}}}', "schema-bare-items")
    no_steps = _schema_copy_fire('{"properties": {}}', "schema-no-steps")
    cannot = "run-state schema CANNOT be checked; the write is denied."
    return [
        ("a duplicate key in run-state-schema.json is refused as unreadable, never last-wins",
         dup.returncode == 2 and cannot in dup.stderr
         and "ArtifactAccessError" in dup.stderr and "duplicate key: 'title'" in dup.stderr,
         dup),
        ("a step schema without its properties keeps its natural KeyError at the catch boundary",
         bare_items.returncode == 2 and cannot in bare_items.stderr
         and "KeyError: 'properties'" in bare_items.stderr, bare_items),
        ("a schema without steps keeps its natural KeyError at the catch boundary",
         no_steps.returncode == 2 and cannot in no_steps.stderr
         and "KeyError: 'steps'" in no_steps.stderr, no_steps),
    ]


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


def _strict_hook_payload_case():
    root = fixture(FIXTURE_MANIFEST)
    target = os.path.join(root, "forbidden", "duplicate.json")
    payload = (
        '{"agent_type":"","agent_type":"harness-documentor",'
        '"tool_name":"Write","tool_input":{"file_path":'
        + json.dumps(target) + ',"content":"x"}}'
    )
    hook = os.path.join(ROOT, ".claude", "skills", "harness", "bin", "check-domain.py")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root, HARNESS_PROJECT_DIR=root)
    result = subprocess.run(
        [hook], input=payload, capture_output=True, text=True, env=env)
    if result.returncode == 0:
        return None
    return (
        "duplicate hook-payload keys are rejected before domain policy evaluation",
        False,
        result,
    )


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
    cases.extend(_declared_type_cases())
    cases.append(_declared_shape_case())
    cases.extend(_run_schema_contract_cases())
    cases.extend(_floor_creation_cases())
    cases.extend(_floor_update_cases())
    strict_failure = _strict_hook_payload_case()
    if strict_failure is not None:
        cases.append(strict_failure)
    return _report(cases)


if __name__ == "__main__":
    raise SystemExit(1 if run_t06_cases() else 0)
