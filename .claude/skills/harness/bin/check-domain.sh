#!/usr/bin/env bash
# PreToolUse hook — block an agent from writing outside its declared domain.
#
# Registered in .claude/settings.json — NOT in agent frontmatter:
#   "PreToolUse": [{ "matcher": "Write|Edit",
#     "hooks": [{ "type": "command",
#       "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh" }] }]
#
# Agent identity comes from `agent_type` in the hook payload, because one global
# registration serves all 16 agents. Agent-frontmatter PreToolUse hooks DO NOT FIRE
# for spawned subagents in this environment (DEC-110, verified three times).
#
# VERIFIED (DEC-100): exit 2 blocks the tool call and stderr reaches the agent.
# Only exit 2 blocks — exit 1 is a NON-blocking error and the write proceeds.
#
# HONEST SCOPE (DEC-85, narrowed by DEC-151): this is a GUARDRAIL, not the
# write-safety mechanism.
#   - It cannot see writes made via Bash. The COMMON bypass shapes (sed -i,
#     perl -pi, tee, redirects, rm/mv/cp) are now denied by the sibling
#     bash-write-guard.sh after a live qa bypass (DEC-151); truly arbitrary
#     shell remains unwinnable and is caught post-hoc, not pre.
#   - Serialization (SPEC 8.5) plus `isolation: worktree` is what actually makes
#     fan-out safe. Do not treat a passing hook as proof of parallel safety.
set -uo pipefail

# `--resolve <path>` — plan-time route resolution (DEC-179). It answers "which agent
# may write this path, or nobody" and is NOT the hook path.
#
# THE STDIN RULE IS THE WHOLE POINT OF THIS BRANCH, and both failure modes were
# measured on the pre-change tree: with stdin an open pipe `payload=$(cat)` blocks
# forever (a plan-time check that looks slow, not broken); with stdin closed it
# reaches the Python body with an empty payload, resolves no agent, and exits 0
# printing NOTHING — a fail-open answer indistinguishable from a clean resolve.
# So this branch must never read stdin: not with a timeout, not non-blockingly,
# not at all.
#
# THE UNSET IN THE ELSE BRANCH IS LOAD-BEARING (VF-1). Mode is selected further down by
# `os.environ.get("HARNESS_RESOLVE_PATH") is not None`, so the variable INHERITED FROM THE
# ENVIRONMENT chose the mode, not argv. Measured before the fix, with payload files:
# harness-documentor writing bin/ exited 2 on a clean env, and 0 with the variable set —
# including set to the EMPTY STRING, because `is not None` accepts it. That is the whole
# guard off: exit 0, no stderr, nothing logged, and an audit afterwards cannot tell
# "permitted" from "disabled". Unset here so the hook path can never be talked out of
# enforcing by its own caller's environment.
#
# On why this is an unset rather than an argv check: the hook is registered in
# settings.json with NO arguments, so argv carries nothing to branch on in a real hook
# invocation. Mode selection is env-driven by design (the bash half exports, the Python
# half reads), and unsetting at the one place the two halves meet is the whole fix.
# An earlier draft of this comment claimed argv-branching would collide with `sys.argv[2]`
# as the agent identity; that is NOT true at the hook path — argv[2] is empty there. The
# claim was corrected rather than left standing, because a wrong reason in a comment is
# what the next person edits against.
#
# `--post` selects the PostToolUse mode (issue #132). The mode travels as an ENVIRONMENT
# VARIABLE and is blanked out of argv, because argv position 2 is the FALLBACK AGENT
# IDENTITY — the real registration is `check-domain.sh --post`, so without this line every
# post invocation of a payload lacking `agent_type` reports its agent as "--post".
#
# STATED HONESTLY, because a mutation test proved the stronger claim false: with the
# blanking removed, every post-mode case still passes. "--post" is not `harness-`-prefixed,
# so `_governed` is False and the ungoverned branch runs — which is the branch that payload
# wanted anyway. The line is therefore DEFENSIVE, not load-bearing: it costs one statement
# and it stops `agent` from holding a value that is not an agent, which becomes a live bug
# the first time anything in the post path reads identity. An earlier version of this
# comment claimed it prevented "a different branch than either real caller"; that was
# wrong, and it is corrected here rather than left for the next reader to edit against.
mode="pre"
if [ "${1:-}" = "--resolve" ]; then
  payload=""
  export HARNESS_RESOLVE_PATH="${2:-}"
else
  unset HARNESS_RESOLVE_PATH
  payload=$(cat)
  if [ "${1:-}" = "--post" ]; then
    mode="post"
    set -- ""
  fi
fi
export HARNESS_HOOK_MODE="$mode"

# Locate the project root WITHOUT depending on cwd. A hook's working directory is
# not guaranteed, and deriving root from pwd made this script fail OPEN whenever it
# ran from anywhere else — silently disabling enforcement rather than reporting it.
# This script lives at <root>/.claude/skills/harness/bin/, so walk up four levels.
# BASH_SOURCE is the one thing only bash can answer, which is why any bash remains.
_self="${BASH_SOURCE[0]:-$0}"
_selfdir="$(cd "$(dirname "$_self")" && pwd)"
_derived="$(cd "$_selfdir/../../../.." && pwd)"

# T-13: ONE interpreter launch, not four. This hook runs on EVERY agent write, and
# four launches cost four Python start-ups per write — measured at 104.7ms for the
# full governed path, of which the interpreter is most. Behaviour is unchanged:
# every early exit, every exit code and every stderr message is identical, and the
# unchanged test suite is the equivalence proof (D-10, REQ-07).
HOOK_PAYLOAD="$payload" PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" \
  python3 - "$_derived" "${1:-}" <<'PY'
import sys, os, re, json

def glob_to_re(pat):
    """Translate a glob to a regex. `**` crosses separators, `*` does not.

    fnmatch cannot do this: its `*` matches `/` too, so `web/*/x` would match
    `web/a/b/x`. And a literal prefix comparison cannot do it either — the bug
    this replaced used str.startswith on the text before `/**`, which silently
    failed for any pattern with a wildcard earlier in the path, e.g.
    `features/*/runs/*-eng/**`. That blocked every lead from its own run dir.
    """
    out, i = [], 0
    while i < len(pat):
        c = pat[i]
        if pat.startswith("**", i):
            out.append(".*"); i += 2
            if pat.startswith("/", i):      # `**/` also matches zero segments
                out.append("/?"); i += 1
        elif c == "*":
            out.append("[^/]*"); i += 1
        elif c == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(c)); i += 1
    return re.compile("^" + "".join(out) + "$")


def matches(path, pat):
    pat = pat.rstrip("/")
    if pat in (".", ""):            # "." means read-anything; never a write grant
        return False
    if pat.endswith("/**"):
        # the directory itself, or anything beneath it
        base = pat[:-3]
        return bool(glob_to_re(base).match(path) or glob_to_re(base + "/**").match(path))
    if glob_to_re(pat).match(path):
        return True
    # a bare dir pattern grants everything under it
    return bool(glob_to_re(pat + "/**").match(path))


# THE CONTROL-PLANE CLASSIFIER (FEAT-15 T-02). Defined at module scope beside
# glob_to_re/matches so the hook path and the --resolve path reach the SAME rule —
# a resolver that granted a base the hook refuses is the build-time discovery
# check-plan-routes.py exists to prevent.
#
# The operator's verbatim four, and the list is CLOSED. `docs/harness/**` is not
# widened to `docs/**` and no fifth entry is added. The accepted risk, signed: a
# future harness-owned path starting with neither `.harness/` nor `.claude/` must be
# added here or it silently becomes a product path. No machinery detects the
# omission — that was ruled out deliberately. This is one more place to remember.
HARNESS_CONTROL_PLANE = [
    "docs/harness/**",
    "docs/PRINCIPLES.md",
    "README.md",
    ".github/**",
]


def is_control_plane_glob(pat):
    """First segment is `.harness` or `.claude`. Used to FILTER GLOBS on the product
    side — a `.harness/expertise/**` grant must not reach a product checkout's own
    `.harness/`."""
    p = pat.lstrip("/")
    if p.startswith("./"):
        p = p[2:]
    return p.split("/", 1)[0] in (".harness", ".claude")


def real(path):
    """Absolute AND symlink-resolved.

    `abspath` alone normalises `..` textually but follows no link, so
    `docs/harness/<link>/agents/x.md` with `<link> -> ../../.claude` stayed inside
    `docs/` for every comparison while the write landed in `.claude/agents/`.
    Reproduced before this fix: through the link exit 0, the same file named directly
    exit 2. The gap predates the two-base rule — `docs/**` matched with no target-side
    test — so this closes a live escape rather than a regression.

    `realpath` resolves the existing prefix of a path that does not exist yet, which is
    the normal case for a Write. Applied to BOTH sides of every comparison: resolving
    only the target would break any checkout reached through a link (`/var` on macOS is
    itself a link to `/private/var`).
    """
    return os.path.realpath(os.path.abspath(path))


def resolve_fleet(root):
    """Resolve the fleet declaration for `root`, returning (workspace_root, bases).

    ONE function called from both the hook path and the --resolve path (FEAT-15 T-04).
    Written twice it would drift, and the two halves disagreeing is precisely the
    build-time discovery check-plan-routes.py exists to prevent: a resolver that grants
    a base the hook refuses lets a plan be signed on a route the build will reject.

    Absent is not unreadable. No file at all means no second base and today's behaviour
    exactly, with nothing imported. A file that will not load exits 2 — the value that
    identifies product paths is the one that failed, so enforcing the readable parts
    would mean classifying paths with the classifier missing.
    """
    fleet_path = os.path.join(root, ".harness", "factory", "fleet.yaml")
    if not os.path.exists(fleet_path):
        return None, [], fleet_path
    try:
        # LAZY, and stderr-muzzled for the import statement ONLY. Measured: under a root
        # holding no docs/harness/SPEC.md, importing factory_config prints a discard
        # notice to stderr — which would reach the agent on every governed write from a
        # fixture root, as noise indistinguishable from a real verdict.
        import io
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()):
            import factory_config
        # The EXPLICIT path, never factory_config.FLEET_PATH: that constant is computed
        # at import time from that module's own root probe (docs/harness/SPEC.md), which
        # is not this hook's probe (.harness/team-config.yaml). Under a fixture root the
        # two disagree and the constant names the live repository.
        fleet = factory_config.load_fleet(fleet_path)
        bases = [real(factory_config.workspace_path(fleet, e["name"]))
                 for e in fleet["repos"]]
        return fleet["workspace_root"], bases, fleet_path
    except Exception as e:
        print("check-domain: BLOCKED — the fleet declaration does not load, so no "
              "product path can be identified.", file=sys.stderr)
        print(f"  {fleet_path}", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        print("  Enforcement is CLOSED rather than partial: the value that identifies "
              "product paths is the one that failed. Fix the file (the main session "
              "owns it — it is in no agent's domain), then retry.", file=sys.stderr)
        sys.exit(2)


def select_base(abs_target, root, workspace_root, workspace_bases, fleet_path):
    """Pick the base a target resolves against, and say how to match in it.

    Returns (base, filter_globs, target_side_test). Shared by the hook path and the
    --resolve path so the two can never disagree. Exits 2 for a target under the
    workspace belonging to no declared repository; returns None for a target in
    neither base, which stays not-a-domain-question.

    Containment is commonpath over abspaths throughout, never a string prefix, so a
    path reached via docs/../src/main.py resolves back inside and lands in the right
    base — and /workspaces/widget-other is not read as inside /workspaces/widget.
    """
    abs_root = real(root)

    def inside(child, parent):
        try:
            return os.path.commonpath([child, parent]) == parent
        except ValueError:      # different drives / unrelated roots
            return False

    if inside(abs_target, abs_root):
        # THE HARNESS BASE. Every glob is applicable — nothing is filtered on the glob
        # side — but a match is accepted only for a control-plane TARGET. That is what
        # stops a src/** grant from reaching this repository's own src/.
        return abs_root, (lambda _g: True), is_control_plane_target
    if workspace_bases and any(inside(abs_target, b) for b in workspace_bases):
        # A PRODUCT BASE. Longest match wins, so a repo checked out beneath another's
        # path resolves against its own base rather than its parent's. Filtering happens
        # on the GLOBS here: a control-plane grant must not reach a product checkout's
        # .harness/ or .claude/. HARNESS_CONTROL_PLANE plays NO part on this side — it is
        # target-side only, and consulting it here would refuse a product checkout's own
        # README.md, the very file its documentor exists to write.
        base = max((b for b in workspace_bases if inside(abs_target, b)), key=len)
        return base, (lambda g: not is_control_plane_glob(g)), (lambda _r: True)
    if workspace_root is not None and inside(abs_target, real(workspace_root)):
        # UNDER THE WORKSPACE, BELONGING TO NO DECLARED REPO. Refused rather than
        # ignored: a checkout there for an unlisted repository is stale or a mistake,
        # and treating it as scratch would reopen the hole for exactly the paths the
        # factory writes to.
        print(f"check-domain: BLOCKED — {abs_target} is under the factory workspace but "
              f"belongs to no repository declared in {fleet_path}.", file=sys.stderr)
        print("  A checkout there for an unlisted repository is stale or a mistake. "
              "Add the repository to `repos` in that file, or remove the directory.",
              file=sys.stderr)
        sys.exit(2)
    return None, None, None


def is_control_plane_target(rel):
    """The TARGET-side test, used only in the harness base.

    Target-keyed, not glob-keyed, and that is load-bearing: team-config.yaml grants
    `docs/**` and holds no `docs/harness/**` entry anywhere, so a glob-keyed
    classifier would have literally nothing to match two of the four named entries
    against. Anchored through the same `matches` idiom, so `README.md` means the
    repository-root readme and never `docs/README.md`, and `.github/**` never matches
    `vendor/.github/x`.
    """
    if is_control_plane_glob(rel):
        return True
    return any(matches(rel, e) for e in HARNESS_CONTROL_PLANE)


# harness_yaml is imported LAZILY, below, after the manifest check — NOT here.
# Ordering is behaviour: the four-launch version reached the DEC-101 "no manifest,
# enforcement OFF" fail-open in BASH, before any interpreter that needed the module.
# Importing at the top made a hook whose module is missing crash with exit 1 before
# it could print that message. Caught by test-check-domain.py's isolated-copy case.
_derived, argv_agent = sys.argv[1:3]

# One parse of the payload, reused by every check below. A failure here is OUR
# problem, not the agent's: fall back to the same empty-payload behaviour the four
# separate launches had, each of which printed "" and let the caller decide.
try:
    d = json.loads(os.environ.get("HOOK_PAYLOAD") or "")
except Exception:
    d = {}

# Agent identity: prefer `agent_type` from the hook payload, fall back to $1.
#
# WHY BOTH: agent-frontmatter PreToolUse hooks DO NOT FIRE for spawned subagents in
# this environment — verified three times with three command forms, zero executions
# (DEC-110). So the hook is registered in settings.json instead, where it does fire,
# and identity has to come from the payload because one global registration serves
# every agent.
agent = (d.get("agent_type") or "") or argv_agent

# --- `--resolve <path>` (DEC-179): plan-time route resolution. Answers WHICH AGENT
# may write a path, so a PLAN task can declare its lane instead of a build phase
# discovering it. Exits BEFORE any payload handling — there is no payload here.
#
# Failure semantics differ from the hook deliberately. The hook fails OPEN on a
# missing manifest (blocking every write in an un-onboarded project is worse than
# not enforcing). A resolver cannot: an unanswerable route silently reported as
# "NOBODY" would put a task in the main-session lane on the strength of a broken
# config. So this path exits 2 and says why.
_resolve_target = os.environ.get("HARNESS_RESOLVE_PATH")
if _resolve_target is not None:
    # Root is derived here rather than reusing the block below, because that block
    # sits AFTER the agent-identity early exits and this path has no agent identity
    # to satisfy — reaching it would mean exiting 0 in silence, which is the exact
    # fail-open this mode exists to remove. Same derivation, same precedence.
    root = os.environ.get("CLAUDE_PROJECT_DIR") or ""
    if not root or not os.access(os.path.join(root, ".harness", "team-config.yaml"), os.R_OK):
        root = _derived if os.access(os.path.join(_derived, ".harness", "team-config.yaml"), os.R_OK) else (root or os.getcwd())
    manifest = os.path.join(root, ".harness", "team-config.yaml")
    if not os.access(manifest, os.R_OK):
        print(f"check-domain: no {manifest} — cannot resolve routes.", file=sys.stderr)
        sys.exit(2)
    import harness_yaml
    try:
        parsed = harness_yaml.load_file(manifest)
    except harness_yaml.DuplicateKeyError as e:
        print(f"check-domain: BLOCKED — the manifest has a duplicate key {e.key!r}.",
              file=sys.stderr)
        print(f"  {manifest}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print("check-domain: BLOCKED — the manifest does not parse, so no domain can be "
              f"resolved: {e}", file=sys.stderr)
        sys.exit(2)

    # THE SAME BASE TREATMENT AS THE HOOK (FEAT-15 T-04, REQ-07). This branch exits
    # before domain_check() and carries its own root derivation and its own manifest
    # load, so T-02's change does not reach it by inheritance. Left alone, the plan
    # checker would keep reporting that a persona owns a base the hook now refuses —
    # exactly the build-time discovery it exists to prevent. Both calls below are the
    # module-scope functions the hook path uses, so the two cannot drift.
    _ws_root, _ws_bases, _fleet_path = resolve_fleet(root)

    _abs = _resolve_target if os.path.isabs(_resolve_target) else os.path.join(root, _resolve_target)
    _abs = real(_abs)
    _base, _glob_filter, _target_test = select_base(
        _abs, root, _ws_root, _ws_bases, _fleet_path)
    if _base is None:
        # Outside both bases — no agent can be named, and NOBODY is the literal answer.
        # Silence here would be the fail-open this branch exists to remove.
        print("NOBODY")
        sys.exit(0)

    # Normalise exactly as the hook does, including the worktree strip — a path given
    # from inside .claude/worktrees/<id>/ must resolve against the checkout the agent
    # is standing in, not against a glob nobody wrote.
    _rel = os.path.relpath(_abs, _base)
    _wt = re.match(r"^\.claude/worktrees/[^/]+/(.+)$", _rel)
    _cands = [_rel] + ([_wt.group(1)] if _wt else [])

    # Every agent carrying a `domain:` list, at EVERY nesting level — members sit
    # under teams[].members[], leads under `leads:`, and harness-orchestrator is a
    # bare top-level key. manifest_domains() already walks all three; this only needs
    # the roster of names to ask it about.
    _names = []
    def _roster(node):
        if isinstance(node, dict):
            if isinstance(node.get("domain"), list) and node.get("name"):
                _names.append(str(node["name"]))
            for v in node.values():
                _roster(v)
        elif isinstance(node, list):
            for i in node:
                _roster(i)
    _roster(parsed)

    _granting = set()
    _shared_hits = []
    for _n in _names:
        _globs, _shared = harness_yaml.manifest_domains(manifest, _n)
        # The SAME two-sided rule the hook applies: filter the globs in the product
        # base, test the target in the harness base. A resolver that skipped either
        # half would name an owner for a path the build refuses.
        if any(matches(c, g) for c in _cands if _target_test(c)
               for g in _globs if _glob_filter(g)):
            _granting.add(_n)
        for g in _shared:
            if not _glob_filter(g):
                continue
            if any(matches(c, g) for c in _cands if _target_test(c)) and g not in _shared_hits:
                _shared_hits.append(g)

    # NOBODY is a LITERAL EMITTED TOKEN, never silence. Empty stdout is the fail-open
    # this branch exists to make impossible: a caller cannot tell "no agent grants
    # this" from "the resolver did not run".
    for _n in sorted(_granting):
        print(_n)
    if not _granting:
        print("NOBODY")
    for g in _shared_hits:
        print(f"SHARED {g}")
    sys.exit(0)

# NO agent identity = the MAIN SESSION, not a subagent. Since DEC-120 the orchestrator
# is a spawned agent and IS governed like any other; this carve-out now protects only
# the main session, which writes little: `## Approval` blocks and the cross-flow log.
# Never govern it — blocking it would make the harness unable to record your decisions.
# Only `harness-*` agents are subject to domains at all.
#
# THIS IS A DOMAIN CARVE-OUT AND NOTHING ELSE. It used to be a bare `sys.exit(0)`, which
# silently took the DEC-150 SHAPE gate below with it — a fourth bypass route issue #132
# does not name, and the one that explains its own evidence: the 226-line feature.yaml
# that ticket records was the MAIN SESSION's. Measured on the pre-change tree, one
# 400-line feature.yaml payload: exit 2 as `harness-orchestrator`, exit 0 with no
# `agent_type`. A context budget is not an authorization question — it binds whoever
# writes the file — so this is a FLAG the domain phase reads, never an exit.
_governed = bool(agent) and agent.startswith("harness-")

# TWO SIGNALS FOR ONE MODE, deliberately. `hook_event_name` comes from the platform;
# `--post` comes from our own registration. Keying on the platform field alone means a
# payload that ever stops carrying it downgrades the post hook to pre-mode SILENTLY —
# `Write` would merely re-check the payload, `Edit` and `Bash` would exit 0, and the
# sweep would vanish with no error anywhere. Keying on the flag alone breaks a
# hand-registration that omits it. Either signal is sufficient; neither is required.
_post = (os.environ.get("HARNESS_HOOK_MODE") == "post"
         or (d.get("hook_event_name") or "") == "PostToolUse")
_tool = d.get("tool_name") or ""

# THE DOMAIN PHASE IS PRE-ONLY. Post-hoc it has nothing to offer and two ways to harm:
# the write already landed, so denying it is noise duplicating a verdict the pre hook
# already gave, and `require_or_bootstrap` below would SPEND the session's single
# bootstrap grant on a check whose answer can no longer change anything. Measured before
# this line existed: a post-mode payload for a path outside the agent's domain exited 2
# with the domain message, after the file was already written.
_domain_phase = _governed and not _post

root = os.environ.get("CLAUDE_PROJECT_DIR") or ""
if not root or not os.access(os.path.join(root, ".harness", "team-config.yaml"), os.R_OK):
    if os.access(os.path.join(_derived, ".harness", "team-config.yaml"), os.R_OK):
        root = _derived
    else:
        root = root or os.getcwd()
manifest = os.path.join(root, ".harness", "team-config.yaml")


ti = d.get("tool_input", {}) or {}
# Write/Edit use file_path; NotebookEdit uses notebook_path.
target = ti.get("file_path") or ti.get("notebook_path") or ""

# EVERY EXIT BELOW IS A DOMAIN VERDICT, so the block is gated on `_governed`. Hoisting
# these to module level is exactly what used to disable the shape gate for the main
# session: each one is correct as an answer to "may this agent write here" and wrong as
# an answer to "may this file look like that", which needs no manifest, no parser and no
# agent identity to decide.
_no_parser = False
_run_domain = _domain_phase
if _domain_phase:
    # No parseable path -> do not block. A hook that blocks on its own parse failure
    # would break every write the moment the payload shape changes. This one stays an
    # EXIT rather than joining the flags below: with no path there is no file to shape-
    # check either, so both phases have nothing to say.
    if not target:
        sys.exit(0)

    # No manifest -> the DOMAIN check fails OPEN, loudly. Blocking every write in a
    # project that has not run /harness-init would be worse than not enforcing.
    #
    # A FLAG, NOT AN EXIT — review finding, and it is this PR's own argument one level
    # down. As an exit it took the SHAPE phase with it, so on a tree with no manifest the
    # same 400-line feature.yaml measured exit 0 as `harness-orchestrator` and exit 2 as
    # the main session: the GOVERNED agent got LESS shape enforcement than the ungoverned
    # one. A missing manifest says nothing about how long a file may be.
    if not os.access(manifest, os.R_OK):
        print(f"check-domain: no {manifest} — enforcement OFF (run /harness-init).",
              file=sys.stderr)
        _run_domain = False

if _run_domain:
    # THE IMPORT SITS UNDER `_run_domain`, NOT UNDER `_domain_phase`, and the difference
    # is a real defect the existing suite caught within a minute. Moved up one level it
    # runs even when the manifest is absent — the exact ordering the comment at the top of
    # this file warns about (`harness_yaml is imported LAZILY, below, after the manifest
    # check`). In the isolated-copy fixture, where the module is deliberately not present,
    # that import raised and the process exited 1 INSTEAD of printing "enforcement OFF"
    # and exiting 0. Exit 1 is non-blocking, so the write proceeded either way; what was
    # lost was DEC-101's deliberate, loud fail-open becoming a silent crash.
    import harness_yaml

    # The RETURN VALUE IS THE DECISION — discarding it makes the whole escape inert.
    # False means "PyYAML is missing and this session's one grant is spent (or no identity
    # resolved)", and only exit 2 blocks (DEC-100), so a bare call would let every write
    # through while the function dutifully printed an install command nobody had to obey.
    # require_or_bootstrap already wrote the reason to stderr; do not restate it.
    if not harness_yaml.require_or_bootstrap(root):
        sys.exit(2)

    # GRANTED, and there is no parser. Stop here — do not fall through into a domain check
    # that cannot be performed. Without this the hook calls manifest_domains anyway and
    # dies with `AttributeError: 'NoneType' object has no attribute 'YAMLError'`, which
    # exits 1; exit 1 is NON-blocking (DEC-100), so the write proceeds and SC-08 looks
    # satisfied while every invocation prints a traceback and enforcement is silently off.
    # Allowing by crash is not allowing. The escape's whole purpose is to let writes
    # through so the machine can be fixed, so allow them deliberately and say nothing more
    # — require_or_bootstrap already printed the install command.
    _no_parser = harness_yaml.yaml is None

else:
    # NO DOMAIN PHASE — the main session, a non-harness agent, post mode, or a governed
    # agent in a project with no manifest. All of them still reach the shape phase, whose
    # state.yaml branch needs a parser but never the BOOTSTRAP GRANT: the grant is a
    # domain escape, spendable once per session, and spending it here would consume the
    # main session's escape on a check that is not the one it exists for. A missing module
    # is absorbed rather than raised, so a shape question is never answered by a crash.
    try:
        import harness_yaml
        _no_parser = harness_yaml.yaml is None
    except Exception:
        _no_parser = True


def domain_check():
    # T-12: the manifest is PARSED, not skimmed. The scanner this replaced matched the
    # literal text `name:`/`path:` line by line, so it never had to close a bracket or
    # resolve a key — which is how one unquoted `#` at team-config.yaml:18 made every
    # key from `orchestrator:` onward unreachable to a real reader while this hook went
    # on enforcing the fragments it still recognised. It reported nothing. A guard that
    # silently sees less than it should is worse than one that stops.
    try:
        globs, shared = harness_yaml.manifest_domains(manifest, agent)
    except harness_yaml.DuplicateKeyError as e:
        # A repeated key in the MANIFEST silently shadows the first (DEC-156's shape,
        # here in the rulebook itself). Which of two conflicting domain lists wins is
        # not something to guess at while holding a write guard.
        print(f"check-domain: BLOCKED — the manifest has a duplicate key {e.key!r}.",
              file=sys.stderr)
        print(f"  {manifest}", file=sys.stderr)
        print("  The second occurrence silently shadows the first, so which domain "
              "applies is ambiguous. Enforcement cannot be trusted until it is fixed.",
              file=sys.stderr)
        sys.exit(2)
    except harness_yaml.YamlParseError as e:
        # FAIL CLOSED, by the user's ruling and DEC-171 am.1's logic. This is NOT the
        # absent-manifest case below, which fails open because an unconfigured project
        # has nothing to enforce: here the project IS configured, the file exists, the
        # hook has no bug, and exactly one action fixes it. No deadlock — the manifest
        # is in no agent's domain and the main session is exempt (`:48`), so the only
        # party who can repair it is the one this guard never governs.
        print("check-domain: BLOCKED — the manifest does not parse, so no domain can be "
              "checked.", file=sys.stderr)
        print(f"  {e.original}", file=sys.stderr)
        print("  Enforcement is CLOSED rather than partial: a rulebook that cannot be "
              "read cannot be half-applied. Fix the file (the main session owns it), "
              "then retry.", file=sys.stderr)
        sys.exit(2)

    # THE FLEET AND THE BASE (FEAT-15 T-01/T-02, REQ-01 through REQ-06). Both steps go
    # through the SAME module-scope functions the --resolve path calls, so the resolver
    # can never grant a base this hook refuses — a plan signed on a route the build
    # rejects is the build-time discovery check-plan-routes.py exists to prevent.
    #
    # Resolution runs for EVERY governed write, whatever the target looks like. A
    # resolution that only ran for paths already shaped like product paths would be
    # deciding the question it exists to answer.
    #
    # The branch this replaced ended in a bare `return`: every path outside the harness
    # root got NO VERDICT. Measured before the change — harness-documentor writing a
    # product repo's src/secrets.py exited 0, harness-code-reviewer (which owns no source
    # path anywhere and holds no Edit tool) writing the same file exited 0, and
    # harness-documentor writing src/main.py INSIDE harness exited 2. The same logical
    # path was blocked in this repo and permitted outside it, silently, with the write
    # landing.
    workspace_root, workspace_bases, fleet_path = resolve_fleet(root)
    _abs_target = real(target)
    base, _glob_filter, target_side_test = select_base(
        _abs_target, root, workspace_root, workspace_bases, fleet_path)
    if base is None:
        # NOT A DOMAIN QUESTION, unchanged. bash-write-guard.sh:211 already said so
        # ("outside repo — not this hook's problem"), and this hook did not: a scratch
        # script at /tmp/x.py was legal via Bash and blocked via Write, so an agent
        # learned to route around a hook whose own message said not to. /tmp,
        # /var/folders and unrelated checkouts keep exactly today's behaviour.
        return
    _abs_root = real(root)
    applicable_globs = [g for g in globs if _glob_filter(g)]
    applicable_shared = [s for s in shared if _glob_filter(s)]

    # Compare base-relative, so an absolute tool path and a relative glob still meet.
    rel = os.path.relpath(_abs_target, base)

    # WORKTREES (DEC-143). A git worktree under .claude/worktrees/<name>/ is a full
    # checkout, but to this hook it was just a subdirectory: the same repo-relative
    # path that globs ALLOW in the main checkout arrived as
    # .claude/worktrees/t01-83/src/... and matched nothing — so in a
    # worktree-per-session project, NO doer could write source at all. Found in
    # kaya-ai at the first build dispatch after plan approval, the most expensive
    # possible place.
    #
    # Fix: match the RAW path first (so a glob that deliberately targets
    # .claude/worktrees/** still works — none exist today, but the edge is real),
    # then strip the worktree prefix and match the in-worktree path against the same
    # globs. This is NOT a widen: identical globs, anchored to the checkout the
    # agent is standing in.
    _wt = re.match(r"^\.claude/worktrees/[^/]+/(.+)$", rel)
    rel_candidates = [rel] + ([_wt.group(1)] if _wt else [])

    # glob_to_re/matches are defined at module scope (above `def domain_check`) so the
    # --resolve path reaches the SAME matcher. Not modified — only moved (D-02).
    # A match is accepted only where the base's target-side test passes. In the product
    # base that test is constant-True and the filtering already happened on the globs;
    # in the harness base every glob is live but only a control-plane target may be
    # granted by one. Discarding the match here rather than filtering globs above is
    # what makes `docs/**` grant <harness>/docs/harness/guide.md AND <product>/docs/x.md
    # while refusing <harness>/src/main.py under a `src/**` grant.
    if any(matches(r, g) for r in rel_candidates for g in applicable_globs
           if target_side_test(r)):
        return

    if any(matches(r, g) for r in rel_candidates for g in applicable_shared
           if target_side_test(r)):
        # Shared paths are owned by nobody and always serialized (DEC-85). Allow the
        # write, but say so — an unnoticed shared-file edit is how two agents collide.
        print(f"check-domain: {agent} is writing SHARED path {rel} "
              f"(owned by nobody, must be serialized).", file=sys.stderr)
        return

    # ACTIONABLE REJECTION (DEC-100b). A probe confirmed that naming only the
    # rejected path leaves an agent with no basis for choosing a valid alternative,
    # so always print what it MAY write.
    #
    # The line must not advertise globs that cannot grant anything in the base that was
    # selected — an agent told it may write `src/**` here, when here is the harness
    # base, is being sent round a loop it cannot exit. In the product base that is the
    # non-control-plane globs; in the harness base, the globs some control-plane target
    # could actually satisfy.
    if base == _abs_root:
        _advertise = [g for g in applicable_globs
                      if is_control_plane_glob(g) or any(
                          matches(e.rstrip("*").rstrip("/"), g) or matches(g.rstrip("*").rstrip("/"), e)
                          for e in HARNESS_CONTROL_PLANE)]
        _shared_advertise = [s for s in applicable_shared if is_control_plane_glob(s)]
    else:
        _advertise = list(applicable_globs)
        _shared_advertise = list(applicable_shared)
    permitted = ", ".join(_advertise) if _advertise else "(no writable domain declared)"
    print(f"check-domain: BLOCKED — {agent} may not write {rel}", file=sys.stderr)
    print(f"  Permitted for you: {permitted}", file=sys.stderr)
    if _shared_advertise:
        print(f"  Shared (allowed, serialized): {', '.join(_shared_advertise)}", file=sys.stderr)
    print(f"  If this path should be yours, it belongs in {os.path.relpath(manifest, root)} "
          f"— do not work around this hook.", file=sys.stderr)
    sys.exit(2)


# The DOMAIN check needs a parser; the STATE-FILE SHAPE gate below mostly does not.
# Review finding 1: the bootstrap-grant `sys.exit(0)` skipped BOTH, so a session with
# no PyYAML could write an unbounded state.yaml with unknown or duplicate top-level
# keys and no denial. Before the T-13 single-interpreter merge those were separate
# launches and the shape gate ran regardless — so this was a regression introduced by
# the merge, not an inherited gap. Skip only what actually needs the parser.
if _run_domain and not _no_parser:
    domain_check()

# ---------------------------------------------------------------------------
# THE SHAPE PHASE (DEC-150/154/159) — issue #132.
#
# Domain asks WHO may write a path. Shape asks WHAT the file may contain. Those are
# independent questions, and until now the second was answered only on the narrow
# intersection where the first happened to be asked. Measured on the pre-change tree
# with ONE 400-line feature.yaml payload against its 200-line budget:
#
#   Write, harness-orchestrator ........ exit 2   <- the only route that ever fired
#   Edit,  harness-orchestrator ........ exit 0   <- no `content` in the payload
#   Bash   (sed -i, cat >, python3 -c) . exit 0   <- bash-write-guard has no shape logic
#   Write, MAIN SESSION ................ exit 0   <- exited at the domain carve-out above
#
# One route of four. The fourth is not in issue #132 and is the one that explains its
# own evidence: the 226-line feature.yaml it records was the MAIN SESSION's, so the tool
# was never the whole story.
#
# Two modes now:
#
#   PreToolUse  (Write) — unchanged. Measure the payload's `content` and BLOCK.
#                 Prevention, kept, because it is the only mode that can prevent.
#   PostToolUse (Write|Edit|Bash) — read what LANDED ON DISK and exit 2, whose stderr
#                 reaches the agent. Detection, not prevention: an Edit payload carries
#                 no whole-file content and arbitrary shell cannot be predicted, so
#                 reconstructing either before the fact would be guessing at the answer
#                 the filesystem is about to give for free. The budget is a CONTEXT
#                 bound, and a report issued immediately after the write still lands
#                 before the next reader loads the file.
#
# check-state.sh sweeps the same budgets at /harness entry — the backstop for a session
# where this hook is not registered at all, which INV-9 now also asserts against.
# ---------------------------------------------------------------------------

ROUTING = ("Routing: current truth REPLACES STATE.md ## Current; per-run findings go in that "
           "run's digest.md; rationale goes in notes/. State files carry no history.")

# The post sweep's candidates. Same four patterns the branches below match, because a
# route that reaches a file the gate cannot name is not covered by it.
#
# THE WORKTREE TIER IS NOT OPTIONAL, and it was a review finding measured on this repo:
# a live agent worktree held 38 files matching these globs and the sweep reached NONE of
# them, because the globs are joined to `root` and a worktree is a separate checkout
# underneath it. Every harness agent works in a worktree (DEC-143), so a Bash-route sweep
# blind to them is blind to the common case. The named-target route already handled this
# via `_norm`; the sweep did not.
_SWEEP_PATTERNS = (
    "CLAUDE.md",
    ".harness/features/*/feature.yaml",
    ".harness/features/*/runs/*/state.yaml",
    ".harness/features/*/notes/handoff-*.md",
    ".harness/features/*/STATE.md",
)
SWEEP_GLOBS = tuple(_p for _p in _SWEEP_PATTERNS) + tuple(
    os.path.join(".claude", "worktrees", "*", _p) for _p in _SWEEP_PATTERNS)
# WHAT THE SWEEP READS, and why it is a HIGH-WATER MARK rather than a fixed window.
#
# A fixed 120 s window was the first design and review broke it twice, both measured:
#
#   1. NO DEDUP. One over-budget feature.yaml, then five unrelated `ls` calls produced
#      five identical exit-2s with byte-identical stderr. A context-budget guard that
#      spends context re-reporting the same file is working against its own purpose.
#   2. BULK MTIME REFRESH. `git checkout --`, `git stash` and `git stash pop` all reset
#      mtime to now — verified here: a file backdated to 2025 came back with age 0 s
#      after `git checkout --`. Routine git usage therefore dragged EVERY state file into
#      the window at once, at 541 ms per Bash call for the next two minutes, and exit 2 on
#      pre-existing violations this change deliberately did not fix.
#
# The stamp fixes both with less logic, not more. A file is read only if it changed since
# THIS SWEEP LAST RAN, so a repeat report is impossible and a bulk refresh costs one pass
# rather than 120 seconds of them. The window survives only as the FIRST-RUN bound, where
# there is no stamp to compare against and reading everything would be the alternative.
#
# Cost, measured on this tree — 120 files, 82 of them state.yaml the gate YAML-parses:
#   read + YAML-parse all 120 ....... 515 ms   <- the sweep with no bound at all
#   stat all 120 .................... 0.2 ms   <- the sweep with one
# Interpreter start-up dominates what remains: ~38 ms of the ~42 ms per post-Bash call.
SWEEP_WINDOW_S = 120
# Git-ignored, one line, mtime-only — the file's CONTENT is never read, only its mtime.
STAMP = os.path.join(".harness", ".shape-sweep-stamp")


def _show(path):
    """Repo-relative WITHOUT the worktree strip — the path a human can act on.

    Paired with `_norm` deliberately: `_norm` answers "which rules apply to this file"
    and must strip, or a worktree write matches no pattern; `_show` answers "which file
    am I talking about" and must NOT strip, or every checkout collapses onto one name.
    """
    return os.path.relpath(os.path.abspath(path), os.path.abspath(root))


def _norm(path):
    """Repo-relative, worktree-stripped (DEC-143). The one path normalisation."""
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    wt = re.match(r"^\.claude/worktrees/[^/]+/(.+)$", rel)
    return wt.group(1) if wt else rel


# THE VERB IS MODE-DEPENDENT, and this was a review finding. In PRE the write is genuinely
# refused. In POST it already LANDED — exit 2 there only carries stderr back to the agent —
# so "BLOCKED" states something that did not happen, on every post route, not merely the
# sweep. An agent told its write was blocked when the file is on disk will do the wrong
# thing about it. Same messages, one honest verb.
VERB = "OVER BUDGET (already written)" if _post else "BLOCKED"

# THE SHAPE-GATE PATTERNS, named ONCE. Four state files plus CLAUDE.md (DEC-181) — the
# count is deliberately not written into this sentence, because the last one that did
# went stale in the same hunk that added the fifth entry. They were four inline `re.match` calls, which
# was fine while the only caller had already been handed the file's text. The post route
# has not: it holds a path, and reading a file to discover it is not a state file costs the
# whole file. Measured by review on a 200 MB non-state path: 228 ms, against 37 ms once the
# pattern is consulted first. Two uses, one definition — duplicating them as a fast-path
# guard would create exactly the silent drift `test-check-state.py` case (o) exists to catch.
RE_FEATURE_YAML = re.compile(r"^\.harness/features/[^/]+/feature\.yaml$")
RE_STATE_YAML   = re.compile(r"^\.harness/features/[^/]+/runs/[^/]+/state\.yaml$")
RE_HANDOFF      = re.compile(r"^\.harness/features/[^/]+/notes/handoff-[a-z0-9-]+\.md$")
RE_STATE_MD     = re.compile(r"^\.harness/features/[^/]+/STATE\.md$")
# CLAUDE.md (issue #139). Not a state file, and included here anyway because this is
# where the four-route machinery already lives — the alternative was a fifth gate.
RE_CLAUDE_MD    = re.compile(r"^CLAUDE\.md$")
# plan.yaml is DELIBERATELY ABSENT (DEC-182). It carries neither a budget nor a vocabulary
# rule, which is what this gate is for: `feature.yaml` 200/20 and `CLAUDE.md` 80 are
# budgets, `state.yaml`'s 23-key whitelist is a vocabulary, and STATE.md and the handoff
# note are both. A plan.yaml check here would be a PARSE check — a third thing — and
# check-plan-routes.py already refuses a malformed plan BEFORE signature, which is when it
# matters, with check-state.sh refusing it again at entry. A third enforcement point buys
# nothing and costs two entries in two pattern lists that have already drifted once.
SHAPE_PATTERNS = (RE_FEATURE_YAML, RE_STATE_YAML, RE_HANDOFF, RE_STATE_MD, RE_CLAUDE_MD)


def has_shape_rules(rel):
    """Cheap path-only predicate: could shape_problems have anything to say about `rel`?

    RENAMED from is_state_file/STATE_PATTERNS. CLAUDE.md is not a state file, and a
    predicate whose name says otherwise is the category error a reviewer flagged — the
    next reader looking for "why is CLAUDE.md in the state-file set" finds no answer
    because the premise is wrong. The gate is about SHAPE; state files are most of what
    has a shape, not the definition of it."""
    return any(p.match(rel) for p in SHAPE_PATTERNS)


def shape_problems(rel, content, display=None):
    """The stderr LINES for one file's text, or [] when it is clean. NEVER exits.

    Returning rather than exiting is the whole reason this is a function: one call site
    blocks a single write, another reports across a sweep, and a third would have to
    duplicate every message to do either. Every message below is byte-identical to the
    inline version it replaces.
    """
    lines = content.splitlines()
    out = []

    # THE PATH GOES IN THE HEADER, and its absence was a live review finding rather than a
    # style note. The pre route names one file the agent just named itself; the SWEEP walks
    # up to 234 candidates across a main checkout and every worktree, and named NONE of
    # them. Measured consequence: one logical file present in main plus four worktrees
    # produced five byte-identical findings, 20 lines of stderr, zero paths — and a
    # reviewer received another agent's transient fixture, unattributable, in their own
    # session. check-state.sh already does this correctly.
    def _head(text):
        # THE DISPLAY PATH IS NOT THE MATCH PATH (review of PR #152). `rel` is
        # worktree-stripped so the patterns match, and for a state file the stripped form
        # still carries `FEAT-NN` — enough to tell two checkouts apart. For CLAUDE.md it
        # collapses to the constant string "CLAUDE.md", so a 114-line copy in ANOTHER
        # agent's worktree told an agent whose own file is 74 lines that "CLAUDE.md is 114
        # lines". That is the same unattributable-finding defect DEC-180 fixed for the
        # sweep generally, surviving in the one path where stripping erases everything.
        return f"check-domain: {VERB} — {display or rel}: {text}"

    def deny(msgs):
        out.append(_head("state-file shape (DEC-150)."))
        out.extend(f"  {m}" for m in msgs)
        out.append(f"  {ROUTING}")

    if RE_FEATURE_YAML.match(rel):
        problems = []
        if len(lines) > 200:
            problems.append(f"feature.yaml is {len(lines)} lines — budget is 200. It is data a script "
                            f"parses, not a journal.")
        comments = sum(1 for l in lines if l.lstrip().startswith("#"))
        if comments > 20:
            problems.append(f"{comments} comment lines — budget is 20. Narrative commentary does not "
                            f"belong in feature.yaml.")
        if problems:
            deny(problems)

    if RE_STATE_YAML.match(rel):
        # DEC-154/160: the run checkpoint carries only whitelisted top-level keys.
        # INV-16 sweeps this at entry; this denies it at write, while the author can
        # fix it — the first post-deploy run (FEAT-03 plan) violated within hours of
        # the sweep landing, so entry-time alone demonstrably does not deter.
        # KEY VOCABULARY stays in sync with CHECKPOINT_KEYS in check-state.sh; the
        # MECHANISM deliberately does not (D-02). check-state.sh sweeps existing files
        # and reports; this denies at write. Since T-12 the duplicate here is caught by
        # the LOADER RAISING, while check-state.sh still scans — same vocabulary, two
        # mechanisms. Do not "resync" them by reverting this to a regex scan: the scan
        # is what let a malformed file pass with its keys silently unread.
        ALLOWED = {"schema_version", "run_id", "feature", "squad", "host", "status", "steps",
                   "cycles_used", "cost", "flow", "task", "team", "branch", "worktree",
                   "review_sha", "pinned_sha", "base_sha", "head_sha", "tip_sha", "commits",
                   "verdict", "severity_max", "digest"}
        # NO PARSER, in a bootstrap-grant session: the shape gate does not run.
        #
        # A line-scan fallback lived here briefly and was REMOVED at the user's ruling. The
        # signed BRIEF forbids it outright — Goal :20-21 "no second code path anywhere, so
        # the brittle regex leaves the tree instead of living on as a fallback nobody
        # exercises", Constraint :48-49 "no line-scan alternative, no degraded mode in any
        # converted script". A branch that runs ONLY when PyYAML is missing is by
        # construction the least-exercised code in this file, which is precisely the rot
        # the constraint is aimed at. I argued the exception in a comment in the same commit
        # that introduced it, with no D-NN and no signature; the goal-check caught it.
        #
        # What is given up is EARLIER detection, not correctness — measured, not assumed: a
        # malformed state.yaml written during a grant is still refused by check-state.sh at
        # the next /harness entry, naming the same offending keys, by a session that can
        # actually read it. One bad file to delete, against a crude reader living on forever
        # in a write guard.
        #
        # A BARE `return []`, not a `sys.exit(0)` as this was before the #132 refactor.
        # Equivalent for a single write — no other branch can match a state.yaml path — but
        # NOT equivalent under the post sweep, where exiting here would abandon every file
        # after this one in the same pass.
        if _no_parser:
            return out

        try:
            doc = harness_yaml.load_str(content, rel)
        except harness_yaml.DuplicateKeyError as e:
            # D-02: the DEC-156 denial SURVIVES, now raised by the loader rather than
            # counted by a regex — which also catches a duplicate at any nesting depth,
            # not merely at column 0.
            out.append(_head("state.yaml is a checkpoint, not a notebook (DEC-154)."))
            out.append(f"  duplicate key {e.key!r} — the second silently shadows the first; "
                       f"replace the placeholder, never append a copy (DEC-156).")
            return out
        except harness_yaml.YamlParseError as e:
            # NEW blocking outcome, deliberate (D-02 consequence #2). The regex this
            # replaced found no keys in a malformed file and therefore reported nothing
            # wrong — it wrote a broken checkpoint and said it was fine.
            out.append(_head("this state.yaml is not valid YAML."))
            out.append(f"  {e.original}")
            out.append("  A checkpoint that cannot be parsed is unreadable to every gate that "
                       "consumes it later; the write is refused while you can still fix it.")
            return out

        # T-17 / D-08: str() BOTH sides. A parsed key is not necessarily a string —
        # YAML 1.1 resolves `on:`, `off:`, `yes:`, `no:` to booleans and `01:` to an int —
        # so an un-coerced comparison against a set of strings silently reports a real key
        # as unknown, and `sorted()` over mixed types raises outright. In a fail-closed
        # hook a raise is a block on every write, not a wrong answer.
        keys = list(doc) if isinstance(doc, dict) else []
        unknown = sorted({str(k) for k in keys if str(k) not in ALLOWED})
        if unknown:
            out.append(_head("state.yaml is a checkpoint, not a notebook (DEC-154)."))
            out.append(f"  non-checkpoint top-level key(s) {unknown} — findings and assessment prose "
                       f"belong in this run's digest.md; a one-line note: per STEP entry is the "
                       f"prose ceiling.")
            # Naming the key is required (DEC-100b), but naming it `True` when the author
            # typed `on:` is not actionable — the reader cannot find `True` in their file.
            # Say what happened instead of leaving them to guess.
            if any(not isinstance(k, str) for k in keys):
                odd = sorted(f"{k!r} ({type(k).__name__})" for k in keys if not isinstance(k, str))
                out.append(f"  NOTE — {', '.join(odd)} came from an UNQUOTED key that YAML resolved to a "
                           f"non-string: `on`/`off`/`yes`/`no`/`true`/`false` become booleans and `01` "
                           f"becomes an int (YAML 1.1). Quote the key to keep it a string.")
            return out

    if RE_HANDOFF.match(rel):
        # DEC-159: the handoff note is working memory for a successor — four fixed
        # sections, hard-capped, denied at write while the author can still fix it.
        # Cap 60 (DEC-160): the first live handoff was 49 lines with zero fat.
        problems = []
        if len(lines) > 60:
            problems.append(f"handoff note is {len(lines)} lines — cap is 60. It is intent, trust,"
                            f" dead ends and a working set, not a narrative; history lives on disk.")
        required = ["## Next", "## Trust", "## Dead ends", "## Working set"]
        low = [l.strip().lower() for l in lines]
        missing = [h for h in required if h.lower() not in low]
        if missing:
            problems.append(f"missing required section(s) {missing} — the four sections are the"
                            f" contract (templates/HANDOFF.md); a freeform handoff drifts like an"
                            f" unvalidated digest did (DEC-156).")
        if problems:
            out.append(_head("handoff shape (DEC-159)."))
            out.extend(f"  {m}" for m in problems)

    if RE_CLAUDE_MD.match(rel):
        # ISSUE #139. CLAUDE.md is read at EVERY session start — the widest blast radius in
        # the repo — and was the only file of its class with no mechanical budget. Its peers
        # all have one: expertise 150, feature.yaml 200/20, handoff 60, STATE.md 120.
        #
        # 80 IS DERIVED, NOT PICKED, and the ticket asked for exactly that. Measured from
        # this file's own history, WHICH STARTS AT A CLEANUP: it was 208-214 lines from
        # April through 2026-07-27, then DEC-135 cut it to 50 — that blow-out is why issue
        # #139 exists at all. Since the cleanup: 50-51 through 07-28, 56 on 08-02, 71 on
        # 08-04, then 84, at which point a human trimmed it twice, to 78 and then 74.
        #
        # The evidence CONSTRAINS the number to roughly 75-83 rather than fixing it at one:
        # above 84 discards the only judgement anyone actually made, and at 74 it bans all
        # growth. 80 sits inside that band with 6 lines of headroom, which is thin on
        # purpose — this file is preloaded into every session, and the two trims say the
        # right response to pressure here is to cut, not to raise the ceiling. An earlier
        # draft called 80 "the only number with evidence"; that overstated it, and the band
        # is stated instead.
        #
        # THE SHRINK EXEMPTION APPLIES HERE, MEASURED AND ACCEPTED. Issue #132 named this
        # for a different option: with the file at 200 lines on disk, a `Write` payload of
        # 150 is DENIED even though it is a large improvement, because the pre gate measures
        # the payload against the budget and 150 > 80. A partial staged shrink is blocked;
        # a full one is not. It is not a trap: `Edit` is never blocked pre-hoc, so the
        # author trims with Edit and the post route reports until they are under. Recorded
        # rather than fixed, because a "smaller than what is on disk" exemption means the
        # pre gate must read the file it is about to overwrite — file I/O and a TOCTOU
        # window in the hot path, to rescue a case with a working alternative.
        #
        # THE TICKET RULED THIS GATE OUT AND ISSUE #132 MADE THAT REASON OBSOLETE. #139 says
        # "check-domain.sh's shape gate is the wrong home: it fires on Write only and the
        # main session is ungoverned by it" — both true when written, neither true now. The
        # main session is the thing that actually edits CLAUDE.md, and it is now bound on
        # all four routes. Re-derived at a5edb13 rather than inherited from the ticket.
        if len(lines) > 80:
            out.append(_head(f"CLAUDE.md is {len(lines)} lines — budget is 80 (DEC-181)."))
            out.append("  It is preloaded into EVERY session, so a line here costs more than "
                       "a line anywhere else. Carry the rule and one clause of why, not the "
                       "biography (DEC-158); rationale belongs in docs/harness/DECISIONS.md.")

    if RE_STATE_MD.match(rel):
        problems = []
        if len(lines) > 120:
            problems.append(f"STATE.md is {len(lines)} lines — budget is 120. It holds no history: "
                            f"## Current is replaced, never appended.")
        h2 = [l.strip() for l in lines if l.startswith("## ")]
        bad = [h for h in h2 if h not in ("## Current", "## Open Questions")]
        if bad:
            problems.append(f"illegal section(s) {bad} — STATE.md is `## Current` + "
                            f"`## Open Questions` and nothing else (SPEC §2).")
        if problems:
            deny(problems)

    return out


# --- WHAT TO CHECK, by mode and route. -------------------------------------
# `targets` is [(repo-relative path, file text)]. Building it is the ONLY thing the two
# modes disagree about; the gate itself is one function above, run over whatever lands here.
targets = []

if not _post:
    # PRE. Only `Write` carries a whole-file `content` to measure, so only `Write` can be
    # blocked before the fact. `d` was parsed once at the top of this process (T-13);
    # re-parsing here was leftover from the four-launch version — and inconsistent
    # leftover: this copy exited 0 on a failure the first one absorbed with `d = {}`, so
    # the two disagreed about what a bad payload means. Review finding 2.
    if _tool != "Write" or not target:
        sys.exit(0)
    targets = [(_norm(target), (d.get("tool_input") or {}).get("content") or "",
                _show(target))]

elif target:
    # POST, with a named file: Write, Edit, NotebookEdit. Read what LANDED — no
    # reconstruction of `old_string`/`new_string`, no `replace_all` semantics, no TOCTOU
    # window, because the filesystem already holds the answer those would approximate.
    _rel = _norm(target)
    if not has_shape_rules(_rel):
        sys.exit(0)
    try:
        with open(os.path.abspath(target), encoding="utf-8", errors="replace") as _f:
            targets = [(_rel, _f.read(), _show(target))]
    except OSError:
        # The tool may have failed, or the path may be a directory or already gone. A
        # post-hoc reporter that raises on an unreadable path would turn every such write
        # into a spurious exit-2 the agent cannot act on.
        sys.exit(0)

else:
    # POST, no named file: Bash, whose payload carries a command and not a path. Sweeping
    # is the only honest answer — classifying arbitrary shell into "wrote a state file" or
    # not is the prediction problem this mode exists to avoid.
    import glob as _glob
    import time as _time
    _now = _time.time()
    _stamp = os.path.join(root, STAMP)
    try:
        _since = os.stat(_stamp).st_mtime
    except OSError:
        # FIRST RUN in this checkout: no high-water mark exists, so fall back to the
        # window. Reading everything instead would put the 515 ms figure on the very
        # first Bash call of every session.
        _since = _now - SWEEP_WINDOW_S
    # CLAMP A MARK FROM THE FUTURE. `chmod 444` a future-dated stamp and the sweep is dead
    # permanently — no code edit, gitignored, `git status` clean, no gate reads it. Clock
    # skew across a VM boundary reaches the same state by accident. A mark ahead of now
    # cannot be a record of a sweep that has happened, so it is not trusted as one.
    if _since > _now:
        _since = _now - SWEEP_WINDOW_S
    _unreadable = False
    for _pat in SWEEP_GLOBS:
        for _p in _glob.glob(os.path.join(root, _pat)):
            try:
                if os.stat(_p).st_mtime <= _since:
                    continue
                with open(_p, encoding="utf-8", errors="replace") as _f:
                    # Third element: the repo-relative path WITHOUT the worktree strip, so
                    # a finding names the checkout it came from.
                    targets.append((_norm(_p), _f.read(), _show(_p)))
            except OSError:
                _unreadable = True
    # ADVANCE THE MARK WHETHER OR NOT ANYTHING WAS FOUND, and whether or not the report
    # below exits 2 — the mark records "the sweep has seen the tree up to here", not
    # "the tree was clean". Tying it to a clean result would reintroduce the repeat-report
    # loop for exactly the files that need fixing.
    #
    # THE MARK IS `_now`, THE MOMENT THIS SWEEP STARTED — never the moment it finished.
    # That one difference is a correctness fix, not tidiness. Writing "now" at the end
    # covers the whole walk, so a file written by ANOTHER agent while this process was
    # walking lands before the new mark and is never reported by anyone: agent A's write
    # falls into the gap between B stat-ing that path and B advancing the stamp. A reviewer
    # reproduced it 40 times out of 40 at a 40 ms offset, and — because the stamp is
    # global and shared — the miss was PERMANENT, surviving five further sweeps until an
    # unrelated touch resurfaced the file. Round 2 had turned a transient miss into a
    # permanent one. Stamping the START instead leaves any write during the walk strictly
    # newer than the mark, so the next sweep picks it up. The cost is that files written
    # during the walk are reported twice at worst; a duplicate report is noise, a
    # permanent miss is the failure this whole change exists to prevent.
    #
    # NOT ADVANCED AT ALL IF ANY CANDIDATE COULD NOT BE READ. An OSError skips that file,
    # and advancing past it would make a transient unreadable state a permanent blind spot
    # by the same mechanism.
    if not _unreadable:
        try:
            os.makedirs(os.path.dirname(_stamp), exist_ok=True)
            with open(_stamp, "w"):
                pass
            os.utime(_stamp, (_now, _now))
        except OSError:
            # An unwritable stamp degrades to the fixed window: noisier, never a miss.
            pass

_problems = []
# UNIFORM 3-TUPLES. The first version threaded `display` through the SWEEP only and left
# the other two routes as 2-tuples, read back with `_t[2] if len(_t) > 2 else None` — a
# mixed arity that was itself the tell. Measured: a PostToolUse Edit naming
# `.claude/worktrees/wt1/CLAUDE.md` printed a bare "CLAUDE.md", so an agent told its file
# was 81 lines opened the 74-line root copy and concluded the gate was stale. I had fixed
# the instance and not the class.
for _rel, _text, _disp in targets:
    _problems.extend(shape_problems(_rel, _text, display=_disp))

if _problems:
    for _line in _problems:
        print(_line, file=sys.stderr)
    sys.exit(2)

sys.exit(0)
PY
