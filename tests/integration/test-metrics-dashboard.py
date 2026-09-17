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

    def test_repository_api_request_is_kpi_payload_under_ceiling(self):
        before = _git(ROOT, "status", "--porcelain=v1").stdout
        app = self.serve.create_app(ROOT)
        started = time.monotonic()
        response = app.test_client().get("/api/kpis?window=all")
        elapsed = time.monotonic() - started
        print(f"full repository /api/kpis elapsed: {elapsed:.3f}s")
        self.assertEqual(200, response.status_code)
        self.assertEqual("kpi/1", response.get_json()["schema"])
        self.assertLess(elapsed, 8.0)
        self.assertEqual(before, _git(ROOT, "status", "--porcelain=v1").stdout)


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
    asset = client.get("/assets/index-DzoXKmQ_.js")
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
