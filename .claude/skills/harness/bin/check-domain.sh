#!/usr/bin/env bash
# PreToolUse hook — block an agent from writing outside its declared domain.
#
# Registered in .claude/settings.json — NOT in agent frontmatter:
#   "PreToolUse": [{ "matcher": "Write|Edit",
#     "hooks": [{ "type": "command",
#       "command": "${CLAUDE_PROJECT_DIR}/.agents/skills/harness/bin/check-domain.sh" }] }]
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
# This script lives at <root>/.agents/skills/harness/bin/, so walk up four levels.
# BASH_SOURCE is the one thing only bash can answer, which is why any bash remains.
_self="${BASH_SOURCE[0]:-$0}"
_selfdir="$(cd "$(dirname "$_self")" && pwd)"
_derived="$(cd "$_selfdir/../../../.." && pwd)"

# T-13: ONE interpreter launch, not four. This hook runs on EVERY agent write, and
# four launches cost four Python start-ups per write — measured at 104.7ms for the
# full governed path, of which the interpreter is most. Behaviour is unchanged:
# every early exit, every exit code and every stderr message is identical, and the
# unchanged test suite is the equivalence proof (D-10, REQ-07).
# `-I` IS LOAD-BEARING, NOT TIDINESS (#556). Python otherwise puts the invoking directory
# at sys.path[0] AHEAD of PYTHONPATH, so a harness_boundary.py in the GOVERNED AGENT cwd
# can replace the policy module. Measured 2026-08-27 at sha 7179095: a stub returning a
# bogus root turned this hook from exit 2 (refused) into exit 0 ("enforcement OFF").
# The bootstrap removes only sys.path[0] before the heredoc imports anything, preserving
# site-packages on Python 3.9. test-no-distribution.py case 7 is the invariant.
HOOK_PAYLOAD="$payload" PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -c 'import sys; sys.path.pop(0); exec(compile(sys.stdin.read(), "<stdin>", "exec"))' "$_derived" "${1:-}" "$_selfdir" <<'PY'
import sys, os, re, json, fnmatch

# THE BOUNDARY RULE LIVES IN harness_boundary.py (FEAT-17 T-01), NOT HERE.
# It used to be defined in this heredoc, which is why bash-write-guard.sh could not
# consult it and enforced a second, weaker version of the same question — the split
# issue #261 reports. A heredoc cannot be imported. Moved verbatim, no behaviour
# changed, both suites unedited.
#
# The import is LAZY and appears at exactly two sites below, both REQUIRED and both
# FAIL CLOSED: the --resolve branch, which exits before the other one is reached, and
# the `if _run_domain:` block. It is deliberately ABSENT from the shape phase, whose
# import must stay absorbing — a fail-closed import there would block the main
# session, the only tier that can repair a broken module.


# harness_yaml is imported LAZILY, below, after the manifest check — NOT here.
# Ordering is behaviour: the four-launch version reached the DEC-101 "no manifest,
# enforcement OFF" fail-open in BASH, before any interpreter that needed the module.
# Importing at the top made a hook whose module is missing crash with exit 1 before
# it could print that message. Caught by test-check-domain.py's isolated-copy case.
_derived, argv_agent, _bin_dir = sys.argv[1:4]
sys.path.insert(0, _bin_dir)


def _root():
    """WHERE THIS HARNESS IS ROOTED — asked of harness_boundary, the one resolver (FEAT-42
    T-10). What stood at the two call sites was the two-name environment chain, a manifest
    probe written twice, and a fall-through to `""` or to `os.getcwd()`. The `""` is why an
    unset environment left every subsequent join relative to whatever directory the hook
    inherited.

    strict=False, DELIBERATELY, and not because strictness is inconvenient. A strict raise
    here would fire on exactly the tree DEC-101 carves out — one with no manifest — and the
    carve-out's whole point is that such a tree fails OPEN, loudly, at exit 0. strict=False
    returns the derived root instead, which is what the deleted code returned for that tree
    too, and the DEC-101 check downstream then prints "enforcement OFF" for it. What is gone
    is only the `""` and the cwd fall-through.

    THE except CLAUSE IS THE BOOTSTRAP, not a second resolver. `_derived` is the bash
    wrapper's own BASH_SOURCE walk, computed before any interpreter starts, and it is the
    only root computable when harness_boundary.py is not on the path at all. That happens in
    exactly one place: the isolated-copy fixture, which copies this script alone into a bare
    tree to prove DEC-101's fail-open still fires. Absorbing the ImportError here does not
    weaken the fail-closed import under `_run_domain` below — inside a real checkout the
    manifest IS readable, so that branch is reached and still refuses at exit 2.
    """
    try:
        import harness_boundary as _hb_root
    except Exception:
        return _derived
    return _hb_root.resolve_root(_bin_dir, strict=False)

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
    root = _root()
    manifest = os.path.join(root, ".harness", "team-config.yaml")
    if not os.access(manifest, os.R_OK):
        print(f"check-domain: no {manifest} — cannot resolve routes.", file=sys.stderr)
        sys.exit(2)
    import harness_yaml

    # FAIL CLOSED, not defensive padding. Unhandled, an ImportError exits 1, and exit 1
    # is NON-BLOCKING (line 14): the write would land and enforcement would go silently
    # off on both routes at once — the same failure direction as issue #103, installed
    # inside its own fix. Exit 2 here is safe because this branch answers a query and
    # blocks no write, so refusing loudly is the right answer from a resolver whose rule
    # is missing (D-06).
    try:
        import harness_boundary
    except Exception as _be:
        print("check-domain: BLOCKED — the boundary module harness_boundary.py could "
              "not be imported, so no domain can be checked.", file=sys.stderr)
        print(f"  {type(_be).__name__}: {_be}", file=sys.stderr)
        print("  Enforcement is CLOSED rather than partial. Restore "
              ".agents/skills/harness/bin/harness_boundary.py, then retry.",
              file=sys.stderr)
        sys.exit(2)

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
    _ws_root, _ws_bases, _fleet_path = harness_boundary.resolve_fleet(root, "check-domain")

    _abs = _resolve_target if os.path.isabs(_resolve_target) else os.path.join(root, _resolve_target)
    _abs = harness_boundary.real(_abs)
    _base, _glob_filter, _target_test = harness_boundary.select_base(
        _abs, root, _ws_root, _ws_bases, _fleet_path, "check-domain")
    if _base is None:
        # Outside both bases — no agent can be named, and NOBODY is the literal answer.
        # Silence here would be the fail-open this branch exists to remove.
        print("NOBODY")
        sys.exit(0)

    # Normalise exactly as the hook does — a path given from inside a worktree must
    # resolve against the checkout the agent is standing in, not against a glob nobody
    # wrote. FEAT-30 T-04: this asks WHICH CHECKOUT via checkout_relative instead of
    # stripping a fixed number of segments, so the depth is not load-bearing here either.
    # Same candidate ordering: base-relative first, checkout-relative second when one is
    # returned and differs from the base.
    _rel = os.path.relpath(_abs, _base)
    _cands = [_rel]
    _ck = harness_boundary.checkout_relative(_abs)
    if _ck is not None and harness_boundary.real(_ck[0]) != harness_boundary.real(_base):
        _cands.append(_ck[1])

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
        if any(harness_boundary.matches(c, g) for c in _cands if _target_test(c)
               for g in _globs if _glob_filter(g)):
            _granting.add(_n)
        for g in _shared:
            if not _glob_filter(g):
                continue
            if any(harness_boundary.matches(c, g) for c in _cands if _target_test(c)) and g not in _shared_hits:
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

root = _root()
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

    # FAIL CLOSED, not defensive padding. Unhandled, an ImportError exits 1, and exit 1
    # is NON-BLOCKING (line 14): the write would land and enforcement would go silently
    # off on both routes at once — the same failure direction as issue #103, installed
    # inside its own fix. Exit 2 is safe HERE specifically because `_run_domain` implies
    # `_domain_phase`, which is `_governed` and not `_post`, so the main session — the
    # only tier that can restore the file — never reaches this line (D-06).
    try:
        import harness_boundary
    except Exception as _be:
        print("check-domain: BLOCKED — the boundary module harness_boundary.py could "
              "not be imported, so no domain can be checked.", file=sys.stderr)
        print(f"  {type(_be).__name__}: {_be}", file=sys.stderr)
        print("  Enforcement is CLOSED rather than partial. Restore "
              ".agents/skills/harness/bin/harness_boundary.py, then retry.",
              file=sys.stderr)
        sys.exit(2)

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


# ---------------------------------------------------------------------------
# T-14 — THE APPROVAL EXCLUSION, sourced from team-config.yaml's
# main_session.writes rather than hardcoded (D-10).
#
# A hardcoded plan.yaml pattern would pass every behavioural case here while
# leaving the record it is meant to enforce still unread. Reading the list is
# the deliverable: delete an entry and the denial stops existing, and the only
# things that notice are the stderr line below and this task's own test.
# ---------------------------------------------------------------------------
APPROVAL_GUARD = True


def _approval_entries(manifest_path):
    """Parse main_session.writes into (glob, fragment_or_None) pairs.

    SPLIT ON THE FIRST SPACE, never the last. That is the mechanism, not a detail.
    Splitting on the last space hands `.harness/*/features/*/BRIEF.md ## Approval` a
    tail of `Approval`, which ends in no colon and starts with no `## `, so it reads as
    fragment-less and contributes NO denial -- and it corrupts the glob into one ending
    `BRIEF.md ##`, matching nothing on disk. Three of the four real entries deny; a
    last-space split leaves exactly one, collapsing the three-file mechanism into the
    plan.yaml special case this task exists not to be.

    Returns (entries, problem). `problem` is a string when the record could not be read,
    and the caller FAILS OPEN LOUDLY on it (DEC-127).
    """
    try:
        doc = harness_yaml.load_file(manifest_path)
    except Exception as exc:
        return [], "could not parse %s (%r)" % (manifest_path, exc)
    if not isinstance(doc, dict) or "main_session" not in doc:
        return [], "no main_session key in %s" % (manifest_path,)
    ms = doc.get("main_session") or {}
    writes = ms.get("writes") if isinstance(ms, dict) else None
    if not isinstance(writes, list) or not writes:
        return [], "main_session.writes is missing or empty in %s" % (manifest_path,)
    entries = []
    for raw in writes:
        if not isinstance(raw, str) or not raw.strip():
            continue
        parts = raw.strip().split(" ", 1)          # FIRST space. See the docstring.
        glob = parts[0]
        frag = parts[1].strip() if len(parts) == 2 else ""
        if frag.endswith(":") or frag.startswith("## "):
            entries.append((glob, frag, raw.strip()))
        else:
            entries.append((glob, None, raw.strip()))   # e.g. .harness/logs/** -- no denial
    return entries, None


def _yaml_key_range(lines, key):
    """The on-disk line range of a top-level mapping key, as [start, end)."""
    start = None
    for i, line in enumerate(lines):
        if line.startswith(key):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        l = lines[j]
        if l.strip() and not l[:1].isspace() and not l.lstrip().startswith("#"):
            end = j
            break
    return (start, end)


def _heading_range(lines, heading):
    """The on-disk line range of a markdown section, heading to the next same-or-shallower."""
    depth = len(heading) - len(heading.lstrip("#"))
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading.strip():
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j].lstrip()
        if s.startswith("#"):
            d = len(s) - len(s.lstrip("#"))
            if d <= depth:
                end = j
                break
    return (start, end)


def _child_indent(lines, rng):
    """The indent the fragment's children actually use ON DISK.

    CONVENTION, NOT A YAML GUARANTEE. The format permits an approval block at any indent.
    Limb B can tell an approval child key from a task key only because every plan.yaml in
    the tree is emitted by harness-pm and, after this feature, by plan-merge.py -- both of
    which control the shape. A future reformatting that put task keys at the same indent as
    the approval block would silently unhook limb B, NOTHING IN THE TREE WOULD NOTICE, and
    there is no propagation checker that would (DEC-188 deleted it). Limb A survives that
    reformatting because it is a substring test against the on-disk range and reads no
    indentation at all; limb B is the part that dies. Measured: of 9 tracked PLAN.md files
    all 9 carry the signature heading at ZERO indent while 27 task lines sit at two spaces
    -- so a hardcoded two-space rule there denies 27 legitimate lines and matches no
    signature. Two of the three covered files, two opposite conventions, one rule.
    """
    for k in range(rng[0] + 1, rng[1]):
        l = lines[k]
        if l.strip() and l[:1].isspace():
            return len(l) - len(l.lstrip())
    return None


def approval_guard(rel, agent_name):
    """DENY a governed agent's write that would change a fragment the main session owns.

    The main session is exempt BY THE MECHANISM, not by a special case: this runs inside
    the _domain_phase region, and check-domain exits 0 for a payload with no agent_type.
    Adding an explicit main-session branch would be a second carve-out to keep in sync,
    and issue #132 records what happened the last time this file grew one.
    """
    if not APPROVAL_GUARD:
        return
    if _tool == "NotebookEdit":
        return

    # EXISTENCE FIRST, AND THE ORDER IS LOAD-BEARING. A first write cannot change a
    # signature that does not exist yet, so there is nothing to say -- and saying it anyway
    # would put a stderr line on an exit-0 path, which the existing suite refuses by name:
    # "noise on an exit-0 path is indistinguishable from a verdict". Reading the record
    # before this check made every passing write to a non-existent path under a fixture
    # manifest print the unreadable-list warning, and it cost a real regression.
    if not os.path.exists(target):
        return

    entries, problem = _approval_entries(manifest)
    if problem:
        print("check-domain: the main_session.writes exclusion list was unreadable (%s) "
              "— NO fragment denial was applied. This line is the only thing that notices "
              "a deleted entry." % (problem,), file=sys.stderr)
        return

    try:
        disk = open(target, encoding="utf-8").read()
    except Exception as exc:
        print("check-domain: could not read %s (%r) — no fragment denial applied."
              % (rel, exc), file=sys.stderr)
        return
    lines = disk.splitlines()

    for glob, frag, raw in entries:
        if frag is None:
            continue                      # fragment-less grant contributes no denial
        if not fnmatch.fnmatch(rel, glob):
            continue

        is_key = frag.endswith(":")
        rng = _yaml_key_range(lines, frag) if is_key else _heading_range(lines, frag)

        # AN ABSENT FRAGMENT IS STILL GOVERNED. Skipping here was the third demonstrated
        # bypass and the worst, because it CHAINS: one Edit deletes the block (allowed under
        # the old containment limb A), and with no key left on disk this `continue` skipped
        # the guard entirely, so a second Edit wrote a forged block back. Two allowed moves
        # to forge a signature. The file EXISTING with no signature does not mean anything
        # may create one -- only that there is no block to overlap, so limb A has nothing to
        # say and limb B carries the whole check.
        absent = rng is None
        if absent:
            rng = (len(lines), len(lines))
        on_disk_block = "" if absent else "\n".join(lines[rng[0]:rng[1]])

        def deny_fragment(why):
            print("check-domain: BLOCKED — %s may not change %s in %s."
                  % (agent_name, frag, rel), file=sys.stderr)
            print("  %s" % (why,), file=sys.stderr)
            print("  That fragment is granted to the MAIN SESSION alone by "
                  "main_session.writes: %r (DEC-120 — only the main session has a user "
                  "channel, so only it can hold a signature the user gave)." % (raw,),
                  file=sys.stderr)
            print("  Every other write to this file goes through "
                  "plan-merge.py, which carries the base approval bytes forward untouched.",
                  file=sys.stderr)
            sys.exit(2)

        if _tool == "Write":
            proposed = ti.get("content")
            if not isinstance(proposed, str):
                return
            plines = proposed.splitlines()
            if is_key:
                # PARSE both sides and compare the loaded value. A whitespace-only reflow
                # is not a signature change, and denying it would make plan-merge.py output
                # undeniable-by-luck.
                try:
                    old = harness_yaml.load_str(disk, target).get(frag[:-1])
                    new = harness_yaml.load_str(proposed, target).get(frag[:-1])
                except Exception as exc:
                    print("check-domain: could not parse one side of %s (%r) — allowing; a "
                          "gate that blocks on its own parse failure breaks every write the "
                          "moment the payload shape changes." % (rel, exc), file=sys.stderr)
                    return
                if old != new:
                    deny_fragment("the %s value differs from the one on disk." % (frag,))
            else:
                prng = _heading_range(plines, frag)
                new_block = "\n".join(plines[prng[0]:prng[1]]) if prng else None
                if new_block is None or new_block.strip() != on_disk_block.strip():
                    deny_fragment("the %s section body differs from the one on disk."
                                  % (frag,))
            return

        if _tool == "Edit":
            old_s = ti.get("old_string")
            new_s = ti.get("new_string")

            # LIMB A — OVERLAP, not containment. THE PANEL DEFEATED THE CONTAINMENT VERSION
            # THREE WAYS and every one crossed a boundary of the range rather than staying
            # inside it. An old_string that starts one line ABOVE the block, or ends one line
            # BELOW it, is not a substring of the block but still replaces every byte of it.
            #
            #   reproduced, all three ALLOWED before this fix:
            #     "feature: X\n\napproval:\n  status: pending\n..." -> quoted key, children at 4
            #     the same span -> "feature: X"                      (deletes the block)
            #     old_string "tasks:" against a file with NO key     (re-introduces a forged one)
            #
            # So the test is INTERSECTION of byte ranges. Locate old_string in the file and ask
            # whether its span touches the fragment's span at all.
            denied_a = False
            if not absent and isinstance(old_s, str) and old_s:
                b0 = disk.find(old_s)
                if b0 != -1:
                    b1 = b0 + len(old_s)
                    # the fragment's byte span, derived from the same line list
                    pre = "\n".join(lines[:rng[0]])
                    f0 = len(pre) + (1 if rng[0] else 0)
                    f1 = f0 + len(on_disk_block)
                    if b0 < f1 and f0 < b1:
                        denied_a = True
                        deny_fragment("old_string OVERLAPS the on-disk %s block (bytes %d-%d "
                                      "against the block at %d-%d), so this edit rewrites part "
                                      "or all of the signature." % (frag, b0, b1, f0, f1))
                elif old_s in on_disk_block:
                    # not found verbatim in the file but is block text -- still governed
                    denied_a = True
                    deny_fragment("old_string is text inside the on-disk %s block."
                                  % (frag,))

            # LIMB B — what new_string INTRODUCES. Token-match the key rather than a prefix
            # test, so a QUOTED key cannot slip past, and govern ANY deeper indent rather than
            # only the exact on-disk one, because re-indenting children 2 -> 4 was the other
            # half of the demonstrated bypass.
            if not denied_a and isinstance(new_s, str) and new_s:
                key = frag[:-1] if is_key else frag
                ind = _child_indent(lines, rng)
                kids = []
                if ind:
                    kids = [l.strip().split(":")[0].strip("\"'")
                            for l in lines[rng[0] + 1:rng[1]]
                            if l.strip() and (len(l) - len(l.lstrip())) == ind and ":" in l]
                for nl in new_s.splitlines():
                    stripped = nl.strip()
                    if not stripped or ":" not in stripped:
                        continue
                    tok = stripped.split(":")[0].strip().strip("\"'")
                    depth = len(nl) - len(nl.lstrip())
                    # the fragment's OWN key, at ANY indent and quoted or not
                    if is_key and tok == key:
                        deny_fragment("new_string introduces or rewrites the %s key (as %r at "
                                      "indent %d). Quoting it or moving its indent does not "
                                      "make it a different key." % (frag, stripped[:40], depth))
                    if not is_key and stripped.lstrip("#").strip() == frag.lstrip("#").strip():
                        deny_fragment("new_string introduces or rewrites the %s heading."
                                      % (frag,))
                    # A CHILD KEY OF THE SIGNATURE, AT ITS ON-DISK INDENT ONLY -- and the
                    # narrowness is deliberate, measured, not timid. "At this indent or
                    # DEEPER" was the first fix and it DENIED EVERY LEGITIMATE TASK EDIT:
                    # approval children sit at 2 and task keys at 4, so `status:` at indent 4
                    # is both a task key and "deeper than the signature". The re-indenting
                    # attack this was meant to catch is already caught by limb A, which now
                    # tests OVERLAP -- any payload that re-indents the block must span it.
                    if ind and kids and tok in kids and depth == ind:
                        deny_fragment("new_string carries the signature child key %r at the "
                                      "on-disk indent %d of the %s block."
                                      % (tok, ind, frag))
            return



RE_FEATURE_ARTIFACT = re.compile(r"^\.harness/[^/]+/features/([^/]+)/")


def feature_checkout_guard(raw_rel, target_path):
    """Bind a governed feature-artifact write to that feature's linked worktree.

    The domain matcher deliberately accepts the same stripped feature path in the main
    checkout and a worktree. During FEAT-45 that let six writes land in main; three
    artifacts existed nowhere else. This is a checkout question, not a broader glob or
    shape rule, and it only narrows a write that the domain decision already allowed.
    """
    match = RE_FEATURE_ARTIFACT.match(raw_rel)
    if match is None:
        return
    feature_id = match.group(1)
    try:
        expected = harness_boundary.worktree_for_feature(root, feature_id)
        if expected is None:
            return
        checkout = harness_boundary.checkout_relative(target_path)
        if checkout is not None and harness_boundary.real(checkout[0]) == harness_boundary.real(expected):
            return
        print(f"check-domain: BLOCKED — {target_path} is a feature artifact whose write "
              f"belongs in worktree {expected}.", file=sys.stderr)
        print(f"  Write this artifact in {expected}, not the main checkout.", file=sys.stderr)
        sys.exit(2)
    except harness_boundary.AmbiguousWorktree as exc:
        print(f"check-domain: BLOCKED — {target_path} belongs to feature {feature_id}, "
              f"but its worktree is ambiguous: {exc}", file=sys.stderr)
        sys.exit(2)
    except Exception:
        # Absorbing by design: a bug in this narrowing check must not turn an existing
        # domain allowance into an ambiguous exit-1 that the host treats as non-blocking.
        return


def domain_check():
    # T-12: the manifest is PARSED, not skimmed. The scanner this replaced matched the
    # literal text `name:`/`path:` line by line, so it never had to close a bracket or
    # resolve a key — which is how one unquoted `#` at team-config.yaml:18 made every
    # key from `orchestrator:` onward unreachable to a real reader while this hook went
    # on enforcing the fragments it still recognised. It reported nothing. A guard that
    # silently sees less than it should is worse than one that stops.
    # ROOT-SIDE: THE SESSION IS STANDING IN AN OUT-OF-PLACE WORKTREE (issue #103).
    # Such a tree carries its own .harness/team-config.yaml, so `root` resolves to it and
    # writes that are in-domain FOR THAT ROOT exit 0.
    #
    # THE GROUNDS, NARROWLY. That session is NOT ungoverned — DEC-180 and issue #132 made
    # the shape caps fire relative to whatever root the session stands in, and the domain
    # rules resolve against that root correctly; re-measured at a29ad06 in
    # notes/answers-2026-08-11-rescope.md. What is left is that the work lands in a
    # checkout nobody merges. This refuses the LOCATION, on the standing ruling that an
    # out-of-place worktree is a mistake. It does not close an enforcement hole, and
    # saying it did would be a wrong reason left in the tree for the next reader.
    #
    # PLACED HERE, INSIDE domain_check, AND THAT IS PARSER-CONTINGENT BY CHOICE. This
    # function is called under `_run_domain and not _no_parser`, so a bootstrap-grant
    # session (PyYAML missing) gets no root-side refusal on this route while the Bash
    # route still refuses. The grant already skips domain_check in the REAL checkout, so
    # it opens the same escape everywhere; the target-side refusal below is already
    # parser-contingent for the same reason; and a lost-work risk does not earn a second
    # assertion cluster on both routes. Do NOT close it by hoisting this above the
    # `if _run_domain and not _no_parser:` call, and do NOT close it by weakening the
    # Bash route to match.
    _root_wt = harness_boundary.worktree_owner(root)
    if _root_wt is not None and _root_wt[1] is None:
        print(f"check-domain: BLOCKED — {_root_wt[0]} holds a .git pointer file that "
              "does not parse, so this session's checkout cannot be placed.",
              file=sys.stderr)
        print("  Repair or remove it, then start the session again.", file=sys.stderr)
        sys.exit(2)
    if _root_wt is not None and not _root_wt[2]:
        # NO REMOVAL GUIDANCE HERE, unlike the target-side verdict below. Measured:
        # `git worktree remove` SUCCEEDS from inside the tree it removes, so printing
        # that instruction to a session whose cwd IS that tree tells it to delete the
        # ground it is standing on.
        print(f"check-domain: BLOCKED — {_root_wt[0]} is a git worktree that is not "
              f"under {harness_boundary.WORKTREES_SEGMENT}/, and this session is rooted "
              "in it.", file=sys.stderr)
        print(f"  Worktrees belong under {harness_boundary.worktree_refusal_location(_root_wt[1])}",
              file=sys.stderr)
        print("  Start the session from the main checkout, or from a checkout under "
              "that location, instead.", file=sys.stderr)
        sys.exit(2)

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
        # FAIL CLOSED, by the user's ruling and DEC-171's logic. This is NOT the
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

    # THE FLEET AND THE BASE (FEAT-15 T-01/T-02, REQ-01 through REQ-06). One call into
    # harness_boundary, which is the SAME rule the --resolve path calls, so the resolver
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
    _verdict = harness_boundary.classify(target, root, globs, shared, "check-domain")

    if _verdict["outcome"] == "out_of_place_worktree":
        # A write INTO a sibling worktree, from a session standing outside it. The
        # removal guidance is correct here and stays: the tree being named is not the
        # one this session is running in.
        if _verdict.get("unparsed"):
            print(f"check-domain: BLOCKED — {_verdict['checkout']} holds a .git pointer "
                  "file that does not parse, so this code cannot say which repository "
                  "owns it or whether it is in a legal place.", file=sys.stderr)
            print("  A checkout that cannot be placed is not one to write into. Repair "
                  "or remove it.", file=sys.stderr)
            sys.exit(2)
        print(f"check-domain: BLOCKED — {target} is inside a git worktree that is not "
              f"under {harness_boundary.WORKTREES_SEGMENT}/.", file=sys.stderr)
        print(f"  Worktrees belong under {_verdict['expected']}", file=sys.stderr)
        print(f"  That tree ({_verdict['checkout']}) should be removed with "
              "`git worktree remove` rather than written into.", file=sys.stderr)
        sys.exit(2)

    if _verdict["outcome"] == "not_a_domain_question":
        # bash-write-guard.sh already said so ("outside repo — not this hook's
        # problem"), and this hook did not: a scratch script at /tmp/x.py was legal via
        # Bash and blocked via Write, so an agent learned to route around a hook whose
        # own message said not to. /tmp, /var/folders and unrelated checkouts keep
        # exactly today's behaviour.
        return

    rel = _verdict["rel"]

    if _verdict["outcome"] == "allow":
        # AFTER the domain verdict, and on the ALLOW path deliberately: harness-pm IS
        # granted plan.yaml and BRIEF.md whole, so a fragment denial placed on the deny
        # path would never fire. This is the difference between the words "except
        # ## Approval" being a COMMENT beside a grant and being enforced.
        feature_checkout_guard(_verdict["rel"], target)
        approval_guard(rel, agent)
        return

    if _verdict["outcome"] == "shared":
        feature_checkout_guard(_verdict["rel"], target)
        # Shared paths are owned by nobody and always serialized (DEC-85). Allow the
        # write, but say so — an unnoticed shared-file edit is how two agents collide.
        print(f"check-domain: {agent} is writing SHARED path {rel} "
              f"(owned by nobody, must be serialized).", file=sys.stderr)
        return

    # ACTIONABLE REJECTION (DEC-100b). A probe confirmed that naming only the rejected
    # path leaves an agent with no basis for choosing a valid alternative, so always
    # print what it MAY write. The module computed the two lists; the WORDING stays
    # here, because the agent-facing verdict names this hook and no other.
    _advertise = _verdict["advertise"]
    _shared_advertise = _verdict["shared_advertise"]
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
    ".harness/*/features/*/feature.json",
    ".harness/*/features/*/runs/*/state.yaml",
    ".harness/*/features/*/notes/handoff-*.md",
    ".harness/*/features/*/STATE.md",
    # plan.yaml (FEAT-41 T-09). The PostToolUse Bash route is the ONE route this rule cannot
    # deny before the fact — a shell write carries a command, not a path — so the sweep is
    # where a dead station word gets caught after it lands.
    ".harness/*/features/*/plan.yaml",
)
# ROOT-LEVEL ONLY. The worktree half used to be spelled here as the segment joined to ONE
# star, which assumed exactly one directory after it: under a `<segment>/<repo>/<id>/`
# layout it reached NO FILE IN ANY WORKTREE, and a glob that matches nothing reports
# nothing — a silent regression, never a refusal. FEAT-30 T-04 derives the worktree
# patterns at sweep time from `harness_boundary.linked_worktrees`, which enumerates the
# checkouts git itself registered, so no depth is assumed anywhere.
SWEEP_GLOBS = tuple(_SWEEP_PATTERNS)
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

# Guards the post-sweep's clean-tracked skip and nothing else. False reproduces the
# pre-2026-08-21 behaviour exactly: every candidate whose mtime beats the mark is swept,
# including the fresh copy `git worktree add` just materialised. Nothing outside this
# file's source text changes it — no environment variable, no flag — so a test proves its
# own assertions are load-bearing by mutating this literal, BY NAME, in a COPY of this
# file. Same pattern as expertise-merge.py's UNION_APPLY and feature-worktree.py's
# REFUSE_ON_DIRTY.
SWEEP_SKIP_CLEAN_TRACKED = True
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
    """Repo-relative, or relative to the checkout the path stands in (DEC-143).

    FEAT-30 T-04: this was the FOURTH consumer of the fixed-segment strip and the only
    one that spelled the segment as its own inline literal — at `eeabc59` it never
    referenced `WORKTREES_SEGMENT` at all. That is why the shape caps went dark under a
    two-level layout while every gate stayed green.

    MEASURED at `eeabc59`, `harness-orchestrator` writing a 204-line STATE.md against a
    120-line budget, same repo-relative path in three places: the main checkout refused
    with the SHAPE reason naming DEC-150; one-level `.claude/worktrees/WT1` also refused
    with that shape reason; two-level `.claude/worktrees/harness/WT1` refused with the
    DOMAIN reason instead. The third never reached the shape gate — the old regex left the
    repository segment in the path, so `WT1/.harness/...` matched none of
    `RE_FEATURE_JSON`, `RE_STATE_YAML`, `RE_HANDOFF` or `RE_STATE_MD`. Fixing classify and
    the resolve path alone would have lifted the domain refusal that was MASKING it:
    writes succeed, budgets unenforced, suite green.

    Reading the segment from the constant in one place also strengthens the existing
    `WORKTREES_SEGMENT` mutation proof in `test-bash-write-guard.py` — mutating the
    constant now reaches this consumer too, where before it left this second copy
    untouched and the proof was blind to it.

    THE IMPORT ABSORBS FAILURE, deliberately, and falls back to the base-relative value.
    The shape phase must not gain a fail-closed dependency: that would block the main
    session on the very write that repairs the module.
    """
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    try:
        import harness_boundary as _hb
        _ck = _hb.checkout_relative(os.path.abspath(path))
        if _ck is not None and _hb.real(_ck[0]) != _hb.real(root):
            return _ck[1]
    except Exception:
        pass
    return rel


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
_I = re.IGNORECASE
RE_FEATURE_JSON = re.compile(r"^\.harness/[^/]+/features/[^/]+/feature\.json$", _I)
RE_STATE_YAML   = re.compile(r"^\.harness/[^/]+/features/[^/]+/runs/[^/]+/state\.yaml$", _I)
RE_HANDOFF      = re.compile(r"^\.harness/[^/]+/features/[^/]+/notes/handoff-[a-z0-9-]+\.md$",
                             _I)
RE_STATE_MD     = re.compile(r"^\.harness/[^/]+/features/[^/]+/STATE\.md$", _I)
# CLAUDE.md (issue #139). Not a state file, and included here anyway because this is
# where the four-route machinery already lives — the alternative was a fifth gate.
RE_CLAUDE_MD    = re.compile(r"^CLAUDE\.md$", _I)
RE_RUN_DIGEST   = re.compile(r"^\.harness/[^/]+/features/[^/]+/runs/[^/]+/digest\.md$", _I)
RE_PLAN_YAML    = re.compile(r"^\.harness/[^/]+/features/[^/]+/plan\.yaml$", _I)
# RE_RUN_DIGEST is deliberately absent from SHAPE_PATTERNS and the post-hoc sweep globs (FEAT-50).
# That rule needs the content that existed BEFORE a whole-file Write. After the write, comparing
# the file with itself cannot fire and would advertise enforcement that does not exist. It carries
# `_I` anyway, for the same reason every pattern here does (F-04, below): a spelling is not a route.
#
# plan.yaml IS PRESENT NOW, AND THAT REVERSES DEC-182 (FEAT-41 T-09, REQ-05). What stood here
# argued the file was deliberately absent because it carries neither a budget nor a vocabulary
# rule, and because a plan.yaml check would be a PARSE check that check-plan-routes.py already
# performs before signature. That reasoning is not wrong so much as silent on a third thing it
# never considered: a WRITE DENIAL.
#
# plan.yaml IS PRESENT, AND THAT REVERSES DEC-182 (FEAT-41 T-09, REQ-05). What stood here argued
# the file was deliberately absent because it carries neither a budget nor a vocabulary rule, and
# because a plan.yaml check would be a PARSE check that check-plan-routes.py already performs
# before signature. That reasoning is not wrong so much as silent on a third thing it never
# considered: a WRITE DENIAL.
#
# plan.yaml now has exactly ONE writer — plan-merge.py, whose verbs take the merge lock, validate
# the station against the vocabulary BEFORE opening the file, and parse the spliced result before
# replacing it. So an editor write is not a shape violation to be MEASURED; it is a route that no
# longer exists. Nothing here duplicates check-plan-routes.py: that tool judges a document, this
# one refuses an author.
#
# IN THE SHAPE REGION, NEVER THE DOMAIN REGION. check-domain exits 0 for a payload with no
# agent_type, so a denial in the domain region would exempt the main session — the one author
# most likely to hand-edit a plan. DEC-180 makes the shape gate independent of domain and
# binding on every author, which is the property this rule needs.
#
# EVERY PATTERN IS CASE-INSENSITIVE, AND THAT CLOSES F-04. The panel found `Plan.yaml` walking
# straight past this denial. Measured on this workstation: `echo x > Plan.yaml` beside an
# existing plan.yaml overwrites it and reports the SAME INODE, so the alternate spelling was a
# write to the real plan that the gate exited 0 on with no stderr at all.
#
# THE WHOLE TUPLE, NOT JUST THE PLAN. The other five carry the same hole and it would be a
# special case to leave them: a `Feature.json` evades the 300-line budget and a `Claude.md`
# evades the 80-line one. The harms differ in KIND -- for plan.yaml a prohibition is bypassed,
# for the rest a measurement is skipped -- but the cause is one, so the fix is one.
#
# IT DENIES ON A CASE-SENSITIVE FILESYSTEM TOO, where `Plan.yaml` is a genuinely different
# file. Deliberate: every pattern here is ANCHORED, so nothing legitimate is swallowed
# (`plan.yaml.bak` and `myplan.yaml` are asserted still allowed), and a loud refusal of a name
# nobody legitimately writes is a far better error than a silent bypass of the only write
# denial this gate has.
#
# THE ON-DISK NAME IS UNAFFECTED, which is why the Bash post-sweep's globs below need no
# change: writing `Plan.yaml` over an existing plan.yaml keeps the original lowercase name, so
# the sweep still finds the file. Only the pre-write route denial could be walked past.
#
# THE TWO PATTERN RULES POINT OPPOSITE WAYS ON PURPOSE: RE_RUN_DIGEST stays OUT of SHAPE_PATTERNS
# because its check cannot fire after the fact (FEAT-50), while RE_PLAN_YAML goes IN because its
# check is a route denial that must fire before it.
SHAPE_PATTERNS = (RE_FEATURE_JSON, RE_STATE_YAML, RE_HANDOFF, RE_STATE_MD, RE_CLAUDE_MD,
                  RE_PLAN_YAML)


def has_shape_rules(rel):
    """Cheap path-only predicate: could shape_problems have anything to say about `rel`?

    RENAMED from is_state_file/STATE_PATTERNS. CLAUDE.md is not a state file, and a
    predicate whose name says otherwise is the category error a reviewer flagged — the
    next reader looking for "why is CLAUDE.md in the state-file set" finds no answer
    because the premise is wrong. The gate is about SHAPE; state files are most of what
    has a shape, not the definition of it."""
    return any(p.match(rel) for p in SHAPE_PATTERNS)


_SCHEMA_UNAVAILABLE_SAID = False


def shape_problems(rel, content, display=None, absolute_path=None):
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

    # Issue #1058: a lead reused a cycle's run directory and a plain digest.md overwrite
    # destroyed the cycle-0 record. This guard is intentionally Write/PRE-only: Edit and
    # Bash carry no complete incoming payload to compare, and POST is already too late.
    if RE_RUN_DIGEST.match(rel) and absolute_path is not None:
        prior = None
        try:
            with open(absolute_path, encoding="utf-8", errors="replace") as prior_file:
                prior = prior_file.read()
        except FileNotFoundError:
            if not os.path.lexists(absolute_path):
                prior = ""
        except OSError:
            pass
        if prior is None:
            out.append(_head("run digest already exists but cannot be read safely; "
                             "refusing a Write that could destroy its recorded content."))
        elif prior.strip() and not content.startswith(prior):
            out.append(_head("run digest already holds a recorded digest; this Write "
                             "would replace rather than extend it. Write this cycle's "
                             "digest into a run directory of its own."))
    if RE_PLAN_YAML.match(rel):
        # THE VOCABULARY RULE, AND IT IS THE ONLY THING THE SWEEP CAN JUDGE (FEAT-41 T-09).
        # Every task status, and the top-level status WHEN PRESENT, must be a mandated station
        # or the terminal marker — IMPORTED from factory_config, never respelled here, because a
        # second copy of the vocabulary is exactly the drift FEAT-41 exists to remove.
        #
        # WHAT THIS CATCHES AND WHAT IT DOES NOT, stated rather than left to be discovered: a
        # dead word or a broken file, yes. A shell write of a LEGAL value, NO — this reads disk
        # and cannot attribute an author, so a `sed` that lands a legal station is
        # indistinguishable from the tool doing its job. The Write and Edit denial below is what
        # closes the editor routes; this is the net under the one route that cannot be denied
        # before the fact.
        #
        # A MISSING TOP-LEVEL status IS LEGAL, and that is a contract rather than an oversight.
        # T-07 is what adds the key to most plans and is NOT a dependency of this task, so the
        # two are unordered: a rule that REQUIRED the key would report a violation on every
        # un-migrated plan this sweep touches. An absent TASK status is legal for the same
        # reason — T-04 leaves it out of harness_yaml's REQUIRED_TASK_FIELDS, and an absent one
        # reads as the not-started station. Only a value OUTSIDE the vocabulary is reported.
        #
        # NOT deny(). Its last line appends the module-level ROUTING constant, which speaks
        # about STATE.md, digests and notes/ — a different file class entirely. See the comment
        # further down that already records this trap in its own words: ONE ROUTING SENTENCE PER
        # FINDING.
        import factory_config as _fc
        # MANDATED_STATIONS, not station_names(board): the declaration itself, with no
        # board to consult. This gate has no board and needs none — the vocabulary is
        # fixed (T-01), and station_names() exists for the COLUMN derivation.
        _legal = set(_fc.MANDATED_STATIONS) | {_fc.TERMINAL_MARKER}
        _bad = []
        try:
            import harness_yaml as _hy
            _doc = _hy.load_str(content, display or rel)
        except Exception:
            # UNPARSEABLE IS NOT THIS RULE'S FINDING. check-plan-routes.py refuses a malformed
            # plan before signature and check-state.sh refuses it again at entry; reporting it
            # a third time here would put one defect in three voices.
            _doc = None
        if isinstance(_doc, dict):
            _top = _doc.get("status")
            if _top is not None and str(_top) not in _legal:
                _bad.append(f"top-level status {str(_top)!r}")
            _tasks = _doc.get("tasks")
            if isinstance(_tasks, list):
                for _t in _tasks:
                    if not isinstance(_t, dict):
                        continue
                    _s = _t.get("status")
                    if _s is not None and str(_s) not in _legal:
                        _bad.append(f"task {_t.get('id', '(no id)')} status {str(_s)!r}")
        if _bad:
            out.append(_head("plan.yaml station vocabulary (FEAT-41 REQ-01)."))
            out.extend(f"  {b} is not a station" for b in _bad)
            out.append(f"  The stations are {', '.join(sorted(_legal))}. "
                       f"Set one with plan-merge.py set-task-station or set-feature-station, "
                       f"which validate the value before it lands.")

    if RE_FEATURE_JSON.match(rel):
        # 300, not 200: FEAT-10 measures 173 lines with 32 runs, roughly 5 lines per run.
        # The comment-line budget is GONE, not relaxed — JSON has no comments, so it could
        # never fire, and a check that cannot fire is a check a reader trusts.
        problems = []
        if len(lines) > 300:
            problems.append(f"feature.json is {len(lines)} lines — budget is 300. It is data a script "
                            f"parses, not a journal.")
        if problems:
            deny(problems)

        # THE SCHEMA CHECK. Imported INSIDE this branch, never at module level: jsonschema
        # costs +42.6 ms median on import (17.3 -> 59.9 ms over 10 isolated launches,
        # 4.26.0, warm bytecode; 395 ms cold). At module level every Write, Edit and Bash
        # in the repo would pay it, for the rare feature.json write. sys.modules caches it,
        # so a POST sweep over many candidates pays it ONCE per invocation, not per file.
        # This file already defers harness_yaml for the same reason (see :139).
        #
        # THE TIGHT try IS FOR feature_schema ITSELF being unimportable — PYTHONPATH not
        # exported, a syntax error, the file missing. It must APPEND to problems, never
        # raise: a raise escaping the per-file loop exits 1, and :14 says exit 1 is
        # NON-BLOCKING, so the bad write would land — fail open in the case the checker
        # exists for.
        #
        # FAIL CLOSED, WITH NO BOOTSTRAP ESCAPE, stated as facts rather than as a
        # comfortable story: the shape phase runs for EVERY writer including the main
        # session, because the no-agent_type carve-out is the _governed FLAG and not an
        # exit. So this denial governs the main-session-direct migration tasks too,
        # deliberately. It does NOT share the PyYAML bootstrap escape —
        # require_or_bootstrap is reached only inside `if _run_domain:` (:333), which the
        # shape phase never enters. No escape is needed: the remedy is `python3 -m pip
        # install jsonschema`, a Bash command no gate denies. That is the difference from
        # the missing-PARSER case, where the gate cannot read its own manifest at all.
        # This branch needs stdlib json and jsonschema ONLY, never PyYAML — do not extend
        # the state.yaml branch's `_no_parser` fail-open to cover it.
        global _SCHEMA_UNAVAILABLE_SAID
        try:
            import feature_schema
            # ISSUE #749 — THE SCHEMA COMES FROM THE TREE THE FILE LIVES IN. `rel` already
            # carries the worktree prefix when the target is inside one, so joining it with
            # `root` gives the real absolute path and feature_schema walks UP from there for
            # that checkout's own feature-schema.json.
            #
            # Measured live 2026-08-23: this refused `source_issues` at /github on a FEAT-26
            # write. The key WAS declared in that worktree's schema and was NOT in main's,
            # and this module is imported through CLAUDE_PROJECT_DIR — the main checkout. So
            # a feature that ADDS a schema key could not write data using it until it
            # merged, and could not demonstrate it working before merging.
            #
            # It falls back to the module's own schema when no checkout schema is above the
            # path, so a target outside any checkout is checked exactly as before.
            _sp = feature_schema.problems_for_text(
                content, display or rel,
                for_path=os.path.join(root, rel) if root else rel)
        except ImportError:
            _sp = ["feature_schema is not importable, so this file CANNOT be checked. "
                   "Expected at .agents/skills/harness/bin/feature_schema.py, reachable on "
                   "PYTHONPATH. Repair the module or reinstall the harness bin directory."]
        except Exception as _se:
            # A BARE `except ImportError` HERE WAS A FAIL-OPEN, and the panel measured it:
            # inject any other exception into problems_for_text and an ILLEGAL document
            # that must exit 2 escapes at exit 1 with a traceback instead — and exit 1 is
            # NON-BLOCKING (line 14), so the bad write lands. A schema loader raises far
            # more than ImportError: a malformed feature-schema.json is JSONDecodeError,
            # an unreadable one is OSError, a jsonschema version drift is SchemaError.
            # Every one of them meant "written anyway".
            #
            # The message is SEPARATE from the ImportError branch on purpose. Saying "not
            # importable" when the module imported fine and then crashed sends the reader
            # to check PYTHONPATH for a fault that is not there — an unattributable
            # finding, the defect DEC-180 fixed twice in this file.
            _sp = ["feature_schema CRASHED while checking this file, so it CANNOT be "
                   "checked: %s: %s. The module IMPORTED — this is a fault inside it or "
                   "in .agents/skills/harness/bin/feature-schema.json, not a missing "
                   "dependency. The write is DENIED rather than allowed through, because "
                   "a checker that cannot run must never be the reason a file passes."
                   % (type(_se).__name__, _se)]
        _out = []
        for _l in _sp:
            if "CANNOT be checked" in _l:
                # ONE MESSAGE PER INVOCATION, not one per file — a corpus-wide sweep would
                # otherwise print an identical block per feature.
                if _SCHEMA_UNAVAILABLE_SAID:
                    continue
                _SCHEMA_UNAVAILABLE_SAID = True
            _out.append(_l)
        if _out:
            # APPEND TO `out`, never print-and-exit. deny() ACCUMULATES — it does not
            # exit — and shape_problems RETURNS its findings to two call sites. A block
            # that printed and exited here would pre-empt the line-budget finding above
            # and bypass the accumulator both callers read. Found by the suite: the
            # 301-line case reported a schema denial instead of its budget denial.
            #
            # ONE ROUTING SENTENCE PER FINDING, which is why this does not call deny():
            # deny() appends the module-level ROUTING constant, speaking about STATE.md,
            # digests and notes/ — a different sentence from the schema's own redirection
            # line, which also names plan.yaml approval.rulings. Two routing sentences in
            # one stderr stream contradict each other about the same file class. The
            # line-budget finding above keeps deny() and therefore keeps ROUTING: it is
            # not a schema finding and its advice is still right.
            out.append(_head("feature execution-state schema."))
            out.extend(f"  {_l}" for _l in _out)

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
        # all have one: expertise 150, feature.json 300, handoff 60, STATE.md 120.
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
                       "biography (DEC-158); rationale belongs in .harness/harness/docs/DECISIONS.md.")

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
# `targets` is [(repo-relative path, file text, display path, absolute path)]. Building it
# is the ONLY thing the two modes disagree about; the gate itself consumes one uniform tuple.
targets = []

# THE plan.yaml ROUTE DENIAL, AND IT SITS AHEAD OF EVERY MODE SPLIT BELOW (FEAT-41 T-09).
#
# WHY HERE AND NOT IN shape_problems' OWN BRANCH. Everything below this point is built around
# MEASURING TEXT: the PRE route exits 0 for any tool but `Write` because only `Write` carries a
# whole-file `content`, which is exactly right for a budget or a key whitelist. This rule is not
# a measurement. It refuses a ROUTE, and a route is fully known from the path and the tool name
# alone — so an `Edit`, which never carries content and would therefore exit 0 four lines below,
# has to be refused before that gate rather than inside it.
#
# BOTH ROUTES, EVERY AUTHOR, AND ONLY BEFORE THE FACT. In POST the write has already landed and
# exit 2 merely carries stderr back; the vocabulary net in shape_problems is what speaks there.
# A SYMLINK IS A ROUTE, AND ITS NAME IS NOT (FEAT-41 H-01).
#
# This is NOT the realpath fix case 8 of the T-09 suite refused, and the distinction is the
# whole point. That one wanted to replace shape-matching WITH resolution, which would have
# WEAKENED the gate: `./`, a `notes/..` traversal, a doubled slash, an absolute path and a
# symlinked feature DIRECTORY are all denied today precisely because the shape of the path as
# written still ends `<something>/plan.yaml`. This ADDS the resolved target as a second thing to
# match, so nothing denied today becomes allowed.
#
# A SYMLINKED FILE IS THE OPPOSITE SHAPE FROM A SYMLINKED DIRECTORY. `notes/innocent.md ->
# plan.yaml` is innocent at every component, so no pattern can match what the author typed,
# while the write lands in the plan. Measured on this runtime: the Write tool FOLLOWS a symlink
# — the link stayed a link and the target's bytes changed — so the route is real, and it runs
# through a path every squad member is already granted.
# WHY BOTH SIDES ARE RESOLVED, recorded because the wrong version shipped once. The first fix used
# `realpath` on the path alone and left the case RED: `/var` is itself a link to `/private/var`
# here, so resolving one side put the result in a different spelling namespace, `_norm` could not
# strip the checkout prefix, and the shape match silently saw nothing. The reaction was to walk
# `readlink` hops instead, which stayed in the right namespace but resolved only the FINAL
# component and capped the walk -- leaving a linked parent directory invisible and a long chain
# failing OPEN (FEAT-41 C2-02). Resolving the ROOT as well removes the original reason, and with
# it the hop cap: realpath follows a chain of any length and raises on a loop.


def _resolved_rel(path):
    """Repo-relative form with EVERY component resolved, or None if it cannot be resolved.

    BOTH SIDES ARE REALPATH'D, and that is the correction to H-01's first fix (FEAT-41 C2-02).
    That version resolved only the final component, so a LINKED PARENT DIRECTORY was invisible:
    `features/<F>/alias/plan.yaml` where `alias -> ../FEAT-OTHER` adds a segment, and
    `RE_PLAN_YAML` anchors on `features/<one segment>/plan.yaml`, so it matched nothing while the
    write landed in another feature's real plan.

    It also replaces the hop walk, which existed only because realpath was used on ONE side:
    `/var` is itself a link to `/private/var` here, so resolving the path but not the root left a
    relpath full of `..` that matched no pattern. Resolving the root too removes that reason, and
    with it the hop cap -- realpath follows a chain of ANY length.

    IT DOES NOT RAISE ON A LOOP, and this docstring claimed it did (FEAT-41 MF-5). MEASURED:
    `os.path.realpath` is non-strict by default and returns the path resolved as far as it can, so
    a symlink loop RESOLVES. A case asserts a loop stays allowed, because a wrong claim here was
    the justification for a fail-closed branch that could never fire.

    ValueError IS CAUGHT, NOT ONLY OSError (FEAT-41 MF-2). realpath raises ValueError on an
    embedded NUL, which used to propagate out of this whole Python body -- and by this file's own
    header exit 1 is NON-BLOCKING, so the write proceeded. `_plan_route` runs unconditionally, so
    one NUL took budgets, domain grants and the route denial down together.
    """
    try:
        return os.path.relpath(os.path.realpath(path), os.path.realpath(root))
    except (OSError, ValueError):
        return None


def _hardlink_plan(path):
    """The plan.yaml this path IS under another name, or None.

    A HARDLINK IS NOT A PATH QUESTION (FEAT-41 C2-02). It has no target to read -- it IS the
    file, so `os.path.islink` is False and no amount of resolution can see it. Only identity can.

    `st_nlink < 2` is the cheap gate and it keeps this off the common path: a file with one link
    cannot be a hardlink to anything, which is every ordinary write. Only a genuinely multiply-
    linked file reaches the scan.
    """
    try:
        st = os.stat(path)
    except (OSError, ValueError):
        # ValueError for the same reason as `_resolved_rel` -- an embedded NUL (FEAT-41 MF-2).
        return None
    if st.st_nlink < 2:
        return None
    import glob as _glob
    for cand in _glob.glob(os.path.join(root, ".harness", "*", "features", "*", "plan.yaml")):
        try:
            cs = os.stat(cand)
        except OSError:
            continue
        if (cs.st_ino, cs.st_dev) == (st.st_ino, st.st_dev):
            return _norm(cand)
    return None


def _plan_route(path):
    """The plan this write would reach, or None. Names the TARGET, never only the link."""
    as_typed = _norm(path)
    if RE_PLAN_YAML.match(as_typed):
        return as_typed
    resolved = _resolved_rel(path)
    if resolved is None:
        # UNRESOLVABLE IS ITS OWN ANSWER, AND IT IS A REFUSAL (FEAT-41 MF-5, and MF-2's remedy
        # lands here). This used to be conditional on `os.path.islink(path)`, which made it DEAD
        # for the case it mattered for: measured, `os.path.islink` on a NUL-bearing path is
        # False, so widening `_resolved_rel`'s except to return None would have reopened the hole
        # two lines from its own fix. Cycle 3's panel saw that coupling; neither of its reviewers
        # could, because one found the crash and the other found the dead branch.
        #
        # REFUSING IS SAFE BECAUSE NON-STRICT realpath ALREADY SUCCEEDS FOR ABSENT PATHS. The
        # only ways left to be unresolvable are pathological -- a NUL, or an OS-level path error.
        # Ordinary work never produces one, and a first write to a not-yet-existing note resolves
        # fine, which its own negative control asserts.
        return as_typed
    if RE_PLAN_YAML.match(resolved):
        return resolved
    return _hardlink_plan(path)


_reached_plan = _plan_route(target) if target else None
if not _post and _tool in ("Write", "Edit", "NotebookEdit") and _reached_plan:
    # THE REASON COMES FIRST, THEN THE ROUTE. A denial that says only what to use instead is
    # indistinguishable from a stuck or over-broad gate, and a reader who takes it for a harness
    # malfunction routes around it through a shell write of a legal station value — the one
    # channel the sweep above admits it cannot attribute to an author. So the refusal has to
    # earn its own credibility in its first sentence.
    # THE BASENAME IS THE ONE THAT EXISTS BESIDE THIS SCRIPT. A refusal naming a file that is
    # not there is unusable — the very failure the reason clause exists to prevent. This script
    # and the writer live in the same bin directory, and the invariant that keeps them together
    # is that both are named in run-unit-tests.sh's own script list.
    _writer = "plan-merge.py"
    # WHEN A LINK IS THE ROUTE, THE DENIAL NAMES WHERE THE WRITE LANDS (FEAT-41 H-01). Refusing
    # `notes/innocent.md` with no further explanation reads as a malfunction, which is the one
    # outcome the reason clause above exists to prevent — and the reader who believes it routes
    # around the gate through a shell write.
    _via = ("" if _reached_plan == _norm(target)
            else f" — the write would land in {_reached_plan}, which it links to")
    sys.stderr.write(
        f"check-domain: DENIED — {_show(target)}{_via}: plan.yaml has exactly ONE writer, "
        f"{_writer}, because every station value must be validated against the vocabulary "
        f"before it lands on disk. An editor write cannot do that, so this is not a shape "
        f"violation to be measured — it is a route that no longer exists (FEAT-41 REQ-05, "
        f"reversing DEC-182).\n"
        f"  Record a task's station:      python3 .claude/skills/harness/bin/{_writer} "
        f"set-task-station --file <plan.yaml> --task T-NN --station <station>\n"
        f"  Record the feature's station: python3 .claude/skills/harness/bin/{_writer} "
        f"set-feature-station --file <plan.yaml> --station <station>\n"
        f"  Add tasks:                    python3 .claude/skills/harness/bin/{_writer} "
        f"add-tasks --file <plan.yaml> --proposal <path>\n"
        f"  Apply a proposal:             python3 .claude/skills/harness/bin/{_writer} "
        f"apply --file <plan.yaml> --proposal <path>\n")
    sys.exit(2)

# FEAT-51: a Claude Code child whose parent is gone may finish analysis, but it may
# not race a replacement writer onto a canonical feature artifact. The explicit
# quarantine path is inert until the resumed parent adopts it.
if (_governed and not _post and _tool in ("Write", "Edit", "NotebookEdit")
        and target):
    _orphan_rel = _norm(target)
    _orphan_basename = os.path.basename(_orphan_rel)
    if _orphan_basename in ("plan.yaml", "BRIEF.md", "feature.json", "STATE.md"):
        try:
            import inflight_registry as _reg
            _artifact = _reg.canonical_artifact(_orphan_rel)
            if _artifact is not None:
                _feature, _basename = _artifact
                _session = d.get("session_id")
                if _reg.orphan_write(root, agent, _feature, _session):
                    _quarantine = _reg.quarantine_rel(
                        _orphan_rel, agent, _session
                    )
                    sys.stderr.write(
                        f"check-domain: BLOCKED — {_show(target)} is canonical, but "
                        f"{agent} holds no live claim for {_feature}. Its parent is gone "
                        f"and a replacement may already be writing.\n"
                        f"  Write the completed result to {_quarantine} instead.\n"
                        f"  It becomes canonical only when the resumed parent runs "
                        f"quarantine.py adopt on that file.\n"
                    )
                    sys.exit(2)
        except Exception as _e:
            print(
                f"check-domain: quarantine boundary was not enforced ({_e!r}) — "
                "passing through.",
                file=sys.stderr,
            )

if not _post:
    # PRE. Only `Write` carries a whole-file `content` to measure, so only `Write` can be
    # blocked before the fact. `d` was parsed once at the top of this process (T-13);
    # re-parsing here was leftover from the four-launch version — and inconsistent
    # leftover: this copy exited 0 on a failure the first one absorbed with `d = {}`, so
    # the two disagreed about what a bad payload means. Review finding 2.
    if _tool != "Write" or not target:
        sys.exit(0)
    targets = [(_norm(target), (d.get("tool_input") or {}).get("content") or "",
                _show(target), os.path.abspath(target))]

elif target:
    # POST, with a named file: Write, Edit, NotebookEdit. Read what LANDED — no
    # reconstruction of `old_string`/`new_string`, no `replace_all` semantics, no TOCTOU
    # window, because the filesystem already holds the answer those would approximate.
    # CLASSIFIED BY WHERE THE WRITE LANDED, NOT BY WHAT WAS TYPED (FEAT-41 H-01). POST opens
    # `os.path.abspath(target)`, which FOLLOWS a link — so without this the reporter would read
    # the plan's bytes and then look up shape rules under the link's innocent name, find none,
    # and exit 0. The PRE denial above already refuses this route for every editor tool; this is
    # the same mechanism on the reporting side, so the two cannot drift apart.
    _rel = next((c for c in (_norm(target), _resolved_rel(target), _hardlink_plan(target))
                 if c and has_shape_rules(c)), _norm(target))
    if not has_shape_rules(_rel):
        sys.exit(0)
    try:
        with open(os.path.abspath(target), encoding="utf-8", errors="replace") as _f:
            targets = [(_rel, _f.read(), _show(target), os.path.abspath(target))]
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
    # THE SWEEP SURFACE: the five patterns at the root, plus the same five inside every
    # checkout git has registered as a linked worktree of this root. ABSORBING, and that
    # matters: an unimportable module must leave the root-level sweep working exactly as it
    # does today rather than taking the whole reporter down.
    # Each entry is (the checkout the pattern belongs to, the glob). The checkout is
    # carried because `_unmodified_since_commit` below asks git a question that only makes
    # sense relative to ONE checkout, and a worktree is a checkout of its own.
    _sweep = [(root, os.path.join(root, _p)) for _p in SWEEP_GLOBS]
    try:
        import harness_boundary as _hb_sweep
        for _wt_root in _hb_sweep.linked_worktrees(root):
            _sweep.extend((_wt_root, os.path.join(_wt_root, _p)) for _p in SWEEP_GLOBS)
    except Exception:
        pass

    # --- mtime IS NOT EVIDENCE OF A WRITE AFTER A CHECKOUT OPERATION.
    #
    # MEASURED 2026-08-21: `feature-worktree.py create` ran `git worktree add`, which
    # materialises a fresh copy of every tracked file, so all 126 files matching
    # SWEEP_GLOBS in the new checkout carried an mtime of that second. The sweep has no
    # status filter — it asks only `st_mtime > _since` — so it shape-checked all 126,
    # including 25 features whose status is Done. Two of them hold long-standing shape
    # violations (FEAT-02's STATE.md has five illegal sections; FEAT-05's is 165 lines
    # against the 120 cap), so creating a worktree reported those two files as
    # `OVER BUDGET (already written)` against the agent that cut the tree.
    #
    # THAT REPORT IS FALSE IN THE ONE FIELD AN AGENT ACTS ON: authorship. It names files
    # the agent never opened, and both live outside any ordinary agent's team-config
    # domain — so an agent that obeys the message is DENIED by this same hook. A gate that
    # instructs an agent to perform a write it will then refuse burns cycles on a premise
    # that was never true. And it is not a one-off: every worktree creation from here on
    # floods the sweep with the whole corpus, because DEC-95 makes a worktree per feature
    # the normal path rather than an occasional one.
    #
    # THE DISCRIMINATOR IS CONTENT, NOT TIME. A file `git worktree add` wrote is byte-
    # identical to its committed blob, by construction. A file an agent wrote is either
    # modified against HEAD or untracked. So the sweep now skips a candidate that is
    # clean-tracked in its own checkout and keeps every modified or untracked one.
    #
    # THE COST, STATED RATHER THAN DISCOVERED: an agent that writes content byte-identical
    # to what is already committed is no longer reported here. That write introduces no
    # uncommitted change, and the committed corpus is check-state.sh's sweep, not this
    # one — INV-23 reported both STATE.md files above on every run while this hook stayed
    # silent about them until a worktree appeared. Two gates, two scopes: check-state.sh
    # owns what is committed, this hook owns what a Bash command just wrote.
    #
    # ABSORBING, deliberately, and it fails OPEN to today's behaviour. If git cannot be
    # reached the candidate is swept exactly as it is now. The alternative — treating an
    # unanswerable question as "clean" — would disable the sweep silently, which is this
    # repository's most-filed defect shape.
    import subprocess as _subprocess
    _clean_cache = {}

    def _unmodified_since_commit(_checkout):
        """The set of repo-relative paths in `_checkout` that DIFFER from HEAD or are
        untracked, or None when git could not answer. None means sweep everything.

        Two `-z` calls rather than one `status --porcelain`: with -z a rename record emits
        the original path as a second NUL-separated field carrying no status prefix, so a
        naive split invents a path. `diff --name-only` and `ls-files --others` both emit
        plain NUL-separated paths with no prefixes and no quoting to undo."""
        if _checkout in _clean_cache:
            return _clean_cache[_checkout]
        _found = None
        try:
            _dirty = set()
            for _argv in (["diff", "--name-only", "-z", "HEAD"],
                          ["ls-files", "-z", "--others", "--exclude-standard"]):
                _r = _subprocess.run(["git", "-C", _checkout] + _argv,
                                     capture_output=True, text=True, timeout=15)
                if _r.returncode != 0:
                    raise RuntimeError(_r.stderr)
                _dirty.update(_x for _x in _r.stdout.split("\0") if _x)
            _found = _dirty
        except Exception:
            _found = None
        _clean_cache[_checkout] = _found
        return _found

    for _checkout, _pat in _sweep:
        _dirty_set = _unmodified_since_commit(_checkout)
        for _p in _glob.glob(_pat):
            try:
                if os.stat(_p).st_mtime <= _since:
                    continue
                # SKIP A CLEAN-TRACKED CANDIDATE. `_dirty_set is None` means git could
                # not answer, and then nothing is skipped.
                if SWEEP_SKIP_CLEAN_TRACKED and _dirty_set is not None:
                    _rel_in_checkout = os.path.relpath(
                        os.path.realpath(_p), os.path.realpath(_checkout))
                    if _rel_in_checkout not in _dirty_set:
                        continue
                with open(_p, encoding="utf-8", errors="replace") as _f:
                    # Display stays unstripped; absolute path identifies the exact checkout.
                    targets.append((_norm(_p), _f.read(), _show(_p), _p))
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
# UNIFORM 4-TUPLES. Every route names the match path, content, display path and exact
# on-disk target; mixed arity turns the guard off at exit 1.
for _rel, _text, _disp, _absolute in targets:
    _problems.extend(shape_problems(_rel, _text, display=_disp,
                                    absolute_path=_absolute))

if _problems:
    for _line in _problems:
        print(_line, file=sys.stderr)
    sys.exit(2)

sys.exit(0)
PY
