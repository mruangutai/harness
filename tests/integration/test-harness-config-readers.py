#!/usr/bin/env python3
"""FEAT-2297 T-03: every harness.json reader and refusal boundary, against one config population.

The malformed shapes are defined ONCE (BROKEN) and every reader meets each of them, plus a valid
built config. A reader must refuse a broken or missing config with a diagnosis that names the
source — never default it to {}, None, "nothing written" or a fallback — and must act normally
on a valid one. Gates and check-state run as real subprocesses; the Bash gates must recognise
their governed command BEFORE reading config, so a repair command stays reachable.
"""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
for path in (BIN, ROOT / "tests", ROOT / "tests" / "integration"):
    sys.path.insert(0, str(path))
from harness_config_support import build_config, write_config  # noqa: E402
import artifact_accessors  # noqa: E402

# name -> (write the broken config into the file at path, token its diagnosis must carry)
BROKEN = {
    "unknown key": (lambda p: p.write_text(json.dumps({**build_config(), "colour": "blue"})), "colour"),
    "version 2": (lambda p: p.write_text(json.dumps({**build_config(), "schema_version": 2})), "upgrade-config.py"),
    "not JSON": (lambda p: p.write_text(json.dumps(build_config())[:-1]), "invalid JSON"),
    "missing": (lambda p: p.unlink(), "No such file"),
}


def _module(name, relative):
    spec = importlib.util.spec_from_file_location(name, BIN / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolve string annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def project(overrides=None):
    """A harness root: the team-config marker plus a built harness.json."""
    root = Path(tempfile.mkdtemp())
    (root / ".harness").mkdir()
    (root / ".harness" / "team-config.yaml").write_text("teams: []\n")
    write_config(root / ".harness" / "harness.json", overrides)
    return root


def outcome(call):
    """('ok', value) or ('refused', diagnosis). An exit-0 SystemExit is a silent skip: 'ok'."""
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            return "ok", call()
    except SystemExit as stop:
        return ("ok", None) if stop.code in (0, None) else ("refused", f"{stop.code} {out.getvalue()}")
    except Exception as error:  # every typed refusal: ArtifactAccessError, FleetError, GatePolicyError ...
        return "refused", f"{type(error).__name__}: {error} {out.getvalue()}"


@contextlib.contextmanager
def cwd(path):
    before = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(before)


def _feature_dir(root):
    feat = root / ".harness" / "harness" / "features" / "FEAT-1-x"
    feat.mkdir(parents=True, exist_ok=True)
    return feat


def _board_station(root):
    with cwd(root):
        code = _module("board_station", "board-station.py").main(["12", "building"])
    if code:
        raise SystemExit(code)
    return code


def _matrix_inputs(root):
    feat = _feature_dir(root)
    (feat / "plan.yaml").write_text("schema: plan/1\nfeature: FEAT-1-x\nstation_only: true\nstatus: plan\ntasks: []\n")
    return _module("validate_digest", "validate-digest.py")._load_matrix_inputs(str(root), str(feat))


def _test_kinds_or_refusal(root):
    kinds, error = _module("validate_digest", "validate-digest.py")._load_test_kinds(str(root))
    if error:
        raise SystemExit(error)
    return kinds


def _era(root):
    import plan_merge.check as check
    when, failure = check._era(str(root))
    if failure:
        raise SystemExit(failure)
    return when


def _unbound(root):
    return _module("gh_sync", "gh-sync.py")._unbound_project_config(str(root))


def _probe(root):
    probe = importlib.util.spec_from_file_location("probe", ROOT / "tests" / "manual" / "probe-issue-types.py")
    module = importlib.util.module_from_spec(probe)
    probe.loader.exec_module(module)
    module._ROOT = str(root)
    return module._load_config()


def _wayfind(root):
    with cwd(root):
        return _module("wayfind", "wayfind.py").cfg()


def _legal_stations(root):
    import plan_merge.guards as guards
    return guards._legal_stations(str(_feature_dir(root) / "plan.yaml"))


def _declared_segments(root):
    """layout_migration applies only where a fleet is declared, so the reader meets one."""
    fleet = root / ".harness" / "factory" / "fleet.yaml"
    fleet.parent.mkdir(parents=True, exist_ok=True)
    fleet.write_text("schema: factory-fleet/1\nrepos:\n  - name: product/app\n    default_branch: main\n"
                     f"workspace_root: {root}/members\n")
    return _module("lm", "layout_migration.py")._declared_segments(str(root))


# reader -> (call(root), what a VALID default config must yield)
READERS = {
    "board-station.main": (_board_station, lambda v: v == 0),
    "board_lifecycle._own_repo": (lambda r: _module("bl", "board_lifecycle.py")._own_repo(str(r)), lambda v: v is None),
    "check-skill-weight._budget": (lambda r: _module("csw", "check-skill-weight.py")._budget(r),
                                   lambda v: v == {"universal": 1900, "agent": 5500}),
    "code-grade._load_test_kinds": (lambda r: _module("cg", "code-grade.py")._load_test_kinds(r),
                                    lambda v: "unit" in v),
    "feature-record._budgets_for": (lambda r: _module("fr", "feature-record.py")._budgets_for(
        str(_feature_dir(r) / "feature.json")), lambda v: v["rework_round_minutes"] == 45),
    "feature_schema._owner_mirror_binding": (
        lambda r: _module("fs", "feature_schema.py")._owner_mirror_binding(str(r)), lambda v: v == (None, None, {})),
    "gate_policy.load_policy": (lambda r: _module("gp", "gate_policy.py").load_policy(
        str(r / ".harness" / "harness.json")), lambda v: v == {"review": "advisory_unless_high"}),
    "gh-sync._unbound_project_config": (_unbound, lambda v: v["github"]["sync"] is False),
    "gh_board.load_board": (lambda r: _module("gb", "gh_board.py").load_board(str(r)), lambda v: v is None),
    "layout_migration._declared_segments": (_declared_segments, lambda v: v == {"app"}),
    "plan_merge.check._era": (_era, lambda v: v is None),
    "plan_merge.guards._legal_stations": (_legal_stations, lambda v: v[:6] == (
        "backlog", "plan", "ready", "building", "review", "done")),
    "validate-digest._load_test_kinds": (_test_kinds_or_refusal, lambda v: "unit" in v),
    "validate-digest._load_matrix_inputs": (_matrix_inputs, lambda v: v[0]["logic"] == {"always": ["unit"], "when": []}),
    "wayfind.cfg": (_wayfind, None),  # a valid default has sync off, which wayfind refuses by design
    "probe-issue-types._load_config": (_probe, lambda v: v["github"]["sync"] is False),
}


class Readers(unittest.TestCase):
    def test_every_reader_refuses_each_broken_config_naming_its_source(self):
        for reader, (call, _) in READERS.items():
            for shape, (breaks, token) in BROKEN.items():
                with self.subTest(reader=reader, config=shape):
                    root = project()
                    breaks(root / ".harness" / "harness.json")
                    state, detail = outcome(lambda: call(root))
                    self.assertEqual("refused", state, f"{reader} accepted a {shape} config: {detail!r}")
                    self.assertIn(token, str(detail))

    def test_every_reader_acts_on_a_valid_default_config(self):
        for reader, (call, expected) in READERS.items():
            if expected is None:
                continue
            with self.subTest(reader=reader):
                root = project()
                state, value = outcome(lambda: call(root))
                self.assertEqual("ok", state, value)
                self.assertTrue(expected(value), value)



class Boards(unittest.TestCase):
    def test_a_valid_board_is_normalised_idempotently(self):
        gh_board = _module("gb", "gh_board.py")
        factory_config = _module("factory_config", "factory_config.py")
        board = {"owner": "acme", "number": " 7 ", "station_field": "Status",
                 "stations": ["backlog", "plan", "ready", "building", "review", "done"]}
        root = project({"github": {"repo": "acme/w", "board": board}})
        loaded = gh_board.load_board(str(root))
        self.assertEqual(7, loaded["number"])
        self.assertIsInstance(loaded["stations"], tuple)
        self.assertEqual(loaded, factory_config.validate_board(loaded))


class RemoteProductConfig(unittest.TestCase):
    def setUp(self):
        self.factory_config = _module("factory_config", "factory_config.py")
        self.factory_config.clear_product_config_memo()
        self.fleet = {"repos": [{"name": "acme/app", "default_branch": "main"},
                                {"name": "acme/ok", "default_branch": "main"}]}
        self.served = {}
        self.calls = []

        def fetch(repo, path, ref):
            self.calls.append(repo)
            return self.served[repo]
        self.factory_config.factory_gh.file_at_ref = fetch

    def test_invalid_remote_text_is_refused_with_its_diagnosis_and_no_local_fallback(self):
        self.served["acme/app"] = json.dumps({**build_config(), "colour": "blue"})
        with self.assertRaises(artifact_accessors.FleetError) as caught:
            self.factory_config.product_config(self.fleet, "acme/app")
        self.assertIn("acme/app@main:.harness/harness.json", str(caught.exception))
        self.assertIn("colour", str(caught.exception))

    def test_success_is_memoised_and_failure_never_is(self):
        self.served["acme/app"] = "{"
        with self.assertRaises(artifact_accessors.FleetError):
            self.factory_config.product_config(self.fleet, "acme/app")
        self.served["acme/app"] = json.dumps(build_config())
        self.factory_config.product_config(self.fleet, "acme/app")
        self.factory_config.product_config(self.fleet, "acme/app")
        self.assertEqual(["acme/app", "acme/app"], self.calls)

    def test_an_invalid_member_fails_the_aggregate_beside_a_valid_one(self):
        self.served["acme/app"] = json.dumps({**build_config(), "schema_version": 2})
        self.served["acme/ok"] = json.dumps(build_config())
        report = {e["repo"]: e for e in self.factory_config.product_config_report(self.fleet)}
        self.assertTrue(report["acme/ok"]["ok"])
        self.assertFalse(report["acme/app"]["ok"])
        self.assertIn("upgrade-config.py", report["acme/app"]["detail"])

    def test_issue_type_overrides_refuse_rather_than_default(self):
        decompose = _module("factory_decompose", "factory_decompose.py")
        decompose.factory_config = self.factory_config
        self.served["acme/app"] = "{"
        with self.assertRaises(artifact_accessors.FleetError):
            decompose._issue_type_overrides(self.fleet, "acme/app")


class GenericReads(unittest.TestCase):
    def test_non_config_json_reads_are_not_schema_validated(self):
        import check_state.ctx as ctx
        import digest_schema
        import run_identity
        feat = _feature_dir(project())
        (feat / "feature.json").write_text(json.dumps({"feature_id": "FEAT-1-x", "anything": 1}))
        self.assertEqual(1, ctx.comparison_record(str(feat / "feature.json"))["anything"])
        self.assertIsInstance(digest_schema.load_schema("harness-qa"), dict)
        (feat / ".run-identity.json").write_text(json.dumps({"run_uid": "u"}))
        self.assertEqual({"run_uid": "u"}, run_identity.read_marker(str(feat)))


# --- real subprocesses -----------------------------------------------------------------------
GATES = {  # gate -> a command it governs
    "gh-close-gate.py": "gh issue close 5",
    "branch-create-gate.py": "git checkout -b feat/FEAT-9-x",
    "merge-gate.py": "gh pr merge 12 --squash",
}
REPAIRS = ("python3 .claude/skills/harness/bin/upgrade-config.py . --config-only",
           "python3 .claude/skills/harness/bin/check-state.py", "ls -la")


def gate(script, command, root):
    result = subprocess.run([str(BIN / script)], input=json.dumps({"tool_input": {"command": command}}),
                            capture_output=True, text=True, env=dict(os.environ, HARNESS_PROJECT_DIR=str(root)))
    denied = '"deny"' in result.stdout
    return result.returncode != 0 or denied, result.stdout + result.stderr


class Gates(unittest.TestCase):
    def test_governed_actions_are_blocked_on_a_broken_config_with_its_diagnosis(self):
        for script, command in GATES.items():
            for action in (command, f"{REPAIRS[0]} && {command}", f"bash -c '{command}'"):
                for shape, (breaks, token) in BROKEN.items():
                    with self.subTest(gate=script, command=action, config=shape):
                        root = project({"github": {"sync": False}})
                        breaks(root / ".harness" / "harness.json")
                        blocked, output = gate(script, action, root)
                        self.assertTrue(blocked, output)
                        self.assertIn(token, output)

    def test_repair_and_unrelated_commands_pass_without_a_config(self):
        for script in GATES:
            for command in REPAIRS:
                with self.subTest(gate=script, command=command):
                    root = project()
                    BROKEN["unknown key"][0](root / ".harness" / "harness.json")
                    blocked, output = gate(script, command, root)
                    self.assertFalse(blocked, output)

    def test_valid_sync_off_is_never_a_config_refusal(self):
        for script, command in GATES.items():
            with self.subTest(gate=script):
                _, output = gate(script, command, project({"github": {"sync": False}}))
                self.assertNotIn("harness.json", output)


class CheckState(unittest.TestCase):
    def run_check_state(self, *args):
        from check_state_support import SCRIPT, _root_env, make_fixture
        root = tempfile.mkdtemp()
        make_fixture(root, "{}", "  parent: 40")
        (Path(root) / ".harness" / "team-config.yaml").write_text("teams: []\n")
        BROKEN["unknown key"][0](Path(root) / ".harness" / "harness.json")
        return subprocess.run([SCRIPT, *args], cwd=root, capture_output=True, text=True, env=_root_env(root))

    def test_an_invalid_config_is_reported_and_grading_stops(self):
        for args in ((), ("--changed",), ("--only", "INV-22")):
            with self.subTest(args=args):
                result = self.run_check_state(*args)
                self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                self.assertIn("colour", result.stdout)
                self.assertNotIn("Traceback", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
