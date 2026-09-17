#!/usr/bin/env python3
"""Loopback-only Flask server for the metrics dashboard."""
import argparse
from datetime import datetime, timezone
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
    import attention
    import artifact_accessors
    import kpi
    import work

    project_root = Path(root).resolve()
    app = Flask(__name__)

    @app.before_request
    def require_loopback_host():
        from flask import request
        if not _trusted_host(request.host):
            return jsonify(error="dashboard is available only to loopback hosts"), 400

    @app.get("/api/kpis")
    def kpis():
        selection = _selection_or_error(project_root, require_all=False)
        if isinstance(selection, tuple):
            return jsonify(selection[0]), selection[1]
        window, _repo, selected_root = selection
        try:
            return jsonify(kpi.compute(selected_root, window))
        except Exception as error:
            return _unavailable(error)

    @app.get("/api/work")
    def work_items():
        selection = _selection_or_error(project_root)
        if isinstance(selection, tuple):
            return jsonify(selection[0]), selection[1]
        window, repo, _selected_root = selection
        try:
            config = artifact_accessors.load_harness_json(project_root / ".harness" / "harness.json")
            limits = attention.thresholds(config)
            items = _selected_items(work.collect(project_root), repo, window, kpi.resolve_window)
            ranked = attention.rank(items, datetime.now(timezone.utc), limits)
            return jsonify(_work_payload(ranked, limits, window, repo))
        except Exception as error:
            return _unavailable(error)

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


def _trusted_host(host: str) -> bool:
    value = host.lower()
    if value.startswith("[::1]"):
        suffix = value.removeprefix("[::1]")
        return suffix == "" or (suffix.startswith(":") and suffix[1:].isdigit())
    name, separator, port = value.partition(":")
    return name in {"localhost", "127.0.0.1"} and (separator == "" or port.isdigit())


def _window_or_error():
    from flask import request
    window = request.args.get("window", "all")
    if window not in {"30d", "90d", "all"}:
        return {"error": "window must be one of 30d, 90d, all"}, 400
    return window


def _asset_mimetype(asset_path: str) -> str | None:
    suffix = Path(asset_path).suffix.lower()
    return MIME_FALLBACKS.get(suffix) or mimetypes.guess_type(asset_path)[0]


def _selection_or_error(root: Path, require_all: bool = True):
    from flask import request
    try:
        window = _window_or_error()
        if isinstance(window, tuple):
            return window
        repo = request.args.get("repo", "all")
        repositories = _repository_roots(root, require_all=require_all or repo != "all")
        if repo not in ("all", *repositories):
            return {"error": f"repo must be one of {', '.join(('all', *repositories))}"}, 400
        return [window, repo, root if repo == "all" else repositories[repo]]
    except Exception as error:
        return {"error": f"dashboard unavailable: {error}"}, 500


def _repository_roots(root: Path, require_all: bool = True) -> dict[str, Path]:
    import artifact_accessors
    fleet_path = root / ".harness" / "factory" / "fleet.yaml"
    repositories = {"harness": root}
    if not require_all or not fleet_path.is_file():
        return repositories
    fleet = artifact_accessors.load_fleet(fleet_path)
    for entry in fleet["repos"]:
        name = entry["name"].rsplit("/", 1)[-1]
        path = Path(fleet["workspace_root"]) / name
        if name in repositories or not path.is_dir():
            raise ValueError(f"configured repository {name} cannot be enumerated at {path}")
        repositories[name] = path
    return repositories


def _selected_items(items, repo: str, window: str, resolve_window):
    start, end = resolve_window(window, datetime.now(timezone.utc))
    selected = [item for item in items if repo == "all" or item.segment == repo]
    if window == "all":
        return selected
    return [item for item in selected if _in_window(_item_updated_at(item), start, end)]


def _in_window(updated, start, end):
    return updated is None or (updated <= end and (start is None or updated >= start))

def _item_updated_at(item):
    try:
        return datetime.fromtimestamp(Path(item.source_path).stat().st_mtime, timezone.utc)
    except OSError:
        return None


def _work_payload(ranked, limits, window: str, repo: str) -> dict:
    items = [_serialize_work_item(item, attention) for item, attention in ranked]
    return {
        "schema": "harness-work/1",
        "window": window,
        "repo": repo,
        "attention_order": ["needs-you", "blocked", "stalled", "over-budget", "running", "stale"],
        "effective_thresholds": {
            "stalled_minutes": limits.stalled_minutes,
            "stale_days": limits.stale_days,
            "over_budget_remaining_cycles": limits.over_budget_remaining_cycles,
        },
        "items": items,
        "errors": [{"source_path": item.source_path, "reason": item.error}
                   for item, _attention in ranked if item.error is not None],
    }


def _serialize_work_item(item, item_attention) -> dict:
    return {
        "id": item.id,
        "kind": item.kind,
        "attention": item_attention.state,
        "attention_reasons": list(item_attention.reasons),
        "name": item.display_name,
        "repository": item.repository or item.segment,
        "segment": item.segment,
        "station": item.station,
        "phase": item.phase,
        "run_status": item.run_status,
        "updated_at": _updated_at(item),
        "elapsed_total": item.elapsed_total,
        "elapsed_by_phase": {
            "plan": item.elapsed_plan,
            "build": item.elapsed_build,
            "validate": item.elapsed_validate,
        },
        "runs": item.run_count,
        "cycles_used": item.cycles_used,
        "max_total_cycles": item.max_total_cycles,
        "tokens": _tokens(item.tokens),
        "main_path": item.main_path,
        "worktree_path": item.worktree_path,
        "source_path": item.source_path,
        "detail": _detail(item),
    }


def _updated_at(item):
    updated = _item_updated_at(item)
    return updated.isoformat().replace("+00:00", "Z") if updated is not None else item.updated_at


def _tokens(tokens):
    if tokens is None:
        return None
    return {
        "measured_total": tokens.get("total"),
        "measured_runs": tokens.get("measured_runs"),
        "total_runs": tokens.get("total_runs"),
        "unmeasured_runs": tokens.get("unmeasured_runs"),
        "by_phase": tokens.get("by_phase"),
    }


def _detail(item):
    if item.kind == "worktree":
        return {
            "canonical_path": item.canonical_path,
            "checkout_role": item.checkout_role,
            "head": item.head,
            "feature_id": item.feature_id,
            "feature_status": item.feature_status,
        }
    if item.kind == "grilling":
        return {"status": item.grilling_status}
    return {"run_started_at": item.run_started_at, "run_ended_at": item.run_ended_at}


def _unavailable(error):
    from flask import jsonify
    return jsonify(error=f"dashboard unavailable: {error}"), 500
 


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
