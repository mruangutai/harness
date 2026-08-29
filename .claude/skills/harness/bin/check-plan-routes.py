#!/usr/bin/env python3
"""check-plan-routes.py — plan-time route check (D-01).

Answers, while a PLAN.md is still being written, whether every task's `files:`
paths land on an agent granted to write them, or are honestly declared
`execution_mode: main-session-direct`. It is a PLAN-PHASE CLI, not a
PreToolUse hook — see D-01 for why this is a new script rather than a mode of
check-state.sh or an invariant of check-domain.sh.

ROUTING IS NEVER RE-IMPLEMENTED HERE (D-02, SC-08): every path is resolved by
shelling out to `check-domain.sh --resolve <path>` with stdin closed. This
file must never gain its own copy of Python's stdlib pattern matcher, its own
glob-to-regex translator, or a bare prefix comparison — a prefix comparison
on the text before `/**` answers False for a pattern with an earlier
wildcard segment (e.g. `.harness/features/*/runs/*-eng/**`), which is the
exact bug check-domain.sh:190-197 records fixing.

Task blocks are found with the SAME regex check-state.sh uses (D-08), copied
rather than shared because check-state.sh belongs to the in-flight FEAT-08 and
PLAN.md is markdown, not YAML.
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
CHECK_DOMAIN = os.path.join(BIN_DIR, "check-domain.sh")

# Copied from check-state.sh:93-94 (D-08) — a duplicated task-BLOCK parser,
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


def resolve_agents(path, root, manifest_root):
    """Return agents from the same resolver script the live hook invokes."""
    check_domain = CHECK_DOMAIN
    if os.path.realpath(root) != os.path.realpath(manifest_root):
        check_domain = os.path.join(
            manifest_root, ".claude", "skills", "harness", "bin", "check-domain.sh")
    proc = subprocess.run(
        [check_domain, "--resolve", path],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 2:
        sys.stderr.write(proc.stderr)
        sys.exit(2)
    agents = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line == "NOBODY" or re.match(r"^SHARED ", line):
            continue
        agents.append(line)
    return sorted(set(agents))


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
    """Return the DEVIATION message when root's manifest differs from the owner's, else None."""
    manifest = os.path.join(owner_root, harness_boundary.MARKER)
    if not os.path.isfile(manifest) or not os.access(manifest, os.R_OK):
        raise ValueError(f"owner manifest is not readable: {manifest}")
    branch_manifest = os.path.join(root, harness_boundary.MARKER)
    if os.path.realpath(branch_manifest) == os.path.realpath(manifest):
        return None
    with open(branch_manifest, "rb") as branch, open(manifest, "rb") as owner:
        if branch.read() == owner.read():
            return None
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
        doc = harness_yaml.load_plan(path)
    except harness_yaml.YamlParseError as e:
        # Exit 2, not a violation. "The plan does not parse" is the checker being unable to
        # run, not the plan being wrong about routing — the same distinction B-7 turned on.
        print(f"check-plan-routes: {path} does not load: {e}", file=sys.stderr)
        return None

    violations = 0
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
                not isinstance(status, str) or status not in LEGAL_TASK_STATUSES):
            # Not str()-coerced first (DEC-192): a list stringifies to something that
            # happens not to be in the tuple, which gives the right answer for the wrong
            # reason and stops giving it the moment the tuple grows. Case sensitive on
            # purpose — "Building" (the board's own spelling, capital B) is the typo a
            # person will actually make, and today it would read as not-done forever.
            findings.append(
                f"VIOLATION {tid}: status {status!r} is not one of {LEGAL_TASK_STATUSES} "
                f"(case sensitive)")
            violations += 1

        globs = [f for f in t["files"] if "*" in f or "?" in f]
        literals = [f for f in t["files"] if f not in globs]
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


# The six board columns collapse to exactly one finished state (D-09/D-10: "shipped" and
# "abandoned" both absorb into Done), so there is exactly one member here. A ONE-ELEMENT
# TUPLE IS CORRECT AND IS NOT A CODE SMELL — the tuple shape is kept over a bare string only
# so a future value could join it without changing the comparison below. Do NOT add
# "shipped" or "abandoned" back as aliases — that would be the old-to-new mapping layer
# D-09 forbids.
# `Abandoned` joins `Done` here: a plan that will never be executed is not actionable,
# which is the same reason shipped plans are skipped. Added 2026-08-14 with the enum.
FINISHED_STATUSES = ("Done", "Abandoned")

# A DIFFERENT VOCABULARY FROM THE ONE ABOVE, deliberately placed beside it so a reader
# sees both and does not conflate them. FINISHED_STATUSES is the board's feature.json
# column set; LEGAL_TASK_STATUSES is plan.yaml's per-TASK status (DEC-192) — a task in
# flight is today indistinguishable from one nobody picked up, because plan.yaml only had
# pending and done. This is the third value, and the set that bounds it.
LEGAL_TASK_STATUSES = ("pending", "building", "done")


def _is_shipped(feature_dir):
    """True when this feature's work is delivered and its plan is a record, not a contract.

    Reads `feature.json`'s `status:` with the real loader. An unreadable or absent
    feature.json means NOT finished — a feature we cannot classify is checked rather than
    skipped, because the failure that matters is a live plan going unexamined, not an old
    one being examined twice.

    EVERY EXIT FROM THIS FUNCTION IS `False` OR A MEMBERSHIP TEST. It never raises, and
    that is the whole point: the first draft put the `return` OUTSIDE its own `try:`, so a
    feature.yaml holding a YAML sequence reached `doc.get` on a list and raised
    AttributeError out of discover_plans(). The process then died with **exit 1 — the code
    that means "violations found"** — after examining nothing, printing no summary, and
    naming no feature. One malformed file anywhere under .harness/features/ silently
    converted the whole checker into a liar.

    That is the same defect this change fixes in passing for check-state.sh (`NameError:
    cj`) and the same one harness_yaml.manifest_domains records as M-02. Three instances,
    one shape: a crash exits 1, and 1 is already spoken for. check-state.sh:160-168 is the
    model — `isinstance(doc, dict)` is checked before anything reads a key off it.
    """
    fy = os.path.join(feature_dir, "feature.json")
    if not os.path.isfile(fy):
        return False
    try:
        import harness_yaml
        doc = harness_yaml.load_file(fy)
    except Exception:
        return False
    # `or {}` is NOT enough here. load_file returns whatever the document is, and a
    # non-empty list is truthy — it would survive `or {}` and then fail on `.get`.
    if not isinstance(doc, dict):
        return False
    # `status: Done  # with a trailing comment` is the live corpus's shape (FEAT-02,
    # FEAT-03, FEAT-04, FEAT-05 all carry one), so take the first whitespace-delimited
    # token. A status that is a list or a mapping stringifies to something that is not in
    # FINISHED_STATUSES, which is the fail-CHECKED direction. D-11 makes this comparison
    # case sensitive — "done" is not "Done" and stays checked.
    token = str(doc.get("status", "")).split()
    return bool(token) and token[0] in FINISHED_STATUSES


def discover_plans():
    """Argv-less discovery: every PLAN.md under the PROJECT ROOT, not under the cwd.

    The glob used to be `.harness/features/*/PLAN.md` relative to the cwd, so running
    this from anywhere but the repo root printed `0 violation(s) across 0 plan(s)` and
    EXITED 0 — a checker that found nothing because it was looking in the wrong place
    was byte-identical to a clean tree (issue #133, B-7). Measured before this fix:
    `cd /tmp && python3 <repo>/.agents/skills/harness/bin/check-plan-routes.py` exited 0.

    Root precedence follows check-domain.sh (`:178-180`, and again at `:276-281` for
    its hook path — two call sites, one rule), because a third derivation is a third
    thing to drift: CLAUDE_PROJECT_DIR if it holds a readable manifest, else the root
    DERIVED from this file's location (bin/ is four levels down).

    ONE BRANCH DIFFERS, DELIBERATELY. check-domain.sh's third branch is
    `root = root or os.getcwd()`; this one is `""` and exits 2. A cwd fallback IS the
    B-7 fail-open — it is how a checker ends up scanning wherever it happens to be
    standing. check-domain.sh can afford it because it demands a readable manifest one
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
    path = os.path.join(root, ".claude", "skills", "harness", "bin", "check-state.sh")
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
    `check-state.sh`, not this checker, not two review rounds on either feature. A human
    reading a task list found it.

    The rule given to the planner at the time was "do not infer the next free number from
    the highest in the file." True, and HALF A CHECK: it names the gate script and says
    nothing about the signed-but-unbuilt plans of other in-flight features. A number is
    free only when BOTH halves agree, and only one half was ever mechanised.

    THE FEATURE DIRECTORY IS THE UNIT, NOT THE PLAN. FEAT-34 had a BRIEF and no
    `plan.yaml` at all, so a plan-only scan reproduces the exact miss. Both files are read
    where they exist.

    A NUMBER ALREADY IN `check-state.sh` IS A REFERENCE, NOT A CLAIM. Plans discuss
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
                        ".agents/skills/harness/bin/check-state.sh could not be read, so "
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
                f"check-state.sh AND unclaimed by every signed-but-unbuilt plan. "
                f"Decide which feature builds first; it keeps the number.")
    return count


def main(argv):
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
