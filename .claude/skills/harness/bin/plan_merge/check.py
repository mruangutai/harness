"""`check`: every anchor and trace in a plan resolved at plan exit (DEC-232). (FEAT-70)"""
import os
import re
import sys

import harness_boundary
import harness_yaml
import plan_anchors
from plan_merge.guards import BIN_DIR, _die, _resolve_plan
import worktree_terminal

# A SERVED REPOSITORY'S PLAN HAS TWO ROOTS (#2064). Its plan lives in the harness PLANNING
# worktree under `.harness/<segment>/features/<id>/`, but the code it names lives in the paired
# CODE worktree (#2058). Anchors resolve against the code worktree; routes are still answered by
# the harness manifest under --root, asked about the ABSOLUTE product path so check-domain
# selects the fleet's product base exactly as the build hook will. Resolving product paths
# against the harness tree was the defect: false passes for paths both trees share
# (docs/…, .harness/…) and NOBODY for every product source path.
HARNESS_SEGMENT = "harness"

# ---------------------------------------------------------------------------
# `check` — resolve every anchor, route and trace before a plan is signed (FEAT-59 SC-07).
#
# FEAT-54's first build dispatch BLOCKED on five plan paths that four goal-check cycles and
# three panel cycles had read and none had resolved: "the first build dispatch found it in one
# member spawn". Readers were asked to find by reading what a script can find by running. This
# verb is that script. It WRITES NOTHING; exit 0 means every `files:` anchor resolves under
# --root, every team task's `execution_agent` is granted its files by the SAME resolver the
# build hook consults (check-plan-routes.resolve_agents -> check-domain.py --resolve), and
# every `traces:` id is present in the sibling BRIEF.md. Exit 1 lists each failure on its own
# FAIL line; exit 2 means the check could not run at all (no manifest under --root).


def _check_plan_routes_module():
    """check-plan-routes.py as a module: the hyphen keeps it out of `import`, and its resolver
    is the ONE route resolver (DEC-179) — re-implementing it here would be a second copy of the
    rule check-domain.py applies at build time, which is the drift SC-07 exists to close."""
    return harness_boundary.load_repo_module(
        "check_plan_routes", os.path.join(BIN_DIR, "check-plan-routes.py"))


def _trace_in_brief(trace, brief_text):
    return re.search(rf"(?<![\w-]){re.escape(str(trace))}(?![\w-])", brief_text) is not None


class _Routes:
    """The route resolver bound to one --root, answering once per path.

    check-domain.py is a subprocess per question, so the answer for a path is cached across
    the tasks that name it. Which checkout answers is check-plan-routes' choice, not ours: it
    runs the check-domain that lives under the resolution manifest's own root, so a worktree
    is answered by its owner (the DEVIATION rule), and no environment is set here — the
    retired env chain is refused by test-no-distribution case 6."""

    def __init__(self, root, code_root):
        self.root = root
        self.code_root = code_root
        self.cpr = _check_plan_routes_module()
        try:
            self.manifest_root, self.deviation = self.cpr.resolution_manifest(root)
        except ValueError as exc:
            _die(2, f"plan-merge: {exc}")
        self._granted = {}

    def granted(self, path):
        if path not in self._granted:
            asked = os.path.join(self.code_root, path) if self.code_root else path
            self._granted[path] = self.cpr.resolve_agents(asked, self.root, self.manifest_root)
        return self._granted[path]


def _literal_paths(task):
    """The bare, non-glob path of every files: entry — what the route question is about."""
    paths = (plan_anchors.path_of(entry) for entry in task.get("files") or [])
    return [p for p in paths if isinstance(p, str) and not plan_anchors.is_glob(p)]


def _route_faults(task, tid, routes):
    """FAIL lines for a team task whose execution_agent is not granted every literal path."""
    if task.get("execution_mode") != "team":
        return []
    agent = task.get("execution_agent")
    if not isinstance(agent, str) or not agent.strip():
        return [f"FAIL {tid} execution_agent: missing, and execution_mode is team — the lane "
                "row is the authority, so name the agent it grants"]
    return [f"FAIL {tid} execution_agent: {agent} is not granted {path} "
            f"(granted: {', '.join(routes.granted(path)) or 'NOBODY'})"
            for path in _literal_paths(task) if agent not in routes.granted(path)]


def _trace_faults(task, tid, brief_text):
    if brief_text is None:
        return []
    return [f"FAIL {tid} traces: {trace} is not in the sibling BRIEF.md"
            for trace in task.get("traces") or [] if not _trace_in_brief(trace, brief_text)]


def _check_task(task, root, brief_text, routes):
    """(failures, anchors_resolved) for one task."""
    tid = str(task.get("id") or "<no id>")
    faults = [plan_anchors.resolve(entry, root) for entry in task.get("files") or []]
    failures = [f"FAIL {tid} files: {fault}" for fault in faults if fault is not None]
    failures += _route_faults(task, tid, routes)
    failures += _trace_faults(task, tid, brief_text)
    return failures, faults.count(None)


def _check_tasks(doc, resolved_plan):
    tasks = doc.get("tasks") if isinstance(doc, dict) else None
    if not isinstance(tasks, list):
        _die(5, f"plan-merge: {resolved_plan} carries no tasks: list to check")
    return tasks


def _plan_segment(resolved_plan):
    """(segment, feature id) from `.harness/<segment>/features/<id>/plan.yaml`."""
    feature_dir = os.path.dirname(resolved_plan)
    segment_dir = os.path.dirname(os.path.dirname(feature_dir))
    return os.path.basename(segment_dir), os.path.basename(feature_dir)


def _code_root(args, root, resolved_plan):
    """The root anchors resolve against: --root for harness's own plan, the required
    --code-root for a served repository's — or the exit-2 refusal that says why not."""
    segment, feature = _plan_segment(resolved_plan)
    if segment == HARNESS_SEGMENT:
        if args.code_root is not None:
            _die(2, f"plan-merge: {resolved_plan} is harness's own plan, so its anchors resolve "
                    "under --root; --code-root is only for a served repository's plan.")
        return None
    if args.code_root is None:
        repo = worktree_terminal.repo_arg_for_segment(segment) or f"<owner>/{segment}"
        _die(2, f"plan-merge: {resolved_plan} is a {segment} plan, so its anchors resolve in "
                f"its code worktree — pass --code-root, the CODE line of: feature-worktree.py "
                f"path --repo {repo} --id {feature}")
    code_root = os.path.abspath(args.code_root)
    if not os.path.isdir(code_root):
        _die(2, f"plan-merge: --code-root {code_root} is not a directory — create the paired "
                "worktree with feature-worktree.py create first.")
    return code_root


def _check_inputs(args):
    """(resolved plan path, root, code root or None, tasks) — or the exit-2/exit-5 refusal."""
    resolved_plan = _resolve_plan(args.file)
    root = os.path.abspath(args.root)
    if not os.path.isfile(os.path.join(root, harness_boundary.MARKER)):
        _die(2, f"plan-merge: {root} carries no {harness_boundary.MARKER}, so no route can be "
                "resolved against it — --root must be a harness checkout.")
    code_root = _code_root(args, root, resolved_plan)
    try:
        doc = harness_yaml.load_file(resolved_plan)
    except harness_yaml.YamlParseError as exc:
        _die(5, f"plan-merge: {resolved_plan} does not load: {exc}")
    return resolved_plan, root, code_root, _check_tasks(doc, resolved_plan)


def _brief_text(resolved_plan):
    """(text or None, failure line or None) for the sibling BRIEF.md. Absent is a failure: the
    traces cannot be checked, and an uncheckable trace must not read as a resolved one."""
    brief = os.path.join(os.path.dirname(resolved_plan), "BRIEF.md")
    if not os.path.isfile(brief):
        return None, f"FAIL BRIEF.md: {brief} is absent, so no traces: id can be checked"
    with open(brief, encoding="utf-8") as fh:
        return fh.read(), None


def _check_all(tasks, root, brief_text, routes):
    """(failures, anchors resolved) across every task, printing an OK line per clean task."""
    failures, total = [], 0
    for task in tasks:
        if not isinstance(task, dict):
            failures.append(f"FAIL tasks: {task!r} is not a mapping")
            continue
        task_failures, count = _check_task(task, root, brief_text, routes)
        total += count
        failures += task_failures
        if not task_failures:
            print(f"OK {task.get('id')} {count} anchor(s) resolved")
    return failures, total


def _overlap_lines(tasks):
    """BUG-1725: one ADVISORY line per normalized path that two or more tasks name. Every
    anchor form reduces to its path, so `a.py#foo` in T-01 and `{path: a.py, quote}` in T-02
    are the same shared file. Advisory because a shared file is sometimes right (a fixture two
    tasks extend) — but a plan whose tasks are LAYERS over the same files gates each one against
    a tree the next one will move, and BUG-285-canonical-reader paid five of ten cycles for
    exactly that before anything said so."""
    owners = {}
    for task in tasks:
        if not isinstance(task, dict):
            continue
        tid = str(task.get("id") or "<no id>")
        for path in dict.fromkeys(_literal_paths(task)):
            owners.setdefault(path, []).append(tid)
    return [f"OVERLAP {path}: {', '.join(tids)}"
            for path, tids in sorted(owners.items()) if len(tids) > 1]


def cmd_check(args):
    resolved_plan, root, code_root, tasks = _check_inputs(args)
    routes = _Routes(root, code_root)
    anchor_root = code_root or root
    brief_text, brief_fault = _brief_text(resolved_plan)
    preface = [f"FAIL {routes.deviation}"] if routes.deviation else []
    preface += [brief_fault] if brief_fault else []
    task_failures, total = _check_all(tasks, anchor_root, brief_text, routes)
    failures = preface + task_failures
    for line in failures:
        print(line)
    for line in _overlap_lines(tasks):
        print(line)
    print(f"CHECK {resolved_plan} against {anchor_root}: {len(tasks)} task(s), {total} "
          f"anchor(s) resolved, {len(failures)} failure(s)")
    sys.exit(1 if failures else 0)
