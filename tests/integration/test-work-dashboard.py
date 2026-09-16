#!/usr/bin/env python3
"""Offline integration fixtures for the dashboard disk collector (T-23)."""
import importlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "harness" / "bin"))
FAILURES = []
CASE_NAMES = (
    "short id matching", "long id matching", "divergent main and worktree copies",
    "worktree-only state", "malformed input", "unreadable worktree falls back to main",
    "malformed worktree plan is source-specific", "multiple segments", "no GitHub dependency",
)


def check(name, condition, detail=""):
    print(f"{'PASS ' if condition else 'FAIL '} {name}{' — ' + detail if detail else ''}")
    if not condition:
        FAILURES.append(name)


def write_feature(path, name, station="building", runs=None):
    path.mkdir(parents=True, exist_ok=True)
    (path / "feature.json").write_text(json.dumps({"feature_id": name, "cycles_used": 2,
        "max_total_cycles": 7, "runs": [] if runs is None else runs}), encoding="utf-8")
    (path / "plan.yaml").write_text(f"schema: plan/1\nfeature: {name}\nstatus: {station}\ntasks: []\n",
                                     encoding="utf-8")


def setup(root):
    (root / ".harness" / "factory").mkdir(parents=True)
    (root / ".harness" / "factory" / "fleet.yaml").write_text(
        f"schema: factory-fleet/1\nworkspace_root: {root / 'workspace'}\nrepos:\n  - name: acme/widget\n    default_branch: main\n", encoding="utf-8")
    main = root / ".harness" / "harness" / "features"
    write_feature(main / "FEAT-71-long-id", "FEAT-71-long-id", "ready")
    write_feature(main / "BUG-72-regression", "BUG-72-regression", "review")
    write_feature(main / "FEAT-73-divergent", "FEAT-73-divergent", "building", [{"verdict": "FAIL"}])
    write_feature(main / "FEAT-74-worktree-state", "FEAT-74-worktree-state", "ready")
    bad = main / "FEAT-75-malformed"; bad.mkdir(parents=True); (bad / "feature.json").write_text("{broken")
    write_feature(main / "FEAT-77-main-fallback", "FEAT-77-main-fallback", "ready",
                  [{"verdict": "MAIN"}])
    write_feature(main / "FEAT-78-malformed-worktree", "FEAT-78-malformed-worktree", "main",
                  [{"verdict": "MAIN"}])
    write_feature(root / ".harness" / "widget" / "features" / "FEAT-76-widget", "FEAT-76-widget", "plan")
    notes = root / ".harness" / "notes"; notes.mkdir(); (notes / "grilling-dashboard-2026-09-16.md").write_text("# Grilling\n\n## Status\nopen\n")
    worktrees = []
    for label, name, station, runs in (("FEAT-71", "FEAT-71-long-id", "building", []), ("BUG-72-regression", "BUG-72-regression", "building", []), ("FEAT-73-divergent", "FEAT-73-divergent", "done", [{"verdict": "PASS"}]), ("FEAT-74", "FEAT-74-worktree-state", "review", [{"verdict": "PENDING"}]), ("FEAT-77", "FEAT-77-main-fallback", "ignored", []), ("FEAT-78", "FEAT-78-malformed-worktree", "worktree", [{"verdict": "WORKTREE"}])):
        worktree = root / ".claude" / "worktrees" / "harness" / label
        if name != "FEAT-77-main-fallback":
            write_feature(worktree / ".harness" / "harness" / "features" / name, name, station, runs)
        if name == "FEAT-78-malformed-worktree":
            (worktree / ".harness" / "harness" / "features" / name / "plan.yaml").write_text(
                "{broken", encoding="utf-8")
        worktrees.append(worktree)
    return main, bad, worktrees


def collect_rows(work, root, worktrees):
    original_paths = work.worktree_terminal._worktree_paths
    original_gh = work.factory_config.factory_gh.file_at_ref
    github_calls = []
    def forbidden(*args, **kwargs):
        github_calls.append((args, kwargs)); raise AssertionError("collector reached GitHub")
    work.worktree_terminal._worktree_paths = lambda path: [str(root), *map(str, worktrees)] if Path(path).resolve() == root.resolve() else []
    work.factory_config.factory_gh.file_at_ref = forbidden
    try:
        rows = {row.display_name: row for row in work.collect(root)}
    finally:
        work.worktree_terminal._worktree_paths = original_paths
        work.factory_config.factory_gh.file_at_ref = original_gh
    return rows, github_calls


def matches(item, **fields):
    return all(getattr(item, name) == value for name, value in fields.items())


def has_error(item, required, forbidden=None):
    return item.error and required in item.error and (forbidden is None or forbidden not in item.error)


def assert_copy_cases(rows, bad, worktrees):
    check("short id matching", matches(rows["FEAT-71-long-id"], worktree_path=str(worktrees[0].resolve())))
    check("long id matching", matches(rows["BUG-72-regression"], worktree_path=str(worktrees[1].resolve())))
    check("divergent main and worktree copies", matches(rows["FEAT-73-divergent"], station="done", run_status="PASS") and rows["FEAT-73-divergent"].source_path.startswith(str(worktrees[2].resolve())))
    check("worktree-only state", matches(rows["FEAT-74-worktree-state"], station="review", run_status="PENDING"))
    check("malformed input", has_error(rows["FEAT-75-malformed"], "feature.json") and rows["FEAT-75-malformed"].source_path == str(bad.resolve()))


def assert_regression_cases(rows, main, worktrees):
    fallback_path = str((main / "FEAT-77-main-fallback").resolve())
    check("unreadable worktree falls back to main", matches(rows["FEAT-77-main-fallback"], station="ready", run_status="MAIN", main_path=fallback_path, worktree_path=str(worktrees[4].resolve()), source_path=fallback_path))
    malformed_path = worktrees[5] / ".harness" / "harness" / "features" / "FEAT-78-malformed-worktree"
    check("malformed worktree plan is source-specific", has_error(rows["FEAT-78-malformed-worktree"], "plan.yaml", "feature.json") and matches(rows["FEAT-78-malformed-worktree"], main_path=str((main / "FEAT-78-malformed-worktree").resolve()), worktree_path=str(worktrees[5].resolve()), source_path=str(malformed_path.resolve()), station=None, run_status=None, cycles_used=None))


def assert_environment_cases(rows, calls):
    check("multiple segments", matches(rows["FEAT-76-widget"], segment="widget") and rows["grilling-dashboard-2026-09-16"].kind == "grilling")
    check("no GitHub dependency", not calls and len(rows) == 9)


def assert_cases(rows, calls, main, bad, worktrees):
    assert_copy_cases(rows, bad, worktrees)
    assert_regression_cases(rows, main, worktrees)
    assert_environment_cases(rows, calls)


def collector_case():
    try:
        work = importlib.import_module("dashboard.work")
    except Exception as error:
        for name in CASE_NAMES: check(name, False, f"collector import failed: {error}")
        return
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "control"
        main, bad, worktrees = setup(root)
        rows, calls = collect_rows(work, root, worktrees)
        assert_cases(rows, calls, main, bad, worktrees)


def main():
    if sys.argv[1:] != ["--case", "collector"]: raise SystemExit("usage: test-work-dashboard.py --case collector")
    collector_case()
    print("Executed 9 collector assertions; discovered 9 collector assertions.")
    raise SystemExit(bool(FAILURES))


if __name__ == "__main__": main()
