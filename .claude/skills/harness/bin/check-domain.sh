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
# Do NOT "fix" this by branching on argv instead: `sys.argv[2]` is already consumed below
# as the agent identity, so argv-branching would touch the hook path's identity contract.
if [ "${1:-}" = "--resolve" ]; then
  payload=""
  export HARNESS_RESOLVE_PATH="${2:-}"
else
  unset HARNESS_RESOLVE_PATH
  payload=$(cat)
fi

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

    # Normalise exactly as the hook does, including the worktree strip — a path given
    # from inside .claude/worktrees/<id>/ must resolve against the checkout the agent
    # is standing in, not against a glob nobody wrote.
    _abs = _resolve_target if os.path.isabs(_resolve_target) else os.path.join(root, _resolve_target)
    _rel = os.path.relpath(os.path.normpath(_abs), root)
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
        if any(matches(c, g) for c in _cands for g in _globs):
            _granting.add(_n)
        for g in _shared:
            if any(matches(c, g) for c in _cands) and g not in _shared_hits:
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
if not agent:
    sys.exit(0)

# Only harness agents are subject to domains.
if not agent.startswith("harness-"):
    sys.exit(0)

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

# No parseable path -> do not block. A hook that blocks on its own parse failure
# would break every write the moment the payload shape changes.
if not target:
    sys.exit(0)

# No manifest -> fail OPEN, loudly. Blocking every write in a project that has
# not run /harness-init would be worse than not enforcing.
if not os.access(manifest, os.R_OK):
    print(f"check-domain: no {manifest} — enforcement OFF (run /harness-init).", file=sys.stderr)
    sys.exit(0)

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

    # Compare repo-relative, so an absolute tool path and a relative glob still meet.
    rel = os.path.relpath(os.path.abspath(target), os.path.abspath(root))

    # OUTSIDE THE REPO IS NOT A DOMAIN QUESTION. bash-write-guard.sh:211 already says
    # so ("outside repo — not this hook's problem"), and this hook did not: a scratch
    # script at /tmp/x.py was legal via Bash and blocked via Write, so an agent
    # learned to route around a hook whose own message says not to. Domain control
    # exists for REPO writes; /tmp is not the repo, is not deployed, and is not state.
    #
    # Keyed on the RESOLVED path escaping the root, never on the string ".." — a repo
    # path reached via docs/../src/main.py resolves back inside and must still block.
    if os.path.commonpath([os.path.abspath(target), os.path.abspath(root)]) != os.path.abspath(root):
        return

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
    if any(matches(r, g) for r in rel_candidates for g in globs):
        return

    if any(matches(r, g) for r in rel_candidates for g in shared):
        # Shared paths are owned by nobody and always serialized (DEC-85). Allow the
        # write, but say so — an unnoticed shared-file edit is how two agents collide.
        print(f"check-domain: {agent} is writing SHARED path {rel} "
              f"(owned by nobody, must be serialized).", file=sys.stderr)
        return

    # ACTIONABLE REJECTION (DEC-100b). A probe confirmed that naming only the
    # rejected path leaves an agent with no basis for choosing a valid alternative,
    # so always print what it MAY write.
    permitted = ", ".join(globs) if globs else "(no writable domain declared)"
    print(f"check-domain: BLOCKED — {agent} may not write {rel}", file=sys.stderr)
    print(f"  Permitted for you: {permitted}", file=sys.stderr)
    if shared:
        print(f"  Shared (allowed, serialized): {', '.join(shared)}", file=sys.stderr)
    print(f"  If this path should be yours, it belongs in {os.path.relpath(manifest, root)} "
          f"— do not work around this hook.", file=sys.stderr)
    sys.exit(2)


# The DOMAIN check needs a parser; the STATE-FILE SHAPE gate below mostly does not.
# Review finding 1: the bootstrap-grant `sys.exit(0)` skipped BOTH, so a session with
# no PyYAML could write an unbounded state.yaml with unknown or duplicate top-level
# keys and no denial. Before the T-13 single-interpreter merge those were separate
# launches and the shape gate ran regardless — so this was a regression introduced by
# the merge, not an inherited gap. Skip only what actually needs the parser.
if not _no_parser:
    domain_check()

# `d` was parsed once at the top of this process (T-13). Re-parsing here was leftover
# from the four-launch version — and inconsistent leftover: this copy exited 0 on a
# failure the first one absorbed with `d = {}`, so the two disagreed about what a bad
# payload means. Review finding 2.
if (d.get("tool_name") or "") != "Write":
    sys.exit(0)
content = (d.get("tool_input") or {}).get("content") or ""

rel = os.path.relpath(os.path.abspath(target), os.path.abspath(root))
wt = re.match(r"^\.claude/worktrees/[^/]+/(.+)$", rel)
if wt:
    rel = wt.group(1)

lines = content.splitlines()

def deny(msgs):
    print("check-domain: BLOCKED — state-file shape (DEC-150).", file=sys.stderr)
    for m in msgs:
        print(f"  {m}", file=sys.stderr)
    print("  Routing: current truth REPLACES STATE.md ## Current; per-run findings go in that "
          "run's digest.md; rationale goes in notes/. State files carry no history.",
          file=sys.stderr)
    sys.exit(2)

if re.match(r"^\.harness/features/[^/]+/feature\.yaml$", rel):
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

if re.match(r"^\.harness/features/[^/]+/runs/[^/]+/state\.yaml$", rel):
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
    if _no_parser:
        sys.exit(0)

    try:
        doc = harness_yaml.load_str(content, rel)
    except harness_yaml.DuplicateKeyError as e:
        # D-02: the DEC-156 denial SURVIVES, now raised by the loader rather than
        # counted by a regex — which also catches a duplicate at any nesting depth,
        # not merely at column 0.
        print("check-domain: BLOCKED — state.yaml is a checkpoint, not a notebook (DEC-154).",
              file=sys.stderr)
        print(f"  duplicate key {e.key!r} — the second silently shadows the first; "
              f"replace the placeholder, never append a copy (DEC-156).", file=sys.stderr)
        sys.exit(2)
    except harness_yaml.YamlParseError as e:
        # NEW blocking outcome, deliberate (D-02 consequence #2). The regex this
        # replaced found no keys in a malformed file and therefore reported nothing
        # wrong — it wrote a broken checkpoint and said it was fine.
        print("check-domain: BLOCKED — this state.yaml is not valid YAML.", file=sys.stderr)
        print(f"  {e.original}", file=sys.stderr)
        print("  A checkpoint that cannot be parsed is unreadable to every gate that "
              "consumes it later; the write is refused while you can still fix it.",
              file=sys.stderr)
        sys.exit(2)

    # T-17 / D-08: str() BOTH sides. A parsed key is not necessarily a string —
    # YAML 1.1 resolves `on:`, `off:`, `yes:`, `no:` to booleans and `01:` to an int —
    # so an un-coerced comparison against a set of strings silently reports a real key
    # as unknown, and `sorted()` over mixed types raises outright. In a fail-closed
    # hook a raise is a block on every write, not a wrong answer.
    keys = list(doc) if isinstance(doc, dict) else []
    unknown = sorted({str(k) for k in keys if str(k) not in ALLOWED})
    if unknown:
        print("check-domain: BLOCKED — state.yaml is a checkpoint, not a notebook (DEC-154).",
              file=sys.stderr)
        print(f"  non-checkpoint top-level key(s) {unknown} — findings and assessment prose "
              f"belong in this run's digest.md; a one-line note: per STEP entry is the "
              f"prose ceiling.", file=sys.stderr)
        # Naming the key is required (DEC-100b), but naming it `True` when the author
        # typed `on:` is not actionable — the reader cannot find `True` in their file.
        # Say what happened instead of leaving them to guess.
        if any(not isinstance(k, str) for k in keys):
            odd = sorted(f"{k!r} ({type(k).__name__})" for k in keys if not isinstance(k, str))
            print(f"  NOTE — {', '.join(odd)} came from an UNQUOTED key that YAML resolved to a "
                  f"non-string: `on`/`off`/`yes`/`no`/`true`/`false` become booleans and `01` "
                  f"becomes an int (YAML 1.1). Quote the key to keep it a string.",
                  file=sys.stderr)
        sys.exit(2)

if re.match(r"^\.harness/features/[^/]+/notes/handoff-[a-z0-9-]+\.md$", rel):
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
        print("check-domain: BLOCKED — handoff shape (DEC-159).", file=sys.stderr)
        for m in problems:
            print(f"  {m}", file=sys.stderr)
        sys.exit(2)

if re.match(r"^\.harness/features/[^/]+/STATE\.md$", rel):
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

sys.exit(0)
PY
