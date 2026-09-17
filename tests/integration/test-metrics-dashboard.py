#!/usr/bin/env python3
"""Behavioral integration coverage for the loopback metrics dashboard API."""
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
DASHBOARD = BIN / "dashboard"
SERVE = DASHBOARD / "serve.py"
FIXTURE = DASHBOARD / "fixtures" / "project-a"


def _load_serve():
    spec = importlib.util.spec_from_file_location("metrics_serve", SERVE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(project, *args):
    return subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)


class MetricsDashboardIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "project-a"
        shutil.copytree(FIXTURE, self.project)
        shutil.copy(ROOT / ".harness" / "harness.json", self.project / ".harness" / "harness.json")
        (self.project / "probe.py").write_text("def probe():\n    return 1\n", encoding="utf-8")
        _git(self.project, "init", "-q")
        _git(self.project, "config", "user.email", "test@example.test")
        _git(self.project, "config", "user.name", "Test User")
        _git(self.project, "add", ".")
        _git(self.project, "commit", "-qm", "fixture")
        self.serve = _load_serve()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_prerequisite_gate_checks_each_requirement_independently(self):
        self.assertEqual([], self.serve.prerequisite_errors(self.project))
        cases = [
            ((3, 9), None, "Python 3.10+", "install Python 3.10+"),
            (sys.version_info[:2], "yaml", "PyYAML", "python3 -m pip install pyyaml"),
            (sys.version_info[:2], "flask", "Flask", "python3 -m pip install flask"),
        ]
        for version, missing, prerequisite, command in cases:
            with self.subTest(prerequisite=prerequisite):
                importer = _importer_missing(missing) if missing else __import__
                errors = self.serve.prerequisite_errors(self.project, version=version, importer=importer)
                self.assertEqual(1, len(errors))
                self.assertIn(prerequisite, errors[0])
                self.assertIn(command, errors[0])
        missing_config = self.project / ".harness" / "harness.json"
        missing_config.unlink()
        errors = self.serve.prerequisite_errors(self.project)
        self.assertEqual(1, len(errors))
        self.assertIn(".harness/harness.json", errors[0])
        self.assertIn("harness-init", errors[0])
        shutil.copy(ROOT / ".harness" / "harness.json", missing_config)
        index = DASHBOARD / "client" / "dist" / "index.html"
        with patch.object(self.serve, "CLIENT_INDEX", index.with_name("missing.html")):
            errors = self.serve.prerequisite_errors(self.project)
        self.assertEqual(1, len(errors))
        self.assertIn("client/dist/index.html", errors[0])
        self.assertIn("npm --prefix", errors[0])

    def test_check_runs_only_prerequisite_gate(self):
        result = subprocess.run(
            [sys.executable, str(SERVE), "--root", str(self.project), "--check"],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)

    def test_busy_port_exits_nonzero_and_names_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
            result = subprocess.run(
                [sys.executable, str(SERVE), "--root", str(self.project), "--port", str(port)],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn(f"port {port} is busy", result.stderr)


    def test_fixture_api_routes_assets_and_no_writes(self):
        before = _git(self.project, "status", "--porcelain=v1").stdout
        client = self.serve.create_app(self.project).test_client()
        response = client.get("/api/kpis?window=all")
        self.assertEqual(200, response.status_code)
        _assert_fixture_payload(self, response.get_json(), self.project)
        _assert_client_routes(self, client)
        self.assertEqual(before, _git(self.project, "status", "--porcelain=v1").stdout)

    def test_work_api_filters_live_disk_payload_and_preserves_static_routes(self):
        control, alpha = _operational_fixture(self)
        client = self.serve.create_app(control).test_client()
        default_kpis = client.get("/api/kpis")
        default_work = client.get("/api/work")
        alpha_kpis = client.get("/api/kpis?window=30d&repo=alpha")
        alpha_work = client.get("/api/work?window=30d&repo=alpha")
        self.assertEqual(200, default_kpis.status_code)
        self.assertEqual(200, default_work.status_code)
        self.assertEqual(200, alpha_kpis.status_code)
        self.assertEqual(200, alpha_work.status_code)
        self.assertEqual("all", default_kpis.get_json()["window"])
        self.assertEqual(str(control.resolve()), default_kpis.get_json()["project"]["root"])
        self.assertEqual("all", default_work.get_json()["window"])
        self.assertEqual("all", default_work.get_json()["repo"])
        self.assertEqual("30d", alpha_kpis.get_json()["window"])
        self.assertEqual(str(alpha.resolve()), alpha_kpis.get_json()["project"]["root"])
        payload = alpha_work.get_json()
        _assert_work_payload(self, payload, "alpha")
        self.assertTrue(any(error["source_path"].endswith("FEAT-203-malformed") for error in payload["errors"]))
        feature = next(item for item in payload["items"] if item["kind"] == "bug")
        self.assertEqual(2, feature["cycles_used"])
        self.assertIsNone(feature["elapsed_by_phase"]["build"])
        self.assertIsNone(feature["elapsed_by_phase"]["validate"])
        self.assertEqual({"measured_total": 3, "measured_runs": 1, "total_runs": 2,
                          "unmeasured_runs": 1, "by_phase": {"plan": 3, "build": None, "validate": None}},
                         feature["tokens"])
        feature_json = Path(feature["source_path"]) / "feature.json"
        feature_json.write_text(json.dumps({"feature_id": "BUG-202-alpha", "branch": "main",
            "cycles_used": 6, "max_total_cycles": 7,
            "runs": [{"squad": "eng", "tokens": None}]}), encoding="utf-8")
        refreshed = client.get("/api/work?window=30d&repo=alpha")
        self.assertEqual(200, refreshed.status_code)
        refreshed_feature = next(item for item in refreshed.get_json()["items"] if item["id"] == feature["id"])
        self.assertEqual(6, refreshed_feature["cycles_used"])
        work_module = sys.modules["work"]
        original_run = subprocess.run
        def no_github(command, *args, **kwargs):
            self.assertNotEqual("gh", command[0])
            return original_run(command, *args, **kwargs)
        with patch.object(work_module.factory_config.factory_gh, "file_at_ref",
                          side_effect=AssertionError("dashboard reached GitHub")):
            with patch("subprocess.run", side_effect=no_github):
                isolated = client.get("/api/work?window=30d&repo=alpha")
        self.assertEqual(200, isolated.status_code)
        self.assertEqual({"error": "window must be one of 30d, 90d, all"},
                         client.get("/api/work?window=invalid").get_json())
        self.assertEqual({"error": "repo must be one of all, harness, alpha"},
                         client.get("/api/kpis?repo=missing").get_json())
        (control / ".harness" / "harness.json").write_text("{}", encoding="utf-8")
        unavailable = client.get("/api/work")
        self.assertEqual(500, unavailable.status_code)
        self.assertTrue(unavailable.is_json)
        self.assertIn("dashboard unavailable:", unavailable.get_json()["error"])
        shutil.copy(ROOT / ".harness" / "harness.json", control / ".harness" / "harness.json")
        shutil.rmtree(alpha)
        enumeration = client.get("/api/work")
        self.assertEqual(500, enumeration.status_code)
        self.assertIn("configured repository alpha cannot be enumerated", enumeration.get_json()["error"])
        _assert_client_routes(self, client)

    def test_repository_api_request_is_kpi_payload_under_ceiling(self):
        before = _git(ROOT, "status", "--porcelain=v1").stdout
        app = self.serve.create_app(ROOT)
        started = time.monotonic()
        response = app.test_client().get("/api/kpis?window=all")
        elapsed = time.monotonic() - started
        print(f"full repository /api/kpis elapsed: {elapsed:.3f}s")
        self.assertEqual(200, response.status_code, response.get_json())
        self.assertEqual("kpi/1", response.get_json()["schema"])
        self.assertLess(elapsed, 8.0)
        self.assertEqual(before, _git(ROOT, "status", "--porcelain=v1").stdout)




def _operational_fixture(test):
    control = Path(test.tempdir.name) / "control"
    alpha = control / "workspace" / "alpha"
    _write_operational_repo(control)
    _write_operational_repo(alpha)
    (control / ".harness" / "factory").mkdir(parents=True)
    (control / ".harness" / "factory" / "fleet.yaml").write_text(
        "schema: factory-fleet/1\n"
        f"workspace_root: {control / 'workspace'}\n"
        "repos:\n  - name: acme/alpha\n    default_branch: main\n", encoding="utf-8")
    _write_operational_feature(control / ".harness" / "harness" / "features" / "FEAT-101-harness",
                               "FEAT-101-harness", "building", 1)
    _write_operational_feature(control / ".harness" / "alpha" / "features" / "BUG-202-alpha",
                               "BUG-202-alpha", "review", 2)
    (control / ".harness" / "alpha" / "features" / "FEAT-203-malformed").mkdir(parents=True)
    return control, alpha


def _write_operational_repo(path):
    path.mkdir(parents=True)
    (path / ".harness").mkdir()
    shutil.copy(ROOT / ".harness" / "harness.json", path / ".harness" / "harness.json")
    (path / "probe.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "test@example.test")
    _git(path, "config", "user.name", "Test User")
    _git(path, "add", ".")
    _git(path, "commit", "-qm", "fixture")


def _write_operational_feature(path, feature_id, station, cycles):
    path.mkdir(parents=True)
    (path / "feature.json").write_text(json.dumps({
        "feature_id": feature_id, "branch": "main", "cycles_used": cycles, "max_total_cycles": 7,
        "runs": [{"squad": "product", "tokens": 3}, {"squad": "eng", "tokens": None}],
    }), encoding="utf-8")
    (path / "plan.yaml").write_text(
        f"schema: plan/1\nfeature: {feature_id}\nstatus: {station}\ntasks: []\n", encoding="utf-8")
    (path / "BRIEF.md").write_text("## Approval\nstatus: approved\ndate: 2026-09-16\n",
                                   encoding="utf-8")


def _assert_work_payload(test, payload, repository):
    expected = {
        "id", "kind", "attention", "attention_reasons", "name", "repository", "segment", "station",
        "phase", "run_status", "updated_at", "elapsed_total", "elapsed_by_phase", "runs",
        "cycles_used", "max_total_cycles", "tokens", "main_path", "worktree_path", "source_path",
        "detail",
    }
    test.assertEqual("harness-work/1", payload["schema"])
    test.assertEqual(["needs-you", "blocked", "stalled", "over-budget", "running", "stale"],
                     payload["attention_order"])
    test.assertEqual({"stalled_minutes": 45, "stale_days": 7, "over_budget_remaining_cycles": 1},
                     payload["effective_thresholds"])
    test.assertTrue(payload["errors"])
    test.assertTrue(all(item["segment"] == repository for item in payload["items"]))
    test.assertEqual(sorted(payload["items"], key=lambda item: (
        payload["attention_order"].index(item["attention"]) if item["attention"] in payload["attention_order"]
        else len(payload["attention_order"]), item["id"])), payload["items"])
    for item in payload["items"]:
        test.assertEqual(expected, set(item))
        test.assertEqual({"plan", "build", "validate"}, set(item["elapsed_by_phase"]))
        test.assertNotIn("cost", json.dumps(item))
        if item["tokens"] is not None:
            test.assertEqual({"measured_total", "measured_runs", "total_runs", "unmeasured_runs", "by_phase"},
                             set(item["tokens"]))
            test.assertEqual({"plan", "build", "validate"}, set(item["tokens"]["by_phase"]))
def _assert_fixture_payload(test, payload, project):
    test.assertEqual("kpi/1", payload["schema"])
    test.assertEqual(str(project.resolve()), payload["project"]["root"])
    test.assertEqual("project-a", payload["project"]["name"])
    test.assertNotEqual(str(ROOT.resolve()), payload["project"]["root"])
    test.assertEqual("all", payload["window"])
    shipped = next(item for item in payload["features"] if item["feature_id"] == "FIX-SHIPPED")
    test.assertEqual("FIX-SHIPPED", shipped["feature_id"])


def _assert_client_routes(test, client):
    routes = [client.get(route) for route in ("/", "/kpi/1", "/work/FIX-SHIPPED")]
    test.assertEqual([200, 200, 200], [route.status_code for route in routes])
    for route in routes:
        route.close()
    asset = client.get("/assets/index-hkwR5g06.js")
    test.assertEqual(200, asset.status_code)
    test.assertNotEqual("text/plain", asset.mimetype)
    test.assertIn("javascript", asset.mimetype)
    asset.close()
    traversal = client.get("/assets/../serve.py")
    test.assertIn(traversal.status_code, {400, 404})
    traversal.close()
    _assert_api_errors(test, client)


def _assert_api_errors(test, client):
    for endpoint in ("/api/kpis?window=nope", "/api/unknown"):
        error = client.get(endpoint)
        test.assertIn(error.status_code, {400, 404})
        test.assertTrue(error.is_json)
        test.assertIn("error", error.get_json())

def _importer_missing(missing):
    def importer(name):
        if name == missing:
            raise ImportError(f"No module named {name}")
        return __import__(name)
    return importer


if __name__ == "__main__":
    unittest.main()
