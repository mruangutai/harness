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
"""
import ast
import glob
import json
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

LEGAL_MAIN_SESSION_TOKEN = "main-session-direct"
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
    import plan_anchors
    try:
        doc = _load_plan_once(path)
    except harness_yaml.YamlParseError as e:
        # Exit 2, not a violation. "The plan does not parse" is the checker being unable to
        # run, not the plan being wrong about routing — the same distinction B-7 turned on.
        print(f"check-plan-routes: {path} does not load: {e}", file=sys.stderr)
        return None

    violations = 0
    _legal = legal_task_statuses()

    # THE FEATURE'S OWN STATION, checked exactly like a task's (FEAT-41 T-04). It is optional:
    # a plan that has not been given a station is not a plan that is wrong about one, and T-07 is
    # what makes this key the station of record. But a value OUTSIDE the vocabulary is a
    # violation here for the same reason it is on a task — the whole feature exists so that one
    # word means one thing in every file that carries it.
    feature_station = doc.get("status")
    if feature_station is not None and (
            not isinstance(feature_station, str)
            or feature_station not in _legal):
        findings.append(
            f"VIOLATION top-level status {feature_station!r} is not one of "
            f"{_legal} (case sensitive)")
        violations += 1

    for t in doc["tasks"]:
        tid = str(t["id"])
        mode = t["execution_mode"]

        budget_lines = 0
        for f in BUDGETED_FIELDS:
            v = t.get(f)
            if isinstance(v, str):
                budget_lines += len(v.splitlines()) or 1
            elif isinstance(v, list):
                budget_lines += len(v)
            elif v is not None:
                budget_lines += 1
        if budget_lines > MACHINE_LINES_PER_TASK:
            findings.append(
                f"VIOLATION {tid}: {budget_lines} machine-field lines — budget is "
                f"{MACHINE_LINES_PER_TASK} per task (DEC-182). Detail that only JUSTIFIES "
                f"the instruction belongs in notes/, not in the contract.")
            violations += 1

        status = t.get("status")
        if status is not None and (
                not isinstance(status, str) or status not in _legal):
            # Not str()-coerced first (DEC-203): a list stringifies to something that
            # happens not to be in the tuple, which gives the right answer for the wrong
            # reason and stops giving it the moment the tuple grows. Case sensitive on
            # purpose, and the case that matters has changed with the vocabulary: the board no
            # longer stores a capitalised name anywhere, so the typo a person will actually make
            # is `pending` — the word this file itself accepted until FEAT-41 T-04 — or a
            # capitalised column name copied off the GitHub board by eye.
            findings.append(
                f"VIOLATION {tid}: status {status!r} is not one of {_legal} "
                f"(case sensitive)")
            violations += 1

        # AN ANCHOR IS RESOLVED BY ITS PATH (FEAT-59 C4). `a.py#foo` and `{path: a.py, quote:
        # ...}` name a place INSIDE a.py; the grant question is about a.py. plan_anchors.py owns
        # the grammar; asking check-domain about `a.py#foo` would answer NOBODY for a granted
        # file, which is the false violation issue #134 already taught this file to fear.
        paths = [plan_anchors.path_of(f) for f in t["files"]]
        globs = [f for f in paths if "*" in f or "?" in f]
        literals = [f for f in paths if f not in globs]
        for g in globs:
            findings.append(f"UNRESOLVED-GLOB {tid} {g}")

        nobody, granted = [], set()
        for entry in literals:
            agents = resolve_agents(entry, root, manifest_root)
            if agents:
                granted.update(agents)
            else:
                nobody.append(entry)

        if nobody:
            if mode == LEGAL_MAIN_SESSION_TOKEN:
                findings.append(
                    f"OK {tid}: declared main-session-direct ({', '.join(nobody)} ungranted)")
            else:
                for path_ in nobody:
                    findings.append(
                        f"VIOLATION {tid}: {path_} ungranted (NOBODY); execution_mode is "
                        f"{mode} — legal tokens: {LEGAL_TOKENS}")
                    violations += 1
        elif literals:
            if mode == LEGAL_MAIN_SESSION_TOKEN:
                findings.append(
                    f"DEVIATION {tid} {', '.join(literals)} granted to "
                    f"{', '.join(sorted(granted))} but declared main-session-direct")
            else:
                findings.append(f"OK {tid} granted to {', '.join(sorted(granted))}")
    return violations


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


# FEAT-64 (SC-05): ONE parse per plan per execution. `_is_shipped` (discovery's shipped-skip
# and the invariant-collision scan) and `process_plan_yaml` (the route check) each called
# `artifact_accessors.load_plan` on the same file, so every live plan was parsed twice and a
# shipped one once more in the collision scan. The outcome of the first load -- the document,
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
    thing to drift: CLAUDE_PROJECT_DIR if it holds a readable manifest, else the root
    DERIVED from this file's location (bin/ is four levels down).

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
    feats = os.path.join(root, ".harness", "*", "features")
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
    seg_dirs = sorted(d for d in glob.glob(feats) if os.path.isdir(d))
    if seg_dirs:
        entries = []
        for _fd in seg_dirs:
            try:
                entries.extend(sorted(os.scandir(_fd), key=lambda e: e.path))
            except OSError as e:
                print(f"check-plan-routes: cannot list {_fd}: {e}", file=sys.stderr)
                sys.exit(2)
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


INV_TOKEN_RE = re.compile(r"\bINV-([0-9]+)\b")

# The EXPLICIT claim. One spelling that works in both files this scans: a bare
# `invariants: 29` or `invariants: [29, 30]` line in `plan.yaml`, and the same line inside
# an HTML comment in `BRIEF.md`, which markdown does not render. A feature may add more
# than one invariant, so the list form is first-class rather than an afterthought.
INV_DECL_RE = re.compile(r"^\s*(?:<!--\s*)?invariants:\s*\[?([0-9,\s]+?)\]?\s*(?:-->)?\s*$",
                         re.M)


def live_invariant_numbers(root):
    """The invariant numbers that ALREADY EXIST, read from the gate script itself.

    Returns a set of ints, or None when the script cannot be read. None is NOT an empty
    set and the caller must not treat it as one: an empty set would make every number in
    every plan look newly claimed and fire on plans that merely cite an existing rule.
    """
    path = os.path.join(root, ".claude", "skills", "harness", "bin", "check-state.py")
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return {int(m) for m in INV_TOKEN_RE.findall(f.read())}
    except OSError:
        return None


def check_invariant_number_collisions(root, findings):
    """TWO UNBUILT FEATURES MUST NOT CLAIM THE SAME `INV-NN`.

    MEASURED 2026-08-23, and this exists because the gap shipped before the check did.
    `FEAT-26-pr-linkage-recorded/plan.yaml` used `INV-28` sixteen times while
    `FEAT-34-worktree-act3-enforced/BRIEF.md` used it eight times. Both features were
    unbuilt, one was signed and entering its build, and NOTHING saw it — not
    `check-state.py`, not this checker, not two review rounds on either feature. A human
    reading a task list found it.

    The rule given to the planner at the time was "do not infer the next free number from
    the highest in the file." True, and HALF A CHECK: it names the gate script and says
    nothing about the signed-but-unbuilt plans of other in-flight features. A number is
    free only when BOTH halves agree, and only one half was ever mechanised.

    THE FEATURE DIRECTORY IS THE UNIT, NOT THE PLAN. FEAT-34 had a BRIEF and no
    `plan.yaml` at all, so a plan-only scan reproduces the exact miss. Both files are read
    where they exist.

    A NUMBER ALREADY IN `check-state.py` IS A REFERENCE, NOT A CLAIM. Plans discuss
    existing invariants constantly; firing on those would make this unreadable within a
    week. Only numbers absent from the gate script are treated as claims.

    SHIPPED FEATURES DO NOT PARTICIPATE. Their plan is a record. A live feature reusing a
    spent number is a real but different problem, and conflating the two would report the
    wrong pair of features.

    A GATE SCRIPT THAT CANNOT BE READ SUPPRESSES THE CHECK AND SAYS SO. Silence here would
    be the same fail-open shape the check exists to catch.
    """
    live = live_invariant_numbers(root)
    if live is None:
        findings.append("NOTE invariant-collision check SKIPPED — "
                        ".agents/skills/harness/bin/check-state.py could not be read, so "
                        "a claimed number cannot be told from a cited one.")
        return 0

    claims = {}
    for fdir in sorted(glob.glob(os.path.join(root, ".harness", "*", "features", "*"))):
        if not os.path.isdir(fdir) or _is_shipped(fdir):
            continue
        name = os.path.basename(fdir)
        declared, inferred = set(), set()
        for fname in ("BRIEF.md", "plan.yaml"):
            fpath = os.path.join(fdir, fname)
            try:
                with open(fpath, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            for m in INV_DECL_RE.finditer(text):
                declared |= {int(n) for n in re.findall(r"[0-9]+", m.group(1))}
            inferred |= {int(m) for m in INV_TOKEN_RE.findall(text)} - live
        # A DECLARATION WINS AND PROSE IS ONLY THE FALLBACK, because a feature that
        # resolves a collision must be able to SAY SO. FEAT-34 documented, correctly, that
        # it moved to INV-29 "not INV-28, because FEAT-26 holds it and builds first" — and
        # the prose scan read those three citations as a claim and reported a collision
        # that no longer existed. Punishing a feature for recording its own reasoning is
        # the wrong incentive, and the check would have been switched off within a week.
        #
        # THE DECLARATION IS NOT AN ESCAPE HATCH. Two features declaring the same number
        # still collide, which case_26g asserts with NEITHER brief writing the token in
        # prose — so only the declaration path can catch that pair.
        for num in (declared or inferred):
            claims.setdefault(num, set()).add(name)

    count = 0
    for num in sorted(claims):
        owners = sorted(claims[num])
        if len(owners) > 1:
            count += 1
            findings.append(
                f"VIOLATION INV-{num} is claimed by {len(owners)} unbuilt features: "
                f"{', '.join(owners)}. A number is free only when it is absent from "
                f"check-state.py AND unclaimed by every signed-but-unbuilt plan. "
                f"Decide which feature builds first; it keeps the number.")
    return count


READER_CALL_CATEGORIES = {
    "json.load": "json_file",
    "json.loads": "json_string",
    "yaml.load": "pyyaml",
    "yaml.safe_load": "pyyaml",
    "harness_yaml.load_file": "harness_yaml_file",
    "harness_yaml.load_str": "harness_yaml_string",
    "harness_yaml.load_plan": "load_plan",
    "factory_config.load_fleet": "load_fleet",
    "harness_yaml.manifest_domains": "manifest_domains",
    "feature_json_write.load_feature_json": "load_feature_json",
}
CANONICAL_ACCESSOR_NAMES = {
    "load_feature_json", "load_harness_json", "load_plan", "load_fleet",
    "manifest_domains", "load_frontmatter", "load_omp_config",
    "read_hook_payload", "parse_gh_json",
}
LEGAL_READER_EXEMPTIONS = {
    "harness_yaml_primitive",
    "in_memory_validation",
    "canonical_writer_transform",
    "module_internal_format",
    "test_or_migration_corpus",
    "sole_state_yaml_reader",
}
READER_CLASSIFICATION_SCHEMA = "canonical-reader-classification/1"
READER_CLASSIFICATION_REL = os.path.join(
    "tests", "integration", "canonical-reader-classification.json")
READER_CATEGORY_REMEDIES = {
    "json_file": "artifact_accessors.load_harness_json",
    "json_string": "artifact_accessors.parse_gh_json",
    "pyyaml": "artifact_accessors.load_frontmatter",
    "harness_yaml_file": "artifact_accessors.load_plan",
    "harness_yaml_string": "artifact_accessors.load_frontmatter",
    "load_plan": "artifact_accessors.load_plan",
    "load_fleet": "artifact_accessors.load_fleet",
    "manifest_domains": "artifact_accessors.manifest_domains",
    "load_feature_json": "artifact_accessors.load_feature_json",
}
T07_TERMINAL_REMEDIES = {
    ".claude/skills/harness/bin/bash-write-guard.py::<module>::manifest_domains#1":
        "artifact_accessors.manifest_domains",
    ".claude/skills/harness/bin/check-domain.py::<module>::manifest_domains#1":
        "artifact_accessors.manifest_domains",
    ".claude/skills/harness/bin/check-domain.py::domain_check::manifest_domains#1":
        "artifact_accessors.manifest_domains",
    ".claude/skills/harness/bin/check-plan-routes.py::process_plan_yaml::load_plan#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/check-plan-routes.py::_task_files::load_plan#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/check-state.py::<module>::load_plan#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/factory_config.py::load_fleet::harness_yaml_file#1":
        "artifact_accessors.load_fleet",
    ".claude/skills/harness/bin/post-merge-sweep.py::_repo_arg_for_segment::load_fleet#1":
        "artifact_accessors.load_fleet",
    ".claude/skills/harness/bin/feature_json_write.py::load_feature_json::json_string#1":
        "artifact_accessors.load_feature_json",
    ".claude/skills/harness/bin/harness_yaml.py::load_plan::harness_yaml_file#1":
        "artifact_accessors.load_plan",
    ".claude/skills/harness/bin/harness_yaml.py::manifest_domains::harness_yaml_file#1":
        "artifact_accessors.manifest_domains",
}
T07_RELOCATED_IMPLEMENTATIONS = {
    ".claude/skills/harness/bin/factory_config.py::load_fleet::harness_yaml_file#1":
        ("load_fleet", "harness_yaml_file", "harness_yaml.load_file"),
    # FEAT-61 T-01: the one json.loads behind every strict reader now lives in
    # artifact_accessors.strict_json_loads; feature.json's canonical read decodes through it.
    ".claude/skills/harness/bin/feature_json_write.py::load_feature_json::json_string#1":
        ("strict_json_loads", "json_string", "json.loads"),
    ".claude/skills/harness/bin/harness_yaml.py::load_plan::harness_yaml_file#1":
        ("load_plan", "harness_yaml_file", "harness_yaml.load_file"),
    ".claude/skills/harness/bin/harness_yaml.py::manifest_domains::harness_yaml_file#1":
        ("manifest_domains", "harness_yaml_file", "harness_yaml.load_file"),
}


def _qualified_name(node, aliases):
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value, aliases)
        if parent:
            return f"{parent}.{node.attr}"
    return None


class _ReaderAliasCollector(ast.NodeVisitor):
    def __init__(self):
        self.aliases = {}

    def visit_Import(self, node):
        for item in node.names:
            self.aliases[item.asname or item.name.split(".")[0]] = item.name

    def visit_ImportFrom(self, node):
        if not node.module:
            return
        for item in node.names:
            if item.name == "*":
                continue
            self.aliases[item.asname or item.name] = f"{node.module}.{item.name}"

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            resolved = _qualified_name(node.value, self.aliases)
            if resolved:
                self.aliases[node.targets[0].id] = resolved
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name) and node.value is not None:
            resolved = _qualified_name(node.value, self.aliases)
            if resolved:
                self.aliases[node.target.id] = resolved
        self.generic_visit(node)


def _normalized_reader_name(qualified, file):
    if (
            file.endswith("/harness_yaml.py")
            and qualified in {"load_file", "load_str"}):
        return f"harness_yaml.{qualified}"
    return qualified


def _reader_category(qualified, file):
    qualified = _normalized_reader_name(qualified, file)
    category = READER_CALL_CATEGORIES.get(qualified)
    if category:
        return category
    if not qualified:
        return None
    name = qualified.rsplit(".", 1)[-1]
    if (
            qualified.startswith("artifact_accessors.")
            and name in CANONICAL_ACCESSOR_NAMES):
        return name
    return qualified if qualified in CANONICAL_ACCESSOR_NAMES else None


class _ReaderCallCollector(ast.NodeVisitor):
    def __init__(self, aliases, file):
        self.aliases = aliases
        self.file = file
        self.symbols = []
        self.calls = []

    def _visit_symbol(self, node):
        self.symbols.append(node.name)
        self.generic_visit(node)
        self.symbols.pop()

    visit_ClassDef = _visit_symbol
    visit_FunctionDef = _visit_symbol
    visit_AsyncFunctionDef = _visit_symbol

    def visit_Call(self, node):
        qualified = _qualified_name(node.func, self.aliases)
        category = _reader_category(qualified, self.file)
        if category:
            self.calls.append({
                "file": self.file,
                "symbol": ".".join(self.symbols) or "<module>",
                "callee": qualified,
                "category": category,
                "line": node.lineno,
                "column": node.col_offset,
            })
        self.generic_visit(node)


def reader_candidates_from_source(source, file):
    tree = ast.parse(source, filename=file)
    aliases = _ReaderAliasCollector()
    aliases.visit(tree)
    collector = _ReaderCallCollector(aliases.aliases, file)
    collector.visit(tree)
    ordinals = {}
    for call in sorted(collector.calls, key=lambda item: (item["line"], item["column"])):
        key = (call["symbol"], call["category"])
        ordinals[key] = ordinals.get(key, 0) + 1
        call["id"] = (
            f"{file}::{call['symbol']}::{call['category']}#{ordinals[key]}")
    return collector.calls


def _reader_source_paths(root):
    bin_root = os.path.join(root, ".claude", "skills", "harness", "bin")
    prefix = os.path.join(".claude", "skills", "harness", "bin")
    paths = []
    for current, dirs, files in os.walk(bin_root):
        dirs[:] = sorted(name for name in dirs if name != "__pycache__")
        for name in sorted(files):
            if name.endswith(".py"):
                absolute = os.path.join(current, name)
                relative = os.path.relpath(absolute, bin_root)
                paths.append((absolute, os.path.join(prefix, relative)))
    return paths


def _scan_reader_tree(root):
    candidates, scanned, findings = [], [], []
    for absolute, relative in _reader_source_paths(root):
        scanned.append(relative)
        try:
            with open(absolute, encoding="utf-8") as source:
                candidates.extend(reader_candidates_from_source(source.read(), relative))
        except (OSError, UnicodeDecodeError, SyntaxError) as error:
            findings.append(
                f"{relative}::<module> source_parse remedy=repair source: {error}. "
                "PLAN AMENDMENT REQUIRED")
    return candidates, scanned, findings


def _row_lookup(rows):
    lookup, findings = {}, []
    for row in rows:
        row_id = row.get("id") if isinstance(row, dict) else None
        if not row_id:
            findings.append("classification row has no id. PLAN AMENDMENT REQUIRED")
        elif row_id in lookup:
            findings.append(
                f"duplicate classification row {row_id}. PLAN AMENDMENT REQUIRED")
        else:
            lookup[row_id] = row
    return lookup, findings




def _exemption_finding(row):
    exemption = row.get("exemption")
    if exemption not in LEGAL_READER_EXEMPTIONS:
        return (
            f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            f"remedy={row.get('remedy', 'unknown')}: illegal exemption "
            f"{exemption!r}. PLAN AMENDMENT REQUIRED")
    if not str(row.get("reason", "")).strip():
        return (
            f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            "remedy=none: exemption requires a reason. PLAN AMENDMENT REQUIRED")
    return None


def _route_finding(row, task_files):
    route = row.get("execution_route")
    category = row.get("dec174_category")
    if category != "none" and route != LEGAL_MAIN_SESSION_TOKEN:
        return (
            f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            f"remedy={row.get('remedy')}: DEC-174 category {category!r} requires "
            "main-session-direct. PLAN AMENDMENT REQUIRED")
    task = row.get("task")
    if task and task != "none" and row.get("file") not in task_files.get(task, ()):
        return (
            f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            f"remedy={row.get('remedy')}: {task} task files omit this source. "
            "PLAN AMENDMENT REQUIRED")
    return None


def _classification_shape_findings(document, scanned_files):
    findings = []
    if document.get("schema") != READER_CLASSIFICATION_SCHEMA:
        findings.append(
            f"classification schema must be {READER_CLASSIFICATION_SCHEMA}. "
            "PLAN AMENDMENT REQUIRED")
    if document.get("scanned_files") != scanned_files:
        findings.append(
            "scanned-file manifest differs from the live Python tree. "
            "PLAN AMENDMENT REQUIRED")
    rows = document.get("rows")
    if not isinstance(rows, list):
        findings.append(
            "classification rows must be a list. PLAN AMENDMENT REQUIRED")
        return findings, None
    return findings, rows




def _state_reader_findings(rows):
    state_readers = [
        row for row in rows
        if isinstance(row, dict)
        and row.get("artifact") == "state.yaml"
        and row.get("exemption") == "sole_state_yaml_reader"
    ]
    if len(state_readers) <= 1:
        return []
    return [
        "second state.yaml reader found; add a canonical accessor. "
        "PLAN AMENDMENT REQUIRED"
    ]


def reader_classification_findings(candidates, scanned_files, document, task_files):
    findings, rows = _classification_shape_findings(document, scanned_files)
    if rows is None:
        return findings
    _lookup, duplicate_findings = _row_lookup(rows)
    findings.extend(duplicate_findings)
    live = {candidate["id"]: candidate for candidate in candidates}
    findings.extend(_unaccounted_candidate_findings(candidates, rows))
    findings.extend(_classified_rows_findings(rows, task_files, live, candidates))
    findings.extend(_state_reader_findings(rows))
    return findings


def _classification_document(path):
    try:
        with open(path, encoding="utf-8") as source:
            document = json.load(source)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return None, [f"{path}: classification cannot be read: {error}"]
    if not isinstance(document, dict):
        return None, [f"{path}: classification must be a JSON object"]
    return document, []


def _expanded_task_paths(root, path):
    if not glob.has_magic(path):
        return [path]
    return [
        os.path.relpath(match, root)
        for match in sorted(glob.glob(os.path.join(root, path)))
    ]


def _task_files(root, plan_relative):
    plan = artifact_accessors.load_plan(os.path.join(root, plan_relative))
    task_files = {}
    for task in plan["tasks"]:
        paths = []
        for entry in task.get("files", []):
            path = str(entry.get("path") if isinstance(entry, dict) else entry).split("#", 1)[0]
            paths.extend(_expanded_task_paths(root, path))
        task_files[str(task["id"])] = paths
    return task_files


_CLASSIFICATION_REMEDY_OVERRIDES = {
    # Signed T-02/T-03 amendments made the concrete public accessors explicit after T-01
    # captured broader route labels. These overrides remain part of the permanent audit.
    ".claude/skills/harness/bin/factory_config.py::product_config::json_string#1":
        "artifact_accessors.load_harness_json",
    ".claude/skills/harness/bin/upgrade-config.py::load_json::json_file#1":
        "artifact_accessors.load_harness_json",
}


def _row_remedy(row):
    return _CLASSIFICATION_REMEDY_OVERRIDES.get(
        row.get("id"), row.get("remedy"))


def _candidate_matches_canonical_row(candidate, row, remedy):
    return (
        candidate.get("file") == row.get("file")
        and candidate.get("symbol") == row.get("symbol")
        and candidate.get("callee") == remedy
    )


def _candidate_matches_relocated(candidate, relocated):
    symbol, category, callee = relocated
    return (
        candidate.get("file") == ".claude/skills/harness/bin/artifact_accessors.py"
        and candidate.get("symbol") == symbol
        and candidate.get("category") == category
        and candidate.get("callee") == callee
    )


def _row_is_canonical(row, candidates):
    relocated = T07_RELOCATED_IMPLEMENTATIONS.get(row.get("id"))
    if relocated is not None:
        return any(
            _candidate_matches_relocated(candidate, relocated)
            for candidate in candidates
        )
    remedy = _row_remedy(row)
    return any(
        _candidate_matches_canonical_row(candidate, row, remedy)
        for candidate in candidates
    )


def _migration_row_state(row, live, candidates):
    if _row_is_canonical(row, candidates):
        return "canonical"
    if row.get("id") in live:
        return "raw"
    return "missing"



def _candidate_matches_remedy(candidate, row):
    return (
        candidate.get("file") == row.get("file")
        and candidate.get("symbol") == row.get("symbol")
        and candidate.get("callee") == _row_remedy(row)
    )


def _candidate_matches_relocated_row(candidate, row):
    relocated = T07_RELOCATED_IMPLEMENTATIONS.get(row.get("id"))
    return (
        relocated is not None
        and _candidate_matches_relocated(candidate, relocated)
    )


def _candidate_is_accounted(candidate, rows):
    identities = {row.get("id") for row in rows if isinstance(row, dict)}
    return (
        candidate.get("id") in identities
        or any(
            _candidate_matches_remedy(candidate, row)
            or _candidate_matches_relocated_row(candidate, row)
            for row in rows if isinstance(row, dict)
        )
    )


def _scanned_manifest_findings(scanned, document):
    expected = set(document.get("scanned_files", []))
    if set(scanned) == expected:
        return []
    return [
        "scanned-file manifest differs from the live Python tree. "
        "PLAN AMENDMENT REQUIRED"
    ]


def _unaccounted_candidate_findings(candidates, rows):
    return [
        f"{candidate['file']}::{candidate['symbol']} "
        f"{candidate['category']} "
        f"remedy={READER_CATEGORY_REMEDIES.get(candidate['category'], 'artifact_accessors')}: "
        "live AST row absent from migration inventory. PLAN AMENDMENT REQUIRED"
        for candidate in candidates
        if not _candidate_is_accounted(candidate, rows)
    ]


def _migration_row_findings(row, live, candidates):
    if _migration_row_state(row, live, candidates) != "missing":
        return []
    return [
        f"{row.get('file')}::{row.get('symbol')} "
        f"{row.get('category')} remedy={_row_remedy(row)}: "
        "artifact row absent from AST and its canonical remedy does not exist. "
        "PLAN AMENDMENT REQUIRED"
    ]


def _unmigrated_row_findings(row, live, candidates):
    same_site = [
        candidate for candidate in candidates
        if candidate.get("file") == row.get("file")
        and candidate.get("symbol") == row.get("symbol")
        and candidate.get("category") == row.get("category")
    ]
    if row.get("id") in live or len(same_site) == 1:
        return []
    return [
        f"{row.get('file')}::{row.get('symbol')} "
        f"{row.get('category')}: artifact row absent from AST. "
        "PLAN AMENDMENT REQUIRED"
    ]


def _classified_disposition_findings(row, live, candidates):
    disposition = row.get("disposition")
    if disposition not in {"canonical", "migrate", "exempt"}:
        return [
            f"{row.get('file')}::{row.get('symbol')} {row.get('category')} "
            f"remedy={row.get('remedy', 'unknown')}: illegal disposition "
            f"{disposition!r}. PLAN AMENDMENT REQUIRED"
        ]
    if disposition == "exempt":
        findings = _unmigrated_row_findings(row, live, candidates)
        exemption = _exemption_finding(row)
        if exemption:
            findings.append(exemption)
        return findings
    state = _migration_row_state(row, live, candidates)
    if disposition == "canonical" and state != "canonical":
        return [
            f"{row.get('id')}: observed state={state}; expected disposition=canonical "
            f"remedy={_row_remedy(row)}. PLAN AMENDMENT REQUIRED"
        ]
    return _migration_row_findings(row, live, candidates)


def _classified_row_finding(row, task_files, live, candidates):
    if not isinstance(row, dict):
        return []
    route = _route_finding(row, task_files)
    route_findings = [route] if route else []
    return route_findings + _classified_disposition_findings(
        row, live, candidates)


def _t07_terminal_observation(row_id, rows, live, candidates):
    matches = [
        row for row in rows
        if isinstance(row, dict) and row.get("id") == row_id
    ]
    if not matches:
        return "missing", None
    if len(matches) != 1:
        return f"duplicate({len(matches)})", matches[0]
    row = matches[0]
    return _migration_row_state(row, live, candidates), row


def _t07_terminal_message(row_id, state, row, expected_remedy):
    observed_task = row.get("task") if row else "<missing>"
    observed_disposition = row.get("disposition") if row else "<missing>"
    observed_remedy = row.get("remedy") if row else "<missing>"
    return (
        f"{row_id}: observed state={state} task={observed_task} "
        f"disposition={observed_disposition} remedy={observed_remedy}; "
        f"expected task=T-07 disposition=canonical remedy={expected_remedy}. "
        "PLAN AMENDMENT REQUIRED"
    )


def _t07_row_matches_contract(state, row, expected_remedy):
    return (
        state == "canonical"
        and row is not None
        and row.get("task") == "T-07"
        and row.get("disposition") == "canonical"
        and row.get("remedy") == expected_remedy
    )


def _t07_expected_finding(row_id, expected_remedy, rows, live, candidates):
    state, row = _t07_terminal_observation(
        row_id, rows, live, candidates)
    if _t07_row_matches_contract(state, row, expected_remedy):
        return None
    return _t07_terminal_message(row_id, state, row, expected_remedy)


def _t07_extra_findings(rows, live, candidates):
    findings = []
    for row in rows:
        if not isinstance(row, dict) or row.get("task") != "T-07":
            continue
        if row.get("id") in T07_TERMINAL_REMEDIES:
            continue
        state = _migration_row_state(row, live, candidates)
        findings.append(_t07_terminal_message(
            row.get("id", "<missing id>"), state, row,
            "<no additional T-07 row>"))
    return findings


def _t07_terminal_findings(rows, candidates):
    live = {candidate["id"]: candidate for candidate in candidates}
    expected = [
        _t07_expected_finding(
            row_id, expected_remedy, rows, live, candidates)
        for row_id, expected_remedy in T07_TERMINAL_REMEDIES.items()
    ]
    return (
        [finding for finding in expected if finding]
        + _t07_extra_findings(rows, live, candidates)
    )


def _selected_migration_rows(rows, task_id):
    return [
        row for row in rows
        if isinstance(row, dict) and row.get("task") == task_id
        and row.get("disposition") in {"migrate", "canonical"}
    ]


def _task_migration_findings(rows, task_id, live, candidates):
    selected = _selected_migration_rows(rows, task_id)
    if not selected:
        return [f"{task_id}: classification has no assigned rows"]
    states = {
        _migration_row_state(row, live, candidates) for row in selected
    }
    if (
        states == {"canonical"}
        and all(row.get("disposition") == "canonical" for row in selected)
    ):
        return []
    return [
        f"{task_id}: migration unit is not terminally canonical "
        f"({', '.join(sorted(states))}). PLAN AMENDMENT REQUIRED"
    ]


def _classified_rows_findings(rows, task_files, live, candidates):
    findings = []
    for row in rows:
        findings.extend(
            _classified_row_finding(row, task_files, live, candidates))
    return findings


def _classification_structure(root, document, scanned, rows):
    task_files, task_findings = _classification_task_files(root, document)
    _lookup, duplicate_findings = _row_lookup(rows)
    findings = (
        _scanned_manifest_findings(scanned, document)
        + task_findings
        + duplicate_findings
    )
    return task_files, findings


def _valid_classification_findings(
        root, document, candidates, scanned, rows, task_id):
    task_files, findings = _classification_structure(
        root, document, scanned, rows)
    live = {candidate["id"]: candidate for candidate in candidates}
    findings.extend(_unaccounted_candidate_findings(candidates, rows))
    findings.extend(
        _classified_rows_findings(rows, task_files, live, candidates))
    if task_id == "T-07":
        findings.extend(_t07_terminal_findings(rows, candidates))
    else:
        findings.extend(
            _task_migration_findings(
                rows, task_id, live, candidates))
    return findings


def classification_task_findings(root, classification_path, task_id):
    """Validate one signed migration unit without mistaking expected cutovers for drift."""
    candidates, scanned, scan_findings = _scan_reader_tree(root)
    document, document_findings = _classification_document(classification_path)
    findings = scan_findings + document_findings
    if document is None:
        return findings
    rows = document.get("rows")
    if not isinstance(rows, list):
        return findings + ["classification rows must be a list"]
    return findings + _valid_classification_findings(
        root, document, candidates, scanned, rows, task_id)


def _audit_result(scanned, candidates, findings, violations):
    exit_code = 2 if findings else (1 if violations else 0)
    return {
        "exit_code": exit_code,
        "unresolved": len(violations),
        "scanned_files": scanned,
        "candidates": candidates,
        "classification_findings": findings,
        "violations": violations,
    }


def _classification_task_files(root, document):
    try:
        return _task_files(root, document.get("plan", "")), []
    except (OSError, ValueError, KeyError, TypeError) as error:
        finding = f"{document.get('plan')}: plan cannot be read: {error}"
        return {}, [finding]


def _migration_violations(rows):
    return [
        f"{row['file']}::{row['symbol']} {row['category']} "
        f"artifact={row['artifact']} remedy={row['remedy']} task={row['task']} "
        f"route={row['execution_route']}"
        for row in rows
        if isinstance(row, dict) and row.get("disposition") == "migrate"
    ]


def audit_canonical_readers(root, classification_path=None):
    classification_path = classification_path or os.path.join(
        root, READER_CLASSIFICATION_REL)
    candidates, scanned, scan_findings = _scan_reader_tree(root)
    document, document_findings = _classification_document(classification_path)
    if document is None:
        return _audit_result(
            scanned, candidates, scan_findings + document_findings, [])
    task_files, task_findings = _classification_task_files(root, document)
    findings = scan_findings + document_findings + task_findings
    findings.extend(
        reader_classification_findings(candidates, scanned, document, task_files))
    return _audit_result(
        scanned, candidates, findings,
        _migration_violations(document.get("rows", [])))


def _run_canonical_reader_audit(root):
    result = audit_canonical_readers(root)
    for finding in result["classification_findings"]:
        print(f"CLASSIFICATION {finding}")
    for violation in result["violations"]:
        print(f"VIOLATION {violation}")
    print(
        f"{result['unresolved']} unresolved reader site(s) across "
        f"{len(result['scanned_files'])} Python file(s)")
    return result["exit_code"]


# ---------------------------------------------------------------------------------------------
# FEAT-61 T-05: THE TWO CONSOLIDATION LOCKS (D-08). Exactly two, by decision — not a generic
# duplicate detector and not a dead-symbol sweep. Each names the one reintroduction path the
# wave closed and would otherwise reopen silently:
#
#   1. A feature-station literal outside factory_config.py. The station table is the one place
#      a lifecycle bucket is spelled; a call site that writes `("plan", "ready", "building",
#      "review")` or `("done",) + TERMINAL_STATIONS` again is the seventh-station-in-nine-of-ten
#      defect this wave removed. BY BUCKET AND CONTEXT, NOT BY WORD. A literal collection is a
#      respelling when it is USED AS A PREDICATE — the target of an `in`/`not in` test, a
#      returned or assigned value — and its names all fall inside ONE lifecycle bucket
#      (ACTIVE_STATIONS or FINISHED_STATIONS), two or more of them. Subset, not equality
#      (validate c1, CR-01): a copied bucket that has ALREADY drifted — `("plan", "ready",
#      "building")` missing `review` — is the most realistic recurrence, and an exact-set check
#      waves it through. plan-merge.py's `_work_started` over {building, review, done} spans
#      both buckets and so matches neither (D-11); a `for` over station keys to derive column
#      names is iteration, not a predicate, and is not flagged. A single name is a station, not
#      a bucket. The `<literal> + <export>` concatenation is flagged wherever it appears.
#   2. A second `spec_from_file_location` under bin/. harness_boundary.load_repo_module owns
#      the registration and failure decisions; a fresh copy re-derives them from scratch.
#
# Tests are not scanned: a test loading its subject by path is that test's own business.
STATION_TABLE_REL = os.path.join(".claude", "skills", "harness", "bin", "factory_config.py")
# FEAT-64: the home symbol is the private body `_load_repo_module`. `load_repo_module` (the
# public entry every caller names) runs that body inside `_as_repo_module_failure`, the ONE
# broad catch the load and call boundaries share -- so the spec call moved one function
# inward while staying the sole one under bin/.
MODULE_LOADER_HOME = (
    os.path.join(".claude", "skills", "harness", "bin", "harness_boundary.py"),
    "_load_repo_module",
)
_STATION_EXPORTS = ("MANDATED_STATIONS", "TERMINAL_STATIONS", "ACTIVE_STATIONS",
                    "FINISHED_STATIONS")


def _unwrap_set_call(node):
    """`set(x)` / `frozenset(x)` → `x`; anything else unchanged."""
    is_set_call = (isinstance(node, ast.Call) and not node.keywords and len(node.args) == 1
                   and isinstance(node.func, ast.Name) and node.func.id in ("set", "frozenset"))
    return node.args[0] if is_set_call else node


def _string_literal_collection(node):
    """The set of strings in a literal tuple/list/set, or `set(...)`/`frozenset(...)` over
    one, or None when the node is anything else (including a collection with a non-string)."""
    node = _unwrap_set_call(node)
    if not isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return None
    if not all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts):
        return None
    return {e.value for e in node.elts}


def _names_station_export(node):
    return (isinstance(node, ast.Attribute) and node.attr in _STATION_EXPORTS) or (
        isinstance(node, ast.Name) and node.id in _STATION_EXPORTS)


def _lifecycle_buckets():
    import factory_config
    return {"ACTIVE_STATIONS": set(factory_config.ACTIVE_STATIONS),
            "FINISHED_STATIONS": set(factory_config.FINISHED_STATIONS)}


def _is_station_concatenation(node):
    """`<string literal> + <STATION export>` in either order — the `("done",) +
    TERMINAL_STATIONS` shape that used to stand in for FINISHED_STATIONS at six sites."""
    if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)):
        return False
    sides = (node.left, node.right)
    return (any(_string_literal_collection(s) for s in sides)
            and any(_names_station_export(s) for s in sides))


_PREDICATE_PARENTS = (ast.Compare, ast.Return, ast.Assign, ast.AnnAssign)


def _respelled_bucket(node, parent, buckets):
    """Which table export a literal node respells, or None: a concatenation anywhere, or a
    literal collection of two or more names inside one bucket, used as a predicate."""
    if _is_station_concatenation(node):
        return "FINISHED_STATIONS by concatenation"
    values = _string_literal_collection(node)
    if not values or len(values) < 2 or not isinstance(parent, _PREDICATE_PARENTS):
        return None
    return next((name for name, bucket in buckets.items() if values <= bucket), None)


def _parents(tree):
    """Child → parent map, with `set(...)`/`frozenset(...)` wrappers looked through so the
    inner tuple sees the Compare/Return the call sits in."""
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    for child, parent in list(parents.items()):
        if _unwrap_set_call(parent) is not parent:
            parents[child] = parents.get(parent)
    return parents


def _feature_station_literal_findings(tree, relative, buckets):
    # Keyed by line so `frozenset(("plan", ...))` — a Call wrapping a Tuple — reports once.
    parents = _parents(tree)
    findings = {}
    for node in ast.walk(tree):
        respelled = _respelled_bucket(node, parents.get(node), buckets)
        if respelled is not None and node.lineno not in findings:
            findings[node.lineno] = (
                f"{relative}::{_call_symbol(tree, node)}:{node.lineno} feature-station literal "
                f"respells factory_config.{respelled} — read the table's export or call "
                "is_active/is_finished (FEAT-61 D-08)")
    return [findings[line] for line in sorted(findings)]


def _callee_name(call):
    func = call.func
    return func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)


def _module_loader_findings(tree, relative):
    home_file, home_symbol = MODULE_LOADER_HOME
    loaders = [
        (node, _call_symbol(tree, node)) for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _callee_name(node) == "spec_from_file_location"
    ]
    return [
        f"{relative}::{symbol}:{node.lineno} second spec_from_file_location under bin/ — "
        "load through harness_boundary.load_repo_module (FEAT-61 D-08)"
        for node, symbol in loaders
        if not (relative == home_file and symbol == home_symbol)
    ]


def _call_symbol(tree, node):
    """The innermost function enclosing `node`, or `<module>`."""
    containers = [
        candidate for candidate in ast.walk(tree)
        if isinstance(candidate, (ast.FunctionDef, ast.AsyncFunctionDef))
        and candidate.lineno <= node.lineno <= candidate.end_lineno
    ]
    if not containers:
        return "<module>"
    return min(containers, key=lambda c: c.end_lineno - c.lineno).name


# ---------------------------------------------------------------------------------------------
# FEAT-62 T-02: THE THREE CHECKER-STRUCTURE LOCKS, plus one invocation-posture scan that is
# deliberately NOT counted as a fourth structural rule. Each names the one way the
# decomposition of check-state.py could grow back:
#
#   1. MODULE BODY. After the trusted bootstrap (everything through `root = sys.argv[1]`), the
#      checker's module body holds imports, definitions, constants and tables, and the guarded
#      main call — never an invariant. A top-level `for`/`while`/`with`/`try` (other than an
#      import guard), an `if` that is not the main guard, or a statement that READS (open, read,
#      glob, subprocess, a canonical accessor) is a block escaping the table. In the same family:
#      a source the runner context parses ONCE (plan.yaml as a mapping; BRIEF.md, STATE.md and
#      PLAN.md as text) is not re-parsed inside an invariant body — `load_plan(...)` or a
#      `read(...)`/`open(...)` naming one of those files there is a second parse of a shared
#      source, which is the drift the context exists to remove.
#   2. READS. Every `Inv` row declares what its function opens (`path:`, `git:`, `gh:`), and
#      that declaration is what `--changed` joins on. A file name the function (or a helper it
#      calls) names in code, a `git` argv it spawns, or a `gh` binary it runs that the row does
#      not declare is a silent hole in selective execution — the run skips the row exactly when
#      that input changed. Message text (f-strings) is not an input and is not scanned.
#   3. AUTHORITY. Every row's `authority` resolves to a live `DEC-NNN` in DECISIONS-INDEX.md and
#      is not STRUCK. DEC-188 says a struck decision is removed from every gate; this is the
#      mechanism — striking a decision reddens every invariant that stood on it until each is
#      re-cited or retired. A decision amended in place under the same number is an accepted,
#      recorded limit.
#
#   POSTURE (not a structural rule): `--changed` is the edit-loop verb and never the gate.
#   No workflow under .github/workflows/ and no hook under .claude/skills/harness/hooks/ may
#   invoke check-state.py with it; CI, command entry and pre-commit run the full table.
BIN_REL = os.path.join(".claude", "skills", "harness", "bin")
CHECKER_REL = os.path.join(BIN_REL, "check-state.py")
DECISIONS_INDEX_REL = os.path.join(".harness", "harness", "docs", "DECISIONS-INDEX.md")
_BOOTSTRAP_END_TARGET = "root"           # the first top-level `root = ...` closes the bootstrap
_READER_CALLEES = {"open", "read", "glob", "iglob", "run", "check_output", "Popen", "listdir",
                   "walk", "load_plan", "load_feature_json", "load_harness_json", "load_fleet",
                   "load_file", "load_repo_module"}
# The runner parses these ONCE into Ctx (plan_docs, record, cj); an invariant that calls the
# loader again has forked the source (FEAT-62 SC-03; feature/harness JSON added by FEAT-63 SC-05,
# which is what let sixteen re-parses sit under a green audit).
_SHARED_SOURCE_LOADERS = {"load_plan", "load_feature_json", "load_harness_json"}
_SHARED_SOURCE_TEXTS = ("BRIEF.md", "STATE.md", "PLAN.md")
_INVARIANT_FN = re.compile(r"^(?:inv_\d+|_inv\d+_\w+|collate_\w+|_collate\d+_\w+)$")
_INPUT_LITERAL = re.compile(r"^[\w.*-]+\.(?:yaml|yml|json|md|py)$")
_READ_KINDS = ("path:", "git:", "gh:")


def _checker_tree(root):
    path = os.path.join(root, CHECKER_REL)
    with open(path, encoding="utf-8") as source:
        return ast.parse(source.read(), filename=CHECKER_REL)


def _bootstrap_end(tree):
    """Line of the first top-level `root = ...`; everything after it is the locked body."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == _BOOTSTRAP_END_TARGET for t in node.targets):
            return node.lineno
    return 0


def _is_main_guard(node):
    test = node.test
    return (isinstance(node, ast.If) and isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name) and test.left.id == "__name__")


def _is_import_guard(node):
    """`try: import x except: x = None` — the one Try shape the body may carry."""
    body_ok = all(isinstance(s, (ast.Import, ast.ImportFrom)) for s in node.body)
    handlers_ok = all(all(isinstance(s, (ast.Assign, ast.Pass)) for s in h.body) for h in node.handlers)
    return isinstance(node, ast.Try) and body_ok and handlers_ok


def _reads_in(node):
    """Callee names in `node` that read the tree — the vocabulary in _READER_CALLEES."""
    return sorted({_callee_name(c) for c in ast.walk(node)
                   if isinstance(c, ast.Call) and _callee_name(c) in _READER_CALLEES})


_BLOCK_KINDS = (ast.For, ast.While, ast.With, ast.AsyncFor, ast.AsyncWith)


def _module_body_shape(node):
    """What is wrong with a top-level statement's SHAPE, or None: a block, a conditional that
    is not the main guard, a try that is not an import guard."""
    if isinstance(node, _BLOCK_KINDS):
        return f"{type(node).__name__.lower()} block at module scope"
    if isinstance(node, ast.If) and not _is_main_guard(node):
        return "conditional at module scope"
    if isinstance(node, ast.Try) and not _is_import_guard(node):
        return "try block at module scope"
    return None


def _module_body_finding(node, relative):
    what = _module_body_shape(node)
    if what is None and isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr)):
        reads = _reads_in(node)
        what = f"reads the tree at module scope ({', '.join(reads)})" if reads else None
    return f"{relative}::<module>:{node.lineno} {what}" if what else None


def _module_body_findings(tree, relative):
    after = _bootstrap_end(tree)
    findings = []
    for node in tree.body:
        if node.lineno <= after:
            continue
        finding = _module_body_finding(node, relative)
        if finding:
            findings.append(finding + " — an invariant lives in a function registered in INVARIANTS (FEAT-62 SC-03)")
    return findings


def _names_shared_text(call):
    return any(isinstance(c, ast.Constant) and isinstance(c.value, str) and c.value in _SHARED_SOURCE_TEXTS
               for c in ast.walk(call))


def _reparsing_calls(fn):
    """(callee, lineno) for every call in `fn` that parses a runner-shared source again."""
    calls = (c for c in ast.walk(fn) if isinstance(c, ast.Call))
    return [(_callee_name(c), c.lineno) for c in calls
            if _callee_name(c) in _SHARED_SOURCE_LOADERS
            or (_callee_name(c) in ("read", "open") and _names_shared_text(c))]


def _reparse_findings(tree, relative):
    """A shared source parsed again inside an invariant body (module-body family)."""
    return [f"{relative}::{fn.name}:{lineno} re-parses a runner-shared source ({callee}) — read it "
            f"from ctx (FEAT-62 SC-03)"
            for fn in _invariant_functions(tree) for callee, lineno in _reparsing_calls(fn)]


def _invariant_functions(tree):
    return [n for n in tree.body if isinstance(n, ast.FunctionDef) and _INVARIANT_FN.match(n.name)]


def _module_functions(tree):
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
        for m in cls.body:
            if isinstance(m, ast.FunctionDef):
                fns[f"{cls.name}.{m.name}"] = m
    return fns


def _is_string_assign(node):
    return (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str))


def _string_constants(tree):
    """Top-level `NAME = "..."` bindings — the `_FEATURE_JSON`-style read aliases."""
    return {t.id: node.value.value
            for node in tree.body if _is_string_assign(node)
            for t in node.targets if isinstance(t, ast.Name)}


def _inv_rows(tree):
    """(name, run function name, reads tuple, authority, lineno) for every Inv(...) in the table."""
    aliases = _string_constants(tree)
    rows = []
    for call in ast.walk(tree):
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "Inv"):
            continue
        name, run, _scope, reads, _contract, authority = call.args
        declared = tuple(aliases.get(e.id) if isinstance(e, ast.Name) else e.value for e in reads.elts)
        rows.append((name.value, run.id, declared, authority.value, call.lineno))
    return rows


def _reachable(fn_name, fns, seen=None):
    """`fn_name` and every check-state function it calls, transitively (module functions by
    name, Ctx methods through `ctx.<method>(...)`)."""
    seen = set() if seen is None else seen
    if fn_name in seen or fn_name not in fns:
        return seen
    seen.add(fn_name)
    for callee in _called_names(fns[fn_name]):
        _reachable(callee, fns, seen)
    return seen


def _called_names(fn):
    """Names `fn` calls that could be check-state functions: bare names, and `ctx.<m>` as
    `Ctx.<m>`."""
    names = []
    for call in (c for c in ast.walk(fn) if isinstance(c, ast.Call)):
        f = call.func
        if isinstance(f, ast.Name):
            names.append(f.id)
        elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "ctx":
            names.append(f"Ctx.{f.attr}")
    return names


# `spawn` is Ctx.spawn, the checker's one process boundary (FEAT-63 T-01): every git/gh read
# now arrives through it, so the lock reads its argv exactly as it read subprocess.run's.
_SPAWN_CALLEES = ("run", "check_output", "Popen", "spawn")
# The one GitHub read check-state.py makes through a module rather than an argv: gh_board's
# board query. Declared on the row as "gh:board".
_BOARD_READ_CALLEE = "board_stations_for"


def _argv_tokens(call):
    """The constant string tokens of a `subprocess.run([...])`-shaped argv, in order; a
    `"literal" % x` token contributes its literal, anything else contributes None so position
    is kept. Empty when the call is not a spawn."""
    if _callee_name(call) not in _SPAWN_CALLEES or not call.args:
        return []
    argv = call.args[0]
    if not isinstance(argv, (ast.List, ast.Tuple)):
        return []
    return [_token_text(e) for e in argv.elts]


def _token_text(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        node = node.left
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and "gh" in node.id.lower():
        return "gh"
    return None


def _git_resource(tokens):
    """`git:<subcommand>` for a git argv; `worktree list` reads as `git:worktree-list`.
    `-C <dir>` is skipped; the first token that is not an option is the subcommand."""
    rest = tokens[1:]
    while rest and rest[0] == "-C":
        rest = rest[2:]
    words = [w for w in rest if w is not None and not w.startswith("-")]
    if not words:
        return "git:"
    return "git:" + ("-".join(words[:2]) if words[0] == "worktree" else words[0])


def _gh_resource(tokens):
    """`gh:<resource>`: the subcommand (`gh auth status` -> gh:auth), or for `gh api` the last
    path segment of the endpoint before its query (`repos/x/milestones?...` -> gh:milestones)."""
    words = [w for w in tokens[1:] if w is not None and not w.startswith("-")]
    if not words:
        return "gh:"
    if words[0] != "api" or len(words) < 2:
        return "gh:" + words[0]
    return "gh:" + words[1].split("?", 1)[0].rstrip("/").rsplit("/", 1)[-1]


def _spawn_resource(call):
    """The `git:<op>` / `gh:<resource>` a call reads, or None: an argv spawn headed by git or a
    gh binary, or the board module's query."""
    if _callee_name(call) == _BOARD_READ_CALLEE:
        return "gh:board"
    tokens = _argv_tokens(call)
    if tokens and tokens[0] == "git":
        return _git_resource(tokens)
    if tokens and tokens[0] == "gh":
        return _gh_resource(tokens)
    return None


def _joined_parts(fn):
    """ids of the constant parts of every f-string in `fn` — message text, not inputs."""
    return {id(v) for node in ast.walk(fn) if isinstance(node, ast.JoinedStr) for v in node.values}


def _input_literals(fn):
    skip = _joined_parts(fn)
    return {n.value for n in ast.walk(fn)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in skip and _INPUT_LITERAL.match(n.value)}


def _observed_inputs(fn):
    """File-name literals (outside f-strings) and git/gh resources read in one function body."""
    resources = {_spawn_resource(n) for n in ast.walk(fn) if isinstance(n, ast.Call)} - {None}
    return _input_literals(fn), resources


def _declared_covers(literal, declared):
    return any(d.startswith("path:") and (d.endswith("/" + literal) or d == "path:" + literal
                                          or os.path.basename(d[5:]) == literal)
               for d in declared)


def _row_inputs(run, fns):
    """Every literal and git/gh resource the row's function and its helpers observe."""
    literals, resources = set(), set()
    for fn_name in sorted(_reachable(run, fns)):
        if fn_name.startswith("Ctx.__init__"):
            continue
        lits, res = _observed_inputs(fns[fn_name])
        literals |= lits
        resources |= res
    return literals, resources


def _row_reads_findings(row, fns, relative):
    name, run, declared, _authority, lineno = row
    findings = [f"{relative}::INVARIANTS:{lineno} {name} declares {d!r}, which is not path:/git:/gh: "
                f"(FEAT-62 SC-04)" for d in declared if not d.startswith(_READ_KINDS)][:1]
    literals, resources = _row_inputs(run, fns)
    findings += [f"{relative}::{run}:{lineno} {name} opens {literal!r} but its row declares no path: read "
                 f"covering it (FEAT-62 SC-04)"
                 for literal in sorted(literals) if not _declared_covers(literal, declared)]
    findings += [f"{relative}::{run}:{lineno} {name} reads {resource} but its row declares no {resource} "
                 f"read (FEAT-62 SC-04)" for resource in sorted(resources) if resource not in declared]
    return findings


def _reads_findings(tree, relative):
    fns = _module_functions(tree)
    return [f for row in _inv_rows(tree) for f in _row_reads_findings(row, fns, relative)]


def _decisions_index(root):
    """{DEC-NNN: struck?} from the index; None when the index cannot be read."""
    path = os.path.join(root, DECISIONS_INDEX_REL)
    try:
        with open(path, encoding="utf-8") as source:
            lines = source.read().splitlines()
    except OSError:
        return None
    entries = {}
    for line in lines:
        m = re.match(r"^- (DEC-\d+) @\S+ \[[^\]]*\] refs:[^:]*:: (.*)$", line)
        if m:
            entries[m.group(1)] = m.group(2).lstrip().startswith("STRUCK")
    return entries


def _authority_findings(tree, relative, root):
    index = _decisions_index(root)
    findings = []
    if index is None:
        return [f"{relative}::INVARIANTS authority audit CANNOT RUN: {DECISIONS_INDEX_REL} is unreadable "
                f"(FEAT-62 SC-05)"]
    for name, _run, _reads, authority, lineno in _inv_rows(tree):
        if authority not in index:
            findings.append(f"{relative}::INVARIANTS:{lineno} {name} cites {authority}, which does not resolve in "
                            f"{DECISIONS_INDEX_REL} — cite the governing decision (FEAT-62 SC-05)")
        elif index[authority]:
            findings.append(f"{relative}::INVARIANTS:{lineno} {name} cites {authority}, which is STRUCK — a struck "
                            f"decision is removed from every gate (DEC-188); re-cite or retire the invariant "
                            f"(FEAT-62 SC-05)")
    return findings


_POSTURE_DIRS = (os.path.join(".github", "workflows"), os.path.join(".claude", "skills", "harness", "hooks"))


def _posture_lines(path):
    """Line numbers in `path` that invoke check-state.py with --changed, or an OSError."""
    try:
        with open(path, encoding="utf-8", errors="replace") as source:
            return [n for n, line in enumerate(source, 1)
                    if "check-state.py" in line and "--changed" in line]
    except OSError as error:
        return error


def _posture_file_findings(rel_dir, name, path):
    lines = _posture_lines(path)
    if isinstance(lines, OSError):
        return [f"{os.path.join(rel_dir, name)} posture scan cannot read it: {lines}"]
    return [f"{os.path.join(rel_dir, name)}:{n} invokes check-state.py --changed — the gate runs the full "
            f"table; --changed is the edit-loop verb only (FEAT-62 SC-06)" for n in lines]


def _posture_files(root):
    for rel_dir in _POSTURE_DIRS:
        directory = os.path.join(root, rel_dir)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                yield rel_dir, name, path


def _posture_findings(root):
    """A workflow or hook that invokes check-state.py with --changed."""
    return [f for rel_dir, name, path in _posture_files(root)
            for f in _posture_file_findings(rel_dir, name, path)]


# --- FEAT-63 T-03 (SC-04, D-03): ONE AST census of broad catches -- handlers typed exactly
# `Exception`, or bare `except:` -- over every Python script under bin/. check-state.py's
# ceiling is zero. Every other script is frozen at the count observed when this lock landed
# (950b2f04 for the legacy set; harness_boundary.py at its post-T-02 count, RepoModuleError's
# load and call boundaries included). Above its own ceiling is one finding naming the file and
# both counts; below is fine (wave 4 burns the allowlist down); allowance never moves between
# files; a script absent from the list has a zero ceiling. Counted from the AST, never from
# source text or comments -- a text grep of this tree once reported 121 where the AST says 118.
#
# FEAT-64 (SC-04): every lib and tool of wave 4 is now ABSENT from the table -- zero by the
# default -- and harness_boundary.py holds at exactly two: `_as_repo_module_failure` (the load
# and call boundary) and `hook_guard` (the hook own-failure idiom, wired by FEAT-65).
#
# FEAT-65 (SC-04): the eleven hooks are gone from the table too. The budget is the two designed
# catches and nothing else; a broad catch anywhere else under bin/ is a finding by default.
BROAD_CATCH_CEILINGS = {
    "harness_boundary.py": 2,
}


def _is_broad_catch(handler):
    return handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id == "Exception")


def _embedded_programs(tree):
    """String constants that parse as Python and carry a try statement: programs the script hands
    to another interpreter (`python3 -I -c`, `python3 -`), whose handlers are as real as its own
    (FEAT-65 c1, CR-01). Prose and docstrings do not parse into a try and are skipped."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str) and "except" in node.value):
            continue
        try:
            inner = ast.parse(node.value)
        except (SyntaxError, ValueError):
            continue
        if any(isinstance(n, ast.Try) for n in ast.walk(inner)):
            yield inner


def _broad_catch_count(path):
    """Broad catches in one script by AST — its own handlers plus those of any executable Python
    it embeds as a string — or None when it does not parse (its own finding)."""
    try:
        with open(path, encoding="utf-8") as stream:
            tree = ast.parse(stream.read())
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None
    trees = [tree, *_embedded_programs(tree)]
    return sum(1 for t in trees for node in ast.walk(t)
               if isinstance(node, ast.ExceptHandler) and _is_broad_catch(node))


def _broad_catch_finding(rel, name, count):
    ceiling = BROAD_CATCH_CEILINGS.get(name, 0)
    if count is None:
        return f"{rel} broad-catch census cannot parse it (FEAT-63 SC-04)"
    if count <= ceiling:
        return None
    return (f"{rel} carries {count} broad catch(es) (`except Exception` or bare `except:`) against "
            f"ceiling {ceiling} — narrow the new one to the boundary's real error class "
            f"(FEAT-63 SC-04)")


def broad_catch_findings(root):
    """The census over every bin/ script, in name order."""
    bin_dir = os.path.join(root, BIN_REL)
    findings = []
    for name in sorted(os.listdir(bin_dir)) if os.path.isdir(bin_dir) else []:
        if not name.endswith(".py"):
            continue
        rel = os.path.join(BIN_REL, name)
        finding = _broad_catch_finding(rel, name, _broad_catch_count(os.path.join(bin_dir, name)))
        if finding:
            findings.append(finding)
    return findings


def feat62_findings(root):
    """The three checker-structure rule families over check-state.py, then the posture scan."""
    relative = CHECKER_REL
    try:
        tree = _checker_tree(root)
    except (OSError, UnicodeDecodeError, SyntaxError) as error:
        return [f"{relative}::<module> source_parse: {error}"]
    findings = _module_body_findings(tree, relative)
    findings.extend(_reparse_findings(tree, relative))
    findings.extend(_reads_findings(tree, relative))
    findings.extend(_authority_findings(tree, relative, root))
    findings.extend(_posture_findings(root))
    findings.extend(broad_catch_findings(root))
    return findings


def consolidation_findings(root):
    """Every FEAT-61 lock violation under bin/, as printable lines; empty on a clean tree."""
    buckets = _lifecycle_buckets()
    findings = []
    for absolute, relative in _reader_source_paths(root):
        try:
            with open(absolute, encoding="utf-8") as source:
                tree = ast.parse(source.read(), filename=relative)
        except (OSError, UnicodeDecodeError, SyntaxError) as error:
            findings.append(f"{relative}::<module> source_parse: {error}")
            continue
        if relative != STATION_TABLE_REL:
            findings.extend(_feature_station_literal_findings(tree, relative, buckets))
        findings.extend(_module_loader_findings(tree, relative))
    findings.extend(feat62_findings(root))
    return findings


def _run_consolidation_audit(root):
    findings = consolidation_findings(root)
    for finding in findings:
        print(f"CONSOLIDATION {finding}")
    print(f"{len(findings)} consolidation finding(s) under bin/")
    return 1 if findings else 0


def main(argv):
    _PLAN_LOADS.clear()
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

    if examined is not None:
        total_violations += check_invariant_number_collisions(root, findings)

    for line in findings:
        print(line)
    print(f"{total_violations} violation(s) across {processed} plan(s)")
    if examined is not None:
        print(f"examined {examined} feature dir(s); "
              f"{examined - processed} skipped as shipped")

    sys.exit(1 if total_violations else 0)


if __name__ == "__main__":
    main(sys.argv)
