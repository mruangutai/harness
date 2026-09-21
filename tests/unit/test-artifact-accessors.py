#!/usr/bin/env python3
"""Contract tests for the public artifact accessor seam."""
import json
import os
import sys
import tempfile
import subprocess
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
import artifact_accessors as accessors  # noqa: E402


class SystemPythonCompatibilityContracts(unittest.TestCase):
    def test_macos_system_python_imports_typed_manifest_records(self):
        if sys.platform != "darwin":
            self.skipTest("macOS system Python is unavailable")
        system_python = Path("/usr/bin/python3")
        if not system_python.is_file():
            self.skipTest("macOS system Python is unavailable")
        version = subprocess.run(
            [str(system_python), "-c", "import sys; print('%s.%s' % sys.version_info[:2])"],
            capture_output=True,
            text=True,
        )
        if version.returncode:
            self.skipTest("macOS system Python is unavailable")
        major, minor = (int(part) for part in version.stdout.strip().split("."))
        if (major, minor) >= (3, 10):
            self.skipTest("macOS system Python is not an affected pre-3.10 runtime")
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(BIN) + os.pathsep + environment.get("PYTHONPATH", "")
        imported = subprocess.run(
            [
                str(system_python),
                "-c",
                "import artifact_accessors; "
                "assert artifact_accessors.ManifestRoleDomains; "
                "assert artifact_accessors.ManifestDomainsView",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=environment,
        )
        self.assertEqual("", imported.stdout)
        self.assertEqual("", imported.stderr)
        self.assertEqual(0, imported.returncode)


class JsonContracts(unittest.TestCase):
    def test_nonfinite_json_constants_are_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "harness.json"
                path.write_text('{"value": ' + value + '}', encoding="utf-8")
                with self.assertRaises(accessors.ArtifactAccessError):
                    accessors.load_harness_json(path)

    def test_in_memory_json_retains_caller_context(self):
        with self.assertRaises(accessors.ArtifactAccessError) as caught:
            accessors.parse_gh_json('{"value": NaN}', "gh issue view acme/widget")
        self.assertIn("gh issue view acme/widget", str(caught.exception))

    def test_github_json_accepts_any_strict_json_value(self):
        cases = (
            ('{"nested": {"value": 7}}', {"nested": {"value": 7}}),
            ('[{"value": 7}, 2]', [{"value": 7}, 2]),
            ('"complete"', "complete"),
            ("42", 42),
            ("true", True),
            ("null", None),
        )
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(
                    expected, accessors.parse_gh_json(text, "gh api result")
                )

    def test_github_json_strict_failures_preserve_context_and_type(self):
        cases = (
            ('{"outer": {"key": 1, "key": 2}}', "duplicate key"),
            ("NaN", "non-finite JSON constant"),
            ("Infinity", "non-finite JSON constant"),
            ("-Infinity", "non-finite JSON constant"),
        )
        context = "gh api repos/acme/widget"
        for text, expected in cases:
            with self.subTest(text=text):
                with self.assertRaisesRegex(
                    accessors.ArtifactAccessError, expected
                ) as caught:
                    accessors.parse_gh_json(text, context)
                self.assertIn(context, str(caught.exception))

    def test_harness_json_accepts_explicit_text_source_with_context(self):
        document = accessors.load_harness_json(
            text='{"nested": {"value": 7}}',
            context="mruangutai/harness@main:.harness/harness.json",
        )
        self.assertEqual({"nested": {"value": 7}}, document)

    def test_harness_json_text_source_has_path_contract(self):
        cases = (
            ('{"nested": {"key": 1, "key": 2}}', "duplicate key"),
            ('{"value": NaN}', "non-finite JSON constant"),
            ('[1, 2, 3]', "not a mapping"),
        )
        context = "remote harness.json"
        for text, expected in cases:
            with self.subTest(text=text):
                with self.assertRaisesRegex(accessors.ArtifactAccessError, expected) as caught:
                    accessors.load_harness_json(text=text, context=context)
                self.assertIn(context, str(caught.exception))

    def test_harness_json_requires_exactly_one_source(self):
        with self.assertRaises(accessors.ArtifactAccessError):
            accessors.load_harness_json()
        with self.assertRaises(accessors.ArtifactAccessError):
            accessors.load_harness_json(
                "harness.json", text="{}", context="remote harness.json"
            )



    def test_feature_json_rejects_malformed_recorded_blocks(self):
        invalid_blocks = (
            {"github": {"parent": True}},
            {"github": {"issues": []}},
            {"factory": {"parent": "not-a-number"}},
            {"factory": {"issues": []}},
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feature.json"
            for block in invalid_blocks:
                with self.subTest(block=block):
                    path.write_text(json.dumps(block), encoding="utf-8")
                    with self.assertRaisesRegex(Exception, "recorded issue number|issues"):
                        accessors.load_feature_json(path)

    def test_feature_json_preserves_absent_blocks_and_numeric_strings(self):
        document = {
            "feature_id": "F1",
            "github": {"parent": "7", "issues": {"T-01": "8"}},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feature.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            self.assertEqual(document, accessors.load_feature_json(path))

    # FEAT-61 T-01: ONE strict decoding primitive. Every strict JSON reader in bin/ (harness.json,
    # feature.json, gh payloads, feature_json_write.parse_doc) goes through it, so a tightening
    # lands everywhere at once instead of in whichever of two hand-copied hook pairs got edited.
    def test_strict_json_loads_rejects_nested_duplicates_and_nonfinite_as_valueerror(self):
        for text in (
            '{"outer": {"key": 1, "key": 2}}',
            '[{"a": 1, "a": 2}]',
            '{"value": NaN}',
            '{"value": Infinity}',
            '{"value": -Infinity}',
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                accessors.strict_json_loads(text)

    def test_strict_json_loads_returns_any_json_value_untouched(self):
        for text, expected in (
            ('{"nested": {"value": 7}}', {"nested": {"value": 7}}),
            ('[{"value": 7}, 2]', [{"value": 7}, 2]),
            ("3", 3),
            ('"x"', "x"),
        ):
            with self.subTest(text=text):
                self.assertEqual(expected, accessors.strict_json_loads(text))

    # The run-step contract is read by two gates (check-state INV-16, check-domain's version-2
    # step closure). One accessor owns the navigation so a schema restructure moves one site.
    def test_load_run_step_contract_returns_step_schema_declared_keys_and_evidence_pattern(self):
        contract = accessors.load_run_step_contract(BIN)
        step_schema, declared, pattern = contract
        with open(BIN / "run-state-schema.json", encoding="utf-8") as handle:
            raw = json.load(handle)["properties"]["steps"]["items"]
        self.assertEqual(raw, step_schema)
        self.assertEqual(set(raw["properties"]), declared)
        self.assertEqual(raw["properties"]["evidence"]["propertyNames"]["pattern"], pattern)

    def test_load_run_step_contract_preserves_natural_failures_for_malformed_shapes(self):
        # Both callers absorb with `except Exception` and print the exception's class and text;
        # wrapping would change those bytes. So: a missing key is a KeyError, a wrong container
        # is a TypeError, exactly as the inline navigation raised them.
        cases = (
            ('{"properties": {}}', KeyError),
            ('{"properties": {"steps": []}}', TypeError),
            ('{"properties": {"steps": {"items": {"properties": {}}}}}', KeyError),
        )
        for text, expected in cases:
            with self.subTest(text=text), tempfile.TemporaryDirectory() as directory:
                (Path(directory) / "run-state-schema.json").write_text(text, encoding="utf-8")
                with self.assertRaises(expected):
                    accessors.load_run_step_contract(directory)

    def test_load_run_step_contract_is_strict_about_the_schema_file_itself(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "run-state-schema.json").write_text(
                '{"properties": {"steps": 1, "steps": 2}}', encoding="utf-8")
            with self.assertRaises(accessors.ArtifactAccessError):
                accessors.load_run_step_contract(directory)

class ManifestDomainsContracts(unittest.TestCase):
    def test_omitted_agent_aggregates_named_role_writes_only(self):
        manifest = """\
roles:
  - name: alpha
    domain:
      - path: alpha-write
      - path: alpha-read
        read: true
nested:
  coordinator:
    name: beta
    domain:
      - path: beta-write
      - path: beta-read
        read: true
shared:
  - path: shared-write
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "team-config.yaml"
            path.write_text(manifest, encoding="utf-8")
            self.assertEqual(
                (["alpha-write", "beta-write"], ["shared-write"]),
                accessors.manifest_domains(path),
            )
            self.assertEqual(
                (["alpha-write", "beta-write"], ["shared-write"]),
                accessors.manifest_domains(path, None),
            )
            self.assertEqual(
                (["alpha-write"], ["shared-write"]),
                accessors.manifest_domains(path, "alpha"),
            )

    def test_view_returns_immutable_ordered_role_records_and_reads_once(self):
        manifest = """\
teams:
  - members:
      - name: member
        domain:
          - path: member-write
          - path: member-read
            read: true
    leads:
      - name: lead
        domain:
          - path: 12
  - members:
      - name: member
        domain:
          - path: member-second
harness-orchestrator:
  name: top
  domain:
    - path: top-write
shared:
  - path: shared-write
  - path: shared-read
    read: true
main_session:
  writes: ["  keep  ", 7, "", "last"]
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "team-config.yaml"
            path.write_text(manifest, encoding="utf-8")
            with mock.patch("harness_yaml.load_file", wraps=__import__("harness_yaml").load_file) as load_file:
                view = accessors.manifest_domains(path, view=True)
            self.assertEqual(1, load_file.call_count)
        self.assertEqual(
            (
                accessors.ManifestRoleDomains("member", ("member-write", "member-second")),
                accessors.ManifestRoleDomains("lead", ("12",)),
                accessors.ManifestRoleDomains("top", ("top-write",)),
            ),
            view.roles,
        )
        self.assertEqual(("shared-write",), view.shared_write_globs)
        self.assertTrue(view.main_session_present)
        self.assertEqual(("  keep  ", "last"), view.main_session_writes)
        with self.assertRaises((AttributeError, TypeError)):
            view.roles += ()
        with self.assertRaises((AttributeError, TypeError)):
            view.roles[0].name = "changed"

    def test_view_coerces_role_names_to_its_public_string_type(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "team-config.yaml"
            path.write_text("roles:\n  - name: 17\n    domain: []\n", encoding="utf-8")
            view = accessors.manifest_domains(path, view=True)
        self.assertEqual((accessors.ManifestRoleDomains("17", ()),), view.roles)
    def test_view_keeps_named_roles_with_missing_or_invalid_domains(self):
        manifest = """\
roles:
  - name: missing
  - name: invalid
    domain: not-a-list
  - name: aggregate
  - name: aggregate
    domain:
      - path: aggregate-first
  - name: aggregate
    domain:
      - path: aggregate-read
        read: true
      - path: aggregate-second
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "team-config.yaml"
            path.write_text(manifest, encoding="utf-8")
            view = accessors.manifest_domains(path, view=True)
        self.assertEqual(
            (
                accessors.ManifestRoleDomains("missing", ()),
                accessors.ManifestRoleDomains("invalid", ()),
                accessors.ManifestRoleDomains(
                    "aggregate", ("aggregate-first", "aggregate-second")
                ),
            ),
            view.roles,
        )

    def test_view_main_session_absence_and_invalid_write_states(self):
        cases = (
            ("roles: []\n", False, None),
            ("main_session: {}\n", True, None),
            ("main_session:\n  writes: wrong\n", True, None),
            ("main_session:\n  writes: []\n", True, None),
            ("main_session:\n  writes: [7, ' ', '']\n", True, ()),
        )
        with tempfile.TemporaryDirectory() as directory:
            for number, (manifest, present, writes) in enumerate(cases):
                path = Path(directory) / f"{number}.yaml"
                path.write_text(manifest, encoding="utf-8")
                view = accessors.manifest_domains(path, view=True)
                self.assertEqual(present, view.main_session_present)
                self.assertEqual(writes, view.main_session_writes)

    def test_view_preserves_strict_yaml_errors_and_rejects_agent(self):
        harness_yaml = __import__("harness_yaml")
        with tempfile.TemporaryDirectory() as directory:
            duplicate = Path(directory) / "duplicate.yaml"
            duplicate.write_text("shared: []\nshared: []\n", encoding="utf-8")
            with self.assertRaises(harness_yaml.DuplicateKeyError):
                accessors.manifest_domains(duplicate, view=True)
            for name, manifest in (
                ("malformed.yaml", "shared: [\n"),
                ("nonmapping.yaml", "[]\n"),
            ):
                path = Path(directory) / name
                path.write_text(manifest, encoding="utf-8")
                with self.assertRaises(harness_yaml.YamlParseError):
                    accessors.manifest_domains(path, view=True)
            with self.assertRaises(harness_yaml.YamlParseError):
                accessors.manifest_domains(Path(directory) / "missing.yaml", view=True)
            non_utf8 = Path(directory) / "non-utf8.yaml"
            non_utf8.write_bytes(b"\xff")
            with self.assertRaises(harness_yaml.YamlParseError):
                accessors.manifest_domains(non_utf8, view=True)
        with self.assertRaisesRegex(TypeError, "view"):
            accessors.manifest_domains("unused.yaml", "alpha", view=True)


class YamlContracts(unittest.TestCase):
    def test_frontmatter_rejects_duplicate_yaml_keys(self):
        with self.assertRaises(accessors.ArtifactAccessError):
            accessors.load_frontmatter("---\nname: one\nname: two\n---\nbody", "agent.md")

    def test_omp_config_accepts_both_yaml_extensions(self):
        with tempfile.TemporaryDirectory() as directory:
            for suffix in (".yml", ".yaml"):
                path = Path(directory) / ("config" + suffix)
                path.write_text("name: omp\n", encoding="utf-8")
                self.assertEqual({"name": "omp"}, accessors.load_omp_config(path))


class WriterContract(unittest.TestCase):
    def test_writer_makes_backup_and_writes_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "harness.json"
            path.write_text('{"schema_version": 1}\n', encoding="utf-8")
            accessors.write_harness_json(path, {"schema_version": 2})
            self.assertEqual({"schema_version": 2}, json.loads(path.read_text(encoding="utf-8")))
            self.assertEqual('{"schema_version": 1}\n', path.with_name("harness.json.harness-bak").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
