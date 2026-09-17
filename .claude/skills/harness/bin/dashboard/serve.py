#!/usr/bin/env python3
"""Loopback-only Flask server for the metrics dashboard."""
import argparse
import importlib
import mimetypes
from pathlib import Path
import socket
import subprocess
import sys

BIN = Path(__file__).resolve().parents[1]
DASHBOARD = Path(__file__).resolve().parent
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))
CLIENT_INDEX = DASHBOARD / "client" / "dist" / "index.html"
CLIENT_DIST = CLIENT_INDEX.parent
MIME_FALLBACKS = {
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".css": "text/css",
    ".html": "text/html",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
    ".map": "application/json",
}


def prerequisite_errors(root: Path, version=None, importer=None) -> list[str]:
    """Return every unmet dashboard runtime prerequisite without serving."""
    version = version or sys.version_info[:2]
    importer = importer or importlib.import_module
    errors = []
    if tuple(version[:2]) < (3, 10):
        errors.append("Python 3.10+ is required; install Python 3.10+")
    errors.extend(_module_errors(importer))
    if not (root / ".harness" / "harness.json").is_file():
        errors.append(".harness/harness.json is required; run python3 .agents/skills/harness/bin/harness-init.py")
    if not CLIENT_INDEX.is_file():
        errors.append("client/dist/index.html is required; run npm --prefix .claude/skills/harness/bin/dashboard/client run build")
    return errors


def _module_errors(importer) -> list[str]:
    errors = []
    for name, label, command in (
        ("yaml", "PyYAML", "python3 -m pip install pyyaml"),
        ("flask", "Flask", "python3 -m pip install flask"),
    ):
        try:
            importer(name)
        except ImportError:
            errors.append(f"{label} is required; run {command}")
    return errors


def create_app(root: Path):
    """Create the dashboard WSGI application rooted at one project."""
    from flask import Flask, jsonify, send_file, send_from_directory
    import kpi

    project_root = Path(root).resolve()
    app = Flask(__name__)

    @app.get("/api/kpis")
    def kpis():
        window = _window_or_error()
        if isinstance(window, tuple):
            return jsonify(window[0]), window[1]
        return jsonify(kpi.compute(project_root, window))

    @app.get("/assets/<path:asset_path>")
    def assets(asset_path):
        mimetype = _asset_mimetype(asset_path)
        return send_from_directory(CLIENT_DIST / "assets", asset_path, mimetype=mimetype)

    @app.get("/api/<path:unused>")
    def missing_api(unused):
        return jsonify(error="API route not found"), 404

    @app.get("/")
    @app.get("/<path:client_path>")
    def client(client_path=""):
        return send_file(CLIENT_INDEX, mimetype="text/html")

    return app


def _window_or_error():
    from flask import request
    window = request.args.get("window", "all")
    if window not in {"30d", "90d", "all"}:
        return {"error": "window must be one of 30d, 90d, all"}, 400
    return window


def _asset_mimetype(asset_path: str) -> str | None:
    suffix = Path(asset_path).suffix.lower()
    return MIME_FALLBACKS.get(suffix) or mimetypes.guess_type(asset_path)[0]


def _git_root(cwd: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise SystemExit("project root is required; run from a git repository or pass --root <project>")
    return Path(result.stdout.strip())


def _require_prerequisites(root: Path) -> None:
    errors = prerequisite_errors(root)
    if errors:
        raise SystemExit("\n".join(f"Prerequisite failed: {error}" for error in errors))


def _require_free_port(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as error:
            raise SystemExit(f"port {port} is busy: {error}") from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--port", type=int, default=8971)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else _git_root(Path.cwd())
    _require_prerequisites(root)
    if args.check:
        return 0
    _require_free_port(args.port)
    create_app(root).run(host="127.0.0.1", port=args.port, threaded=True, debug=False, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
