#!/usr/bin/env python3
"""Issue #1033 / DEC-212: a config change that alters a VALUE'S SHAPE (a key's
container type, required-ness, or structural nesting) must be bound to the
`integration` floor, or a task like FEAT-41 T-01 can ship a broken state gate
green — 112/112 unit-green while `check-state.sh`'s own INV-26 block and
`board_lifecycle.py` threw a `TypeError` against the changed shape.

This is a pure data/prose fix (a `test_matrix.config.when` clause, a
`_matrix_provenance` entry, a new fixed predicate name, and skill prose
teaching a reviewer to use it) — nothing here forks a subprocess, so this is
a UNIT-kind test, not integration. What it guards against is regression by
omission: someone editing `.harness/harness.json` later and silently
dropping the `when` clause or its provenance entry, or a `signed` reference
that points at a decision that was never actually written.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PROJECT_CONFIG = os.path.join(ROOT, ".harness", "harness.json")
TEMPLATE_CONFIG = os.path.join(ROOT, ".claude", "skills", "harness", "templates", "harness.json")
DECISIONS_MD = os.path.join(ROOT, ".harness", "harness", "docs", "DECISIONS.md")
QA_GATE_SKILL = os.path.join(ROOT, ".claude", "skills", "harness-qa-gate", "SKILL.md")
VERIFICATION_SKILL = os.path.join(
    ROOT, ".claude", "skills", "harness-verification-rules", "SKILL.md")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _config_has_shape_predicate(doc, label):
    matrix = doc.get("test_matrix", {})
    config = matrix.get("config", {})
    when = config.get("when", [])
    matched = [w for w in when
               if isinstance(w, dict) and w.get("kind") == "integration"
               and w.get("if") == "touches_config_shape"]
    check(f"{label}: test_matrix.config.when requires integration on "
          "touches_config_shape",
          len(matched) == 1, f"when={when!r}")


def case_project_config_binds_shape_to_integration():
    doc = _load(PROJECT_CONFIG)
    _config_has_shape_predicate(doc, "project harness.json")

    provenance = doc.get("_matrix_provenance", {}).get("config")
    check("project harness.json: _matrix_provenance.config exists",
          isinstance(provenance, dict), f"{provenance!r}")
    if isinstance(provenance, dict):
        check("project harness.json: _matrix_provenance.config.added "
              "names integration",
              provenance.get("added") == ["integration"], f"{provenance!r}")
        check("project harness.json: _matrix_provenance.config is signed DEC-212",
              provenance.get("signed") == "DEC-212", f"{provenance!r}")


def case_template_config_binds_shape_to_integration():
    doc = _load(TEMPLATE_CONFIG)
    _config_has_shape_predicate(doc, "templates/harness.json")


def case_decision_212_exists_and_is_named_correctly():
    with open(DECISIONS_MD, encoding="utf-8") as f:
        text = f.read()
    check("DECISIONS.md declares ## DEC-212",
          "## DEC-212" in text, "no DEC-212 heading found")
    check("DEC-212's heading names touches_config_shape's purpose",
          "config-shape change" in text.split("## DEC-212", 1)[-1][:200],
          "DEC-212 heading text does not describe a config-shape change")


def case_skills_teach_the_new_predicate():
    with open(QA_GATE_SKILL, encoding="utf-8") as f:
        qa_gate = f.read()
    check("harness-qa-gate/SKILL.md mentions touches_config_shape",
          "touches_config_shape" in qa_gate, "predicate name absent from skill prose")
    check("harness-qa-gate/SKILL.md cites DEC-212",
          "DEC-212" in qa_gate, "no DEC-212 citation in skill prose")

    with open(VERIFICATION_SKILL, encoding="utf-8") as f:
        verification = f.read()
    check("harness-verification-rules/SKILL.md mentions touches_config_shape",
          "touches_config_shape" in verification,
          "predicate name absent from skill prose")


def main():
    case_project_config_binds_shape_to_integration()
    case_template_config_binds_shape_to_integration()
    case_decision_212_exists_and_is_named_correctly()
    case_skills_teach_the_new_predicate()

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(RESULTS) - fails}/{len(RESULTS)} cases passed.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
