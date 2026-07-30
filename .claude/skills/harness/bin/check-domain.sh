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

payload=$(cat)

# Agent identity: prefer `agent_type` from the hook payload, fall back to $1.
#
# WHY BOTH: agent-frontmatter PreToolUse hooks DO NOT FIRE for spawned subagents in
# this environment — verified three times with three command forms, zero executions
# (DEC-110). So the hook is registered in settings.json instead, where it does fire,
# and identity has to come from the payload because one global registration serves
# every agent.
agent="$(printf '%s' "$payload" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("agent_type", "") or "")
except Exception:
    print("")
' 2>/dev/null)"
[ -n "$agent" ] || agent="${1:-}"

# NO agent identity = the MAIN SESSION, not a subagent. Since DEC-120 the orchestrator
# is a spawned agent and IS governed like any other; this carve-out now protects only
# the main session, which writes little: `## Approval` blocks and the cross-flow log.
# Never govern it — blocking it would make the harness unable to record your decisions.
[ -n "$agent" ] || exit 0

# Only harness agents are subject to domains.
case "$agent" in
  harness-*) ;;
  *) exit 0 ;;
esac

# Locate the project root WITHOUT depending on cwd. A hook's working directory is
# not guaranteed, and deriving root from pwd made this script fail OPEN whenever it
# ran from anywhere else — silently disabling enforcement rather than reporting it.
# This script lives at <root>/.claude/skills/harness/bin/, so walk up five levels.
_self="${BASH_SOURCE[0]:-$0}"
_selfdir="$(cd "$(dirname "$_self")" && pwd)"
_derived="$(cd "$_selfdir/../../../.." && pwd)"

root="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$root" ] || [ ! -r "$root/.harness/team-config.yaml" ]; then
  if [ -r "$_derived/.harness/team-config.yaml" ]; then
    root="$_derived"
  else
    root="${root:-$(pwd)}"
  fi
fi
manifest="$root/.harness/team-config.yaml"

target=$(printf '%s' "$payload" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    print(""); raise SystemExit
ti = d.get("tool_input", {}) or {}
# Write/Edit use file_path; NotebookEdit uses notebook_path.
print(ti.get("file_path") or ti.get("notebook_path") or "")
' 2>/dev/null)

# No parseable path -> do not block. A hook that blocks on its own parse failure
# would break every write the moment the payload shape changes.
[ -n "$target" ] || exit 0

# No manifest -> fail OPEN, loudly. Blocking every write in a project that has
# not run /harness-init would be worse than not enforcing.
if [ ! -r "$manifest" ]; then
  echo "check-domain: no $manifest — enforcement OFF (run /harness-init)." >&2
  exit 0
fi

domain_check() {
python3 - "$agent" "$target" "$manifest" "$root" <<'PY'
import sys, os, re

agent, target, manifest, root = sys.argv[1:5]

# Deliberately not using a YAML lib: this must run with zero dependencies on any
# machine. We read only two things per member — its name and its domain/shared
# path lists — so a narrow line scanner is sufficient and predictable.
lines = open(manifest, encoding="utf-8").read().splitlines()

def collect(section_owner):
    """Paths under the entry whose `name:` matches section_owner, plus shared."""
    mine, shared, cur = [], [], None
    for ln in lines:
        s = ln.strip()
        m = re.match(r"^-?\s*(?:name|- name):\s*(\S+)", s)
        if m:
            cur = m.group(1).strip('"\'')
            continue
        if s.startswith("shared:"):
            cur = "__shared__"
            continue
        pm = re.search(r"path:\s*([^,}\s]+)", s)
        if pm:
            p = pm.group(1).strip('"\'')
            if cur == section_owner and "read: true" not in s:
                mine.append(p)
            elif cur == "__shared__":
                shared.append(p)
    return mine, shared

globs, shared = collect(agent)

# Compare repo-relative, so an absolute tool path and a relative glob still meet.
rel = os.path.relpath(os.path.abspath(target), os.path.abspath(root))

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

if any(matches(r, g) for r in rel_candidates for g in globs):
    sys.exit(0)

if any(matches(r, g) for r in rel_candidates for g in shared):
    # Shared paths are owned by nobody and always serialized (DEC-85). Allow the
    # write, but say so — an unnoticed shared-file edit is how two agents collide.
    print(f"check-domain: {agent} is writing SHARED path {rel} "
          f"(owned by nobody, must be serialized).", file=sys.stderr)
    sys.exit(0)

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
PY
}

domain_check; rc=$?
[ "$rc" -eq 0 ] || exit "$rc"

# ---- STATE-FILE SHAPE GATE (DEC-150) ------------------------------------------------
# feature.yaml and STATE.md are read at every cycle/spawn, so they must stay
# index-sized. This gate denies the Write that starts the accretion — the 141KB
# feature.yaml observed in the field was built one read-modify-write at a time,
# and every increment passes the full content through this hook. Write only:
# the governed writers (orchestrator, leads) hold no Edit, and an Edit payload
# cannot be sized without reading the target.
# Payload rides an env var: `python3 -` takes its PROGRAM from stdin, so piping
# the payload alongside a heredoc silently loses it (the gate's first draft did
# exactly that and passed everything).
HOOK_PAYLOAD="$payload" python3 - "$target" "$root" <<'PY'
import sys, os, re, json

target, root = sys.argv[1:3]
try:
    d = json.loads(os.environ.get("HOOK_PAYLOAD") or "")
except Exception:
    sys.exit(0)
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
