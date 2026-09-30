#!/usr/bin/env python3
"""digest_schema.py and bin/digest-schemas/ — the live persona object contract (FEAT-1928 SC-03).

Every one of the 16 runtime personas has one closed schema file. A representative valid
object passes for each; a missing, an extra, a wrong-type and a near-miss-enum object fail.
Loader strictness (duplicate keys, malformed schema, duplicate $id), alias resolution and
the validator CLI's object-input decoder are exercised on a temporary schema directory.
"""
from pathlib import Path
import copy
import json
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import digest_schema  # noqa: E402

PERSONAS = (
    "harness-ai-dev", "harness-backend-dev", "harness-code-reviewer",
    "harness-data-engineer", "harness-dev-ops", "harness-documentor", "harness-eng-lead",
    "harness-frontend-dev", "harness-orchestrator", "harness-pm", "harness-product-lead",
    "harness-qa", "harness-security-reviewer", "harness-ui-reviewer",
    "harness-validator-lead", "harness-visual-designer",
)

UNIVERSAL = {"headline": "did the thing",
             "open_questions": [{"id": "Q1", "question": "Retry-After?", "blocking": False}],
             "files_touched": ["a.py"], "expertise_update": []}
DEV = {"tests_added": 2, "suite": "pass", "blocked_on": "none", "task": "T-01",
       "task_verify": "pass"}
FINDING = {"kind": "form", "scope": "none", "severity": "low", "reader": "code-reviewer",
           "summary": "typo", "why": "README.md:3"}
REVIEW = {"severity_max": "low", "must_fix": [], "findings": [FINDING]}
LEAD = {"team": "build", "steps_run": 1, "cycles_used": 1, "must_fix": [], "branch": "none",
        "escalations": [], "adequacy_notes": [],
        "members": [{"step": "s1", "persona": "harness-qa", "verdict": "PASS",
                     "headline": "green", "files_touched": []}],
        "sc_status": [], "needs_approval": "none", "severity_max": "none", "matrix_ok": "none",
        "coverage_gaps": [], "findings": [], "readers": []}

# (persona, persona fields, a field whose enum admits a near miss, the near-miss value)
VALID = {
    "harness-ai-dev": (DEV, "suite", "passed"),
    "harness-backend-dev": (DEV, "task_verify", "ok"),
    "harness-data-engineer": (DEV, "suite", "Pass"),
    "harness-frontend-dev": (DEV, "suite", "pas"),
    "harness-dev-ops": ({"change_type": "config", "applied": [], "suite": "n/a", "task": "T-02",
                         "task_verify": "pass", "test_kinds_written": []},
                        "change_type", "configuration"),
    "harness-pm": ({"feasibility": "clear", "surface": "M", "recommend": "proceed",
                    "risk": "low", "tasks": 3, "decisions": 1, "needs_approval": True,
                    "flags": [], "sc_status": [{"id": "SC-01", "verdict": "met",
                                                "method": "automated", "evidence": "t.py:4"}]},
                   "risk", "medium"),
    "harness-qa": ({"suite": "pass", "failures": 0, "coverage_gaps": [], "matrix_ok": True,
                    "fail_first": [{"sc": "SC-01", "evidence": "notes/red.txt"}],
                    "kinds": [{"kind": "unit", "state": "satisfied", "cmd": "pytest",
                               "named_tests": 4}],
                    "sc_evidence": [{"id": "SC-01", "test": "t.py:4"}]},
                   "suite", "passing"),
    "harness-code-reviewer": ({**REVIEW, "code_grade": "grade_2", "reviewed": "abc..def",
                               "grade_2_reasons": ["f: tolerable"], "spec_violations": [],
                               "human_commits_in_scope": []},
                              "code_grade", "grade2"),
    "harness-security-reviewer": ({**REVIEW, "in_scope": True, "scope_reason": "none",
                                   "threat_model": [{"boundary": "client -> /export",
                                                     "stride": "I", "mitigated": True}]},
                                  "severity_max", "medium"),
    "harness-ui-reviewer": ({**REVIEW, "mode": "B", "in_scope": True, "states_unspecified": [],
                             "contract_violations": [], "a11y": []}, "mode", "b"),
    "harness-visual-designer": ({"contract": "written", "mockups": [], "direction_choices": [],
                                 "needs_prototype": False, "why": "none", "prototype": "none"},
                                "contract", "write"),
    "harness-documentor": ({"docs_updated": ["README.md"], "gaps": [], "stale_found": []},
                           None, None),
    "harness-product-lead": ({**LEAD, "needs_approval": True}, "severity_max", "medium"),
    "harness-validator-lead": ({**LEAD, "matrix_ok": True,
                                "readers": [{"reader": "scope", "status": "ran",
                                             "persona": "harness-pm", "reason": "none"}],
                                "findings": [{**FINDING, "kind": "proportionality",
                                              "scope": "task"}]},
                               "severity_max", "hi"),
    "harness-eng-lead": ({**LEAD, "amendments": [{"task": "T-01", "field": "verify",
                                                  "was": "a", "now": "b", "reason": "typo"}]},
                         "severity_max", "critical!"),
    "harness-orchestrator": ({"feature": "FEAT-1", "status": "in_review",
                              "runs": [{"id": "r1", "squad": "plan", "verdict": "PASS"}],
                              "cycles_used": 2, "briefing": "none", "judgement": "none"},
                             "status", "in-review"),
}


def make(persona, **digest_overrides):
    fields, _field, _bad = VALID[persona]
    digest = {**copy.deepcopy(UNIVERSAL), **copy.deepcopy(fields), **digest_overrides}
    return {"VERDICT": "PASS", "DIGEST": digest, "artifact": "notes/run/digest.md"}


def errors(persona, obj):
    return digest_schema.validate_object(persona, obj)


def array_item_violations(node, at, common, seen=()):
    """Every array without concrete `items`, and every multi-type `type` list, under `node`."""
    if isinstance(node, list):
        return [bad for i, child in enumerate(node)
                for bad in array_item_violations(child, f"{at}/{i}", common, seen)]
    if not isinstance(node, dict):
        return []
    ref = node.get("$ref")
    if isinstance(ref, str) and ref.startswith("common.json#/$defs/"):
        name = ref.rsplit("/", 1)[1]
        return [] if name in seen else array_item_violations(common[name], ref, common,
                                                               seen + (name,))
    types = node.get("type")
    types = types if isinstance(types, list) else [types]
    out = []
    if len([t for t in types if t not in (None, "null")]) > 1:
        out.append(f"{at}: type list {node['type']!r} — spell alternatives as anyOf")
    if "array" in types:
        items = node.get("items")
        if not isinstance(items, dict) or not ({"type", "enum", "anyOf", "$ref"} & set(items)):
            out.append(f"{at}: array without typed items ({items!r})")
    return out + [bad for key, child in node.items() if isinstance(child, (dict, list))
                  for bad in array_item_violations(child, f"{at}/{key}", common, seen)]


def object_violations(node, at, common, seen=()):
    """Every object schema that is open or leaves a property optional, and every JSON null."""
    if isinstance(node, list):
        return [bad for i, child in enumerate(node)
                for bad in object_violations(child, f"{at}/{i}", common, seen)]
    if not isinstance(node, dict):
        return []
    ref = node.get("$ref")
    if isinstance(ref, str) and ref.startswith("common.json#/$defs/"):
        name = ref.rsplit("/", 1)[1]
        return [] if name in seen else object_violations(common[name], ref, common,
                                                         seen + (name,))
    types = node.get("type")
    types = types if isinstance(types, list) else [types]
    out = []
    if "null" in types or ("const" in node and node["const"] is None) \
            or None in (node.get("enum") or []):
        out.append(f"{at}: JSON null")
    if "object" in types:
        keys = list(node.get("properties") or {})
        if node.get("additionalProperties") is not False:
            out.append(f"{at}: object is not additionalProperties false")
        if sorted(node.get("required") or []) != sorted(keys) or not keys:
            out.append(f"{at}: required {node.get('required')!r} != properties {keys!r}")
    return out + [bad for key, child in node.items() if isinstance(child, (dict, list))
                  for bad in object_violations(child, f"{at}/{key}", common, seen)]


class PersonaSchemas(unittest.TestCase):
    def test_exactly_sixteen_persona_files_plus_common(self):
        names = sorted(p.name for p in (BIN / "digest-schemas").glob("*.json"))
        self.assertEqual(names, sorted(["common.json"] + [f"{p}.json" for p in PERSONAS]))
        self.assertEqual(sorted(VALID), sorted(PERSONAS))

    def test_every_persona_schema_is_closed_and_refs_common(self):
        for persona in PERSONAS:
            schema = digest_schema.load_schema(persona)
            self.assertIs(schema["additionalProperties"], False, persona)
            self.assertIs(schema["properties"]["DIGEST"]["additionalProperties"], False, persona)
            self.assertTrue(schema["properties"]["VERDICT"]["$ref"].startswith("common.json#"))

    def test_every_object_is_closed_and_fully_required(self):
        """OpenAI strict requires every declared key and refuses undeclared ones, so every
        object schema (after $ref resolution, entry objects and anyOf branches included) is
        additionalProperties false with required == its property keys; JSON null never appears."""
        common = digest_schema.common_defs()
        roots = [(f"common.json#/$defs/{name}", node) for name, node in common.items()]
        roots += [(f"{persona}.json#", digest_schema.load_schema(persona)) for persona in PERSONAS]
        self.assertEqual([bad for at, node in roots for bad in object_violations(node, at, common)],
                         [])

    def test_object_walk_flags_open_or_partly_required_objects(self):
        props = {"a": {"type": "string"}, "b": {"type": "string"}}
        for node in ({"type": "object", "required": ["a", "b"], "properties": props},
                     {"type": "object", "additionalProperties": False, "required": ["a"],
                      "properties": props},
                     {"items": {"type": "object", "additionalProperties": False, "required": []}},
                     {"anyOf": [{"type": "null"}]}, {"const": None}, {"enum": ["x", None]}):
            self.assertTrue(object_violations(node, "#", {}), node)
        self.assertEqual(object_violations(
            {"type": "object", "additionalProperties": False, "required": ["a", "b"],
             "properties": props, "if": {"properties": {"a": {"const": "x"}}}}, "#", {}), [])

    def test_every_array_declares_typed_items(self):
        """OpenAI strict rejects the whole yield tool on one array without `items` (measured on
        Codex: "array schema missing items"), and `items: {}`/`true` admits anything. Walked
        after $ref resolution, conditionals and unreferenced common $defs included."""
        common = digest_schema.common_defs()
        roots = [(f"common.json#/$defs/{name}", node) for name, node in common.items()]
        roots += [(f"{persona}.json#", digest_schema.load_schema(persona)) for persona in PERSONAS]
        self.assertEqual([bad for at, node in roots for bad in array_item_violations(node, at, common)],
                         [])

    def test_array_walk_flags_untyped_items(self):
        for node in ({"type": "array"}, {"type": ["string", "array"], "items": {"type": "string"}},
                     {"type": "array", "items": {}}, {"type": "array", "items": True},
                     {"properties": {"x": {"anyOf": [{"type": "array"}]}}},
                     {"then": {"properties": {"x": {"type": "array", "items": {"pattern": "x"}}}}}):
            self.assertTrue(array_item_violations(node, "#", {}), node)
        self.assertEqual(array_item_violations(
            {"type": "array", "items": {"$ref": "common.json#/$defs/text"}}, "#",
            {"text": {"type": "string"}}), [])

    def test_representative_valid_objects_pass(self):
        for persona in PERSONAS:
            self.assertEqual(errors(persona, make(persona)), [], persona)

    def test_missing_field_fails(self):
        for persona in PERSONAS:
            for key in ("headline", "files_touched"):
                obj = make(persona)
                del obj["DIGEST"][key]
                self.assertTrue(errors(persona, obj), f"{persona} without {key}")
            obj = make(persona)
            del obj["artifact"]
            self.assertTrue(errors(persona, obj), persona)

    def test_extra_field_fails(self):
        for persona in PERSONAS:
            self.assertTrue(errors(persona, make(persona, files_touched_=[])), persona)
            obj = make(persona)
            obj["extra"] = 1
            self.assertTrue(errors(persona, obj), persona)

    def test_wrong_type_fails(self):
        for persona in PERSONAS:
            self.assertTrue(errors(persona, make(persona, open_questions=0)), persona)
            self.assertTrue(errors(persona, make(persona, headline="  ")), persona)
            obj = make(persona)
            obj["VERDICT"] = "pass"
            self.assertTrue(errors(persona, obj), persona)

    def test_near_miss_enum_fails(self):
        for persona in PERSONAS:
            _fields, field, bad = VALID[persona]
            if field is None:
                continue
            self.assertTrue(errors(persona, make(persona, **{field: bad})), f"{persona} {field}")

    def test_persona_specific_optional_fields_stay_on_their_persona(self):
        self.assertTrue(errors("harness-validator-lead", make("harness-validator-lead",
                                                              amendments=[])))
        self.assertTrue(errors("harness-security-reviewer", make("harness-security-reviewer",
                                                                 mode="A")))
        self.assertTrue(errors("harness-ui-reviewer", make("harness-ui-reviewer",
                                                           code_grade="pass")))
        self.assertTrue(errors("harness-qa", make("harness-qa", findings=[])))

    def test_nullable_rules(self):
        for value in ("n/a", "none", "NULL"):
            self.assertEqual(errors("harness-qa", make("harness-qa", matrix_ok=value)), [])
        self.assertTrue(errors("harness-qa", make("harness-qa", matrix_ok="mostly")))
        self.assertTrue(errors("harness-qa", make("harness-qa", failures="n/a")))
        self.assertTrue(errors("harness-pm", make("harness-pm", feasibility="n/a")))

    def test_every_digest_field_is_required(self):
        """No optional DIGEST keys (operator ruling): dropping any one field fails, the
        formerly documented-optional and conditional ones included."""
        for persona in PERSONAS:
            for key in make(persona)["DIGEST"]:
                obj = make(persona)
                del obj["DIGEST"][key]
                self.assertTrue(errors(persona, obj), f"{persona} without {key}")

    def test_inapplicable_fields_take_the_sentinel(self):
        cases = {"harness-security-reviewer": {"in_scope": "none", "threat_model": []},
                 "harness-ui-reviewer": {"mode": "none", "in_scope": "none"},
                 "harness-visual-designer": {"needs_prototype": "none"},
                 "harness-qa": {"kinds": [], "sc_evidence": []},
                 "harness-code-reviewer": {"code_grade": "pass", "grade_2_reasons": []},
                 "harness-eng-lead": {"amendments": []}}
        for persona, fields in cases.items():
            self.assertEqual(errors(persona, make(persona, **fields)), [], persona)
        self.assertTrue(errors("harness-ui-reviewer", make("harness-ui-reviewer", mode="C")))
        self.assertTrue(errors("harness-code-reviewer", make(
            "harness-code-reviewer", code_grade="pass", grade_2_reasons=["stray"])))

    def test_task_governs_task_verify(self):
        self.assertEqual(errors("harness-backend-dev",
                                make("harness-backend-dev", task="none", task_verify="n/a")), [])
        self.assertTrue(errors("harness-backend-dev",
                               make("harness-backend-dev", task="none", task_verify="pass")))
        for dispatch_task in ("none", "T-01"):
            obj = make("harness-backend-dev", task=dispatch_task, task_verify="n/a")
            del obj["DIGEST"]["task_verify"]
            self.assertTrue(errors("harness-backend-dev", obj), dispatch_task)
        for bad in ("T-NN", "not-T-01-really"):
            self.assertTrue(errors("harness-backend-dev", make("harness-backend-dev", task=bad)))

    def test_list_entry_shapes(self):
        cr = "harness-code-reviewer"
        self.assertTrue(errors(cr, make(cr, findings=["kind: substance"])))
        self.assertTrue(errors(cr, make(cr, findings=[{**FINDING, "kind": "substantive"}])))
        self.assertTrue(errors(cr, make(cr, findings=[{**FINDING, "kind": "proportionality"}])))
        self.assertTrue(errors(cr, make(cr, findings=[{**FINDING, "scope": "task"}])))
        self.assertTrue(errors(cr, make(cr, findings=[{"kind": "form"}])))
        self.assertTrue(errors(cr, make(cr, must_fix=[{"id": "F1"}])))
        self.assertTrue(errors(cr, make(cr, grade_2_reasons=[])))
        self.assertTrue(errors(cr, make(cr, spec_violations=[{"kind": "drift", "path": "a",
                                                              "ref": "SC-01"}])))
        qa = "harness-qa"
        self.assertTrue(errors(qa, make(qa, fail_first=[{"sc": "SC-NN", "evidence": "x"}])))
        self.assertTrue(errors(qa, make(qa, fail_first=[{"sc": "SC-01", "evidence": " "}])))
        kind = {"kind": "unit", "state": "satisfied", "cmd": "pytest", "named_tests": 4}
        self.assertEqual(errors(qa, make(qa, kinds=[{**kind, "state": "not_applicable",
                                                     "cmd": "none", "named_tests": "none"}])), [])
        self.assertTrue(errors(qa, make(qa, kinds=[{**kind, "state": "done"}])))
        self.assertTrue(errors(qa, make(qa, kinds=[{"kind": "unit", "state": "satisfied"}])))
        self.assertTrue(errors(qa, make(qa, kinds=[{**kind, "cmd": None}])))
        self.assertTrue(errors(qa, make(qa, open_questions=[{"id": "Q1", "question": "x"}])))
        lead = "harness-eng-lead"
        skipped = {"step": "advise", "persona": "fable-advisor", "status": "skipped",
                   "reason": "agent not resolvable"}
        self.assertEqual(errors(lead, make(lead, members=[skipped])), [])
        for bad in ({"persona": "harness-qa"}, {**skipped, "status": "ran"},
                    {**skipped, "verdict": "PASS"},
                    {"step": "s1", "persona": "harness-qa", "verdict": "PASS"}):
            self.assertTrue(errors(lead, make(lead, members=[bad])), bad)
        write = {"op": "add", "target": "P-01", "section": "Patterns", "entry": "WHEN x DO y",
                 "why": "seen twice"}
        drop = {"op": "drop", "target": "P-02", "section": "Gotchas", "why": "stale"}
        self.assertEqual(errors(lead, make(lead, expertise_update=[write, drop])), [])
        for bad in ({**drop, "entry": "none"}, {**write, "op": "merge"},
                    {**write, "section": "Rules"}, {k: v for k, v in write.items() if k != "why"}):
            self.assertTrue(errors(lead, make(lead, expertise_update=[bad])), bad)
        files = {"task": "T-01", "field": "files", "was": ["a.py", {"path": "b.py", "quote": "x"}],
                 "now": ["a.py"], "reason": "r"}
        self.assertEqual(errors(lead, make(lead, amendments=[files])), [])
        for entry in ({"task": "SC-01", "field": "intent", "was": "a", "now": "b", "reason": "r"},
                      {"task": "T-01", "field": "title", "was": "a", "now": "b", "reason": "r"},
                      {"task": "T-01", "field": "files", "was": "a", "now": "b", "reason": "r"},
                      {**files, "was": [{"path": "b.py"}]},
                      {"task": "T-01", "field": "intent", "was": "a", "now": "b",
                       "reason": "two\nlines"},
                      {"task": "T-01", "field": "intent", "was": "a", "now": "b", "reason": "r",
                       "by": "me"}):
            self.assertTrue(errors(lead, make(lead, amendments=[entry])), entry)
        vl = "harness-validator-lead"
        reader = {"reader": "advisor", "status": "skipped", "persona": "fable-advisor",
                  "reason": "host refusal"}
        self.assertEqual(errors(vl, make(vl, readers=[reader])), [])
        self.assertTrue(errors(vl, make(vl, readers=[{**reader, "reason": "none"}])))
        self.assertTrue(errors(vl, make(vl, readers=[{**reader, "status": "ran"}])))
        self.assertTrue(errors("harness-orchestrator", make("harness-orchestrator", runs=["r1"])))

    def test_reject_judgement_binds_to_status(self):
        o = "harness-orchestrator"
        judgement = {"kind": "reject", "superseded_by": 12, "reason": "wrong ticket"}
        self.assertEqual(errors(o, make(o, status="rejected", cycles_used=0,
                                        judgement=judgement)), [])
        self.assertEqual(errors(o, make(o, status="rejected", cycles_used=0,
                                        judgement={**judgement, "superseded_by": "none"})), [])
        self.assertTrue(errors(o, make(o, status="rejected", cycles_used=0, judgement="none")))
        self.assertTrue(errors(o, make(o, status="rejected", cycles_used=1, judgement=judgement)))
        self.assertTrue(errors(o, make(o, judgement=judgement)))
        for bad in ({**judgement, "kind": "close"}, {**judgement, "superseded_by": 0},
                    {**judgement, "by": "x"}, {**judgement, "reason": "r" * 241}):
            self.assertTrue(errors(o, make(o, status="rejected", cycles_used=0, judgement=bad)))


class Resolution(unittest.TestCase):
    def test_canonical_persona_aliases(self):
        for persona in PERSONAS:
            self.assertEqual(digest_schema.canonical_persona(persona), persona)
        cases = {"main-session": "harness-backend-dev", "dev": "harness-backend-dev",
                 "qa": "harness-qa", "reviewer": "harness-code-reviewer",
                 "lead": "harness-eng-lead", "orchestrator": "harness-orchestrator",
                 "dev-ops": "harness-dev-ops", "eng-lead": "harness-eng-lead"}
        for alias, want in cases.items():
            self.assertEqual(digest_schema.canonical_persona(alias), want, alias)
        with self.assertRaises(digest_schema.DigestSchemaError):
            digest_schema.canonical_persona("harness-intern")
        with self.assertRaises(digest_schema.DigestSchemaError):
            digest_schema.canonical_persona("common")

    def test_decode_object_json(self):
        obj = make("harness-pm")
        self.assertEqual(digest_schema.decode_object_json(json.dumps(obj)), obj)
        for bad in ('{"VERDICT": "PASS", "VERDICT": "FAIL"}', "[1]", "{not json", "NaN"):
            with self.assertRaises(digest_schema.DigestSchemaError):
                digest_schema.decode_object_json(bad)


class LoaderStrictness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="digest-schemas-test-"))
        shutil.copytree(BIN / "digest-schemas", self.tmp, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def loader(self):
        return digest_schema.SchemaStore(self.tmp)

    def test_live_directory_loads_and_caches(self):
        store = self.loader()
        self.assertIs(store.schema("harness-qa"), store.schema("harness-qa"))
        self.assertIs(digest_schema.load_schema("harness-qa"),
                      digest_schema.load_schema("qa"))

    def test_duplicate_key_rejected(self):
        (self.tmp / "harness-qa.json").write_text('{"type": "object", "type": "array"}')
        with self.assertRaisesRegex(digest_schema.DigestSchemaError, "harness-qa.json"):
            self.loader().schema("harness-qa")

    def test_malformed_json_rejected(self):
        (self.tmp / "common.json").write_text("{")
        with self.assertRaisesRegex(digest_schema.DigestSchemaError, "common.json"):
            self.loader().schema("harness-pm")

    def test_invalid_schema_rejected(self):
        doc = json.loads((self.tmp / "harness-pm.json").read_text())
        doc["type"] = 7
        (self.tmp / "harness-pm.json").write_text(json.dumps(doc))
        with self.assertRaisesRegex(digest_schema.DigestSchemaError, "harness-pm.json"):
            self.loader().schema("harness-pm")

    def test_duplicate_id_rejected(self):
        doc = json.loads((self.tmp / "harness-pm.json").read_text())
        doc["$id"] = json.loads((self.tmp / "harness-qa.json").read_text())["$id"]
        (self.tmp / "harness-pm.json").write_text(json.dumps(doc))
        with self.assertRaisesRegex(digest_schema.DigestSchemaError, "duplicate"):
            self.loader().schema("harness-qa")

    def test_missing_persona_file_rejected(self):
        (self.tmp / "harness-qa.json").unlink()
        with self.assertRaisesRegex(digest_schema.DigestSchemaError, "harness-qa"):
            self.loader().schema("harness-qa")


if __name__ == "__main__":
    unittest.main()
