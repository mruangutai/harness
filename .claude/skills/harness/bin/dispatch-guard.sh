#!/usr/bin/env bash
# PreToolUse hook (matcher: Task|Agent) — DEC-155/DEC-156: a harness agent never
# passes `model:` in a dispatch. The member's model is pinned in its agent
# frontmatter (DEC-152's tiers); a per-invocation parameter silently outranks the
# pin, re-deciding org design per-dispatch with nothing recording it. Observed
# live (kaya-ai FEAT-02, T-02): a lead's `model: "opus"` ran a sonnet-pinned doer
# on opus, unsanctioned and invisible to every gate.
#
# Registered in .claude/settings.json — NOT agent frontmatter (frontmatter
# PreToolUse hooks do not fire for spawned subagents, DEC-110):
#   "PreToolUse": [{ "matcher": "Task|Agent",
#     "hooks": [{ "type": "command",
#       "command": "${CLAUDE_PROJECT_DIR}/.agents/skills/harness/bin/dispatch-guard.sh" }] }]
#
# Only exit 2 blocks (DEC-100). Fail OPEN on our own parse failure — a guard that
# blocks every spawn the moment the payload shape changes is worse than no guard.
# The MAIN SESSION (no agent_type) is never governed: model choice at the user
# channel is the user's.
set -uo pipefail

payload=$(cat)

# T-08: resolved from BASH_SOURCE, never $PWD, so a test can point DISPATCH_GUARD_BIN at a
# copied tree and the guard imports THAT copy of inflight_registry.py.
GUARD_BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

printf '%s' "$payload" | HARNESS_GUARD_BIN_DIR="$GUARD_BIN_DIR" python3 -I -c '
import sys, json, os

try:
    d = json.load(sys.stdin)
except Exception as e:
    print(f"dispatch-guard: unreadable hook payload ({e}) — passing through.", file=sys.stderr)
    sys.exit(0)

agent = d.get("agent_type") or ""
if not agent.startswith("harness-"):
    sys.exit(0)  # main session or a non-harness agent — not governed.

ti = d.get("tool_input") or {}
model = ti.get("model")
if model:
    print(f"dispatch-guard: BLOCKED — {agent} passed model: {model!r} in a dispatch.",
          file=sys.stderr)
    print("  A member runs on the model pinned in its agent frontmatter — that pin is org design",
          file=sys.stderr)
    print("  (DEC-152 tiers), not a dispatch option. If this task genuinely needs a stronger model,",
          file=sys.stderr)
    print("  that is an ESCALATION: raise it in open_questions with the evidence and let it be",
          file=sys.stderr)
    print("  decided above you and recorded (DEC-155). Re-dispatch without the model parameter.",
          file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# T-08 — the single-flight claim (issue #551). EVERY branch below fails OPEN.
#
# NO APOSTROPHES ANYWHERE IN THIS BLOCK. The whole python program is one
# single-quoted shell argument, so a lone apostrophe closes it and bash then
# parses python as shell. That is why no comment here uses a possessive.
# ---------------------------------------------------------------------------
dispatched = ti.get("subagent_type") or ti.get("agent") or ""
if not dispatched.startswith("harness-"):
    # A gap of OURS, said out loud rather than swallowed — the precedent this file already
    # sets above, and that validate-digest.py sets again in its own pass-through line.
    if dispatched:
        print("dispatch-guard: dispatched persona %r is not a harness agent — no claim recorded."
              % (dispatched,), file=sys.stderr)
    else:
        print("dispatch-guard: no dispatched persona on this payload — no claim recorded.",
              file=sys.stderr)
    sys.exit(0)


# ---------------------------------------------------------------------------
# THE DISPATCH DECLARES ITS FEATURE (FEAT-42 T-18, issue #742). This is the ONE site in the
# whole system that can see a dispatch prompt: measured in
# FEAT-31/notes/probe-hook-payload-identity.md, a PreToolUse payload carries eleven keys and
# tool_input.prompt exists only on the DISPATCH payload. So this field fixes this gate and
# reaches no other hook.
#
# THIS IS THE ONE BRANCH HERE THAT FAILS CLOSED. Everything below passes through on its own
# failure, because a guard that blocks every spawn the moment a payload shape changes is
# worse than no guard. This one cannot: the declared feature is the only signal that says
# which checkout an agent was ASSIGNED to, and the agent process working directory does not
# follow its assignment. That is the defect, and a missing declaration is not a degraded
# answer -- it is no answer.
# ---------------------------------------------------------------------------
import re

FEATURE_RE = re.compile(r"(?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+")
prompt = ti.get("prompt") or ti.get("task") or ""
first_line = prompt.splitlines()[0] if prompt.splitlines() else ""
prefix = "HARNESS-FEATURE: "
declared = first_line[len(prefix):] if first_line.startswith(prefix) else ""
if not declared or not FEATURE_RE.fullmatch(declared):
    print("dispatch-guard: BLOCKED — this governed dispatch has no valid first-line feature.",
          file=sys.stderr)
    print("  The FIRST line of the prompt must be, spelled exactly:", file=sys.stderr)
    print("    HARNESS-FEATURE: FEAT-42-one-root-resolver", file=sys.stderr)
    print("  BUG-NN-slug is also valid. A later line or another id form is refused.",
          file=sys.stderr)
    sys.exit(2)

try:
    sys.path.insert(0, os.environ.get("HARNESS_GUARD_BIN_DIR") or ".")
    import harness_boundary as hb
    import inflight_registry as reg
except Exception as exc:
    print("dispatch-guard: registry libraries unavailable (%s) — passing through." % (exc,),
          file=sys.stderr)
    sys.exit(0)


def _root_for(flow):
    owner_root = hb.resolve_root(os.environ.get("HARNESS_GUARD_BIN_DIR") or os.getcwd(),
                                 strict=False)
    if not owner_root:
        return None
    try:
        for wt in hb.linked_worktrees(owner_root):
            if os.path.basename(wt) == flow:
                return wt
    except Exception:
        pass
    return owner_root


try:
    root = _root_for(declared)
except Exception as exc:
    root = None
    print("dispatch-guard: could not resolve the checkout for %s (%s) — no claim recorded."
          % (declared, exc), file=sys.stderr)
if not root:
    print("dispatch-guard: no checkout root for this dispatch — no claim recorded.",
          file=sys.stderr)
    sys.exit(0)

# T-09 -- a shell-less persona cannot resolve the feature tree itself. The
# dispatcher supplies the resolved value and this block checks it before claim.
try:
    owner_root = hb.resolve_root(os.environ.get("HARNESS_GUARD_BIN_DIR") or os.getcwd(),
                                 strict=False)
    tools_file = os.path.join(owner_root, ".omp", "agents", dispatched + ".md")
    raw_agent = open(tools_file, encoding="utf-8").read()
    frontmatter = raw_agent.split("---", 2)[1]
    tools_match = re.search(r"(?ms)^tools:\s*\n(.*?)(?=^[A-Za-z_-]+:|\Z)", frontmatter)
    if tools_match is None:
        raise ValueError("no tools key")
    has_bash = bool(re.search(r"(?m)^\s*-\s*bash\s*$", tools_match.group(1)))
except Exception as exc:
    print("dispatch-guard: could not read tool grants for %s (%s) -- passing through."
          % (dispatched, exc), file=sys.stderr)
    has_bash = True

if not has_bash:
    declared_root = None
    for prompt_line in prompt.splitlines():
        stripped = prompt_line.strip()
        if stripped.startswith("HARNESS-FEATURE-TREE-ROOT: "):
            declared_root = stripped[len("HARNESS-FEATURE-TREE-ROOT: "):]
            break
    if not declared_root:
        print("dispatch-guard: BLOCKED -- %s holds no shell and requires "
              "HARNESS-FEATURE-TREE-ROOT: from inflight_registry.py feature-root --feature %s."
              % (dispatched, declared), file=sys.stderr)
        sys.exit(2)
    if not os.path.isabs(declared_root):
        print("dispatch-guard: BLOCKED -- HARNESS-FEATURE-TREE-ROOT value must be absolute: %r"
              % (declared_root,), file=sys.stderr)
        sys.exit(2)
    try:
        expected_root = reg.feature_root(owner_root, declared)
    except Exception as exc:
        print("dispatch-guard: feature tree resolver failed (%s) -- passing through." % (exc,),
              file=sys.stderr)
    else:
        if os.path.realpath(declared_root) != os.path.realpath(expected_root):
            print("dispatch-guard: BLOCKED -- declared feature-tree root %s disagrees with resolver %s."
                  % (declared_root, expected_root), file=sys.stderr)
            sys.exit(2)

runtime = d.get("harness_runtime") or "claude"
supervisor_pid = d.get("supervisor_pid") if runtime == "omp" else None
if runtime == "omp" and (not isinstance(supervisor_pid, int) or supervisor_pid <= 0):
    print("dispatch-guard: OMP dispatch has no valid supervisor pid — passing through "
          "without a claim.", file=sys.stderr)
    sys.exit(0)

try:
    session = d.get("session_id")
    existing, expired = reg.live_claim(
        root, dispatched, session=session, feature=declared
    )
    if expired:
        print("dispatch-guard: expired %d stale claim(s) for %s."
              % (expired, dispatched), file=sys.stderr)
    if reg.is_single_flight(dispatched) and existing:
        command = reg.release_cmd(root, dispatched, feature=declared)
        for line in reg.refusal_lines(dispatched, existing, command):
            print(line, file=sys.stderr)
        sys.exit(2)
    receipt = reg.claim_with_receipt(
        root,
        dispatched,
        agent,
        d.get("cwd") or "",
        session=session,
        feature=declared,
        runtime=runtime,
        supervisor_pid=supervisor_pid,
    )
    if receipt is None:
        print("dispatch-guard: BLOCKED — single-flight claim raced for %s in %s."
              % (dispatched, declared), file=sys.stderr)
        sys.exit(2)
    print(json.dumps({
        "harness_claim": {
            "root": root,
            "feature": declared,
            "agent": dispatched,
            "claim_id": receipt.get("claim_id"),
        }
    }, sort_keys=True))
except SystemExit:
    raise
except Exception as exc:
    print("dispatch-guard: claim step failed (%s: %s) — passing through, the dispatch is NOT "
          "blocked." % (type(exc).__name__, exc), file=sys.stderr)
    sys.exit(0)

sys.exit(0)
'
exit $?
