"""`check`: every anchor and trace in a plan resolved at plan exit (DEC-232). (FEAT-70)"""
import datetime
import os
import re
import sys

import artifact_accessors
import factory_config
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

# ---------------------------------------------------------------------------
# `check` — resolve every anchor, route and trace before a plan is signed (FEAT-59 SC-07).
#
# FEAT-54's first build dispatch BLOCKED on five plan paths that four goal-check cycles and
# three panel cycles had read and none had resolved: "the first build dispatch found it in one
# member spawn". Readers were asked to find by reading what a script can find by running. This
# verb is that script. It WRITES NOTHING; exit 0 means every `files:` anchor resolves under
# --root, every team task's `execution_agent` is granted its files by the SAME resolver the
# build hook consults (check-plan-routes.resolve_agents -> check-domain.py --resolve), and
# every `traces:` id is present in the sibling BRIEF.md, and CI's per-plan rule set
# (check-plan-routes.process_plan_yaml: budget, stations, routing) reports no VIOLATION
# (#2239). Exit 1 lists each failure on its own FAIL line; exit 2 means the check could not run
# at all (no manifest under --root); exit 5 means the plan does not load or validate.


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


def _code_root(args, root, resolved_plan):
    """The root anchors resolve against: --root for harness's own plan, the required
    --code-root for a served repository's — or the exit-2 refusal that says why not."""
    segment = harness_boundary.plan_segment(resolved_plan)
    feature = os.path.basename(os.path.dirname(resolved_plan))
    if segment == harness_boundary.HARNESS_SEGMENT:
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
    """(resolved plan path, root, code root or None, plan doc, tasks) — or the exit-2/exit-5
    refusal."""
    resolved_plan = _resolve_plan(args.file, recover=False)
    root = os.path.abspath(args.root)
    if not os.path.isfile(os.path.join(root, harness_boundary.MARKER)):
        _die(2, f"plan-merge: {root} carries no {harness_boundary.MARKER}, so no route can be "
                "resolved against it — --root must be a harness checkout.")
    code_root = _code_root(args, root, resolved_plan)
    try:
        doc = harness_yaml.load_file(resolved_plan)
    except harness_yaml.YamlParseError as exc:
        _die(5, f"plan-merge: {resolved_plan} does not load: {exc}")
    return resolved_plan, root, code_root, doc, _check_tasks(doc, resolved_plan)


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


# ---------------------------------------------------------------------------
# FEAT-2229: decision dispositions on an eligible pending draft (SC-02, SC-03).
#
# A draft is ELIGIBLE when its approval is pending, its feature station is not terminal, it
# carries the writer's `drafted_at` stamp (union._seed_new_plan), and --root's harness.json
# configures `decision_dispositions_era_start` with the stamp at or after it — null meaning
# every stamped draft. A plan with no stamp is a pre-writer legacy plan, and a project with no
# era key has not adopted the rule; neither is newly refused. A malformed era or stamp is a
# FAIL, never an implicit exemption. Approved and terminal work is history: its quoted clause
# may legitimately be gone once the amendment it planned has landed.
#
# These are the MECHANICAL checks only: every row's dec indexed; keep/amend never on a STRUCK
# entry; the clause an exact substring of that decision's own section; an amend/strike
# successor resolvable; a task owning the segment's DECISIONS.md to carry an amend/strike.
# Whether the rows are COMPLETE, and whether a strike is justified, is the scope reader's.
ERA_KEY = "decision_dispositions_era_start"
# The established DECISIONS-INDEX.md row (structure_audit._decisions_index); a ruling that
# opens with STRUCK — in any case, `Struck under DEC-188` included — marks the entry struck.
INDEX_ROW_RE = re.compile(r"^- (DEC-\d+) @\S+ \[[^\]]*\] refs:[^:]*:: (.*)$")
# The ONE fence/heading scanner for locating a decision's section, per CommonMark (4.2, 4.5):
# fence lines and ATX headings take 0-3 spaces of indentation — 4 or more is an indented code
# line, content that neither opens, closes nor heads anything. A fence is a run of 3+ backticks
# or tildes plus an info string; a backtick opener's info string may not hold a backtick. A
# closer is the opener's character, at least as long, followed only by whitespace; an unclosed
# fence runs to the end of the file. A heading is 1-6 `#` then a space, tab or line end.
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]|$)")
# What may follow a DEC-NNN in its heading: line end, whitespace, `:`, `(`, an em/en dash, or a
# hyphen followed by a space — never an identifier continuation (a letter, digit, `_`, `.`, or
# a hyphen joined to more identifier).
DEC_ID_END = r"(?=$|\s|[:(\u2014\u2013]|-\s)"


def _instant(value):
    """A timezone-qualified datetime from an ISO-8601 string, or None."""
    if not isinstance(value, str):
        return None
    try:
        when = datetime.datetime.fromisoformat(value)
    except ValueError:
        return None
    return when if when.tzinfo is not None else None


def _era(root):
    """(era instant or None, FAIL line or None) from --root's own validated harness.json — the
    supplied root, never a discovered one. The schema defaults an absent era to null, meaning
    every draft is in era (FEAT-2297); a missing or invalid config is a FAIL line."""
    path = os.path.join(root, ".harness", "harness.json")
    try:
        value = artifact_accessors.load_harness_json(path)[ERA_KEY]
    except artifact_accessors.ArtifactAccessError as exc:
        return None, f"FAIL {ERA_KEY}: {exc}, so the era is unknown"
    when = _instant(value)
    if value is not None and when is None:
        return None, (f"FAIL {ERA_KEY}: {value!r} in {path} is not a timezone-qualified "
                      "ISO-8601 instant")
    return when, None


def _is_draft(doc):
    approval = doc.get("approval")
    return (isinstance(approval, dict) and approval.get("status") == "pending"
            and doc.get("status") not in factory_config.FINISHED_STATIONS)


def _eligibility(doc, root):
    """(eligible, FAIL lines) for the disposition requirement on this plan."""
    if not _is_draft(doc) or doc.get("drafted_at") is None:
        return False, []
    drafted = _instant(doc["drafted_at"])
    if drafted is None:
        return False, [f"FAIL drafted_at: {doc['drafted_at']!r} is not a timezone-qualified "
                       "ISO-8601 instant"]
    era, fault = _era(root)
    if fault is not None:
        return False, [fault]
    return era is None or drafted >= era, []


def _read_text(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _struck_by_dec(index_text):
    """{DEC-NNN: struck?} from DECISIONS-INDEX.md text."""
    rows = (INDEX_ROW_RE.match(line) for line in index_text.splitlines())
    return {m.group(1): m.group(2).lstrip().lower().startswith("struck") for m in rows if m}


def _heading_level(line, dec=None):
    """The `#` count of an ATX heading line (naming `dec` when given), else 0. A heading names
    `dec` only on the FULL identifier: `## DEC-10x`, `## DEC-10_a`, `## DEC-10-1` and
    `## DEC-10.5` are not DEC-10 (SEC-C4-01)."""
    m = HEADING_RE.match(line)
    if m is None or (dec is not None and re.match(
            rf" {{0,3}}#{{1,6}}[ \t]+{re.escape(dec)}{DEC_ID_END}", line) is None):
        return 0
    return len(m.group(1))


def _opener(run, info):
    """`run` when it opens a fence, else None: a backtick info string may not hold a backtick."""
    return None if run[0] == "`" and "`" in info else run


def _fence_after(line, fence):
    """The open fence's opening run after `line`, or None outside any fence. A run carrying an
    info string (```python inside an open ``` fence) is content and keeps the fence open."""
    m = FENCE_RE.match(line)
    if m is None:
        return fence
    run, info = m.group(1), m.group(2)
    if fence is None:
        return _opener(run, info)
    closes = run[0] == fence[0] and len(run) >= len(fence) and not info.strip()
    return None if closes else fence


def _real_headings(lines):
    """[(index, level)] for every heading line outside a fence, fences tracked from the top
    of the file — a fenced `## DEC-NN` example is never a heading."""
    headings, fence = [], None
    for at, line in enumerate(lines):
        if fence is None and _heading_level(line):
            headings.append((at, _heading_level(line)))
        fence = _fence_after(line, fence)
    return headings


class _Authority:
    """One segment's decision record: `.harness/<segment>/docs/DECISIONS.md` and its index
    under --root — harness's own, or a served segment's central documents, never another's."""

    def __init__(self, root, segment):
        self.rel = os.path.join(".harness", segment, "docs", "DECISIONS.md")
        self.index_rel = os.path.join(".harness", segment, "docs", "DECISIONS-INDEX.md")
        index_text = _read_text(os.path.join(root, self.index_rel))
        self.lines = (_read_text(os.path.join(root, self.rel)) or "").splitlines(keepends=True)
        self.headings = _real_headings(self.lines)
        self.struck = None if index_text is None else _struck_by_dec(index_text)

    def section(self, dec):
        """The text of `dec`'s own heading section up to the next real heading at its level or
        shallower, or None when no real heading names it."""
        for pos, (start, level) in enumerate(self.headings):
            if _heading_level(self.lines[start], dec):
                end = next((at for at, deeper in self.headings[pos + 1:] if deeper <= level),
                           len(self.lines))
                return "".join(self.lines[start:end])
        return None


def _owns_decisions(tasks, rel):
    """True when some task's normalized files: path is the segment's DECISIONS.md."""
    return any(os.path.normpath(str(plan_anchors.path_of(entry))) == rel
               for task in tasks if isinstance(task, dict) for entry in task.get("files") or [])


def _successor_fault(row, authority, plan_ids):
    successor = row.get("successor")
    if successor in plan_ids or successor in authority.struck:
        return None
    return (f"successor {successor} is neither a decisions: id of this plan nor indexed in "
            f"{authority.index_rel}")


def _replacement_faults(row, ctx):
    """The amend/strike-only faults: an unresolved successor and no DECISIONS.md owner."""
    if row.get("disposition") not in ("amend", "strike"):
        return []
    authority, plan_ids, owned = ctx
    faults = [_successor_fault(row, authority, plan_ids)]
    if not owned:
        faults.append(f"no task's files: names {authority.rel}, so no task carries this "
                      f"{row.get('disposition')}")
    return [fault for fault in faults if fault]


def _row_faults(row, ctx):
    """Every mechanical fault of one well-formed row, as messages."""
    authority = ctx[0]
    dec, disposition = row.get("dec"), row.get("disposition")
    if dec not in authority.struck:
        return [f"not indexed in {authority.index_rel}"]
    faults = []
    if authority.struck[dec] and disposition in ("keep", "amend"):
        faults.append(f"is STRUCK, so it cannot be {disposition}ed — only struck")
    section = authority.section(dec)
    if section is None or str(row.get("clause")) not in section:
        faults.append(f"clause {row.get('clause')!r} is not verbatim in {dec}'s own section of "
                      f"{authority.rel}")
    return faults + _replacement_faults(row, ctx)


def _rows_faults(rows, ctx):
    lines = []
    for index, row in enumerate(rows):
        if isinstance(row, dict):
            where = f"FAIL decisions_affected[{index}] {row.get('dec')}"
            lines += [f"{where}: {fault}" for fault in _row_faults(row, ctx)]
    return lines


def _disposition_faults(doc, tasks, resolved_plan, root):
    """FAIL lines for an eligible draft's decisions_affected; [] for every other plan."""
    eligible, faults = _eligibility(doc, root)
    if not eligible:
        return faults
    if not isinstance(doc.get("decisions_affected"), list):
        return ["FAIL decisions_affected: an eligible pending draft must record its decision "
                "dispositions (`[]` claims none)"]
    authority = _Authority(root, harness_boundary.plan_segment(resolved_plan))
    if authority.struck is None:
        return [f"FAIL decisions_affected: {authority.index_rel} is unreadable under {root}, so "
                "no row can be checked"]
    plan_ids = {d.get("id") for d in doc.get("decisions") or [] if isinstance(d, dict)}
    ctx = (authority, plan_ids, _owns_decisions(tasks, authority.rel))
    return _rows_faults(doc["decisions_affected"], ctx)


def _overlap_lines(tasks):
    """BUG-1725: one ADVISORY line per normalized path that two or more tasks name. Every
    anchor form reduces to its path, so `a.py#foo` in T-01 and `{path: a.py, quote}` in T-02
    are the same shared file. Advisory because a shared file is sometimes right (a fixture two
    tasks extend) — but a plan whose tasks are LAYERS over the same files gates each one against
    a tree the next one will move, and BUG-285 paid five of ten cycles for
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


def _route_gate_failures(resolved_plan, root, routes):
    """#2239: CI's per-plan rule set — check-plan-routes.process_plan_yaml, the ONE copy of the
    DEC-182 budget, station and routing rules — run on this plan alone, each VIOLATION a FAIL.
    Asked with --root (never the code worktree) and the manifest root `_Routes` resolved, as CI
    asks. A plan the processor cannot load (it returns None, reason on stderr) is a refusal,
    never a clean pass. Its NOBODY routing line is a separate rule from `_route_faults`'
    execution_agent grant, so both are reported, never deduped."""
    findings = []
    if routes.cpr.process_plan_yaml(resolved_plan, findings, root, routes.manifest_root) is None:
        _die(5, f"plan-merge: {resolved_plan} fails plan validation, so CI's route gate cannot "
                "check it (the reason is printed above).")
    return [f"FAIL {line}" for line in findings if line.startswith("VIOLATION")]


def _preface(routes, brief_fault):
    """The plan-wide FAIL lines printed before any task's: a DEVIATION and an absent BRIEF."""
    return [line for line in (routes.deviation and f"FAIL {routes.deviation}", brief_fault) if line]


def _report(failures, tasks, summary):
    """Print every FAIL, then every OVERLAP advisory, then the CHECK summary; exit 1 on any FAIL."""
    for line in failures + _overlap_lines(tasks):
        print(line)
    print(f"{summary}, {len(failures)} failure(s)")
    sys.exit(1 if failures else 0)


def cmd_check(args):
    resolved_plan, root, code_root, doc, tasks = _check_inputs(args)
    routes = _Routes(root, code_root)
    anchor_root = code_root or root
    brief_text, brief_fault = _brief_text(resolved_plan)
    # The gate first: a plan it cannot load exits 5 before any OK line or resolver spawn.
    gate_failures = _route_gate_failures(resolved_plan, root, routes)
    task_failures, total = _check_all(tasks, anchor_root, brief_text, routes)
    task_failures += _disposition_faults(doc, tasks, resolved_plan, root)
    _report(_preface(routes, brief_fault) + task_failures + gate_failures, tasks,
            f"CHECK {resolved_plan} against {anchor_root}: {len(tasks)} task(s), {total} "
            "anchor(s) resolved")
