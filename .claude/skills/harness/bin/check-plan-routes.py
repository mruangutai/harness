#!/usr/bin/env python3
"""check-plan-routes.py — plan-time route check (D-01).

Answers, while a PLAN.md is still being written, whether every task's `files:`
paths land on an agent granted to write them, or are honestly declared
`execution_mode: main-session-direct`. It is a PLAN-PHASE CLI, not a
PreToolUse hook — see D-01 for why this is a new script rather than a mode of
check-state.py or an invariant of check-domain.py.

ROUTING IS NEVER RE-IMPLEMENTED HERE (D-02, SC-08): every path is resolved by
shelling out to `check-domain.py --resolve <path>` with stdin closed. This
file must never gain its own copy of Python's stdlib pattern matcher, its own
glob-to-regex translator, or a bare prefix comparison — a prefix comparison
on the text before `/**` answers False for a pattern with an earlier
wildcard segment (e.g. `.harness/features/*/runs/*-eng/**`), which is the
exact bug check-domain.py:190-197 records fixing.

Task blocks are found with the SAME regex check-state.py uses (D-08), copied
rather than shared because check-state.py belongs to the in-flight FEAT-08 and
PLAN.md is markdown, not YAML.

The --canonical-reader-audit and --consolidation-audit modes are implemented in
canonical_reader_audit.py and structure_audit.py beside this file. They are
gate-imported libraries under DEC-174's library clause; this file stays the
enumerated gate, and a change that makes it use different audit code is a
main-session-direct cutover.
"""
import glob
import os
import re
import subprocess
import sys

BIN_DIR = os.path.dirname(os.path.abspath(__file__))

# THE ONE RESOLVER (FEAT-42 T-13). Imported at module scope beside BIN_DIR because the root
# is needed before anything else this script does, and because a tree without it is a tree
# this script cannot answer about at all.
sys.path.insert(0, BIN_DIR)
import harness_boundary  # noqa: E402  (the path insert above has to come first)
import artifact_accessors  # noqa: E402
import feature_corpus  # noqa: E402
# The two audit modes live in these gate-imported libraries (FEAT-2489).
from canonical_reader_audit import LEGAL_MAIN_SESSION_TOKEN, _run_canonical_reader_audit  # noqa: E402
from structure_audit import _run_consolidation_audit  # noqa: E402
CHECK_DOMAIN = os.path.join(BIN_DIR, "check-domain.py")

# Copied from check-state.py:93-94 (D-08) — a duplicated task-BLOCK parser,
# never a duplicated path matcher.
TASK_RE = re.compile(
    r"^(?:-\s*|#+\s*)(T-\d+)\b(.*?)(?=^(?:-\s*|#+\s*)T-\d+\b|\Z)",
    re.M | re.S,
)

# `[ \t]*`, NEVER `\s*`, after the colon (issue #134). `\s` matches NEWLINES, so the
# original `files:\s*(.*)$` swallowed the line break on a list-form block and captured
# the FIRST LIST ITEM — dash included — as if it were the whole files: value.
#
# That produced a false positive AND a fail-open at once, which is why this is worth
# the comment. Measured on a three-path fixture before the fix:
#   VIOLATION T-01: - .harness/harness/docs/SPEC.md ungranted   <- granted; the dash broke it
#   ...and .gitignore, which genuinely resolves to NOBODY, was NEVER CHECKED.
# One bogus violation masking one real one. The visible symptom was the false
# rejection; the dangerous half was the four other entries nobody ever looked at.
FILES_RE = re.compile(r"^[ \t]*files:[ \t]*(.*)$", re.M)
# A list item under a `files:` block. Stops at the next `key:` line or a blank line.
LIST_ITEM_RE = re.compile(r"^[ \t]*-[ \t]*(.+?)[ \t]*$")
KEY_LINE_RE = re.compile(r"^[ \t]*[A-Za-z_][A-Za-z0-9_]*:")
# The pre-FEAT-06 shape: `- files:` as a list item. Detected only to give a
# better message; never parsed.
LEGACY_FILES_RE = re.compile(r"^[ \t]*-[ \t]*files:", re.M)
MODE_RE = re.compile(r"^\s*execution_mode:\s*(\S+)", re.M)

LEGAL_TOKENS = "team, main-session-direct"  # D-07


def _resolver_invocation(root, manifest_root):
    if os.path.realpath(root) == os.path.realpath(manifest_root):
        return CHECK_DOMAIN, None
    owner_check_domain = os.path.join(
        manifest_root, ".claude", "skills", "harness", "bin",
        "check-domain.py")
    if os.path.isfile(owner_check_domain):
        return owner_check_domain, None
    env = os.environ.copy()
    env[harness_boundary.PROJECT_DIR_ENV] = manifest_root
    return CHECK_DOMAIN, env


def _agents_from_output(output):
    lines = (line.strip() for line in output.splitlines())
    return sorted({
        line for line in lines
        if line and line != "NOBODY" and not re.match(r"^SHARED ", line)
    })


def resolve_agents(path, root, manifest_root):
    """Return agents from the same resolver script the live hook invokes."""
    check_domain, env = _resolver_invocation(root, manifest_root)
    proc = subprocess.run(
        [check_domain, "--resolve", path],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode == 2:
        sys.stderr.write(proc.stderr)
        sys.exit(2)
    return _agents_from_output(proc.stdout)


def _owner_root(root):
    """Return the owner checkout root, raising if a worktree cannot establish one."""
    worktree = harness_boundary.worktree_owner(root)
    if worktree is None:
        return root
    _, owner_root, legitimate = worktree
    if owner_root is None or not legitimate:
        raise ValueError(f"cannot establish the owner checkout for {root}")
    return owner_root


def _manifest_deviation(root, owner_root):
    """Return the DEVIATION message when root's manifest ROUTES differ from the owner's.

    THE COMPARISON IS PARSED, NOT BYTE-FOR-BYTE (FEAT-41 T-09/T-15). It was a byte compare, and
    a byte compare cannot tell a COMMENT from a ROUTE. Measured: T-09 was required to rewrite two
    trailing comments in this manifest, changing no grant and no domain — `yaml.safe_load` of the
    two files returns EQUAL objects — and six cases in this file's own suite went red, because
    each runs a fixture plan against the live checkout and the deviation is counted as a
    violation. Any feature that so much as re-words a comment here inherited that.

    WHAT THE MESSAGE CLAIMS IS WHAT IS NOW CHECKED. It says "routes were resolved against the
    owner manifest", so the question is whether the ROUTES differ. They are the parsed content;
    comments are not routes. A route change still deviates, which the paired cases below pin.

    THE BYTE COMPARE SURVIVES AS A FAST PATH, because identical bytes cannot hold differing
    routes and the parse costs a file read plus a YAML load on every invocation otherwise.

    AN UNPARSEABLE BRANCH MANIFEST IS A DEVIATION, never a silent pass. It cannot be shown to
    agree, and this function's whole job is to say when agreement is not established.
    """
    manifest = os.path.join(owner_root, harness_boundary.MARKER)
    if not os.path.isfile(manifest) or not os.access(manifest, os.R_OK):
        raise ValueError(f"owner manifest is not readable: {manifest}")
    branch_manifest = os.path.join(root, harness_boundary.MARKER)
    if os.path.realpath(branch_manifest) == os.path.realpath(manifest):
        return None
    with open(branch_manifest, "rb") as branch, open(manifest, "rb") as owner:
        if branch.read() == owner.read():
            return None
    import harness_yaml
    try:
        if (
                artifact_accessors.manifest_domains(branch_manifest)
                == artifact_accessors.manifest_domains(manifest)):
            return None
    except (artifact_accessors.ArtifactAccessError, artifact_accessors.FleetError,
            harness_yaml.YamlParseError, OSError, UnicodeError, KeyError, TypeError,
            ValueError):
        # FEAT-64: the manifest's own failure classes -- unreadable, unparseable, or a mapping
        # of the wrong shape -- mean agreement is not established, which is what the DEVIATION
        # line below says. The same tuple harness_boundary.run_dir_grant_globs names for the
        # same accessor. Anything else is a defect and propagates.
        pass
    return (
        f"DEVIATION {branch_manifest} differs from {manifest}; routes were "
        "resolved against the owner manifest because that is what the hook consults"
    )


def resolution_manifest(root):
    """Return the owner manifest the hook uses and any branch/owner deviation."""
    owner_root = _owner_root(root)
    deviation = _manifest_deviation(root, owner_root)
    return owner_root, deviation


def _clean(entry):
    return entry.strip().strip("`").strip().rstrip(",").strip()


def parse_files(body, files_match):
    """Entries from a `files:` value, in EVERY shape the tree actually uses.

    Three shapes, and missing any of them is a FAIL-OPEN rather than a parse error —
    unresolved entries simply are not checked, and the run still reports success:

      1. same-line:            files: a, b, c
      2. same-line WRAPPED:    files: a,          <- trailing comma, continues below
                                 b
      3. block:                files:
                                 - a
                                 - b

    Shape 2 is live in FEAT-08 (3 tasks). Before this, its continuation lines were
    dropped: T-01 declares two paths and the checker resolved one, reporting DEVIATION
    on the single path it had seen. Shape 3 was the issue-#134 case.
    """
    same_line = files_match.group(1).strip()
    rest = body[files_match.end():].splitlines()[1:]

    if same_line:
        raw = [same_line]
        # A trailing comma means the value continues. Keep taking indented, non-key
        # lines while the previous one ends in a comma.
        if same_line.rstrip().endswith(","):
            for line in rest:
                if not line.strip() or KEY_LINE_RE.match(line) or LIST_ITEM_RE.match(line):
                    break
                raw.append(line.strip())
                if not line.strip().endswith(","):
                    break
        return [c for c in (_clean(e) for e in " ".join(raw).split(",")) if c]

    # Block form. `$` stops BEFORE the newline, so splitlines() yields an empty first
    # element — dropping it matters: without the [1:] above the loop breaks on that
    # empty string and parses nothing, which prints "0 violations" and IS the fail-open.
    entries = []
    key_indent = len(files_match.group(0)) - len(files_match.group(0).lstrip())
    for line in rest:
        if not line.strip():
            break
        m = LIST_ITEM_RE.match(line)
        if not m:
            break                       # a `key:` line, or prose — the block ended
        # A bullet DEDENTED past the `files:` key belongs to the enclosing list, not to
        # this value. Without this the loop ate any following bullet as a path — the
        # KEY_LINE_RE guard could never fire, because a line starting `-` never matches
        # `[A-Za-z_]` at the same offset.
        if (len(line) - len(line.lstrip())) <= key_indent:
            break
        c = _clean(m.group(1))
        if c:
            entries.append(c)
    return entries


def process_task(tid, body, findings, root, manifest_root):
    """Append findings for one task block. Returns the number of VIOLATIONs added."""
    files_match = FILES_RE.search(body)
    if not files_match:
        # A `- files:` LIST-ITEM key (the pre-FEAT-06 shape, still in FEAT-03/04/05)
        # is deliberately NOT parsed: its children are prose — "create `path`",
        # "edit `path` (`key`)" — and extracting paths from prose would produce
        # confident wrong answers, which is worse than declining. Say which case
        # this is, because "no files: line" on a task that visibly HAS one reads as
        # a checker bug and sent one reader looking for one.
        if LEGACY_FILES_RE.search(body):
            findings.append(
                f"VIOLATION {tid}: files: is a `- files:` list item with prose "
                f"children (pre-FEAT-06 shape) — not machine-readable. Rewrite it as "
                f"`files: <path>, <path>` or a `- <path>` block to have it checked."
            )
        else:
            findings.append(f"VIOLATION {tid}: no files: line")
        return 1

    mode_match = MODE_RE.search(body)
    mode_token = mode_match.group(1) if mode_match else None

    entries = parse_files(body, files_match)

    glob_entries = [e for e in entries if "*" in e or "?" in e]
    literal_entries = [e for e in entries if e not in glob_entries]

    for entry in glob_entries:
        findings.append(f"UNRESOLVED-GLOB {tid} {entry}")

    if not literal_entries:
        # SILENCE HERE IS THE FAIL-OPEN. An empty entry list is indistinguishable from
        # "every path was granted", and both used to return 0 with no output — so a
        # files: value this parser could not read looked exactly like a clean task.
        # Say so instead. Not a VIOLATION: the plan may be fine and the parser wrong,
        # which is precisely why a human has to look.
        if not glob_entries:
            findings.append(
                f"UNPARSED {tid}: files: is present but no path could be read from it "
                f"— NOT the same as 'all granted'. Nothing was checked for this task."
            )
        return 0

    nobody_paths = []
    granted_agents = set()
    for entry in literal_entries:
        agents = resolve_agents(entry, root, manifest_root)
        if agents:
            granted_agents.update(agents)
        else:
            nobody_paths.append(entry)

    violations = 0
    if nobody_paths:
        if mode_token == LEGAL_MAIN_SESSION_TOKEN:
            findings.append(
                f"OK {tid}: declared main-session-direct "
                f"({', '.join(nobody_paths)} ungranted)"
            )
        else:
            declared = mode_token or "(missing)"
            for path in nobody_paths:
                findings.append(
                    f"VIOLATION {tid}: {path} ungranted (NOBODY); "
                    f"execution_mode is {declared} — legal tokens: {LEGAL_TOKENS}"
                )
                violations += 1
    else:
        # every literal path resolved to a granting agent
        if mode_token == LEGAL_MAIN_SESSION_TOKEN:
            findings.append(
                f"DEVIATION {tid} {', '.join(literal_entries)} granted to "
                f"{', '.join(sorted(granted_agents))} but declared main-session-direct"
            )
        else:
            # The agent set is NAMED, not just counted, and that is load-bearing rather than
            # cosmetic. This branch fires whenever every path resolved to somebody, so an
            # `OK {tid}` that says only "somebody" cannot distinguish the real resolver from a
            # hand-rolled prefix comparison — measured, the prefix version OVER-grants
            # (`.harness/features/` prefixes every feature file), so it also lands here, also
            # prints OK, and the checker silently becomes a no-op that never reports a
            # violation. Naming the set is what lets the test tell the two apart. Same shape
            # the DEVIATION line above already uses.
            findings.append(f"OK {tid} granted to {', '.join(sorted(granted_agents))}")

    return violations


# Machine-field lines allowed per task, on the plan.yaml path (DEC-182).
#
# PER TASK, NOT PER FILE, and that asymmetry against every peer budget is deliberate. A
# plan is a LIST — its length tracks how many tasks a feature has, not how much fat it
# carries. feature.json (300), STATE.md (120), handoff (60) and CLAUDE.md (80) all govern
# files whose content does not grow with task count. A flat cap here would be a cap on how
# many tasks a feature may have, which is a scoping decision wearing a budget's clothes.
# DERIVED PER TASK, and the first draft was not. That draft said 30, justified as "~12%
# headroom over the worst", computed from the per-PLAN MEANS (11.5 / 21.2 / 26.7 / 19.9).
# The budget is enforced PER TASK, so a mean was the wrong statistic and review caught it.
#
# WHAT IS ACTUALLY MEASURED, AND WHAT IS NOT. Three independent hand-conversions of the
# 36 tasks in the four live plans agree on two anchors and on nothing else worth quoting:
#
#   48   the largest task that is a task
#   89   the smallest task that is an inlined script
#
# An earlier draft of this comment cited "max 209" and "over 30: 5 tasks". Both were
# wrong, and the cause is worth recording because it is a trap for the next person who
# measures this. FEAT-08 T-12's `verify:` is five physical lines (748-752), terminated by
# a `## ` heading at 753 — NOT a `key:` line. An extractor that scans for the next key
# swallows the rest of the section and reports 199, 246 or 251 depending on where it gives
# up. Two reviewers and I produced three different numbers from the same file.
#
# So no distribution of the ENFORCED metric is quoted here. A number nobody can reproduce
# is not evidence, and citing one is how "derived, not picked" becomes a costume. The two
# anchors are the only figures that survived independent check, and they are enough to
# place the cap. The one measurement quoted below is of the REJECTED alternative, kept
# because it is what disqualified that alternative -- not offered as a warrant for 50.
#
# THE HONEST CAVEAT: `find .harness -name plan.yaml` returns ZERO. This budget has never
# been applied to a real file of the format it governs, and the anchors come from
# converting a different format by hand. The first migrated plan is what will settle it.
#
# WHY 50, AND WHY `verify:` STAYS COUNTED. Excluding `verify:` was the tidier-looking fix,
# because DEC-154's read-vs-match test does arguably reach it — the lead carries it
# VERBATIM to the member. It was measured and rejected: without `verify:` the distribution
# is median 11, max 21, and the per-field maxima across ALL eight plans sum to 23
# (files 3, traces 12, depends_on 8) -- against ANY cap at or above 30, and this one is
# 50. A task could not reach even 31 without ~25 list entries, a shape nobody has ever
# written. That is not a budget, it is a cap
# that cannot fire — and a threshold made unreachable is how a gate passes while the
# behaviour it names is gone.
#
# So the cap sits between the two anchors: above 48, below 89. An inlined script belongs
# in a file the plan NAMES, not in the contract, and at 50 the gate says so.
MACHINE_LINES_PER_TASK = 50

# Fields whose value is MATCHED rather than read, and therefore counted against the budget.
# `intent:` is excluded on purpose: it is the literal dispatch prompt and it is READ, which
# is DEC-154's test for which half a value belongs in.
BUDGETED_FIELDS = ("files", "verify", "traces", "depends_on", "change_type",
                   "execution_mode", "execution_agent", "execution_reason", "status", "id",
                   "title")


def process_plan_yaml(path, findings, root, manifest_root):
    """The plan.yaml path (DEC-182): a real loader, no regexes.

    Everything `_clean`, FILES_RE, LIST_ITEM_RE, KEY_LINE_RE, LEGACY_FILES_RE and MODE_RE
    existed for is gone here — not because they were badly written, but because they were
    reading markdown as if it were data. `files:` is a list because YAML says so; a bolted
    annotation is part of the string because YAML says so; `execution_mode` is one of two
    tokens because load_plan says so.
    """
    import harness_yaml
    try:
        doc = _load_plan_once(path)
    except harness_yaml.YamlParseError as e:
        # Exit 2, not a violation. "The plan does not parse" is the checker being unable to
        # run, not the plan being wrong about routing — the same distinction B-7 turned on.
        print(f"check-plan-routes: {path} does not load: {e}", file=sys.stderr)
        return None

    legal = legal_task_statuses()
    base = _plan_route_base(path, findings, manifest_root)
    # FEAT-68: findings are reported in this sequence; each rule returns its violation count.
    violations = _feature_station_rule(doc, findings, legal) + (base is False)
    for t in doc["tasks"]:
        tid = str(t["id"])
        violations += _budget_rule(t, tid, findings)
        violations += _task_status_rule(t, tid, findings, legal)
        if base is not False:
            violations += _routing_rule(t, tid, findings, root, manifest_root, base)
    return violations


def _plan_route_base(path, findings, manifest_root):
    """Where this plan's paths are asked about: None for harness's own plan (relative to the
    harness tree, as always), the fleet's product base for a served repository's (#2077), or
    False — with its VIOLATION recorded — when the fleet declares no such repository, since a
    route that cannot be asked must not read as granted or as NOBODY."""
    segment = harness_boundary.plan_segment(path)
    if segment == harness_boundary.HARNESS_SEGMENT:
        return None
    base = harness_boundary.product_base(manifest_root, segment, "check-plan-routes")
    if base is None:
        findings.append(f"VIOLATION {path}: served repository segment {segment!r} is not "
                        "declared in the fleet, so its routes cannot be resolved")
        return False
    return base


def _feature_station_rule(doc, findings, legal):
    # THE FEATURE'S OWN STATION, checked exactly like a task's (FEAT-41 T-04). It is optional:
    # a plan that has not been given a station is not a plan that is wrong about one, and T-07 is
    # what makes this key the station of record. But a value OUTSIDE the vocabulary is a
    # violation here for the same reason it is on a task — the whole feature exists so that one
    # word means one thing in every file that carries it.
    feature_station = doc.get("status")
    if feature_station is not None and (
            not isinstance(feature_station, str)
            or feature_station not in legal):
        findings.append(
            f"VIOLATION top-level status {feature_station!r} is not one of "
            f"{legal} (case sensitive)")
        return 1
    return 0


def _budget_lines(t):
    budget_lines = 0
    for f in BUDGETED_FIELDS:
        v = t.get(f)
        if isinstance(v, str):
            budget_lines += len(v.splitlines()) or 1
        elif isinstance(v, list):
            budget_lines += len(v)
        elif v is not None:
            budget_lines += 1
    return budget_lines


def _budget_rule(t, tid, findings):
    budget_lines = _budget_lines(t)
    if budget_lines > MACHINE_LINES_PER_TASK:
        findings.append(
            f"VIOLATION {tid}: {budget_lines} machine-field lines — budget is "
            f"{MACHINE_LINES_PER_TASK} per task (DEC-182). Detail that only JUSTIFIES "
            f"the instruction belongs in notes/, not in the contract.")
        return 1
    return 0


def _task_status_rule(t, tid, findings, legal):
    status = t.get("status")
    if status is not None and (
            not isinstance(status, str) or status not in legal):
        # Not str()-coerced first (DEC-203): a list stringifies to something that
        # happens not to be in the tuple, which gives the right answer for the wrong
        # reason and stops giving it the moment the tuple grows. Case sensitive on
        # purpose, and the case that matters has changed with the vocabulary: the board no
        # longer stores a capitalised name anywhere, so the typo a person will actually make
        # is `pending` — the word this file itself accepted until FEAT-41 T-04 — or a
        # capitalised column name copied off the GitHub board by eye.
        findings.append(
            f"VIOLATION {tid}: status {status!r} is not one of {legal} "
            f"(case sensitive)")
        return 1
    return 0


def _routing_rule(t, tid, findings, root, manifest_root, base=None):
    mode = t["execution_mode"]
    literals = _literal_paths(t, tid, findings)
    nobody, granted = _resolve_grants(literals, root, manifest_root, base)
    if nobody:
        return _ungranted_findings(tid, mode, nobody, findings)
    if literals:
        _granted_findings(tid, mode, literals, granted, findings)
    return 0


def _literal_paths(t, tid, findings):
    import plan_anchors
    # AN ANCHOR IS RESOLVED BY ITS PATH (FEAT-59 C4). `a.py#foo` and `{path: a.py, quote:
    # ...}` name a place INSIDE a.py; the grant question is about a.py. plan_anchors.py owns
    # the grammar; asking check-domain about `a.py#foo` would answer NOBODY for a granted
    # file, which is the false violation issue #134 already taught this file to fear.
    paths = [plan_anchors.path_of(f) for f in t["files"]]
    globs = [f for f in paths if "*" in f or "?" in f]
    literals = [f for f in paths if f not in globs]
    for g in globs:
        findings.append(f"UNRESOLVED-GLOB {tid} {g}")
    return literals


def _resolve_grants(literals, root, manifest_root, base=None):
    nobody, granted = [], set()
    for entry in literals:
        agents = resolve_agents(os.path.join(base, entry) if base else entry, root, manifest_root)
        if agents:
            granted.update(agents)
        else:
            nobody.append(entry)
    return nobody, granted


def _ungranted_findings(tid, mode, nobody, findings):
    if mode == LEGAL_MAIN_SESSION_TOKEN:
        findings.append(
            f"OK {tid}: declared main-session-direct ({', '.join(nobody)} ungranted)")
        return 0
    for path_ in nobody:
        findings.append(
            f"VIOLATION {tid}: {path_} ungranted (NOBODY); execution_mode is "
            f"{mode} — legal tokens: {LEGAL_TOKENS}")
    return len(nobody)


def _granted_findings(tid, mode, literals, granted, findings):
    if mode == LEGAL_MAIN_SESSION_TOKEN:
        findings.append(
            f"DEVIATION {tid} {', '.join(literals)} granted to "
            f"{', '.join(sorted(granted))} but declared main-session-direct")
    else:
        findings.append(f"OK {tid} granted to {', '.join(sorted(granted))}")


def process_plan(path, findings, root, manifest_root):
    """Returns the violation count for one plan, or None if the path exits 2.

    Routes on the FILENAME. plan.yaml gets the loader; PLAN.md keeps the regex reader for
    the migration window (DEC-182) — existing plans are never rewritten or converted, so
    the reader stays while any unshipped feature still carries a PLAN.md, and goes once
    none does.
    """
    if not os.path.exists(path):
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        return None

    if os.path.basename(path) == "plan.yaml":
        return process_plan_yaml(path, findings, root, manifest_root)

    with open(path) as f:
        text = f.read()

    violations = 0
    for tid, body in TASK_RE.findall(text):
        violations += process_task(tid, body, findings, root, manifest_root)
    return violations


# THIS SET DESCRIBES plan.yaml's STATION VOCABULARY AS OF T-07, AND IS LOWERCASE.
#
# THE LOWERCASING WAITED FOR THIS TASK, DELIBERATELY. T-04's intent said to do it there, and
# that was premature in a way worth recording: while `_is_shipped` still read feature.json,
# whose vocabulary was capitalised, a lowercase set matched NOTHING — measured, `1 skipped as
# shipped` where it had been 39, and 67 violations across 39 shipped plans, every one a
# legacy-shape complaint about a plan that is a record rather than a contract. A lowercase word
# pointed at a still-capitalised file is the defect, not the fix. T-07 moves the read and the
# vocabulary in the same edit, which is the only order in which either is correct.
#
# The terminal marker joined `done` on 2026-08-14: a plan that will never be executed is not
# actionable, which is the same reason shipped plans are skipped. THE TUPLE SHAPE IS CORRECT AND
# IS NOT A CODE SMELL — kept so a value could join without changing the comparison. Do NOT add
# "shipped" back as an alias: that would be the old-to-new mapping layer D-09 forbids.
#
# DERIVED, NEVER SPELLED, for the reason `legal_task_statuses` below is: a literal here is a
# second vocabulary. The import is lazy for that function's exact reason — cases 19b, 19b2 and
# 21 copy this file alone into a temp directory, where a module-scope import is a traceback.
#
# FEAT-61 T-05: the view, not the strict predicate. `_is_shipped` promises never to raise and
# treats an unknown token as "checked" — `factory_config.is_finished` raises on one by design
# (D-03), so the membership test stays and the tuple it tests is the table's own
# FINISHED_STATIONS rather than a hand-concatenated `("done",) + TERMINAL_STATIONS`.
def finished_stations():
    import factory_config
    return factory_config.FINISHED_STATIONS


# ONE VOCABULARY NOW, WHICH IS THE WHOLE POINT OF FEAT-41. Until T-04 this file carried a
# private three-value set — pending, building, done — sitting beside the finished-station set
# under a comment warning the reader not to conflate the two. There is nothing left to
# conflate: a task's
# status is one of the six stations harness.json declares, or the terminal marker. `pending` is
# not a value any more, in any file.
#
# READ, NEVER RESPELLED: plan-merge.py validates writes against exactly this, so a plan this
# checker accepts is exactly a plan that tool would have written.
#
# COMPUTED THROUGH A FUNCTION WITH A LAZY IMPORT, and the laziness is load-bearing: cases 19b,
# 19b2 and 21 copy THIS FILE ALONE into a temp directory and run it, to prove an unresolvable
# root exits 2 with a reason rather than crashing. A module-scope `import factory_config` turned
# all three into a ModuleNotFoundError traceback before the script could report anything —
# measured. `harness_yaml` is imported inside its own function for exactly this reason.
def legal_task_statuses():
    import factory_config
    return tuple(factory_config.MANDATED_STATIONS) + factory_config.TERMINAL_STATIONS


# FEAT-64 (SC-05): ONE parse per plan per execution. `_is_shipped` (discovery's shipped-skip)
# and `process_plan_yaml` (the route check) each called `artifact_accessors.load_plan` on the
# same file, so every live plan was parsed twice. The outcome of the first load -- the document,
# or the YamlParseError it raised -- is what every later reader in the same run receives;
# nothing on disk changes between them. Cleared in main() so a test that drives main() twice
# in one interpreter sees its own writes.
_PLAN_LOADS = {}


def _load_plan_once(path):
    key = os.path.realpath(path)
    if key not in _PLAN_LOADS:
        import harness_yaml
        try:
            _PLAN_LOADS[key] = artifact_accessors.load_plan(path)
        except harness_yaml.YamlParseError as error:
            _PLAN_LOADS[key] = error
    hit = _PLAN_LOADS[key]
    if isinstance(hit, Exception):
        raise hit
    return hit


def _is_shipped(feature_dir):
    """True when this feature's work is delivered and its plan is a record, not a contract.

    Reads the sibling `plan.yaml`'s top-level station with the real loader — the ONE file that
    records it (T-07). An unreadable or absent plan means NOT finished — a feature we cannot
    classify is checked rather than
    skipped, because the failure that matters is a live plan going unexamined, not an old
    one being examined twice.

    EVERY EXIT FROM THIS FUNCTION IS `False` OR A MEMBERSHIP TEST. It never raises, and
    that is the whole point: the first draft put the `return` OUTSIDE its own `try:`, so a
    feature.yaml holding a YAML sequence reached `doc.get` on a list and raised
    AttributeError out of discover_plans(). The process then died with **exit 1 — the code
    that means "violations found"** — after examining nothing, printing no summary, and
    naming no feature. One malformed file anywhere under .harness/features/ silently
    converted the whole checker into a liar.

    That is the same defect this change fixes in passing for check-state.py (`NameError:
    cj`) and the same one the manifest-domain accessor records as M-02. Three instances,
    one shape: a crash exits 1, and 1 is already spoken for. check-state.py:160-168 is the
    model — `isinstance(doc, dict)` is checked before anything reads a key off it.
    """
    fy = os.path.join(feature_dir, "plan.yaml")
    if not os.path.isfile(fy):
        # THE PLAN.md-ERA RECORD IS FINISHED BY CONSTRUCTION, and this branch is a CORRECTION to
        # T-07's intent rather than a case it specified. The intent said a feature directory with
        # no plan.yaml "keeps nothing ... because those features are finished and no reader needs
        # a station for them". This reader needs one: with the station read from plan.yaml and no
        # plan.yaml present, all ten such features stopped being skipped, and the tree went from
        # 0 violations across 1 plan to 44 across 9 — every one of them legacy-shape noise in a
        # plan that shipped years of cycles ago. That noise is precisely why issue #133's gate
        # could not be switched on, and case_24's own docstring records the original measurement.
        #
        # WHY A PLAN.md IS SUFFICIENT EVIDENCE, measured rather than assumed: NO production code
        # in this tree writes a PLAN.md. Every reference to it across bin/ is a read
        # (check-state.py, gh-sync.py, this file); the only writers are test fixtures. A
        # directory carrying one therefore predates plan.yaml, and its plan is a record.
        #
        # FAIL-CHECKED IN THE OTHER DIRECTION: a directory with NEITHER file is still False, so
        # nothing is skipped on the strength of an absence alone — and discovery finds no plan to
        # check there anyway, so the branch below is about PLAN.md and only PLAN.md.
        return os.path.isfile(os.path.join(feature_dir, "PLAN.md"))
    import harness_yaml
    try:
        doc = _load_plan_once(fy)
    except harness_yaml.YamlParseError:
        # load_plan's whole failure surface: load_file wraps the read's OSError/UnicodeError
        # (F-01), and validate_plan_doc's PlanSchemaError is a YamlParseError. Unreadable is
        # NOT finished, per the docstring; the diagnostic is process_plan_yaml's to print.
        return False
    # `or {}` is NOT enough here. load_file returns whatever the document is, and a
    # non-empty list is truthy — it would survive `or {}` and then fail on `.get`.
    if not isinstance(doc, dict):
        return False
    # `status: done  # with a trailing comment` is a shape the live corpus carries, so take the
    # first whitespace-delimited token. A status that is a list or a mapping stringifies to
    # something that is not a finished station, which is the fail-CHECKED direction.
    #
    # THE COMPARISON STAYS CASE SENSITIVE, and that survives the migration intact: the station
    # vocabulary is lowercase now, so a capitalised `Done` in plan.yaml is CHECKED rather than
    # skipped. case_24 asserts exactly that, with the case it names inverted by this task — it
    # is still the case that proves the sensitivity is load-bearing rather than documented. A
    # case fold here was tried and reverted under the old vocabulary and stays rejected: it is
    # the fail-OPEN direction on the one file this function is allowed to trust.
    token = str(doc.get("status", "")).split()
    return bool(token) and token[0] in finished_stations()


def discover_plans():
    """Argv-less discovery: every PLAN.md under the PROJECT ROOT, not under the cwd.

    The glob used to be `.harness/features/*/PLAN.md` relative to the cwd, so running
    this from anywhere but the repo root printed `0 violation(s) across 0 plan(s)` and
    EXITED 0 — a checker that found nothing because it was looking in the wrong place
    was byte-identical to a clean tree (issue #133, B-7). Measured before this fix:
    `cd /tmp && python3 <repo>/.agents/skills/harness/bin/check-plan-routes.py` exited 0.

    Root precedence follows check-domain.py (`:178-180`, and again at `:276-281` for
    its hook path — two call sites, one rule), because a third derivation is a third
    thing to drift: the Harness project-root environment override if it carries the harness marker, else the root
    DERIVED from this file's location (bin/ is four levels down), as harness_boundary.resolve_root
    decides.

    ONE BRANCH DIFFERS, DELIBERATELY. check-domain.py's third branch is
    `root = root or os.getcwd()`; this one is `""` and exits 2. A cwd fallback IS the
    B-7 fail-open — it is how a checker ends up scanning wherever it happens to be
    standing. check-domain.py can afford it because it demands a readable manifest one
    line later and exits 2 anyway; here the glob would simply come back empty and
    report success. Exit 2 means "the checker could not run", which is also what
    distinguishes this from a freshly-onboarded project: that project HAS a manifest
    and legitimately has zero features, and it still exits 0. Zero plans is not an error.
    """
    # THE PROBE IS THE MANIFEST FILE, NEVER `isdir(".harness")`, and that distinction is
    # the only thing standing between this fix and B-7 reappearing: a `.harness/`
    # directory can exist under `$HOME` for reasons that have nothing to do with any
    # project. `$HOME/.harness/` EXISTS on this machine because it holds the 2026-08-10
    # backup archives, so any directory probe still resolves `$HOME` as a project root.
    # Verified on this machine. A reviewer ran the counterfactual: swap the file probe
    # for a directory test and running `check-plan-routes.py` from anywhere under such a
    # `$HOME` prints `0 violation(s) across 0 plan(s)` and exits 0 — the exact defect
    # this function was written to remove.
    #
    # `test-check-plan-routes.py` case (20) pins every copy of this probe to the same
    # filename for that reason. Do not "simplify" it to a directory check.
    # THE RULE ITSELF NOW LIVES IN harness_boundary (FEAT-42 T-13). What stood here was the
    # model implementation the rest of that feature was copied from: the two-name chain, the
    # manifest probe, the announced discard and the refusal. All four are resolve_root's, so
    # the local copy goes and the shared one answers. The reasoning above about WHICH probe
    # is correct stays here because it is the reason MARKER is a file and not a directory.
    #
    # strict=True, and the raise is CAUGHT so the refusal keeps this script's own voice. The
    # discard announcement is resolve_root's and already reaches stderr, so it is not
    # restated here — two lines saying the same thing is how one of them goes stale.
    derived = harness_boundary.root_from_script(BIN_DIR)
    try:
        root = harness_boundary.resolve_root(BIN_DIR)
    except ValueError:
        print(
            "check-plan-routes: no readable .harness/team-config.yaml under the override "
            f"or {derived} — I do not know where to look, so 'no plans' would be a "
            "lie. Point the override at a harness checkout, or pass PLAN.md paths "
            "explicitly.",
            file=sys.stderr,
        )
        sys.exit(2)
    # ONE WALK, AND THE PATHS COME OUT OF IT. `glob.glob` swallows OSError, so a directory
    # it cannot enter is indistinguishable from one holding no PLAN.md — measured with NO
    # code change at all, `chmod 000` on the four dirs carrying all 36 violations gave
    # `0 violation(s) across 4 plan(s)`, exit 0, and a clean `git status`, because git does
    # not track directory modes.
    #
    # The first fix scanned for readability and THEN globbed separately. Review showed that
    # leaves a window between the two walks: with a 2 s sleep injected, a `chmod 000` in
    # the gap produced `0 violation(s) across 1 plan(s)`, exit 0, silent. Deriving the plan
    # list from the same walk that checked it closes the window and drops a whole glob.
    #
    # X_OK, NOT R_OK|X_OK — and the reason is a coupling worth stating rather than a
    # preference. Entering a directory to stat a KNOWN filename needs execute, not read;
    # read is only needed to LIST it. The first fix demanded both and would have exited 2 on
    # a mode-0311 or 0100 directory it could in fact have checked perfectly. That is a
    # denial of service on a script issue #133 wants promoted to a gate. This holds ONLY
    # because the filename below is a literal: switch it to a pattern like `PLAN*.md` and
    # listing becomes necessary again — measured, `PLAN*.md` at 0311 silently loses a
    # feature. If you ever generalise that name, R_OK comes back with it.
    # THE WALK COVERS THE MAIN CORPUS TOO (FEAT-1559). A sparse worktree holds one feature
    # directory, so a walk of `root` alone would route-check that one plan and call it the tree.
    # From a linked worktree the owner root's corpus is walked after this checkout's own, and a
    # `<segment>/<name>` already seen here is not walked again there: the local copy is the live
    # one. The key carries the segment because two segments may hold the same feature name
    # (#2077's fixture does). A broken sparse layout refuses first, exit 2, like every other
    # "I cannot see the tree" case below.
    #
    # THEN THE NAME SET, BEFORE THE WALK. The walk enumerates what is present, so a tracked
    # feature directory missing from the landed corpus would simply not be walked and its plan
    # never checked — a clean total over fewer plans than exist. `require_landed` compares the
    # tracked names against the reached ones and refuses the shortfall by name.
    try:
        _refusal = feature_corpus.layout_refusal(root)
        walk_roots = feature_corpus.corpus_roots(root)
    except feature_corpus.CorpusError as e:
        _refusal = str(e)
    if _refusal:
        print(f"check-plan-routes: {_refusal}", file=sys.stderr)
        sys.exit(2)
    try:
        feature_corpus.require_landed(root)
    except feature_corpus.CorpusError as e:
        print(f"check-plan-routes: {e}. A route audit over fewer plans than exist would report "
              f"clean about the ones it never walked. Restore the directory in that checkout "
              f"(`git checkout -- <path>`), then rerun.", file=sys.stderr)
        sys.exit(2)
    plans, unreadable = [], []
    # TWO COUNTS, BECAUSE ONE CANNOT TELL THE TWO ZEROES APART. `0 plan(s)` used to mean
    # either "discovery is broken" or "every feature has shipped", and the CI gate had to
    # guess — it guessed "broken" and failed a healthy tree the day the last feature went
    # Done (2026-08-13, FEAT-18). `examined` counts feature directories the walk entered;
    # `plans` counts what it will check. examined == 0 on a tree that has features is the
    # fail-open issue #133 names. examined > 0 with no plans is an all-shipped tree, which
    # is legitimate and says so.
    examined = 0
    # ONE SEGMENT LEVEL, then features. glob's `*` never matches a leading dot, so the
    # dot-exclusion the comment below demands at the feature level holds at the segment
    # level too, by the same mechanism rather than a second rule.
    seg_dirs = []
    for walk_root in walk_roots:
        feats = os.path.join(walk_root, ".harness", "*", "features")
        # corpus-scope: owner-root
        seg_dirs.extend((walk_root, d) for d in sorted(glob.glob(feats)) if os.path.isdir(d))
    if seg_dirs:
        entries, _seen = [], set()
        for _walk_root, _fd in seg_dirs:
            try:
                _listed = sorted(os.scandir(_fd), key=lambda e: e.path)
            except OSError as e:
                print(f"check-plan-routes: cannot list {_fd}: {e}", file=sys.stderr)
                sys.exit(2)
            for _e in _listed:
                _key = os.path.relpath(_e.path, _walk_root)
                if _key not in _seen:
                    _seen.add(_key)
                    entries.append(_e)
        for entry in entries:
            # DOTTED ENTRIES ARE NOT FEATURES, and this restores glob's semantics rather
            # than reinterpreting them. `glob`'s `*` never matched a leading dot; `scandir`
            # returns everything. Measured on a `.FEAT-HIDDEN/PLAN.md` fixture: the old
            # mechanism found 0 plans, the rewrite found 1. The scan line still advertises
            # `features/*/PLAN.md`, so the search must keep meaning what that says.
            if entry.name.startswith("."):
                continue
            try:
                if not entry.is_dir():
                    continue
            except OSError:
                # DirEntry.is_dir() RAISES rather than swallowing — a symlink to an
                # unreachable target lands here, and silently skipping it would be the
                # same lie as the glob told.
                unreadable.append(os.path.relpath(entry.path, root))
                continue
            if not os.access(entry.path, os.X_OK):
                unreadable.append(os.path.relpath(entry.path, root))
                continue
            # BOTH FILENAMES, plan.yaml first. DEC-182 replaced the markdown-that-looks-
            # like-YAML format; shipped features keep their PLAN.md and its reader is
            # PERMANENT, not deprecated — the eight already on disk are never rewritten.
            # A feature carrying both is a half-finished migration and is refused below
            # rather than silently preferred, because "which one is authoritative" is
            # exactly the ambiguity issue #147 was filed about.
            # SHIPPED FEATURES ARE NOT ROUTE-CHECKED, and this is a removal rather than a
            # trade-off. Checking them was the default behaviour of a glob, never a
            # decision: the work shipped, the routes were taken, and the plan will not be
            # re-executed, so a finding on it is not actionable by anyone. Measured before
            # this line: 36 violations across 8 plans, of which 27 were `no files: line`
            # and 8 the pre-FEAT-06 prose shape, and 1 real routing defect. 35 of the 36
            # were format noise in SHIPPED plans; the one real finding is in FEAT-08, which
            # is awaiting_user and stays checked.
            #
            # That noise is the whole reason issue #133's gate could never be turned on:
            # /harness entry would have failed every time with 35 findings nobody intended
            # to fix. Skipping them takes the tree to 1 finding, on live work.
            #
            # `status:` is a BORROWED SIGNAL and the honest name for it is era. It means
            # "how far along is this feature", not "which format does it use". It is the
            # only marker on disk — no feature.json carries schema_version — so it is used
            # deliberately rather than a new field being invented for one transition.
            # COUNTED HERE, ABOVE THE SHIPPED SKIP AND BELOW THE READABILITY GUARDS: a
            # directory this walk could not enter is NOT examined, so it must not inflate
            # the number that proves discovery worked.
            examined += 1
            if _is_shipped(entry.path):
                continue
            plan = None
            both = [os.path.join(entry.path, n) for n in ("plan.yaml", "PLAN.md")]
            present = [q for q in both if os.path.lexists(q)]
            if len(present) > 1:
                unreadable.append(
                    f"{os.path.relpath(entry.path, root)} has BOTH plan.yaml and PLAN.md")
                continue
            plan = present[0] if present else both[1]
            # LEXISTS DECIDES PRESENCE, isfile DECIDES USABILITY, and conflating them was a
            # REGRESSION this rewrite introduced against the glob it replaced. `glob`
            # resolved the literal trailing component with `lexists`; `os.path.isfile` calls
            # stat and SWALLOWS OSError. Measured against the previous commit on identical
            # fixtures: a `PLAN.md` that is a broken symlink went exit 2 -> exit 0 silent; a
            # `PLAN.md` symlinked into a chmod-000 directory did the same, which also made
            # the os.access check below UNREACHABLE — isfile had already eaten the EACCES.
            # A path literally named PLAN.md that will not resolve is exactly what the error
            # message below calls indistinguishable from nothing.
            if not os.path.lexists(plan):
                continue
            if not os.path.isfile(plan) or not os.access(plan, os.R_OK):
                unreadable.append(os.path.relpath(plan, root))
                continue
            # A PLAN.md present but unreadable used to raise PermissionError out of
            # process_plan with EXIT 1 — the code meaning "violations found" — no summary
            # line, and every later plan unprocessed. Both the direct case (mode 000) and
            # the indirect one (a symlink into an unreadable directory) land above.
            plans.append(plan)
    if unreadable:
        print(f"check-plan-routes: {len(unreadable)} path(s) under .harness/*/features/ cannot "
              f"be read — {', '.join(sorted(unreadable))}. A path I cannot read is "
              f"indistinguishable from one that holds nothing, so reporting a total would "
              f"be a lie about the tree.", file=sys.stderr)
        sys.exit(2)
    return root, sorted(plans), examined


def main(argv):
    _PLAN_LOADS.clear()
    # COUPLED: the Canonical-reader audit step in .github/workflows/tests.yml parses the summary line that canonical_reader_audit._run_canonical_reader_audit prints.
    if argv[1:] in (["--canonical-reader-audit"], ["--consolidation-audit"]):
        try:
            root = harness_boundary.resolve_root(BIN_DIR)
        except ValueError as error:
            print(f"check-plan-routes: {error}", file=sys.stderr)
            sys.exit(2)
        if argv[1] == "--consolidation-audit":
            sys.exit(_run_consolidation_audit(root))
        sys.exit(_run_canonical_reader_audit(root))
    examined = None
    if len(argv) > 1:
        try:
            root = harness_boundary.resolve_root(BIN_DIR)
        except ValueError as error:
            print(f"check-plan-routes: {error}", file=sys.stderr)
            sys.exit(2)
        paths = argv[1:]
    else:
        root, paths, examined = discover_plans()
        print(f"scanning {root}/.harness/*/features/*/{{plan.yaml,PLAN.md}}")

    try:
        manifest_root, deviation = resolution_manifest(root)
    except ValueError as error:
        print(f"check-plan-routes: {error}", file=sys.stderr)
        sys.exit(2)
    print(f"MANIFEST {os.path.join(manifest_root, harness_boundary.MARKER)}")

    findings = []
    total_violations = 0
    if deviation:
        findings.append(deviation)
        total_violations += 1
    processed = 0
    for path in paths:
        count = process_plan(path, findings, root, manifest_root)
        if count is None:
            sys.exit(2)
        total_violations += count
        processed += 1

    for line in findings:
        print(line)
    print(f"{total_violations} violation(s) across {processed} plan(s)")
    if examined is not None:
        print(f"examined {examined} feature dir(s); "
              f"{examined - processed} skipped as shipped")

    sys.exit(1 if total_violations else 0)


if __name__ == "__main__":
    main(sys.argv)
