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

METRICS_CASES = (
    "shipped elapsed phases", "in-progress elapsed phases", "missing boundaries stay null",
    "all measured tokens", "none measured tokens", "mixed token coverage presentation",
    "no dollar cost",
)

WORKTREE_CASES = (
    "worktrees include every canonical path exactly once",
    "worktrees retain primary linked detached orphan terminal and error rows",
    "only linked worktrees override feature copies",
    "worktrees use terminal classification and repository identity",
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
    notes = root / ".harness" / "notes"; notes.mkdir(); (notes / "grilling-dashboard-2026-09-16.md").write_text("---\nstatus: open\nbecame: null\n---\n# Grilling\n")
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
        rows = {row.display_name: row for row in work.collect(root) if row.kind != "worktree"}
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


# ---- metrics (T-31, DEC-229) ---------------------------------------------------------------
def metric_feature(main, name, station, runs, handoffs=()):
    path = main / name
    write_feature(path, name, station, runs)
    (path / "BRIEF.md").write_text("## Approval\nstatus: approved\ndate: 2026-09-10\n",
                                  encoding="utf-8")
    notes = path / "notes"; notes.mkdir()
    for phase, seq in handoffs:
        (notes / f"handoff-{phase}.md").write_text(
            f"# Handoff — {name}, {phase} → next — written at sha, seq-{seq}\n",
            encoding="utf-8")


def metrics_case():
    from datetime import datetime, timezone
    work = importlib.import_module("dashboard.work")
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    runs = [
        {"id": "p", "squad": "product", "started_at": "2026-09-10T01:00:00Z",
         "ended_at": "2026-09-10T02:00:00Z", "tokens": 3},
        {"id": "b", "squad": "eng", "started_at": "2026-09-11T02:00:00Z",
         "ended_at": "2026-09-11T05:00:00Z", "tokens": 7},
        {"id": "v", "squad": "validator", "started_at": "2026-09-12T05:00:00Z",
         "ended_at": "2026-09-12T07:00:00Z", "tokens": 11},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "control"; main = root / ".harness" / "harness" / "features"
        (root / ".harness" / "factory").mkdir(parents=True)
        (root / ".harness" / "factory" / "fleet.yaml").write_text(
            "schema: factory-fleet/1\nworkspace_root: /nonexistent\nrepos: []\n", encoding="utf-8")
        metric_feature(main, "FEAT-80-shipped", "done", runs, (("plan", 1), ("build", 2), ("validate", 3)))
        metric_feature(main, "BUG-81-progress", "review", runs[:2], (("plan", 1), ("build", 2)))
        metric_feature(main, "FEAT-82-missing", "building", runs[:1])
        metric_feature(main, "FEAT-83-none", "building", [{**runs[0], "tokens": None}])
        metric_feature(main, "FEAT-84-mixed", "building", [{**runs[0], "tokens": 5}, {**runs[1], "tokens": None}], (("plan", 1),))
        original_now = work._now
        work._now = lambda: now
        try:
            rows = {row.display_name: row for row in work.collect(root)}
        finally:
            work._now = original_now
        shipped, progress, missing, measured, none, mixed = (rows[name] for name in (
            "FEAT-80-shipped", "BUG-81-progress", "FEAT-82-missing", "FEAT-80-shipped",
            "FEAT-83-none", "FEAT-84-mixed"))
        check("shipped elapsed phases", matches(shipped, phase="done", elapsed_total=198000,
              elapsed_plan=7200, elapsed_build=97200, elapsed_validate=93600), repr(shipped))
        check("in-progress elapsed phases", matches(progress, phase="validate", elapsed_total=388800,
              elapsed_plan=7200, elapsed_build=97200, elapsed_validate=284400), repr(progress))
        check("missing boundaries stay null", missing.phase == "plan" and missing.elapsed_plan == 388800
              and missing.elapsed_build is None and missing.elapsed_validate is None, repr(missing))
        check("all measured tokens", measured.tokens == {"total": 21, "measured_runs": 3,
              "total_runs": 3, "unmeasured_runs": 0, "by_phase": {"plan": 3, "build": 7, "validate": 11},
              "presentation": "unmeasured 0 of 3 runs"}, repr(measured.tokens))
        check("none measured tokens", none.tokens == {"total": None, "measured_runs": 0,
              "total_runs": 1, "unmeasured_runs": 1, "by_phase": {"plan": None, "build": None, "validate": None},
              "presentation": "unmeasured 1 of 1 runs"}, repr(none.tokens))
        check("mixed token coverage presentation", mixed.tokens["presentation"] == "unmeasured 1 of 2 runs")
        check("no dollar cost", "cost" not in shipped.to_dict() and "cost" not in shipped.tokens)

# ---- worktrees (T-26, DEC-229) -------------------------------------------------------------
def worktree_case():
    work = importlib.import_module("dashboard.work")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "control"
        _main, _bad, worktrees = setup(root)
        rows, paths = _collect_worktree_rows(work, root, worktrees)
        _assert_worktree_paths(rows, paths)
        _assert_worktree_kinds(rows, worktrees)
        _assert_worktree_precedence(rows, worktrees)
        _assert_worktree_identity(rows, worktrees)


def _collect_worktree_rows(work, root, worktrees):
    workspace = root / "workspace" / "widget"
    workspace.mkdir(parents=True)
    orphan = root / ".claude" / "worktrees" / "harness" / "FEAT-61-orphan"
    orphan.mkdir(parents=True)
    paths = [root, *worktrees, orphan, workspace]
    original_paths = work.worktree_terminal._worktree_paths
    original_classify = work.worktree_terminal.classify_all
    work.worktree_terminal._worktree_paths = _worktree_paths(root, worktrees, orphan, workspace)
    work.worktree_terminal.classify_all = _worktree_classifications(worktrees, orphan)
    try:
        return work.collect(root), paths
    finally:
        work.worktree_terminal._worktree_paths = original_paths
        work.worktree_terminal.classify_all = original_classify


def _worktree_paths(root, worktrees, orphan, workspace):
    def paths(path):
        return ([str(root), *map(str, worktrees), str(orphan)]
                if Path(path).resolve() == root.resolve() else [str(workspace)])
    return paths


def _worktree_classifications(worktrees, orphan):
    return lambda path: [
        {"path": str(worktrees[2]), "feature_id": "FEAT-73-divergent",
         "klass": "terminal", "repo": "harness", "reason": "landed"},
        {"path": str(orphan), "feature_id": None, "klass": "exempt_absent",
         "repo": "harness", "reason": "absent"},
    ]


def _worktree_only(rows):
    return [row for row in rows if row.kind == "worktree"]


def _assert_worktree_paths(rows, paths):
    row_paths = [row.canonical_path for row in _worktree_only(rows)]
    check("worktrees include every canonical path exactly once",
          sorted(row_paths) == sorted(str(path.resolve()) for path in paths)
          and len(row_paths) == len(set(row_paths)))


def _assert_worktree_kinds(rows, worktrees):
    primary, linked, orphan, terminal = _worktree_kind_rows(rows, worktrees)
    check("worktrees retain primary linked detached orphan terminal and error rows",
          _assert_primary_and_linked(primary, linked) and _assert_orphan_and_terminal(orphan, terminal))


def _worktree_kind_rows(rows, worktrees):
    worktree_rows = _worktree_only(rows)
    by_path = {row.canonical_path: row for row in worktree_rows}
    return (next(row for row in worktree_rows if row.checkout_role == "primary"),
            by_path[str(worktrees[0].resolve())],
            next(row for row in worktree_rows if row.feature_status == "absent"),
            by_path[str(worktrees[2].resolve())])


def _assert_primary_and_linked(primary, linked):
    return (primary.checkout_role == "primary" and linked.checkout_role == "linked"
            and linked.feature_id == "FEAT-71-long-id" and linked.feature_status == "active")


def _assert_orphan_and_terminal(orphan, terminal):
    return orphan.feature_status == "absent" and terminal.feature_status == "terminal"


def _assert_worktree_precedence(rows, worktrees):
    feature = next(row for row in rows if row.display_name == "FEAT-71-long-id")
    primary = next(row for row in _worktree_only(rows) if row.checkout_role == "primary")
    check("only linked worktrees override feature copies",
          feature.worktree_path == str(worktrees[0].resolve()) and primary.feature_id is None)


def _assert_worktree_identity(rows, worktrees):
    terminal = next(row for row in _worktree_only(rows)
                    if row.canonical_path == str(worktrees[2].resolve()))
    check("worktrees use terminal classification and repository identity",
          terminal.repository == "harness" and terminal.feature_id == "FEAT-73-divergent")


# ---- attention (T-24, D-25) ---------------------------------------------------------------
ATTENTION_CASES = (
    "needs-you awaiting_user", "needs-you open questions", "needs-you pending approval",
    "blocked run", "stalled after threshold", "running before threshold", "over-budget after stalled",
    "stale after seven days", "terminal has no attention", "open grilling is needs-you",
    "source error has no attention", "precedence and tie order", "thresholds reject bool",
    "thresholds reject zero", "thresholds reject missing block",
    "stalled at exactly 45 minutes", "running at 44m59s", "stale at exactly seven days",
    "fresh at seven days minus one second", "precedence follows ORDER under mutation",
    "tie order is oldest write then id",
)
MINUTE = 60
DAY = 24 * 60 * MINUTE


def touch(path, seconds_ago, now):
    import os
    stamp = now.timestamp() - seconds_ago
    os.utime(path, (stamp, stamp))


def attention_feature(main, name, station="building", run_status=None, cycles=(2, 7), questions=0,
                      approval="approved", age_seconds=MINUTE, now=None):
    d = main / name
    runs = [{"id": "r1", "squad": "eng", "verdict": "PASS"}] if run_status else []
    d.mkdir(parents=True, exist_ok=True)
    (d / "feature.json").write_text(json.dumps({"feature_id": name, "cycles_used": cycles[0],
        "max_total_cycles": cycles[1], "runs": runs}), encoding="utf-8")
    (d / "plan.yaml").write_text(f"schema: plan/1\nfeature: {name}\napproval:\n  status: {approval}\nstatus: {station}\ntasks: []\n", encoding="utf-8")
    q = "".join(f"- question {i}\n" for i in range(questions)) or "- None\n"
    (d / "STATE.md").write_text(f"# STATE\n\n## Current\n\n- status: x\n\n## Open Questions\n\n{q}", encoding="utf-8")
    if run_status:
        (d / "runs" / "r1").mkdir(parents=True)
        (d / "runs" / "r1" / "state.yaml").write_text(f"schema_version: 2\nrun_id: r1\nstatus: {run_status}\n", encoding="utf-8")
    for f in (d / "feature.json", d / "plan.yaml", d / "STATE.md", *([d / "runs" / "r1" / "state.yaml"] if run_status else [])):
        touch(f, age_seconds, now)
    return d


def _attention_fixture(root, now):
    """One feature per state, the two exact boundaries on each side, a broken one, an open note."""
    main = root / ".harness" / "harness" / "features"
    (root / ".harness" / "factory").mkdir(parents=True)
    (root / ".harness" / "factory" / "fleet.yaml").write_text("schema: factory-fleet/1\nworkspace_root: /nonexistent\nrepos: []\n", encoding="utf-8")
    attention_feature(main, "FEAT-01-await", run_status="awaiting_user", now=now)
    attention_feature(main, "FEAT-02-questions", questions=2, now=now)
    attention_feature(main, "FEAT-03-pending", approval="pending", now=now)
    attention_feature(main, "FEAT-04-blocked", run_status="blocked", now=now)
    attention_feature(main, "FEAT-05-stalled", run_status="running", age_seconds=46 * MINUTE, now=now)
    attention_feature(main, "FEAT-06-running", run_status="running", age_seconds=44 * MINUTE, now=now)
    attention_feature(main, "FEAT-07-budget", run_status="running", cycles=(6, 7), age_seconds=46 * MINUTE, now=now)
    attention_feature(main, "FEAT-08-stale", station="ready", age_seconds=7 * DAY + MINUTE, now=now)
    attention_feature(main, "FEAT-09-done", station="done", age_seconds=30 * DAY, now=now)
    attention_feature(main, "FEAT-10-fresh", station="ready", age_seconds=60 * MINUTE, now=now)
    attention_feature(main, "FEAT-12-overbudget", run_status="running", cycles=(6, 7), age_seconds=5 * MINUTE, now=now)
    attention_feature(main, "FEAT-13-stall-edge", run_status="running", age_seconds=45 * MINUTE, now=now)
    attention_feature(main, "FEAT-14-run-edge", run_status="running", age_seconds=45 * MINUTE - 1, now=now)
    attention_feature(main, "FEAT-15-stale-edge", station="ready", age_seconds=7 * DAY, now=now)
    attention_feature(main, "FEAT-16-fresh-edge", station="ready", age_seconds=7 * DAY - 1, now=now)
    bad = main / "FEAT-11-broken"; bad.mkdir(parents=True); (bad / "feature.json").write_text("{broken")
    notes = root / ".harness" / "notes"; notes.mkdir(); (notes / "grilling-x-2026-09-16.md").write_text("---\nstatus: open\nbecame: null\n---\n# Grilling\n")


def _assert_needs_you(a):
    check("needs-you awaiting_user", a["FEAT-01-await"].state == "needs-you" and any("awaiting" in r for r in a["FEAT-01-await"].reasons))
    check("needs-you open questions", a["FEAT-02-questions"].state == "needs-you" and any("2 open question" in r for r in a["FEAT-02-questions"].reasons))
    check("needs-you pending approval", a["FEAT-03-pending"].state == "needs-you")
    check("open grilling is needs-you", a["grilling-x-2026-09-16"].state == "needs-you")


def _assert_states(a):
    _assert_needs_you(a)
    check("blocked run", a["FEAT-04-blocked"].state == "blocked")
    check("stalled after threshold", a["FEAT-05-stalled"].state == "stalled")
    check("running before threshold", a["FEAT-06-running"].state == "running")
    check("over-budget after stalled", a["FEAT-07-budget"].state == "stalled" and "cycles 6/7" in a["FEAT-07-budget"].reasons and a["FEAT-12-overbudget"].state == "over-budget")
    check("stale after seven days", a["FEAT-08-stale"].state == "stale" and a["FEAT-10-fresh"].state is None)
    check("terminal has no attention", a["FEAT-09-done"].state is None and a["FEAT-09-done"].reasons == ())
    check("source error has no attention", a["FEAT-11-broken"].state is None and a["FEAT-11-broken"].reasons and "source error" in a["FEAT-11-broken"].reasons[0])


def _assert_boundaries(a):
    """V-20: the thresholds are inclusive at exactly 45 minutes and exactly seven days."""
    check("stalled at exactly 45 minutes", a["FEAT-13-stall-edge"].state == "stalled")
    check("running at 44m59s", a["FEAT-14-run-edge"].state == "running")
    check("stale at exactly seven days", a["FEAT-15-stale-edge"].state == "stale")
    check("fresh at seven days minus one second", a["FEAT-16-fresh-edge"].state is None)


def _assert_ranking(att, rows, now, limits):
    ranked = [item.display_name for item, _ in att.rank(rows.values(), now, limits)]
    expected_head = ["FEAT-01-await", "FEAT-02-questions", "FEAT-03-pending", "grilling-x-2026-09-16", "FEAT-04-blocked",
                     "FEAT-05-stalled", "FEAT-07-budget", "FEAT-13-stall-edge", "FEAT-12-overbudget",
                     "FEAT-14-run-edge", "FEAT-06-running", "FEAT-08-stale", "FEAT-15-stale-edge"]
    check("precedence and tie order", ranked[:len(expected_head)] == expected_head, str(ranked))
    stalled = [n for n in ranked if n in ("FEAT-05-stalled", "FEAT-07-budget", "FEAT-13-stall-edge")]
    check("tie order is oldest write then id", stalled == ["FEAT-05-stalled", "FEAT-07-budget", "FEAT-13-stall-edge"], str(stalled))
    original = att.ORDER
    att.ORDER = tuple(reversed(original))
    try:
        mutated = [item.display_name for item, _ in att.rank(rows.values(), now, limits)]
    finally:
        att.ORDER = original
    states_in_order = [att.derive(rows[n], now, limits).state for n in mutated if att.derive(rows[n], now, limits).state]
    check("precedence follows ORDER under mutation", states_in_order == sorted(states_in_order, key=lambda s: tuple(reversed(original)).index(s)) and mutated[0] == "FEAT-08-stale", str(mutated[:4]))


def _assert_thresholds(att):
    for name, block in (("thresholds reject bool", {"stalled_minutes": True, "stale_days": 7, "over_budget_remaining_cycles": 1}),
                        ("thresholds reject zero", {"stalled_minutes": 45, "stale_days": 0, "over_budget_remaining_cycles": 1})):
        try: att.thresholds({"dashboard": block}); check(name, False)
        except ValueError: check(name, True)
    try: att.thresholds({}); check("thresholds reject missing block", False)
    except ValueError: check("thresholds reject missing block", True)


def attention_case():
    from datetime import datetime, timezone
    try:
        work = importlib.import_module("dashboard.work"); att = importlib.import_module("dashboard.attention")
    except Exception as error:
        for name in ATTENTION_CASES: check(name, False, f"import failed: {error}")
        return
    now = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)
    limits = att.thresholds({"dashboard": {"stalled_minutes": 45, "stale_days": 7, "over_budget_remaining_cycles": 1}})
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "control"
        _attention_fixture(root, now)
        rows, _ = collect_rows(work, root, [])
        a = {name: att.derive(item, now, limits) for name, item in rows.items()}
        _assert_states(a)
        _assert_boundaries(a)
        _assert_ranking(att, rows, now, limits)
    _assert_thresholds(att)


def main():
    cases = {"collector": (collector_case, len(CASE_NAMES)),
             "metrics": (metrics_case, len(METRICS_CASES)),
             "attention": (attention_case, len(ATTENTION_CASES)),
             "worktrees": (worktree_case, len(WORKTREE_CASES))}
    if len(sys.argv) == 1:
        selected = cases.items()
    elif len(sys.argv) == 3 and sys.argv[1] == "--case" and sys.argv[2] in cases:
        selected = [(sys.argv[2], cases[sys.argv[2]])]
    else:
        raise SystemExit("usage: test-work-dashboard.py [--case collector|metrics|attention|worktrees]")
    total = 0
    for name, (fn, count) in selected:
        fn()
        total += count
        print(f"Executed {count} {name} assertions; discovered {count} {name} assertions.")
    print(f"Executed {total} assertions; discovered {total} assertions.")
    raise SystemExit(bool(FAILURES))


if __name__ == "__main__": main()
