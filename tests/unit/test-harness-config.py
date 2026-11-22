#!/usr/bin/env python3
"""FEAT-2297: the version-3 harness.json contract behind artifact_accessors.load_harness_json.

Every valid input comes from the one fixture builder; every invalid one is a valid result with
one field corrupted, so each refusal row names exactly the rule it breaks.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from harness_config_support import EXCLUDED_KIND as EXCLUDED, build_config  # noqa: E402
import artifact_accessors as accessors  # noqa: E402

TEMPLATE = ROOT / ".claude" / "skills" / "harness" / "templates" / "harness.json"


def load(document):
    return accessors.load_harness_json(text=json.dumps(document), context="case")


def prose_free(value):
    if isinstance(value, dict):
        return {k: prose_free(v) for k, v in value.items() if not k.startswith("_")
                or k == "_matrix_provenance"}
    if isinstance(value, list):
        return [prose_free(v) for v in value]
    return value


def corrupt(path, value, base=None):
    """A valid built config with the leaf at `path` replaced (or deleted when value is DELETE)."""
    document = copy.deepcopy(base if base is not None else build_config())
    *parents, leaf = path
    node = document
    for key in parents:
        node = node.setdefault(key, {})
    if value is DELETE:
        node.pop(leaf, None)
    else:
        node[leaf] = value
    return document


DELETE = object()
BOARD = {"owner": "acme", "number": 7, "station_field": "Status",
         "stations": ["backlog", "plan", "ready", "building", "review", "done"]}
SYNCED = {"github": {"sync": True, "repo": "acme/widgets", "board": BOARD}}
LOCAL = {"detect": "p.py", "exclude": "", "cmd": "p.py", "status": "locally_run",
         "runner_note": "needs credentials"}


class Defaults(unittest.TestCase):
    def test_minimal_config_takes_every_template_default(self):
        config = build_config()
        self.assertEqual(prose_free(load(json.loads(TEMPLATE.read_text()))), prose_free(config))
        self.assertEqual(3, config["schema_version"])
        for era in ("panel_era_start", "seam_era_start", "decision_dispositions_era_start"):
            self.assertIsNone(config[era])
        self.assertEqual({}, config["_matrix_provenance"])
        self.assertEqual({"agent_prefix": "[harness:<step-id>]", "human_prefix": "[harness:human]"},
                         config["commit_attribution"])
        self.assertEqual([".harness/**", ".claude/worktrees/**"], config["dirty_tree_whitelist"])
        self.assertEqual(30, config["log_retention_days"])
        self.assertEqual({"review": "advisory_unless_high"}, config["gates"])
        self.assertEqual({"sync": False, "repo": None, "board": None, "issue_types": {}},
                         prose_free(config["github"]))
        self.assertEqual({"max_total_cycles": 10, "max_total_runs": 20,
                          "orchestrator_context_warn_tokens": 200000, "plan_phase_warn_minutes": 90,
                          "rework_round_minutes": 45,
                          "preload_warn_words": {"universal": 1900, "agent": 5500}},
                         prose_free(config["budgets"]))
        self.assertEqual(["component", "eval", "functional", "integration", "typecheck", "ui", "unit"],
                         sorted(config["test_kinds"]))
        for name, kind in config["test_kinds"].items():
            with self.subTest(kind=name):
                self.assertEqual((None, "unresolved"), (kind["cmd"], kind["status"]))
        self.assertEqual({"always": [], "when": [
            {"kind": "unit", "if": "touches_runtime_code"},
            {"kind": "integration", "if": "fix_confined_to_tests_and_contract_docs"},
            {"kind": "__bug_class__", "if": "match_bug_class"}]}, config["test_matrix"]["bugfix"])

    def test_missing_leaves_of_a_present_object_default(self):
        config = build_config({"budgets": {"max_total_cycles": 4, "preload_warn_words": {"agent": 9}},
                               "github": {"issue_types": {"Bug": "Defect"}}})
        self.assertEqual((4, 20), (config["budgets"]["max_total_cycles"], config["budgets"]["max_total_runs"]))
        self.assertEqual({"universal": 1900, "agent": 9}, config["budgets"]["preload_warn_words"])
        self.assertEqual((False, None, None, {"Bug": "Defect"}),
                         tuple(config["github"][k] for k in ("sync", "repo", "board", "issue_types")))

    def test_present_values_explicit_null_and_map_populations_are_kept(self):
        config = build_config({
            "panel_era_start": "2026-01-02", "seam_era_start": None,
            "decision_dispositions_era_start": "2026-11-22T01:58:29+00:00",
            "test_matrix": {"logic": {"always": ["unit"]}},
            "test_kinds": {"eval": EXCLUDED, "unit": {"detect": "t/**", "exclude": "", "cmd": None,
                                                      "status": "active"}},
            **SYNCED})
        self.assertEqual("2026-01-02", config["panel_era_start"])
        self.assertIsNone(config["seam_era_start"])
        self.assertEqual({"logic": {"always": ["unit"], "when": []}}, config["test_matrix"])
        self.assertEqual(["eval", "unit"], sorted(config["test_kinds"]))
        self.assertEqual(BOARD, config["github"]["board"])

    def test_structural_near_misses_that_are_valid(self):
        for name, overrides in {
            "underscore prose anywhere": {"_note": 1, "budgets": {"_why": [1]}, "github": {"_x": None},
                                          "test_kinds": {"_k": "prose", "eval": {**EXCLUDED, "_r": 2}}},
            "board number as padded digits": {"github": {**SYNCED["github"],
                                                         "board": {**BOARD, "number": " 12 "}}},
            "board number integer-valued float": {"github": {**SYNCED["github"],
                                                             "board": {**BOARD, "number": 7.0}}},
            "board without sync": {"github": {"sync": False, "repo": "acme/w", "board": BOARD}},
            "active kind with null cmd": {"test_kinds": {"unit": {"detect": "t", "exclude": "",
                                                                  "cmd": None, "status": "active"}}},
            "locally run kind": {"test_kinds": {"omp_session_accessor": LOCAL}},
            "zulu instant on any interpreter": {"decision_dispositions_era_start": "2026-11-22T01:58:29Z"},
            "signed matrix provenance": {"_matrix_provenance": {
                "api": {"removed": ["functional"], "added": [], "signed": "DEC-187"}}},
        }.items():
            with self.subTest(name):
                build_config(overrides)


REFUSED = [
    # (description, path, corrupted value, base overrides)
    ("unknown root key", ("colour",), "blue", None),
    ("unknown nested key", ("budgets", "extra"), 1, None),
    ("operational provenance is validated", ("_matrix_provenance", "api"), {"removed": []}, None),
    ("provenance names an unknown kind", ("_matrix_provenance", "api"),
     {"removed": ["service"], "added": [], "signed": "DEC-1"}, None),
    ("bool version", ("schema_version",), True, None),
    ("string version", ("schema_version",), "3", None),
    ("future version", ("schema_version",), 4, None),
    ("impossible date", ("panel_era_start",), "2026-02-30", None),
    ("unpadded date", ("seam_era_start",), "2026-1-2", None),
    ("instant without zone", ("decision_dispositions_era_start",), "2026-11-22T01:58:29", None),
    ("instant out of range", ("decision_dispositions_era_start",), "2026-11-22T25:00:00+00:00", None),
    ("numeric-string budget", ("budgets", "max_total_runs"), "20", None),
    ("bool budget", ("budgets", "max_total_cycles"), True, None),
    ("fractional budget", ("budgets", "max_total_cycles"), 1.5, None),
    ("negative cycles", ("budgets", "max_total_cycles"), -1, None),
    ("zero positive budget", ("budgets", "rework_round_minutes"), 0, None),
    ("zero preload words", ("budgets", "preload_warn_words", "agent"), 0, None),
    ("negative retention", ("log_retention_days",), -1, None),
    ("review enum", ("gates", "review"), "strict", None),
    ("whitelist entry", ("dirty_tree_whitelist",), [""], None),
    ("attribution prefix", ("commit_attribution", "agent_prefix"), "", None),
    ("repo with whitespace", ("github", "repo"), "acme /w", None),
    ("repo without owner", ("github", "repo"), "widgets", None),
    ("repo GitHub would refuse", ("github", "repo"), "a!/b", None),
    ("sync without repo", ("github", "repo"), DELETE, SYNCED),
    ("board without repo", ("github", "repo"), None, {"github": {"repo": "a/b", "board": BOARD}}),
    ("reordered stations", ("github", "board", "stations"),
     ["plan", "backlog", "ready", "building", "review", "done"], SYNCED),
    ("board number text", ("github", "board", "number"), "seven", SYNCED),
    ("incomplete board", ("github", "board", "station_field"), DELETE, SYNCED),
    ("empty board owner", ("github", "board", "owner"), "", SYNCED),
    ("unknown issue type", ("github", "issue_types", "Epic"), "Epic", None),
    ("empty issue type", ("github", "issue_types", "Bug"), "", None),
    ("unknown change type", ("test_matrix", "service"), {"always": []}, None),
    ("row without always", ("test_matrix", "logic", "always"), DELETE, None),
    ("unknown matrix kind", ("test_matrix", "logic", "always"), ["custom_kind"], None),
    ("when entry extra key", ("test_matrix", "api", "when"),
     [{"kind": "integration", "if": "touches_db_or_external", "also": 1}], None),
    ("unknown condition", ("test_matrix", "api", "when"), [{"kind": "integration", "if": "sometimes"}], None),
    ("bug class sentinel unpaired", ("test_matrix", "api", "when"),
     [{"kind": "__bug_class__", "if": "touches_runtime_code"}], None),
    ("bug class condition unpaired", ("test_matrix", "api", "when"),
     [{"kind": "unit", "if": "match_bug_class"}], None),
    ("unknown kind", ("test_kinds", "widget"), dict(LOCAL), None),
    ("status-less kind", ("test_kinds", "unit", "status"), DELETE, None),
    ("unknown status", ("test_kinds", "unit", "status"), "skipped", None),
    ("empty detect", ("test_kinds", "unit", "detect"), "", None),
    ("empty cmd", ("test_kinds", "unit", "cmd"), "", None),
    ("excluded without reason", ("test_kinds", "eval", "excluded_because"), DELETE,
     {"test_kinds": {"eval": EXCLUDED}}),
    ("excluded unsigned", ("test_kinds", "eval", "signed"), "187", {"test_kinds": {"eval": EXCLUDED}}),
    ("locally run without note", ("test_kinds", "ui", "runner_note"), DELETE, {"test_kinds": {"ui": LOCAL}}),
    ("locally run without cmd", ("test_kinds", "ui", "cmd"), None, {"test_kinds": {"ui": LOCAL}}),
]


class Refusals(unittest.TestCase):
    def test_each_broken_rule_is_refused_at_its_key_path(self):
        for description, path, value, base in REFUSED:
            with self.subTest(description):
                document = corrupt(path, value, build_config(base) if base else None)
                with self.assertRaises(accessors.ArtifactAccessError) as caught:
                    load(document)
                self.assertIn("case:", str(caught.exception))
                self.assertIn(f": {'.'.join(path)}", str(caught.exception))

    def test_version_two_names_the_upgrade(self):
        with self.assertRaisesRegex(accessors.ArtifactAccessError,
                                    r"case: schema_version: .*upgrade-config\.py"):
            load(corrupt(("schema_version",), 2))

    def test_first_error_is_chosen_by_key_path_and_names_the_rule(self):
        document = corrupt(("gates", "review"), "strict", corrupt(("budgets", "max_total_runs"), "x"))
        with self.assertRaisesRegex(accessors.ArtifactAccessError,
                                    r"^case: budgets\.max_total_runs: .*\[type\]$"):
            load(document)

    def test_nested_duplicate_and_nonfinite_values_are_refused(self):
        for text in ('{"schema_version": 3, "budgets": {"max_total_runs": 1, "max_total_runs": 2}}',
                     '{"schema_version": 3, "budgets": {"max_total_runs": NaN}}'):
            with self.subTest(text), self.assertRaises(accessors.ArtifactAccessError):
                accessors.load_harness_json(text=text, context="case")


class Sources(unittest.TestCase):
    def test_missing_file_and_wrong_source_count_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = os.path.join(directory, "harness.json")
            for call in (lambda: accessors.load_harness_json(missing),
                         lambda: accessors.load_harness_json(),
                         lambda: accessors.load_harness_json(missing, text="{}")):
                with self.subTest(call), self.assertRaises(accessors.ArtifactAccessError):
                    call()

    def test_each_load_returns_an_independent_mapping(self):
        first = build_config()
        first["dirty_tree_whitelist"].append("x/**")
        first["test_kinds"]["unit"]["status"] = "active"
        second = build_config()
        self.assertEqual([".harness/**", ".claude/worktrees/**"], second["dirty_tree_whitelist"])
        self.assertEqual("unresolved", second["test_kinds"]["unit"]["status"])

    def test_cli_prints_the_validated_config(self):
        printed = subprocess.run(
            [sys.executable, str(ROOT / "tests" / "harness_config_support.py"),
             "--overrides-json", '{"log_retention_days": 7}'],
            capture_output=True, text=True, check=True).stdout
        self.assertEqual(build_config({"log_retention_days": 7}), json.loads(printed))


class RuntimeProjections(unittest.TestCase):
    def test_runtime_copies_of_schema_vocabularies_are_equal_to_it(self):
        """Three runtime modules keep their own copy of a schema vocabulary; a drifted copy either
        refuses valid config or acts on values the schema no longer admits."""
        import factory_config
        import gate_policy
        import gh_issue_types
        import harness_config
        schema = json.loads(Path(harness_config.SCHEMA_PATH).read_text(encoding="utf-8"))
        self.assertEqual(schema["$defs"]["board"]["properties"]["stations"]["const"],
                         list(factory_config.MANDATED_STATIONS))
        self.assertEqual(set(schema["properties"]["gates"]["properties"]["review"]["enum"]),
                         gate_policy.GATE_VOCABULARIES["review"])
        self.assertEqual(list(schema["properties"]["github"]["properties"]["issue_types"]["properties"]),
                         list(gh_issue_types.LEGAL_OVERRIDE_KEYS))


if __name__ == "__main__":
    unittest.main()
