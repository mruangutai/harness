#!/usr/bin/env python3
"""Issue #1033 / DEC-212: a config change that alters a VALUE'S SHAPE (a key's
container type, required-ness, or structural nesting) must be bound to the
`integration` floor, or a task like FEAT-41 T-01 can ship a broken state gate
green — 112/112 unit-green while `check-state.py`'s own INV-26 block and
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
import sys

from unit_support import ROOT
from check_support import Checks

PROJECT_CONFIG = ROOT / ".harness" / "harness.json"
TEMPLATE_CONFIG = ROOT / ".claude" / "skills" / "harness" / "templates" / "harness.json"
DECISIONS_MD = ROOT / ".harness" / "harness" / "docs" / "DECISIONS.md"
VERIFICATION_SKILL = ROOT / ".claude" / "skills" / "harness-verification-rules" / "SKILL.md"

C = Checks()
check = C.check


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _decision_body(text, heading, n):
    """The n characters after `heading`, or None when the heading is absent."""
    i = text.find(heading)
    return None if i < 0 else text[i + len(heading):i + len(heading) + n]


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


def _config_has_bugfix_predicates(doc, label):
    bugfix = doc.get("test_matrix", {}).get("bugfix", {})
    when = bugfix.get("when", [])
    expected = [
        {"kind": "unit", "if": "touches_runtime_code"},
        {"kind": "integration", "if": "fix_confined_to_tests_and_contract_docs"},
        {"kind": "__bug_class__", "if": "match_bug_class"},
    ]
    check(f"{label}: bugfix has no unconditional test kind",
          bugfix.get("always") == [], f"always={bugfix.get('always')!r}")
    check(f"{label}: bugfix predicates are complete and unique",
          when == expected, f"when={when!r}")


def case_project_config_shape_provenance(doc):
    provenance = doc.get("_matrix_provenance", {}).get("config")
    if check("project harness.json: _matrix_provenance.config exists",
             isinstance(provenance, dict), f"{provenance!r}"):
        check("project harness.json: _matrix_provenance.config.added "
              "names integration",
              provenance.get("added") == ["integration"], f"{provenance!r}")
        check("project harness.json: _matrix_provenance.config is signed DEC-212",
              provenance.get("signed") == "DEC-212", f"{provenance!r}")


def case_project_config_bugfix_provenance(doc):
    provenance = doc.get("_matrix_provenance", {}).get("bugfix")
    if check("project harness.json: _matrix_provenance.bugfix exists",
             isinstance(provenance, dict), f"{provenance!r}"):
        check("project harness.json: bugfix provenance records moved and added kinds",
              provenance.get("removed") == ["unit"]
              and provenance.get("added") == ["unit", "integration"],
              f"{provenance!r}")
        check("project harness.json: bugfix provenance is signed DEC-217",
              provenance.get("signed") == "DEC-217", f"{provenance!r}")


def case_configs_bind_shape_and_route_bugfix():
    project = _load(PROJECT_CONFIG)
    _config_has_shape_predicate(project, "project harness.json")
    case_project_config_shape_provenance(project)
    _config_has_bugfix_predicates(project, "project harness.json")
    case_project_config_bugfix_provenance(project)

    template = _load(TEMPLATE_CONFIG)
    _config_has_shape_predicate(template, "templates/harness.json")
    _config_has_bugfix_predicates(template, "templates/harness.json")


def case_decision_212_exists_and_is_named_correctly(text):
    body = _decision_body(text, "## DEC-212", 200)
    check("DECISIONS.md declares ## DEC-212",
          body is not None, "no DEC-212 heading found")
    check("DEC-212's heading names touches_config_shape's purpose",
          "config-shape change" in (body or ""),
          "DEC-212 heading text does not describe a config-shape change")


def case_decision_217_exists_and_defines_bugfix_predicates(text):
    body = _decision_body(text, "## DEC-217", 2500)
    if check("DECISIONS.md declares ## DEC-217",
             body is not None, "no DEC-217 heading found"):
        check("DEC-217 defines both bugfix predicates",
              "touches_runtime_code" in body
              and "fix_confined_to_tests_and_contract_docs" in body,
              "predicate definitions absent from DEC-217")


def case_skills_teach_the_new_predicate():
    verification = VERIFICATION_SKILL.read_text(encoding="utf-8")
    check("harness-verification-rules/SKILL.md mentions touches_config_shape",
          "touches_config_shape" in verification,
          "predicate name absent from skill prose")


def main():
    case_configs_bind_shape_and_route_bugfix()
    decisions = DECISIONS_MD.read_text(encoding="utf-8")
    case_decision_212_exists_and_is_named_correctly(decisions)
    case_decision_217_exists_and_defines_bugfix_predicates(decisions)
    case_skills_teach_the_new_predicate()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
