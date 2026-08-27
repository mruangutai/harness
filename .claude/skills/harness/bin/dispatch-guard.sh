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

FEATURE_RE = re.compile(r"HARNESS-FEATURE:[ \t]*(\S+)[ \t]*")

prompt = ti.get("prompt") or ""
declared = None
for line in prompt.splitlines():
    m = FEATURE_RE.fullmatch(line.strip())
    if m:
        declared = m.group(1)
        break

if not declared:
    print("dispatch-guard: BLOCKED — this governed dispatch declares no feature.",
          file=sys.stderr)
    print("  The FIRST line of the prompt must be, spelled exactly:", file=sys.stderr)
    print("    HARNESS-FEATURE: FEAT-42-one-root-resolver", file=sys.stderr)
    print("  with the id of the feature this dispatch belongs to. It is the only signal that",
          file=sys.stderr)
    print("  tells this gate which checkout you were assigned to; your working directory does",
          file=sys.stderr)
    print("  not follow your assignment. Re-dispatch with the line.", file=sys.stderr)
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
    """The checkout the DECLARED feature is worked in.

    NO GIT SUBPROCESS: this runs ahead of every governed dispatch, and DEC-193 forbids one on
    the governed-write path anyway. owner_root comes from resolve_root, the one resolver, given
    HARNESS_GUARD_BIN_DIR -- the bash wrapper set that from BASH_SOURCE, because this program is
    fed to python3 -c and has no __file__ of its own. strict=False so an unrooted tree yields
    the derived answer rather than raising: every branch in this gate but the declaration check
    fails open. The worktree list comes from reading the pointer files under .git/worktrees; the
    worktrees come from reading the pointer files under .git/worktrees. A worktree whose
    directory segment equals the declared id IS the root; if no worktree carries that id the
    feature is being worked in the main checkout and owner_root is the root.

    THE REGISTRY STAYS PER-CHECKOUT. One shared file would refuse a second feature pm while
    the first feature pm is live, breaking parallel features to fix a within-feature defect.
    What changed is the INPUT, not the shape: the claim now lands where the ASSIGNMENT says
    rather than where the dispatcher happened to be standing.
    """
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

try:
    # THE SESSION IS PASSED SO A FOREIGN SESSION STALE CLAIM IS NOT COUNTED LIVE (T-06/T-17).
    session = d.get("session_id")
    existing, expired = reg.live_claim(root, dispatched, session=session)
    if expired:
        print("dispatch-guard: expired %d stale claim(s) for %s." % (expired, dispatched),
              file=sys.stderr)
    if reg.is_single_flight(dispatched) and existing:
        # THE REMEDY IS ABSOLUTE AND NAMES ONE AGENT, never release-all: that command sets the
        # registry to an empty object and wipes every claim of every agent, and on 2026-08-26
        # following the old printed advice would have destroyed a live claim.
        for line in reg.refusal_lines(dispatched, existing, reg.release_cmd(root, dispatched)):
            print(line, file=sys.stderr)
        sys.exit(2)
    # A claim for EVERY harness-* persona, not only the single-flight ones. D-06 and D-09 both
    # stand on the dispatcher edge existing on disk, and this is the ONE moment both identities
    # — dispatcher and dispatched — are in a single payload.
    reg.claim(root, dispatched, agent, d.get("cwd") or "", session=session)
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
