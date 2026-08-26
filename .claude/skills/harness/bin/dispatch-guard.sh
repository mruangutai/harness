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

printf '%s' "$payload" | HARNESS_GUARD_BIN_DIR="$GUARD_BIN_DIR" python3 -c '
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
dispatched = ti.get("subagent_type") or ""   # the measured key path, see notes/research-FEAT-32-hook-payloads.md
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


def _root_from(payload):
    """THE ROOT COMES FROM THE PAYLOAD, not from where this script lives.

    Measured: the hook resolves through CLAUDE_PROJECT_DIR to the MAIN checkout while the
    payload cwd is the FEATURE worktree. One shared registry would refuse the FEAT-33 pm
    because the FEAT-32 pm is live — breaking parallel features to fix a within-feature
    defect. Operator ruling, recorded in D-06 terms as per-checkout.
    """
    start = payload.get("cwd") or (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or ""
    cur = os.path.abspath(start) if start else ""
    while cur and cur != os.path.dirname(cur):
        # THE MANIFEST FILE, not the .harness DIRECTORY. Probing the directory resolves
        # $HOME as a root in the global install -- B-7 verbatim, and case_20 of the
        # invariant suite catches it by name.
        if os.path.isfile(os.path.join(cur, ".harness", "team-config.yaml")):
            return cur
        cur = os.path.dirname(cur)
    return (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or None


root = _root_from(d)
if not root:
    print("dispatch-guard: no checkout root for this dispatch — no claim recorded.",
          file=sys.stderr)
    sys.exit(0)

try:
    sys.path.insert(0, os.environ.get("HARNESS_GUARD_BIN_DIR") or ".")
    import inflight_registry as reg
except Exception as exc:
    print("dispatch-guard: inflight_registry unavailable (%s) — passing through." % (exc,),
          file=sys.stderr)
    sys.exit(0)

try:
    existing, expired = reg.live_claim(root, dispatched)
    if expired:
        print("dispatch-guard: expired %d stale claim(s) for %s." % (expired, dispatched),
              file=sys.stderr)
    if reg.is_single_flight(dispatched) and existing:
        for line in reg.refusal_lines(dispatched, existing, reg.RELEASE_ALL_CMD):
            print(line, file=sys.stderr)
        sys.exit(2)
    # A claim for EVERY harness-* persona, not only the single-flight ones. D-06 and D-09 both
    # stand on the dispatcher edge existing on disk, and this is the ONE moment both identities
    # — dispatcher and dispatched — are in a single payload.
    reg.claim(root, dispatched, agent, d.get("cwd") or "")
except SystemExit:
    raise
except Exception as exc:
    # claim() DOES raise. Lock contention raises MergeRefusal at the deadline; the docstring
    # claimed otherwise and has been corrected. Catching it is what makes the D-07 fail-open
    # posture true rather than aspirational — an uncaught exception here exits non-zero.
    print("dispatch-guard: claim step failed (%s: %s) — passing through, the dispatch is NOT "
          "blocked." % (type(exc).__name__, exc), file=sys.stderr)
    sys.exit(0)

sys.exit(0)
'
exit $?
